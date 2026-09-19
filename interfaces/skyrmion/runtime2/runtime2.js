import {WorldEngine} from './world-engine.js';
import {SixDOFPhysics} from './physics-6dof.js';
import {VEHICLES,VEHICLE_ORDER,vehicle} from './vehicle-registry.js';
import {ConventionalFlightModel} from './conventional-model.js';
import {ExperimentalFlightModel} from './experimental-model.js';
import {MissionReplay} from './mission-replay.js';
import {ProofTelemetry} from './proof-telemetry.js';
import {clamp,norm,qToEuler} from './math.js';
import {stateIssue,copyState} from './flight-state.js';
export class SkyrmionRuntime2 extends EventTarget{
 constructor({fixedStepHz=120,spawn={}}={}){
  super();if(!Number.isFinite(fixedStepHz)||fixedStepHz<60||fixedStepHz>240)throw new Error('fixedStepHz must be 60–240');
  this.schema='SKYRMION-RUNTIME-2.2';this.fixedStepHz=fixedStepHz;this.dt=1/fixedStepHz;
  this.world=new WorldEngine();this.physics=new SixDOFPhysics();this.mission=new MissionReplay();this.proof=new ProofTelemetry();
  this.spawn={lat:36.1699,lon:-115.1398,altitudeM:3658,speedMps:216,heading:0,...spawn};
  this.accumulator=0;this.lastNow=0;this.running=false;this.raf=0;this.mantaFrame=null;this.stepCount=0;this.fault=null;
  this._loadVehicle('f16',this.spawn);
 }
 _loadVehicle(id,spawn){
  if(!VEHICLES[id])throw new Error('Unknown craft '+id);
  const next=vehicle(id),model=next.evidence==='conventional'?new ConventionalFlightModel(next):new ExperimentalFlightModel(next);
  const state=this.physics.createState(next,spawn);
  if(stateIssue(state))throw new Error(stateIssue(state));
  const world=this.world.sample(state);
  const trim=model.kind==='conventional'?model.trim(state,world,spawn.heading||0):null;
  this.vehicle=next;this.vehicleIndex=VEHICLE_ORDER.indexOf(id);this.model=model;this.e47=model.e47;this.trim=trim;
  this.state=state;this.commandControls={throttle:state.controls.throttle,pitch:0,roll:0,yaw:0};
  this.lastPropulsion=model.propulsion(state,world);this.mantaFrame=null;this.fault=null;this.accumulator=0;
  this.proof=new ProofTelemetry();this.lastGood=copyState(state);this._inspect();
 }
 setVehicle(id){
  // Only a valid geographic location crosses the selection boundary. Dynamics,
  // controls, E47 state, and receipts are constructed afresh for the selected craft.
  const p=stateIssue(this.state)?this.lastGood.position:this.state.position;
  this._loadVehicle(id,{...this.spawn,...p});this.emit();
 }
 reset(){this._loadVehicle(this.vehicle.id,this.spawn);this.emit();}
 teleport(position){
  const base=stateIssue(this.state)?this.lastGood.position:this.state.position;
  this._loadVehicle(this.vehicle.id,{...this.spawn,...base,...position});this.emit();
 }
 setControls(c){for(const axis of ['throttle','pitch','roll','yaw'])if(Number.isFinite(c[axis]))this.commandControls[axis]=clamp(c[axis],axis==='throttle'?0:-1,1);}
 _inspect(world=this.world.sample(this.state)){
  return this.proof.inspect({state:this.state,vehicle:this.vehicle,world,e47:this.e47?.snapshot()??null,propulsion:this.lastPropulsion,fixedStepHz:this.fixedStepHz,fault:this.fault});
 }
 _reject(reason,attemptedTime){
  this.fault={reason,vehicleId:this.vehicle.id,attemptedTime:Number.isFinite(attemptedTime)?attemptedTime:null};
  this.state=copyState(this.lastGood);this._inspect();return this.telemetry();
 }
 step(){
  if(this.fault)return this.telemetry();
  const issue=stateIssue(this.state);if(issue)return this._reject(issue,this.state.t);
  const candidate=copyState(this.state),world=this.world.sample(candidate);
  const result=this.model.step(this.physics,candidate,world,this.dt,this.commandControls);
  candidate.position=this.world.integrateGeodetic(candidate.position,this.physics.velocityNed(candidate),this.dt);
  const nextIssue=stateIssue(candidate);if(nextIssue)return this._reject(nextIssue,candidate.t);
  this.state=candidate;this.lastGood=copyState(candidate);this.lastPropulsion=result.propulsion;this.stepCount++;
  // Inspect this exact state before serializing it, including immediately after a craft change.
  const currentWorld=this.world.sample(this.state);this._inspect(currentWorld);
  const telemetry=this.telemetry(currentWorld);this.mission.sample(this.state,telemetry,this.dt);return telemetry;
 }
 telemetry(world=this.world.sample(this.state)){
  const e=qToEuler(this.state.quaternion),speed=norm(this.state.velocityBody),e47=this.e47?.snapshot()??null;
  return {schema:this.schema,vehicleId:this.vehicle.id,vehicleName:this.vehicle.name,evidence:this.vehicle.evidence,model:this.model.kind,t:this.state.t,lat:this.state.position.lat,lon:this.state.position.lon,altitude_m:this.state.position.altitudeM,speed,speedKt:speed/0.514444,heading:e.yaw,pitch:e.pitch,roll:e.roll,alpha:this.state.last.alpha,beta:this.state.last.beta,mach:speed/world.speedOfSound,qbar:this.vehicle.evidence==='conventional'?.5*world.density*speed*speed:0,controls:{...this.state.controls},commandControls:{...this.commandControls},bodyRates:{roll:this.state.omegaBody[0],pitch:this.state.omegaBody[1],yaw:this.state.omegaBody[2]},world,e47,proof:this.proof.last,propulsion:this.lastPropulsion.receipt,fault:this.fault};
 }
 emit(){
  const d=this.telemetry();
  if(typeof globalThis.dispatchEvent==='function'){
   globalThis.dispatchEvent(new CustomEvent('skyrmion:flight-state',{detail:{lat:d.lat,lon:d.lon,altitude_m:d.altitude_m,heading:d.heading,pitch:d.pitch,roll:d.roll,speed:d.speed,domain:d.altitude_m>120000?2:d.altitude_m>45000?1:0,active:this.vehicleIndex,enabled:true,runtime2:true}}));
   globalThis.dispatchEvent(new CustomEvent('skyrmion:runtime2-telemetry',{detail:d}));
  }
  this.dispatchEvent(new CustomEvent('telemetry',{detail:d}));
 }
 frame=now=>{if(!this.running)return;if(!this.lastNow)this.lastNow=now;const elapsed=Math.max(0,Math.min(.05,(now-this.lastNow)/1000));this.lastNow=now;this.accumulator+=elapsed;let n=0;while(this.accumulator>=this.dt&&n<12){this.step();this.accumulator-=this.dt;n++;}this.emit();this.raf=requestAnimationFrame(this.frame)};
 applyReplayFrame(frame){
  if(!VEHICLES[frame?.vehicleId]||stateIssue(frame)){
   this._reject('Replay contains an invalid flight frame',frame?.t);this.mission.stopReplay();this.emit();return false;
  }
  if(this.vehicle.id!==frame.vehicleId)this._loadVehicle(frame.vehicleId,{...this.spawn,...frame.position});
  this.state={...this.state,...copyState(frame)};delete this.state.telemetry;
  this.state.last={alpha:frame.telemetry?.alpha??0,beta:frame.telemetry?.beta??0,mach:frame.telemetry?.mach??0,qbar:frame.telemetry?.qbar??0};
  this.commandControls={...frame.controls};this.lastGood=copyState(this.state);this.fault=null;
  this.lastPropulsion=this.model.propulsion(this.state,this.world.sample(this.state));this._inspect();this.emit();return true;
 }
 playReplay(options={}){if(this.mission.frames.length<2)return false;this.stop();return this.mission.startReplay(frame=>this.applyReplayFrame(frame),{...options,onEnd:()=>{this.start();options.onEnd?.();}})}
 stopReplay(){this.mission.stopReplay();this.start()}
 start(){if(this.running)return;this.running=true;this.lastNow=0;this.raf=requestAnimationFrame(this.frame)}
 stop(){this.running=false;if(this.raf)cancelAnimationFrame(this.raf);this.raf=0;}
 exportProof(){return {schema:'SKYRMION-RUNTIME-2-RECEIPT',generatedAt:new Date().toISOString(),runtime:this.schema,fixedStepHz:this.fixedStepHz,vehicle:this.vehicle,proof:this.proof.last,e47:this.e47?.snapshot()??null,missionFrames:this.mission.frames.length,fault:this.fault}}
}
