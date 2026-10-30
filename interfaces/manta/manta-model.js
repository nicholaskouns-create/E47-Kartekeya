import {SixDOFPhysics} from '../skyrmion/runtime2/physics-6dof.js';
import {WorldEngine} from '../skyrmion/runtime2/world-engine.js';

const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const norm=v=>Math.hypot(...v);

export const MANTA_VERSION='1.0.0';
export const MISSION_DURATION_S=48;
export const FIXED_STEP_HZ=120;
export const DT=1/FIXED_STEP_HZ;

export const MORPH_AXES=Object.freeze({
  span:{min:-0.18,max:0.22,rate:0.12},
  sweep:{min:-0.20,max:0.35,rate:0.18},
  camber:{min:-0.16,max:0.20,rate:0.16},
  twist:{min:-0.18,max:0.18,rate:0.18},
  thickness:{min:-0.10,max:0.12,rate:0.10},
  stiffness:{min:0,max:1,rate:0.45}
});

export const REFERENCE=Object.freeze({
  dryMassKg:6000,
  fuelKg:1200,
  wing:{area:46,span:18,chord:3.05,sweepRad:0.48},
  inertia:[68000,90000,125000],
  maxThrustN:145000,
  aero:{CL0:0.16,CLa:4.25,CD0:0.026,k:0.075,Cm0:0.018,Cma:-0.58,Clp:-0.38,Cnr:-0.25},
  limits:{alpha:0.58,beta:0.35}
});

export function missionCommand(t){
  if(t<8) return {throttle:.78,pitch:.018,roll:0,yaw:0,morph:{span:.05,sweep:.03,camber:.08,twist:.02,thickness:0,stiffness:.58},phase:'CLIMB'};
  if(t<16) return {throttle:.82,pitch:.012,roll:.08,yaw:.01,morph:{span:.14,sweep:-.08,camber:.14,twist:.08,thickness:.03,stiffness:.78},phase:'TURN'};
  if(t<26) return {throttle:.90,pitch:-.008,roll:0,yaw:0,morph:{span:-.08,sweep:.28,camber:-.04,twist:-.03,thickness:-.04,stiffness:.84},phase:'DASH'};
  if(t<36) return {throttle:.86,pitch:.055,roll:-.05,yaw:-.008,morph:{span:.20,sweep:-.12,camber:.18,twist:.12,thickness:.06,stiffness:.92},phase:'PULL'};
  return {throttle:.74,pitch:0,roll:0,yaw:0,morph:{span:0,sweep:0,camber:0,twist:0,thickness:0,stiffness:.62},phase:'RECOVER'};
}

class MorphPlant{
  constructor(enabled=true){
    this.enabled=enabled;
    this.state={span:0,sweep:0,camber:0,twist:0,thickness:0,stiffness:.62};
    this.rate={span:0,sweep:0,camber:0,twist:0,thickness:0,stiffness:0};
    this.boundHits=0;
    this.energyJ=0;
  }
  step(target,dt){
    let power=0;
    for(const [axis,lim] of Object.entries(MORPH_AXES)){
      const tgt=this.enabled?clamp(target[axis]??0,lim.min,lim.max):(axis==='stiffness'?.62:0);
      const err=tgt-this.state[axis],dv=clamp(err,-lim.rate*dt,lim.rate*dt);
      this.rate[axis]=dv/dt;
      this.state[axis]+=dv;
      if(this.enabled && (target[axis]<lim.min||target[axis]>lim.max))this.boundHits++;
      const axisWeight={span:7.5e4,sweep:8.5e4,camber:5.2e4,twist:4.8e4,thickness:4.2e4,stiffness:2.6e4}[axis];
      power += axisWeight*this.rate[axis]*this.rate[axis] + (axis==='stiffness'?4200*this.state.stiffness:0);
    }
    if(!this.enabled)power=0;
    this.energyJ += power*dt;
    return power;
  }
}

