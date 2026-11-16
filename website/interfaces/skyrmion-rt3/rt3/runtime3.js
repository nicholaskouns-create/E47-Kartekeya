// SKYRMION RT3 · flight runtime.
// Model isolation is enforced here and re-checked every step: a conventional craft
// never touches the E47 drive, and an experimental craft is handed exactly zero
// aerodynamic load. Neither can quietly borrow the other's physics.
import {clamp,cross,norm,qMul,qNormalize,qRotate,qRotateInv,qToEuler} from './math.js';
import {standardAtmosphere,windProfile,DrydenTurbulence} from './atmosphere.js';
import {normalGravity,integrateGeodetic,transportRateNed,earthRateNed,rangeMeters,curvature} from './geodesy.js';
import {AeroModel} from './aero.js';
import {PropulsionModel,MassModel} from './propulsion.js';
import {GearModel} from './gear.js';
import {FlightControlSystem} from './fcs.js';
import {E47Drive} from './e47-drive.js';
import {DormandPrince,rk4} from './integrator.js';
import {VEHICLES,VEHICLE_ORDER,vehicle as pickVehicle} from './vehicles.js';
import {ProofTelemetry,stateIssue,copyState} from './telemetry.js';

// Gaussian elimination with partial pivoting, used only by the trim solver.
function solve3(A,b){
 const M=[[...A[0],b[0]],[...A[1],b[1]],[...A[2],b[2]]];
 for(let c=0;c<3;c++){
  let piv=c;for(let r=c+1;r<3;r++)if(Math.abs(M[r][c])>Math.abs(M[piv][c]))piv=r;
  if(Math.abs(M[piv][c])<1e-14)return null;
  [M[c],M[piv]]=[M[piv],M[c]];
  for(let r=0;r<3;r++){if(r===c)continue;const f=M[r][c]/M[c][c];for(let k=c;k<4;k++)M[r][k]-=f*M[c][k]}
 }
 return [M[0][3]/M[0][0],M[1][3]/M[1][1],M[2][3]/M[2][2]];
}
const CONTROLS=()=>({throttle:.72,pitch:0,roll:0,yaw:0,flap:0,gear:0,brake:0,afterburner:0,wheelBrake:0});

export class SkyrmionRuntime3 extends EventTarget{
 constructor({fixedStepHz=120,adaptive=true,turbulence=.6,spawn={},groundSampler=null}={}){
  super();
  if(!Number.isFinite(fixedStepHz)||fixedStepHz<60||fixedStepHz>480)throw new Error('fixedStepHz must be 60-480');
  this.schema='SKYRMION-RUNTIME-3.0';
  this.fixedStepHz=fixedStepHz;this.dt=1/fixedStepHz;this.adaptive=adaptive;
  this.integrator=new DormandPrince();this.suggestedDt=this.dt;
  this.turbulence=new DrydenTurbulence({intensity:turbulence});
  this.wind={speed10:6,direction10:.6,roughness:.12};
  this.groundSampler=groundSampler;
  this.spawn={lat:36.1699,lon:-115.1398,altitudeM:3658,speedMps:216,heading:0,...spawn};
  this.origin={...this.spawn};
  this.proof=new ProofTelemetry();
  this.accumulator=0;this.lastNow=0;this.running=false;this.raf=0;this.stepCount=0;this.fault=null;this.overstress=null;
  this.frames=[];this.recording=true;
  this.load('f16',this.spawn);
 }

