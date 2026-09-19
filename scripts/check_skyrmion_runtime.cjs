const {test}=require('node:test');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {resolve}=require('node:path');
const {readFileSync}=require('node:fs');
const dir=resolve(__dirname,'../website/interfaces/skyrmion/runtime2');
const moduleAt=name=>import(pathToFileURL(resolve(dir,name)).href);
const runtime=()=>moduleAt('runtime2.js');

for(const id of ['f16','sr71','x15'])test(`${id}: trimmed neutral flight remains level for 120 seconds`,async()=>{
 const {SkyrmionRuntime2}=await runtime(),r=new SkyrmionRuntime2();r.setVehicle(id);
 for(let i=0;i<14400;i++)r.step();
 const d=r.telemetry();assert.equal(d.fault,null);assert.ok(Math.abs(d.altitude_m-3658)<.01);assert.ok(Math.abs(d.speed-216)<.01);
 assert.ok(Math.hypot(...r.state.omegaBody)<1e-6);assert.equal(r.e47,null);assert.equal(d.e47,null);assert.equal(d.proof.pass,true);
});

test('original F-16 72% throttle mission no longer diverges at 4.57 seconds',async()=>{
 const {SkyrmionRuntime2}=await runtime(),r=new SkyrmionRuntime2({spawn:{altitudeM:3658,speedMps:216}});r.setControls({throttle:.72});
 for(let i=0;i<120*120;i++){const d=r.step();assert.equal(d.fault,null);assert.ok(Math.abs(d.bodyRates.pitch)<1);assert.ok(d.speed<2000);}
 assert.equal(r.mission.frames.length,1200);
 for(const f of r.mission.frames){assert.equal(f.telemetry.proof.t,f.t);assert.equal(f.telemetry.proof.vehicle.id,f.vehicleId);assert.equal(f.telemetry.proof.pass,true);}
});

test('positive pitch commands nose-up and the damper opposes pitch rate',async()=>{
 const {SkyrmionRuntime2}=await runtime(),r=new SkyrmionRuntime2();
 r.setControls({pitch:.3});for(let i=0;i<30;i++)r.step();assert.ok(r.state.omegaBody[1]>0);
 r.reset();r.state.omegaBody[1]=.1;const before=r.state.omegaBody[1];r.step();assert.ok(r.state.omegaBody[1]<before);
});

test('maneuvers and release remain finite across all seven craft',async()=>{
 const {SkyrmionRuntime2}=await runtime();
 for(const id of ['f16','sr71','x15','eidolon','manta','skyrmion','jacob']){
  const r=new SkyrmionRuntime2();r.setVehicle(id);
  for(let i=0;i<120*60;i++){
   r.setControls({pitch:i<120?.25:0,roll:i>=240&&i<360?.3:0,yaw:i>=480&&i<600?.2:0});
   const d=r.step();assert.equal(d.fault,null,id);assert.equal(d.proof.pass,true,id);assert.ok(Math.abs(d.bodyRates.pitch)<2,id);
  }
 }
});

test('invalid states pause without sending NaN to the scene; switching starts clean',async()=>{
 const {SkyrmionRuntime2}=await runtime(),r=new SkyrmionRuntime2();r.step();
 const saved=structuredClone(r.state);r.state.velocityBody[0]=NaN;const d=r.step();
 assert.ok(d.fault);assert.equal(d.proof.pass,false);assert.deepEqual(r.state,saved);assert.ok(Number.isFinite(d.speed));
 const oldState=r.state;r.setVehicle('jacob');assert.notEqual(r.state,oldState);assert.equal(r.fault,null);assert.ok(r.e47);assert.equal(r.proof.last.vehicle.id,'jacob');assert.equal(r.proof.last.pass,true);
 const oldE47=r.e47;r.setVehicle('manta');assert.notEqual(r.e47,oldE47);
 r.setVehicle('sr71');assert.equal(r.e47,null);assert.equal(r.proof.last.e47,null);assert.equal(r.proof.last.vehicle.id,'sr71');
 assert.equal(r.proof.last.propulsion.engine,'j58');assert.equal(r.state.t,0);
});

test('invalid serialized replay frames are rejected and cannot contaminate a craft',async()=>{
 const {SkyrmionRuntime2}=await runtime(),r=new SkyrmionRuntime2();const valid=structuredClone(r.state);
 const frame={...structuredClone(valid),vehicleId:'jacob',position:{lat:null,lon:null,altitudeM:null},quaternion:[null,null,null,null]};
 assert.equal(r.applyReplayFrame(frame),false);assert.equal(r.vehicle.id,'f16');assert.deepEqual(r.state,valid);assert.equal(r.proof.last.pass,false);
 r.setVehicle('sr71');assert.equal(r.fault,null);assert.equal(r.step().proof.pass,true);
});

test('each craft loads matching math, force coefficients, and sources',async()=>{
 const {craftMath}=await moduleAt('craft-math.js'),{VEHICLES}=await moduleAt('vehicle-registry.js');
 for(const [id,v] of Object.entries(VEHICLES)){
  const m=craftMath(id);assert.equal(m.name,v.name);assert.ok(m.equations.length>=8);assert.ok(m.sources.length>=2);
  assert.equal(m.equations.some(([label])=>label==='Kernel'),v.evidence!=='conventional');
 }
 assert.ok(craftMath('manta').equations.some(([label])=>label==='Morph displacement'));
 assert.match(craftMath('jacob').note,/ephemeris is not part/);
});

test('shared rigid-body solver conserves speed under torque-free spherical rotation',async()=>{
 const {SixDOFPhysics}=await moduleAt('physics-6dof.js'),p=new SixDOFPhysics(),v={id:'test',massKg:1,inertia:[1,1,1]},s=p.createState(v,{speedMps:216});s.omegaBody=[0,2,0];
 const zero={forceBody:[0,0,0],momentBody:[0,0,0],alpha:0,beta:0,mach:0,qbar:0};
 for(let i=0;i<1200;i++)p.step(v,s,{gravity:0},1/120,()=>({aero:zero,propulsion:zero}));
 assert.ok(Math.abs(Math.hypot(...s.velocityBody)-216)<.001);
});

test('renderer constructs seven independent rigs without cloning live userData',()=>{
 const terrain=readFileSync(resolve(dir,'../terrain-3d.js'),'utf8'),boot=readFileSync(resolve(dir,'bootstrap.js'),'utf8');
 assert.match(terrain,/makeManta\(\),makeSkyrmion\(\),makeSyntaxJacob\(\)/);assert.doesNotMatch(boot,/jacob\.clone|fleet\.splice/);
});
