import {WorldEngine} from './world-engine.js';
import {SixDOFPhysics} from './physics-6dof.js';
import {VEHICLE_ORDER,vehicle} from './vehicle-registry.js';
import {PropulsionRegistry} from './propulsion-registry.js';
import {E47Runtime} from './e47-runtime.js';
import {MissionReplay} from './mission-replay.js';
import {ProofTelemetry} from './proof-telemetry.js';
import {clamp,norm,qToEuler} from './math.js';
export class SkyrmionRuntime2 extends EventTarget{
 constructor({fixedStepHz=120,spawn={}}={}){super();this.schema='SKYRMION-RUNTIME-2.1';this.fixedStepHz=fixedStepHz;this.dt=1/fixedStepHz;this.world=new WorldEngine();this.physics=new SixDOFPhysics();this.propulsion=new PropulsionRegistry();this.e47=new E47Runtime();this.mission=new MissionReplay();this.proof=new ProofTelemetry();this.vehicleIndex=0;this.vehicle=vehicle(VEHICLE_ORDER[0]);this.state=this.physics.createState(this.vehicle,spawn);this.commandControls={...this.state.controls};this.lastPropulsion={forceBody:[0,0,0],momentBody:[0,0,0],receipt:{mode:'conventional'}};this.accumulator=0;this.lastNow=0;this.running=false;this.mantaFrame=null;this.stepCount=0;}
 setVehicle(id){const next=vehicle(id);const speed=Math.max(80,norm(this.state.velocityBody));this.vehicle=next;this.vehicleIndex=VEHICLE_ORDER.indexOf(next.id);this.state.vehicleId=next.id;this.state.velocityBody=[speed,0,0];this.state.omegaBody=[0,0,0];this.state.controls={throttle:this.commandControls.throttle??.72,pitch:0,roll:0,yaw:0};this.commandControls={...this.state.controls};this.e47.seed(47+Math.max(0,this.vehicleIndex));this.emit();}
 teleport({lat,lon,altitudeM}){if(Number.isFinite(lat))this.state.position.lat=lat;if(Number.isFinite(lon))this.state.position.lon=lon;if(Number.isFinite(altitudeM))this.state.position.altitudeM=altitudeM;this.emit();}
 setControls(c){Object.assign(this.commandControls,{throttle:clamp(c.throttle??this.commandControls.throttle,0,1),pitch:clamp(c.pitch??this.commandControls.pitch,-1,1),roll:clamp(c.roll??this.commandControls.roll,-1,1),yaw:clamp(c.yaw??this.commandControls.yaw,-1,1)});}
 _slew(current,target,rate){const maxDelta=Math.max(.001,rate)*this.dt,delta=clamp(target-current,-maxDelta,maxDelta);return current+delta}
 _updateFlightControls(world){
  const cmd=this.commandControls,ctl=this.state.controls;
  if(this.vehicle.evidence!=='conventional'){
    const rate=2.4;
    ctl.roll=this._slew(ctl.roll,cmd.roll,rate);ctl.pitch=this._slew(ctl.pitch,cmd.pitch,rate);ctl.yaw=this._slew(ctl.yaw,cmd.yaw,rate);ctl.throttle=this._slew(ctl.throttle,cmd.throttle,1.8);
    return;
  }
  const f=this.vehicle.fcs||{},V=Math.max(1,norm(this.state.velocityBody)),qbar=.5*world.density*V*V;
  const authority=clamp(22000/Math.max(8000,qbar),.34,1);
  const p=this.state.omegaBody[0]||0,q=this.state.omegaBody[1]||0,r=this.state.omegaBody[2]||0,beta=this.state.last.beta||0;
  const rollTarget=clamp((cmd.roll*(f.rollGain??.8)*authority)-p*(f.rollDamp??.2),-1,1);
  const pitchTarget=clamp((cmd.pitch*(f.pitchGain??.75)*authority)-q*(f.pitchDamp??.24),-1,1);
  const coordinated=(cmd.roll||0)*(f.coordination??.08)*clamp(V/140,0,1);
  const yawTarget=clamp((cmd.yaw*(f.yawGain??.35)*authority)+coordinated+beta*(f.betaDamp??1.25)-r*(f.yawDamp??.8),-.58,.58);
  ctl.roll=this._slew(ctl.roll,rollTarget,f.rollRate??2.2);
  ctl.pitch=this._slew(ctl.pitch,pitchTarget,f.pitchRate??1.8);
  ctl.yaw=this._slew(ctl.yaw,yawTarget,f.yawRate??1.0);
  ctl.throttle=this._slew(ctl.throttle,cmd.throttle,f.throttleRate??1.4);
 }
 step(){const world=this.world.sample(this.state);this._updateFlightControls(world);const V=norm(this.state.velocityBody),sig={alpha:this.state.last.alpha,mach:V/world.speedOfSound,controlNorm:Math.hypot(this.state.controls.pitch,this.state.controls.roll,this.state.controls.yaw)},e47=this.e47.step(sig);this.lastPropulsion=this.propulsion.step(this.vehicle.propulsion,{vehicle:this.vehicle,state:this.state,world,controls:this.state.controls,mach:sig.mach,e47,mantaFrame:this.mantaFrame});this.physics.step(this.vehicle,this.state,world,this.lastPropulsion,this.dt);this.state.position=this.world.integrateGeodetic(this.state.position,this.physics.velocityNed(this.state),this.dt);const telemetry=this.telemetry(world,e47);this.mission.sample(this.state,telemetry,this.dt);if(++this.stepCount%12===0)this.proof.inspect({state:this.state,vehicle:this.vehicle,world,e47,propulsion:this.lastPropulsion,fixedStepHz:this.fixedStepHz});return telemetry;}
 telemetry(world=this.world.sample(this.state),e47=this.e47.snapshot()){const e=qToEuler(this.state.quaternion),speed=norm(this.state.velocityBody);return {schema:this.schema,vehicleId:this.vehicle.id,vehicleName:this.vehicle.name,evidence:this.vehicle.evidence,t:this.state.t,lat:this.state.position.lat,lon:this.state.position.lon,altitude_m:this.state.position.altitudeM,speed,speedKt:speed/0.514444,heading:e.yaw,pitch:e.pitch,roll:e.roll,alpha:this.state.last.alpha,beta:this.state.last.beta,mach:this.state.last.mach,qbar:this.state.last.qbar,controls:{...this.state.controls},commandControls:{...this.commandControls},bodyRates:{roll:this.state.omegaBody[0],pitch:this.state.omegaBody[1],yaw:this.state.omegaBody[2]},world,e47,proof:this.proof.last,propulsion:this.lastPropulsion.receipt};}
 emit(){const d=this.telemetry(),emitGlobal=typeof globalThis.dispatchEvent==='function';if(emitGlobal){globalThis.dispatchEvent(new CustomEvent('skyrmion:flight-state',{detail:{lat:d.lat,lon:d.lon,altitude_m:d.altitude_m,heading:d.heading,pitch:d.pitch,roll:d.roll,speed:d.speed,domain:d.altitude_m>120000?2:d.altitude_m>45000?1:0,active:this.vehicleIndex,enabled:true,runtime2:true}}));globalThis.dispatchEvent(new CustomEvent('skyrmion:runtime2-telemetry',{detail:d}));}this.dispatchEvent(new CustomEvent('telemetry',{detail:d}));}
 frame=now=>{if(!this.running)return;if(!this.lastNow)this.lastNow=now;const elapsed=Math.min(.05,(now-this.lastNow)/1000);this.lastNow=now;this.accumulator+=elapsed;let n=0;while(this.accumulator>=this.dt&&n<8){this.step();this.accumulator-=this.dt;n++;}this.emit();requestAnimationFrame(this.frame)};
 applyReplayFrame(frame){const v=vehicle(frame.vehicleId);this.vehicle=v;this.vehicleIndex=VEHICLE_ORDER.indexOf(v.id);this.state={...this.state,t:frame.t,vehicleId:v.id,position:{...frame.position},velocityBody:[...frame.velocityBody],quaternion:[...frame.quaternion],omegaBody:[...frame.omegaBody],controls:{...frame.controls}};this.commandControls={...frame.controls};this.emit();}
 playReplay(options={}){this.stop();return this.mission.startReplay(frame=>this.applyReplayFrame(frame),options)}
 stopReplay(){this.mission.stopReplay();this.start()}
 start(){if(this.running)return;this.running=true;this.lastNow=0;requestAnimationFrame(this.frame)} stop(){this.running=false}
 exportProof(){return {schema:'SKYRMION-RUNTIME-2-RECEIPT',generatedAt:new Date().toISOString(),runtime:this.schema,fixedStepHz:this.fixedStepHz,vehicle:this.vehicle,proof:this.proof.last,e47:this.e47.snapshot(),missionFrames:this.mission.frames.length}}
}