 // ---- construction -------------------------------------------------------
 load(id,spawn=this.spawn){
  const v=pickVehicle(id);
  if(!VEHICLES[id])throw new Error('Unknown craft '+id);
  const conventional=v.evidence==='conventional';
  this.vehicle=v;this.vehicleIndex=VEHICLE_ORDER.indexOf(id);
  this.mass=new MassModel(v);this.mass.reset(1);
  this.aero=conventional?new AeroModel(v):null;
  this.engine=conventional?new PropulsionModel(v):null;
  this.gear=conventional?new GearModel(v):null;
  this.fcs=conventional?new FlightControlSystem(v):null;
  this.drive=conventional?null:new E47Drive(v.drive);
  const heading=spawn.heading??0;
  this.state={
   t:0,position:{lat:spawn.lat,lon:spawn.lon,altitudeM:spawn.altitudeM},
   velocityBody:[spawn.speedMps,0,0],
   quaternion:[Math.cos(heading/2),0,0,Math.sin(heading/2)],
   omegaBody:[0,0,0],controls:CONTROLS(),vehicleId:id,
   accelBody:[0,0,0],last:{alpha:0,beta:0,mach:0,qbar:0,CL:0,CD:0,V:spawn.speedMps,loadFactor:1,separation:0,regime:'subsonic'}
  };
  this.command={...CONTROLS()};
  this.turbulence.reset();this.gust=[0,0,0];
  const issue=stateIssue(this.state);
  if(issue)throw new Error(issue);
  // An aircraft on the ramp has no trim state. Trimming at taxi speed produces a
  // saturated elevator that then poisons the control law all the way down the
  // runway, so below flying speed the craft is simply set up on the ground.
  const flying=conventional&&(spawn.speedMps??0)>(v.vRotateMps??70)*1.15;
  if(conventional&&flying)this.trimResult=this.trim(heading);
  else{
   this.trimResult=null;
   if(conventional){
    this.state.controls.throttle=0;this.state.controls.gear=1;this.state.controls.pitch=0;
    this.command={...this.command,throttle:0,gear:1,pitch:0,roll:0,yaw:0};
    this.engine.spool.reset(this.engine.spool.idle);this.fcs.reset(0);
   }
  }
  this.lastAero=conventional?this.aero.forces(this.state,this.environment(),{groundHeightM:this.groundClearance(),massKg:this.mass.massKg}):null;
  this.lastPropulsion=this.propulsionReceipt();
  this.lastGear=null;this.fault=null;this.overstress=null;this.accumulator=0;this.frames=[];
  this.proof=new ProofTelemetry();this.lastGood=copyState(this.state);
  this.inspect();
  return this.state;
 }
 setVehicle(id){
  // Only a valid geographic position crosses the selection boundary. Dynamics,
  // controls, fuel, drive state and receipts are all constructed afresh.
  const p=stateIssue(this.state)?this.lastGood.position:this.state.position;
  const heading=qToEuler(this.state.quaternion).yaw;
  this.load(id,{...this.spawn,...p,heading});this.emit();return this.state;
 }
 reset(){this.load(this.vehicle.id,this.spawn);this.emit()}
 teleport(position){
  const base=stateIssue(this.state)?this.lastGood.position:this.state.position;
  this.load(this.vehicle.id,{...this.spawn,...base,...position});this.emit();
 }

 // ---- environment --------------------------------------------------------
 groundElevation(){
  if(typeof this.groundSampler!=='function')return 0;
  const h=this.groundSampler(this.state.position.lat,this.state.position.lon);
  return Number.isFinite(h)?h:0;
 }
 groundClearance(){return this.state.position.altitudeM-this.groundElevation()}
 environment(state=this.state){
  const atm=standardAtmosphere(state.position.altitudeM);
  const agl=Math.max(0,state.position.altitudeM-this.groundElevation());
  const base=windProfile({...this.wind,altitudeAglM:agl});
  const windNed=[base[0]+this.gust[0],base[1]+this.gust[1],base[2]+this.gust[2]];
  return {...atm,gravity:normalGravity(state.position.altitudeM,state.position.lat),
   windNed,altitudeAglM:agl,mach:norm(state.velocityBody)/atm.speedOfSound};
 }

 // ---- loads --------------------------------------------------------------
 propulsionReceipt(){
  if(this.engine)return this.engine.forces(this.state,this.environment(),this.mass.fuelKg);
  return this.drive.forces(this.state,this.mass.massKg,this.mass.inertia,this.drive.snapshot());
 }
 // Every force acting on the airframe, assembled for one integrator stage.
 loads(state,env,driveSnapshot){
  if(this.aero){
   const aero=this.aero.forces(state,env,{groundHeightM:Math.max(0,state.position.altitudeM-this.groundElevation()),massKg:this.mass.massKg});
   const propulsion=this.engine.forces(state,{...env,mach:aero.mach},this.mass.fuelKg);
   const velocityNed=qRotate(state.quaternion,state.velocityBody);
   const gearLoad=this.gear.forces(state,env,{groundElevationM:this.groundElevation(),velocityNed});
   return {aero,propulsion,gear:gearLoad,e47:null};
  }
  const zero={forceBody:[0,0,0],momentBody:[0,0,0],alpha:0,beta:0,mach:env.mach??0,qbar:0,CL:0,CD:0,
   V:norm(state.velocityBody),loadFactor:0,separation:0,regime:'n/a'};
  return {aero:zero,propulsion:this.drive.forces(state,this.mass.massKg,this.mass.inertia,driveSnapshot),
   gear:{forceBody:[0,0,0],momentBody:[0,0,0],weightOnWheels:false,maxCompression:0,contacts:0,struts:[]},
   e47:driveSnapshot};
 }

