const {test}=require('node:test');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {resolve}=require('node:path');
const dir=resolve(__dirname,'../website/interfaces/skyrmion-rt3/rt3');
const mod=name=>import(pathToFileURL(resolve(dir,name)).href);
const still=opts=>mod('runtime3.js').then(({SkyrmionRuntime3})=>{
 const r=new SkyrmionRuntime3({turbulence:0,...opts});r.setWind({speed10:0});return r;
});

test('WGS84 normal gravity reproduces the published equator and pole values',async()=>{
 const {normalGravity,curvature,WGS84}=await mod('geodesy.js');
 assert.ok(Math.abs(normalGravity(0,0)-9.7803253359)<1e-7);
 assert.ok(Math.abs(normalGravity(0,90)-9.8321849378)<1e-6);
 const {M,N}=curvature(36*Math.PI/180);
 assert.ok(M<N,'meridian radius is shorter than prime-vertical at mid latitude');
 assert.ok(N<WGS84.a*1.002&&M>6.35e6);
});

test('standard atmosphere is exact at sea level and monotone upward',async()=>{
 const {standardAtmosphere}=await mod('atmosphere.js');
 const sl=standardAtmosphere(0);
 assert.ok(Math.abs(sl.temperatureK-288.15)<1e-9);
 assert.ok(Math.abs(sl.pressurePa-101325)<1e-6);
 assert.ok(Math.abs(sl.density-1.225)<1e-4);
 let prev=Infinity;
 for(const h of [0,5000,11000,20000,32000,47000,71000,86000]){
  const a=standardAtmosphere(h);
  assert.ok(a.density<prev,'density falls with altitude at '+h);
  assert.ok(a.pressurePa>0&&a.speedOfSound>200&&a.viscosity>0);
  prev=a.density;
 }
});

test('Dormand-Prince beats fixed RK4 against a known exact solution',async()=>{
 const {DormandPrince,rk4}=await mod('integrator.js');
 const f=y=>[y[1],-y[0]];
 const dp=new DormandPrince({absTol:1e-10,relTol:1e-10});
 let y=[1,0],next=.01,z=[1,0];
 for(let i=0;i<1000;i++){const r=dp.integrate(y,.01,f,next);y=r.y;next=r.nextDt;z=rk4(z,.01,f).y}
 const dpErr=Math.abs(y[0]-Math.cos(10)),rkErr=Math.abs(z[0]-Math.cos(10));
 assert.ok(dpErr<rkErr/100,`adaptive ${dpErr} should be far below fixed ${rkErr}`);
 assert.equal(dp.stats().rejects,0);
});

test('transonic drag rise is zero below the critical Mach, continuous, and decays supersonically',async()=>{
 const {waveDrag,compressibility}=await mod('aero.js');
 assert.equal(waveDrag(.7,.82,.028),0);
 assert.equal(waveDrag(.82,.82,.028),0);
 assert.ok(waveDrag(.95,.82,.028)>0);
 const below=waveDrag(1.0499,.82,.028),at=waveDrag(1.05,.82,.028);
 assert.ok(Math.abs(below-at)<1e-6,'no discontinuity at the rollover');
 assert.ok(waveDrag(2,.82,.028)<at&&waveDrag(3,.82,.028)<waveDrag(2,.82,.028));
 // Lift slope peaks near drag divergence then falls, with nothing singular at M = 1.
 const curve=[.3,.6,.8,1,1.2,2,3].map(m=>compressibility(m,4.6).liftFactor);
 assert.ok(curve.every(Number.isFinite));
 assert.ok(curve[2]>curve[0]&&curve[6]<curve[3]);
});

test('all three aircraft trim to machine precision on the real force model',async()=>{
 for(const [id,speed,altitudeM] of [['f16',216,3658],['sr71',290,3658],['sr71',960,25900],['x15',216,3658]]){
  const r=await still();
  r.load(id,{...r.spawn,speedMps:speed,altitudeM});
  assert.ok(r.trimResult.residual<1e-8,`${id} at ${altitudeM} m trimmed to ${r.trimResult.residual}`);
  assert.ok(r.trimResult.throttle>0&&r.trimResult.throttle<=1);
 }
});

