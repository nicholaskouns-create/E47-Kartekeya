// SKYRMION RT3 · flight control system.
// Carries actuator lag, dynamic-pressure authority scaling, a load-factor limiter
// and an angle-of-attack limiter. The limiters are what let a pilot pull full aft
// stick without departing, which is how a fly-by-wire aircraft actually behaves.
import {clamp,actuate} from './math.js';

export class FlightControlSystem{
 constructor(vehicle){
  this.vehicle=vehicle;this.f=vehicle.fcs||{};this.schema='RT3-FCS-1.1';
  this.trimPitch=0;this.limiter={alpha:false,g:false};
 }
 reset(trimPitch=0){this.trimPitch=trimPitch;this.limiter={alpha:false,g:false}}
 step(state,command,env,aero,dt){
  const f=this.f,ctl=state.controls;
  const qbar=Math.max(1,aero.qbar??1);
  // Surface authority falls as dynamic pressure rises: the same deflection does
  // far more at 600 knots than at 150.
  const authority=clamp(22000/Math.max(8000,qbar),.3,1);
  const [p,q,r]=state.omegaBody;

  // Load-factor limiter: scale back nose-up command as the limit is approached.
  const gLimit=f.gLimit??9,nz=aero.loadFactor??1;
  let pitchCmd=command.pitch;
  if(pitchCmd>0&&nz>gLimit*.78){
   const margin=clamp((gLimit-nz)/(gLimit*.22),0,1);
   if(margin<1)this.limiter.g=true;
   pitchCmd*=margin;
  }else this.limiter.g=false;
  // Angle-of-attack limiter, applied on top of the G limiter.
  const alphaLimit=f.alphaLimit??.44,alpha=aero.alpha??0;
  if(pitchCmd>0&&alpha>alphaLimit*.8){
   const margin=clamp((alphaLimit-alpha)/(alphaLimit*.2),0,1);
   if(margin<1)this.limiter.alpha=true;
   pitchCmd*=margin;
  }else this.limiter.alpha=false;

  const coordinated=command.roll*(f.coordination??.08)*clamp(aero.V/140,0,1);
  const beta=aero.beta??0;
  const targets={
   roll:clamp(command.roll*(f.rollGain??.8)*authority-p*(f.rollDamp??.2),-1,1),
   pitch:clamp(this.trimPitch+pitchCmd*(f.pitchGain??.75)*authority-q*(f.pitchDamp??.24),-1,1),
   yaw:clamp(command.yaw*(f.yawGain??.35)*authority+coordinated+beta*(f.betaDamp??1.25)-r*(f.yawDamp??.8),-.58,.58),
   throttle:clamp(command.throttle,0,1)
  };
  const tau=f.tau??.06;
  for(const axis of ['roll','pitch','yaw'])
   ctl[axis]=actuate(ctl[axis],targets[axis],dt,f[axis+'Rate']??1.8,tau);
  ctl.throttle=actuate(ctl.throttle,targets.throttle,dt,f.throttleRate??1.6,.12);
  // Configuration axes move slowly and have no lag term worth modelling.
  for(const [axis,rate] of [['flap',.35],['gear',.25],['brake',1.6],['afterburner',1.2],['wheelBrake',3]])
   if(Number.isFinite(command[axis]))ctl[axis]=clamp(ctl[axis]+clamp(command[axis]-ctl[axis],-rate*dt,rate*dt),0,1);
  return ctl;
 }
}