 // ---- integration --------------------------------------------------------
 derivative(y,state,env,mass,inertia,driveSnapshot,capture){
  const s={...state,velocityBody:[y[0],y[1],y[2]],omegaBody:[y[3],y[4],y[5]],
   quaternion:qNormalize([y[6],y[7],y[8],y[9]])};
  const L=this.loads(s,env,driveSnapshot);
  if(capture)capture.value=L;
  const omega=s.omegaBody;
  const gBody=qRotateInv(s.quaternion,[0,0,env.gravity*mass]);
  // Earth rate and transport rate: the navigation frame is itself rotating, which
  // is a real acceleration at these speeds even though it is a small one.
  const velocityNed=qRotate(s.quaternion,s.velocityBody);
  const rot=earthRateNed(s.position.lat).map((w,i)=>2*w+transportRateNed(s.position,velocityNed)[i]);
  const frameAccelNed=cross(rot,velocityNed);
  const frameBody=qRotateInv(s.quaternion,frameAccelNed);
  const coriolis=cross(omega,s.velocityBody);
  const gyro=cross(omega,[inertia[0]*omega[0],inertia[1]*omega[1],inertia[2]*omega[2]]);
  const acc=[0,1,2].map(i=>
   (gBody[i]+L.aero.forceBody[i]+L.propulsion.forceBody[i]+L.gear.forceBody[i])/mass
   -coriolis[i]-frameBody[i]);
  const ang=[0,1,2].map(i=>
   (L.aero.momentBody[i]+L.propulsion.momentBody[i]+L.gear.momentBody[i]-gyro[i])/inertia[i]);
  const qd=qMul(s.quaternion,[0,omega[0],omega[1],omega[2]]).map(v=>v*.5);
  return [...acc,...ang,...qd];
 }