test('with fuel burn frozen, trimmed flight holds altitude and attitude for 120 seconds',async()=>{
 for(const id of ['f16','sr71','x15']){
  const r=await still();
  r.load(id,{...r.spawn,speedMps:id==='sr71'?290:216});
  r.mass.burn=()=>r.mass.fuelKg; // isolate the aerodynamics from the mass change
  for(let i=0;i<14400;i++)r.step();
  const d=r.telemetry();
  assert.equal(d.fault,null,id);
  assert.ok(Math.abs(d.altitude_m-3658)<.5,`${id} drifted ${d.altitude_m-3658} m`);
  assert.ok(Math.abs(d.speed-(id==='sr71'?290:216))<.05,id);
  assert.ok(Math.hypot(...Object.values(d.bodyRates))<1e-5,id);
  assert.equal(d.proof.pass,true,id);
 }
});

test('fuel burn lightens the aircraft and the trimmed aircraft climbs because of it',async()=>{
 const r=await still();
 r.load('x15',{...r.spawn,speedMps:216});
 const start=r.mass.fuelKg;
 for(let i=0;i<120*60;i++)r.step();
 const d=r.telemetry();
 assert.ok(d.mass.fuelKg<start,'fuel is consumed');
 assert.ok(d.mass.totalKg<r.vehicle.dryMassKg+start,'mass falls with it');
 assert.ok(d.altitude_m>3658,'a lighter trimmed aircraft climbs');
 assert.equal(d.proof.pass,true);
 assert.ok(d.proof.checks.massConservation);
});

test('the aircraft rests on its gear and rolls to rotation speed without leaving the surface',async()=>{
 const r=await still({groundSampler:()=>610});
 r.load('f16',{...r.spawn,altitudeM:612.2,speedMps:.1});
 assert.equal(r.trimResult,null,'an aircraft below flying speed is not trimmed');
 r.setControls({throttle:0,gear:1,wheelBrake:1});
 for(let i=0;i<600;i++)r.step();
 let d=r.telemetry();
 assert.equal(d.gear.weightOnWheels,true);
 assert.equal(d.gear.contacts,3);
 assert.ok(d.gear.maxCompression>.01&&d.gear.maxCompression<.36,'struts carry the weight without bottoming');
 assert.ok(d.altitude_agl_m>0&&d.altitude_agl_m<4,'sits on the surface rather than through it');
 assert.ok(d.speed<2,'brakes hold it');
 r.setControls({throttle:1,afterburner:1,wheelBrake:0,gear:1});
 let airborne=false;
 for(let i=0;i<120*40;i++){
  r.step();
  const t=r.telemetry();
  assert.ok(t.altitude_m>=609.9,'never penetrates the surface');
  if(t.speed>72){r.setControls({pitch:.35});}
  if(t.speed>72&&!t.gear.weightOnWheels){airborne=true;break}
 }
 assert.ok(airborne,'reaches rotation speed and lifts off');
 assert.equal(r.telemetry().proof.pass,true);
});