export class MantaABRuntime{
  constructor(){
    this.world=new WorldEngine();
    this.physics=new SixDOFPhysics();
    this.reset();
  }
  makeVehicle(id){
    return {id,name:id==='manta-morph'?'MANTA MORPH':'FIXED BASELINE',evidence:'experimental-simulation',massKg:REFERENCE.dryMassKg+REFERENCE.fuelKg,inertia:[...REFERENCE.inertia],wing:{...REFERENCE.wing}};
  }
  makeCase(id,morphEnabled){
    const vehicle=this.makeVehicle(id);
    const state=this.physics.createState(vehicle,{lat:36.1699,lon:-115.1398,altitudeM:3658,speedMps:216,heading:0});
    state.controls={throttle:.76,pitch:0,roll:0,yaw:0};
    return {vehicle,state,morph:new MorphPlant(morphEnabled),fuelKg:REFERENCE.fuelKg,mdot:0,morphPowerW:0,peakQ:0,peakAlpha:0,peakG:0,distanceM:0,initial:{...state.position},path:[],lastCoeff:{CL:0,CD:0,Cm:0}};
  }
  reset(){
    this.t=0;this.running=false;this.done=false;this.frame=0;
    this.morphCase=this.makeCase('manta-morph',true);
    this.baseCase=this.makeCase('manta-fixed',false);
  }
  derived(c){
    const s=c.morph.state,base=REFERENCE;
    const span=base.wing.span*(1+0.42*s.span);
    const area=base.wing.area*(1+0.20*s.span+0.10*s.camber-0.05*s.sweep);
    const chord=area/span;
    const sweepRad=base.wing.sweepRad+0.72*s.sweep;
    const mass=REFERENCE.dryMassKg+c.fuelKg;
    const mr=mass/(REFERENCE.dryMassKg+REFERENCE.fuelKg);
    const inertia=[
      base.inertia[0]*mr*(1+0.82*s.span-0.18*s.sweep+0.12*s.thickness),
      base.inertia[1]*mr*(1+0.24*s.span+0.44*s.sweep+0.08*s.thickness),
      base.inertia[2]*mr*(1+0.66*s.span+0.22*s.sweep+0.10*s.thickness)
    ].map(v=>Math.max(4000,v));
    return {span,area,chord,sweepRad,mass,inertia};
  }
  controls(state,cmd,dt){
    for(const axis of ['roll','pitch','yaw','throttle']){
      const rate=axis==='throttle'?1.6:2.2;
      const lo=axis==='throttle'?0:-1;
      state.controls[axis]=clamp(state.controls[axis]+clamp(cmd[axis]-state.controls[axis],-rate*dt,rate*dt),lo,1);
    }
  }
  aero(c,state,world){
    const s=c.morph.state,r=c.morph.rate,g=this.derived(c);
    const [u,v,w]=state.velocityBody,V=Math.max(.1,Math.hypot(u,v,w)),alpha=Math.atan2(w,u),beta=Math.asin(clamp(v/V,-1,1));
    const a=REFERENCE.aero,al=clamp(alpha,-REFERENCE.limits.alpha,REFERENCE.limits.alpha),qbar=.5*world.density*V*V;
    const stall=Math.max(0,Math.cos(alpha))**2;
    const CL=(a.CL0+(a.CLa*(1+.16*s.span-.11*s.sweep))*al+.88*state.controls.pitch+1.15*s.camber+.54*s.twist)*stall;
    const CD=a.CD0*(1-.08*s.sweep+.07*s.thickness)+a.k*CL*CL+.035*beta*beta+0.034*Math.abs(s.sweep)+0.020*Math.abs(r.span)+0.016*Math.abs(r.camber)+1.05*Math.sin(alpha)**2;
    const Cm=a.Cm0+a.Cma*al+.92*state.controls.pitch-.30*s.camber+.34*s.twist-.06*s.sweep-5.2*state.omegaBody[1]*g.chord/(2*V);
    const [p,,rr]=state.omegaBody;
    const Cl=a.Clp*p*g.span/(2*V)+.13*state.controls.roll+.08*s.twist;
    const Cn=a.Cnr*rr*g.span/(2*V)+.16*state.controls.yaw-.06*s.sweep*beta;
    const CY=-.62*beta+.18*state.controls.yaw;
    const L=qbar*g.area*CL,D=qbar*g.area*CD,Y=qbar*g.area*CY,ca=Math.cos(alpha),sa=Math.sin(alpha);
    c.lastCoeff={CL,CD,Cm};c.peakQ=Math.max(c.peakQ,qbar);c.peakAlpha=Math.max(c.peakAlpha,Math.abs(alpha));
    return {forceBody:[-D*ca+L*sa,Y,-D*sa-L*ca],momentBody:[qbar*g.area*g.span*Cl,qbar*g.area*g.chord*Cm,qbar*g.area*g.span*Cn],alpha,beta,qbar,mach:V/world.speedOfSound};
  }
  propulsion(c,state){
    const throttle=state.controls.throttle;
    const thrust=REFERENCE.maxThrustN*throttle;
    return {forceBody:[thrust,0,-thrust*.018*state.controls.pitch],momentBody:[0,0,0]};
  }
  stepCase(c,cmd){
    const world=this.world.sample(c.state);
    this.controls(c.state,cmd,DT);
    const thrust=REFERENCE.maxThrustN*c.state.controls.throttle;
    const fuelFlow=0.11+0.00000335*thrust;
    c.mdot=-fuelFlow;
    c.fuelKg=Math.max(0,c.fuelKg-fuelFlow*DT);
    c.morphPowerW=c.morph.step(cmd.morph,DT);
    const geom=this.derived(c);
    c.vehicle.massKg=geom.mass;c.vehicle.inertia=geom.inertia;c.vehicle.wing={area:geom.area,span:geom.span,chord:geom.chord,sweepRad:geom.sweepRad};
    this.physics.step(c.vehicle,c.state,world,DT,s=>({aero:this.aero(c,s,world),propulsion:this.propulsion(c,s,world)}));
    c.state.position=this.world.integrateGeodetic(c.state.position,this.physics.velocityNed(c.state),DT);
    const gLoad=norm(c.state.accelBody)/Math.max(.1,world.gravity);c.peakG=Math.max(c.peakG,gLoad);
    const R=6378137,lat0=c.initial.lat*Math.PI/180;
    const dx=(c.state.position.lon-c.initial.lon)*Math.PI/180*R*Math.cos(lat0),dz=-(c.state.position.lat-c.initial.lat)*Math.PI/180*R;
    c.distanceM=Math.hypot(dx,dz);
    if(this.frame%12===0)c.path.push({x:dx,y:c.state.position.altitudeM-c.initial.altitudeM,z:dz});
  }
  step(){
    if(this.done)return this.snapshot();
    const cmd=missionCommand(this.t);
    this.stepCase(this.morphCase,cmd);this.stepCase(this.baseCase,cmd);
    this.t+=DT;this.frame++;
    if(this.t>=MISSION_DURATION_S)this.done=true;
    return this.snapshot(cmd.phase);
  }
  snapshot(phase=missionCommand(this.t).phase){
    const pack=c=>{const g=this.derived(c),speed=norm(c.state.velocityBody);return {t:this.t,phase,speed,altitudeM:c.state.position.altitudeM,position:{...c.state.position},quaternion:[...c.state.quaternion],omega:[...c.state.omegaBody],controls:{...c.state.controls},morph:{...c.morph.state},morphRate:{...c.morph.rate},CL:c.lastCoeff.CL,CD:c.lastCoeff.CD,Cm:c.lastCoeff.Cm,inertia:[...g.inertia],massKg:g.mass,mdot:c.mdot,fuelKg:c.fuelKg,morphPowerW:c.morphPowerW,morphEnergyJ:c.morph.energyJ,boundHits:c.morph.boundHits,peakQ:c.peakQ,peakAlpha:c.peakAlpha,peakG:c.peakG,distanceM:c.distanceM,path:c.path};};
    const m=pack(this.morphCase),b=pack(this.baseCase);
    return {schema:'MANTA-AB-6DOF-1.0',version:MANTA_VERSION,t:this.t,duration:MISSION_DURATION_S,done:this.done,morph:m,baseline:b,delta:{speed:m.speed-b.speed,altitude:m.altitudeM-b.altitudeM,distance:m.distanceM-b.distanceM,fuelUsed:(REFERENCE.fuelKg-m.fuelKg)-(REFERENCE.fuelKg-b.fuelKg),energyJ:m.morphEnergyJ}};
  }
  runToEnd(){while(!this.done)this.step();return this.snapshot();}
  exportReceipt(){return {schema:'MANTA-AB-RECEIPT-1.0',generatedAt:new Date().toISOString(),fixedStepHz:FIXED_STEP_HZ,missionDurationS:MISSION_DURATION_S,identicalMissionCommands:true,baselineGeometry:'fixed',morphGeometry:'state-coupled',final:this.snapshot()};}
}