 step(dt=this.dt){
  if(this.fault)return this.telemetry();
  const issue=stateIssue(this.state);
  if(issue)return this.reject(issue,this.state.t);
  const state=copyState(this.state);
  const env0=this.environment(state);

  // Per-step bookkeeping happens exactly once, outside the integrator stages:
  // hysteresis, spool, turbulence and the spectral drive are stateful and must not
  // be advanced four or seven times per step.
  if(this.aero){
   this.fcs.step(state,this.command,env0,this.state.last,dt);
   this.aero.separation.step(this.state.last.alpha,this.vehicle.limits.alpha,dt);
   this.engine.advance(state.controls.throttle,dt);
  }else{
   for(const axis of ['roll','pitch','yaw','throttle']){
    const rate=axis==='throttle'?1.8:2.4;
    state.controls[axis]+=clamp(this.command[axis]-state.controls[axis],-rate*dt,rate*dt);
   }
  }
  this.gust=this.turbulence.step(dt,Math.max(12,norm(state.velocityBody)),env0.altitudeAglM,this.wind.speed10);
  const driveSnapshot=this.drive
   ? this.drive.step({alpha:0,mach:env0.mach,controlNorm:Math.hypot(state.controls.pitch,state.controls.roll,state.controls.yaw)},dt)
   : null;

  const env=this.environment(state);
  const mass=this.mass.massKg,inertia=this.mass.inertia;
  const capture={value:null};
  const y0=[...state.velocityBody,...state.omegaBody,...state.quaternion];
  const f=y=>this.derivative(y,state,env,mass,inertia,driveSnapshot,null);
  let y;
  if(this.adaptive){
   const r=this.integrator.integrate(y0,dt,f,this.suggestedDt);
   y=r.y;this.suggestedDt=r.nextDt;
  }else y=rk4(y0,dt,f).y;

  const velocityNedBefore=qRotate(state.quaternion,state.velocityBody);
  state.velocityBody=[y[0],y[1],y[2]];
  state.omegaBody=[y[3],y[4],y[5]];
  state.quaternion=qNormalize([y[6],y[7],y[8],y[9]]);
  const velocityNedAfter=qRotate(state.quaternion,state.velocityBody);
  // Trapezoidal position update: second order in dt, which matters over a long flight.
  const meanNed=velocityNedBefore.map((v,i)=>(v+velocityNedAfter[i])/2);
  state.position=integrateGeodetic(state.position,meanNed,dt);
  state.t+=dt;

  // Final loads at the committed state: these are the numbers reported, and the
  // same evaluation supplies the body acceleration.
  const finalLoads=this.loads(state,this.environment(state),driveSnapshot);
  this.derivativeCache=finalLoads;
  const g2=this.environment(state).gravity;
  const gBody=qRotateInv(state.quaternion,[0,0,g2*mass]);
  state.accelBody=[0,1,2].map(i=>
   (gBody[i]+finalLoads.aero.forceBody[i]+finalLoads.propulsion.forceBody[i]+finalLoads.gear.forceBody[i])/mass);
  state.last={alpha:finalLoads.aero.alpha,beta:finalLoads.aero.beta,mach:finalLoads.aero.mach,
   qbar:finalLoads.aero.qbar,CL:finalLoads.aero.CL,CD:finalLoads.aero.CD,V:finalLoads.aero.V,
   loadFactor:finalLoads.aero.loadFactor,separation:finalLoads.aero.separation,regime:finalLoads.aero.regime};

  if(this.engine)this.mass.burn(this.engine.fuelFlow,dt);
  // The surface is a hard stop. If the integrator still put the airframe below it,
  // the descent is arrested rather than the altitude being silently reset, which
  // would let the aircraft plough along underground at full rate of descent.
  const contactFloor=this.groundElevation()+.05;
  if(state.position.altitudeM<contactFloor){
   const ned=qRotate(state.quaternion,state.velocityBody);
   const impact=ned[2];
   if(impact>0){
    ned[2]=0;
    state.velocityBody=qRotateInv(state.quaternion,ned);
    state.omegaBody=state.omegaBody.map(w=>w*.2);
   }
   state.position.altitudeM=contactFloor;
   const limit=this.vehicle.gearSinkLimitMps??4.5;
   if(impact>limit&&!this.overstress)
    this.overstress={reason:'Touchdown rate exceeded gear limit',sinkRateMps:impact,limitMps:limit,t:state.t};
  }

  const nextIssue=stateIssue(state);
  if(nextIssue)return this.reject(nextIssue,state.t);
  this.state=state;this.lastGood=copyState(state);
  this.lastAero=finalLoads.aero;this.lastPropulsion=finalLoads.propulsion;this.lastGear=finalLoads.gear;
  this.lastE47=finalLoads.e47;this.stepCount++;
  this.inspect();
  if(this.recording&&this.stepCount%12===0)this.record();
  return this.telemetry();
 }