test('conventional and experimental models stay isolated across every craft, every step',async()=>{
 const {VEHICLE_ORDER}=await mod('vehicles.js');
 for(const id of VEHICLE_ORDER){
  const r=await still();
  r.load(id,{...r.spawn,speedMps:216});
  for(let i=0;i<120*30;i++){
   r.setControls({pitch:i<120?.22:0,roll:i>=240&&i<400?.3:0,yaw:i>=500&&i<620?.2:0});
   const d=r.step();
   assert.equal(d.fault,null,id);
   assert.equal(d.proof.pass,true,`${id} step ${i}`);
   assert.equal(d.proof.checks.evidenceBoundary,true,id);
  }
  const d=r.telemetry();
  if(r.vehicle.evidence==='conventional'){
   assert.equal(d.e47,null,id);
   assert.equal(d.propulsion.mode,'conventional',id);
   assert.equal(r.drive,null,id);
  }else{
   assert.equal(d.propulsion.mode,'experimental-simulation',id);
   assert.ok(d.e47.capture>=0&&d.e47.capture<=1,id);
   assert.equal(r.aero,null,'an experimental craft has no aerodynamic model object at all');
   // Zero aerodynamic load, exactly: it cannot borrow lift it has not earned.
   assert.deepEqual(r.lastAero.forceBody,[0,0,0],id);
   assert.deepEqual(r.lastAero.momentBody,[0,0,0],id);
   assert.equal(r.lastAero.qbar,0,id);
   assert.deepEqual(r.derivativeCache.aero.forceBody,[0,0,0],id);
  }
 }
});

test('the E47 drive reads the generated canonical lock rather than local literals',async()=>{
 const {E47Drive}=await mod('e47-drive.js');
 const d=new E47Drive('eidolon_scalar');
 const s=d.snapshot();
 assert.equal(s.carrier,125);
 assert.equal(s.kernelDim,47);
 assert.equal(s.omegaC,47/125);
 assert.equal(s.lock,'E47-LOCK-FROM-SRC-E47');
 for(let i=0;i<400;i++)d.step({controlNorm:.2,mach:.8});
 const after=d.snapshot();
 assert.ok(after.capture>s.capture,'the spectral filter concentrates onto the kernel');
 assert.ok(after.residual<s.residual);
});

test('an invalid state pauses without sending NaN downstream, and switching starts clean',async()=>{
 const r=await still();
 r.step();
 const saved=structuredClone(r.state);
 r.state.velocityBody[0]=NaN;
 const d=r.step();
 assert.ok(d.fault);
 assert.equal(d.proof.pass,false);
 assert.deepEqual(r.state,saved);
 assert.ok(Number.isFinite(d.speed));
 r.setVehicle('jacob');
 assert.equal(r.fault,null);
 assert.ok(r.drive);
 assert.equal(r.aero,null);
 assert.equal(r.proof.last.vehicle.id,'jacob');
 r.setVehicle('sr71');
 assert.equal(r.drive,null);
 assert.equal(r.proof.last.e47,null);
 assert.equal(r.telemetry().propulsion.engine,'j58');
});

test('attitude stays a unit quaternion through sustained maneuvering',async()=>{
 const {qNorm}=await mod('math.js');
 const r=await still();
 r.load('f16',{...r.spawn,speedMps:216});
 for(let i=0;i<120*90;i++){
  r.setControls({pitch:Math.sin(i/190)*.6,roll:Math.cos(i/130)*.8,yaw:Math.sin(i/310)*.3,throttle:.9});
  r.step();
  assert.ok(Math.abs(qNorm(r.state.quaternion)-1)<1e-9);
 }
 assert.equal(r.telemetry().proof.pass,true);
});

test('the City engine bus binds every shared engine and degrades rather than throwing',async()=>{
 const {CityEngineBus}=await mod('engine-bus.js');
 const bus=new CityEngineBus();
 await bus.connect({lat:36.1699,lon:-115.1398});
 const r=bus.report();
 for(const key of ['worldEngine','worldBinding','e47Lock','stargate','cityGeo','instrument'])
  assert.equal(r.bound[key],'bound',key+' should bind');
 assert.equal(r.kernel.carrier,125);
 assert.equal(r.kernel.kernelDim,47);
 assert.ok(r.weather&&r.solar,'the world engine supplies weather and solar state');
 const rt=await still();
 const wind=bus.windFor(rt);
 assert.ok(Number.isFinite(wind.speed10));
 const packet=bus.stargatePacket({...rt.telemetry(),e47:{capture:.4,residual:.2,omegaC:47/125,iterations:5}});
 assert.equal(packet.evidence_class,'E2');
 assert.equal(packet.interpretation.physicalPromotion,false);
 bus.destroy();
});
