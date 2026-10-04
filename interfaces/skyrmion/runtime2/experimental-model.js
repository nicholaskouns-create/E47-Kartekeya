import {E47Runtime} from './e47-runtime.js';
import {clamp,norm} from './math.js';

export const EXPERIMENTS=Object.freeze({
 eidolon_scalar:{maxThrustN:180000,torqueGain:1.25,label:'scalar-coherence'},
 manta_morph:{maxThrustN:145000,torqueGain:1.65,label:'programmable-matter/spectral-morph'},
 skyrmion_coherence:{maxThrustN:205000,torqueGain:1.45,label:'coherence-propulsion'},
 syntax_jacob:{maxThrustN:220000,torqueGain:1.05,label:'coherence/inertial'}
});
export class ExperimentalFlightModel{
 constructor(vehicle){
  if(vehicle.evidence!=='experimental-simulation'||!EXPERIMENTS[vehicle.propulsion])throw new Error('Experimental model requires an experimental vehicle');
  this.vehicle=vehicle;this.kind='experimental-simulation';this.e47=new E47Runtime();
 }
 propulsion(state,world,e47=this.e47.snapshot()){
  const a=EXPERIMENTS[this.vehicle.propulsion],c=state.controls;
  const coherence=clamp(.3+.9*e47.capture-.05*Math.log10(1+e47.residual),.15,1.2),F=a.maxThrustN*c.throttle*coherence,g=a.torqueGain*this.vehicle.massKg;
  return {forceBody:[F,0,-F*.04*c.pitch],momentBody:[g*c.roll,g*1.2*c.pitch,g*.7*c.yaw].map((m,i)=>m-1.8*this.vehicle.inertia[i]*state.omegaBody[i]),receipt:{mode:this.kind,adapter:this.vehicle.propulsion,label:a.label,coherence}};
 }
 step(physics,state,world,dt,cmd){
  for(const axis of ['roll','pitch','yaw','throttle']){const rate=axis==='throttle'?1.8:2.4;state.controls[axis]+=clamp(cmd[axis]-state.controls[axis],-rate*dt,rate*dt);}
  const e47=this.e47.step({alpha:0,mach:norm(state.velocityBody)/world.speedOfSound,controlNorm:Math.hypot(state.controls.pitch,state.controls.roll,state.controls.yaw)});
  physics.step(this.vehicle,state,world,dt,s=>({aero:{forceBody:[0,0,0],momentBody:[0,0,0],alpha:0,beta:0,qbar:0,mach:norm(s.velocityBody)/world.speedOfSound},propulsion:this.propulsion(s,world,e47)}));
  return {propulsion:this.propulsion(state,world,e47),e47};
 }
}