 // ---- trim ---------------------------------------------------------------
 // Newton solve on the force model that actually flies, rather than on a reduced
 // approximation of it. Unknowns are angle of attack, elevator and throttle;
 // residuals are vertical acceleration, along-track acceleration and pitch angular
 // acceleration. Trimming against the real model is why the aircraft is handed over
 // in equilibrium instead of settling into a phugoid.
 trim(heading=0){
  const v=this.vehicle,state=this.state,V=norm(state.velocityBody);
  const mass=this.mass.massKg,inertia=this.mass.inertia;
  // Power is one continuous variable: 0-1 is dry throttle, 1-2 opens the
  // afterburner. An SR-71 cannot hold level flight down low on dry thrust, so a
  // solver that could only move the throttle would simply fail on it.
  const apply=([alpha,elev,power])=>{
   const p=clamp(power,Math.max(this.engine.spool.idle,.001),2),throttle=Math.min(1,p),ab=clamp(p-1,0,1);
   state.quaternion=qNormalize([Math.cos(alpha/2),0,Math.sin(alpha/2),0]);
   state.velocityBody=[V*Math.cos(alpha),0,V*Math.sin(alpha)];
   state.controls.pitch=clamp(elev,-1,1);
   state.controls.throttle=throttle;state.controls.afterburner=ab;
   this.engine.spool.reset(throttle);
  };
  const residual=x=>{
   apply(x);
   const env=this.environment(state);
   const aero=this.aero.forces(state,env,{groundHeightM:1e6,massKg:mass});
   const prop=this.engine.forces(state,{...env,mach:aero.mach},this.mass.fuelKg);
   const gBody=qRotateInv(state.quaternion,[0,0,env.gravity*mass]);
   const fBody=[0,1,2].map(i=>gBody[i]+aero.forceBody[i]+prop.forceBody[i]);
   const aNed=qRotate(state.quaternion,fBody.map(f=>f/mass));
   // The navigation frame rotates under the aircraft. Trimming without that term
   // leaves a small standing acceleration that slowly excites the phugoid.
   const vNed=qRotate(state.quaternion,state.velocityBody);
   const rot=earthRateNed(state.position.lat).map((w,i)=>2*w+transportRateNed(state.position,vNed)[i]);
   const frame=cross(rot,vNed);
   return [aNed[2]-frame[2],aNed[0]-frame[0],aero.momentBody[1]/inertia[1]];
  };
  const idle=this.engine.spool.idle;
  let x=[.03,0,Math.max(idle,.6)];
  for(let iter=0;iter<40;iter++){
   const r0=residual(x);
   if(Math.hypot(...r0)<1e-9)break;
   // Numeric Jacobian: three extra model evaluations per iteration, which costs
   // nothing once and saves the aircraft wallowing for the next two minutes.
   const J=[[0,0,0],[0,0,0],[0,0,0]],h=[1e-6,1e-6,1e-6];
   for(let c=0;c<3;c++){
    const xp=[...x];xp[c]+=h[c];
    const rp=residual(xp);
    for(let rI=0;rI<3;rI++)J[rI][c]=(rp[rI]-r0[rI])/h[c];
   }
   const d=solve3(J,r0.map(r=>-r));
   if(!d)break;
   const relax=iter<4?.6:1;
   x=[clamp(x[0]+d[0]*relax,-.3,v.limits.alpha),clamp(x[1]+d[1]*relax,-1,1),clamp(x[2]+d[2]*relax,Math.max(idle,.001),2)];
  }
  const [alpha,elev,power]=x;
  const throttle=Math.min(1,clamp(power,Math.max(idle,.001),2)),afterburner=clamp(power-1,0,1);
  apply(x);
  // Rotate the solved longitudinal trim onto the requested heading.
  state.quaternion=qNormalize(qMul([Math.cos(heading/2),0,0,Math.sin(heading/2)],[Math.cos(alpha/2),0,Math.sin(alpha/2),0]));
  this.command={...this.command,throttle,afterburner,pitch:0,roll:0,yaw:0};
  this.fcs.reset(elev);
  const env=this.environment(state);
  const aero=this.aero.forces(state,env,{groundHeightM:1e6,massKg:mass});
  state.last={alpha:aero.alpha,beta:aero.beta,mach:aero.mach,qbar:aero.qbar,CL:aero.CL,CD:aero.CD,
   V:aero.V,loadFactor:aero.loadFactor,separation:0,regime:aero.regime};
  const r=residual(x);
  apply(x);
  state.quaternion=qNormalize(qMul([Math.cos(heading/2),0,0,Math.sin(heading/2)],[Math.cos(alpha/2),0,Math.sin(alpha/2),0]));
  return {alpha,pitch:elev,throttle,afterburner,mach:aero.mach,residual:Math.hypot(...r)};
 }

 // ---- integrity ----------------------------------------------------------
 reject(reason,attemptedTime){
  this.fault={reason,vehicleId:this.vehicle.id,attemptedTime:Number.isFinite(attemptedTime)?attemptedTime:null};
  this.state=copyState(this.lastGood);this.inspect();return this.telemetry();
 }
 inspect(){
  return this.proof.inspect({
   state:this.state,vehicle:this.vehicle,mass:this.mass,env:this.environment(),
   e47:this.drive?this.drive.snapshot():null,propulsion:this.lastPropulsion,
   gear:this.lastGear,fixedStepHz:this.fixedStepHz,fault:this.fault,
   integrator:this.adaptive?this.integrator.stats():{schema:'RT3-RK4',accepts:this.stepCount,rejects:0}
  });
 }

 // ---- output -------------------------------------------------------------
 telemetry(){
  const e=qToEuler(this.state.quaternion),last=this.state.last;
  const env=this.environment(),ned=qRotate(this.state.quaternion,this.state.velocityBody);
  return {
   schema:this.schema,t:this.state.t,vehicleId:this.vehicle.id,vehicleName:this.vehicle.name,
   evidence:this.vehicle.evidence,
   position:{...this.state.position},
   altitude_m:this.state.position.altitudeM,altitude_agl_m:env.altitudeAglM,
   speed:norm(this.state.velocityBody),
   groundSpeed:Math.hypot(ned[0],ned[1]),verticalSpeed:-ned[2],
   heading:(e.yaw*180/Math.PI+360)%360,pitch:e.pitch*180/Math.PI,roll:e.roll*180/Math.PI,
   bodyRates:{roll:this.state.omegaBody[0],pitch:this.state.omegaBody[1],yaw:this.state.omegaBody[2]},
   aero:{alpha:last.alpha,beta:last.beta,mach:last.mach,qbar:last.qbar,CL:last.CL,CD:last.CD,
    loadFactor:last.loadFactor,separation:last.separation,regime:last.regime},
   mass:{totalKg:this.mass.massKg,fuelKg:this.mass.fuelKg,fuelFraction:this.mass.fuelFraction},
   environment:{density:env.density,temperatureK:env.temperatureK,pressurePa:env.pressurePa,
    speedOfSound:env.speedOfSound,gravity:env.gravity,windNed:env.windNed,gust:[...this.gust]},
   gear:this.gear&&this.lastGear?{weightOnWheels:this.lastGear.weightOnWheels,contacts:this.lastGear.contacts,
    maxCompression:this.lastGear.maxCompression,touchdownRateMps:this.gear.touchdownRateMps}:null,
   limiter:this.fcs?{...this.fcs.limiter}:null,
   controls:{...this.state.controls},
   range_m:rangeMeters(this.origin,this.state.position),
   e47:this.drive?this.drive.snapshot():null,
   propulsion:this.lastPropulsion?.receipt??null,
   proof:this.proof.last,fault:this.fault,overstress:this.overstress,steps:this.stepCount
  };
 }
 record(){
  this.frames.push({t:this.state.t,vehicleId:this.vehicle.id,position:{...this.state.position},
   quaternion:[...this.state.quaternion],velocityBody:[...this.state.velocityBody],
   omegaBody:[...this.state.omegaBody],controls:{...this.state.controls},fuelKg:this.mass.fuelKg});
  if(this.frames.length>7200)this.frames.shift();
 }
 setControls(c){
  for(const axis of ['throttle','pitch','roll','yaw','flap','gear','brake','afterburner','wheelBrake'])
   if(Number.isFinite(c[axis]))
    this.command[axis]=clamp(c[axis],['pitch','roll','yaw'].includes(axis)?-1:0,1);
 }
 setWind(next){this.wind={...this.wind,...next}}
 emit(){this.dispatchEvent(new CustomEvent('telemetry',{detail:this.telemetry()}))}
 start(){
  if(this.running||typeof requestAnimationFrame!=='function')return;
  this.running=true;this.lastNow=0;this.raf=requestAnimationFrame(this.frame);
 }
 stop(){this.running=false;if(this.raf)cancelAnimationFrame(this.raf);this.raf=0}
 frame=now=>{
  if(!this.running)return;
  if(!this.lastNow)this.lastNow=now;
  const elapsed=Math.max(0,Math.min(.05,(now-this.lastNow)/1000));
  this.lastNow=now;this.accumulator+=elapsed;
  let n=0;
  while(this.accumulator>=this.dt&&n<12){this.step();this.accumulator-=this.dt;n++}
  this.emit();this.raf=requestAnimationFrame(this.frame);
 };
}
export {VEHICLES,VEHICLE_ORDER};
