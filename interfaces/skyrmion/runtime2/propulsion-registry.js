import {clamp} from './math.js';
const conventional=(id,maxThrustN,fn)=>({id,evidence:'conventional',step(ctx){const factor=fn?fn(ctx):1;return {forceBody:[maxThrustN*clamp(ctx.controls.throttle,0,1)*factor,0,0],momentBody:[0,0,0],receipt:{mode:'conventional',engine:id}}}});
export class PropulsionRegistry{
 constructor(){this.adapters=new Map();
  this.register(conventional('f100',129000,({mach})=>clamp(1-.035*Math.max(0,mach-1),.72,1.08)));
  this.register(conventional('j58',290000,({mach})=>clamp(.58+.22*mach,.55,1.38)));
  this.register(conventional('x15_rocket',254000,({world})=>clamp(1+.12*(1-world.density/1.225),1,1.13)));
  this.registerExperimental('eidolon_scalar',1.8e5,1.25,'scalar-coherence');
  this.registerExperimental('manta_morph',1.45e5,1.65,'programmable-matter/spectral-morph');
  this.registerExperimental('skyrmion_coherence',2.05e5,1.45,'coherence-propulsion');
  this.registerExperimental('syntax_jacob',2.2e5,1.05,'coherence/inertial');
 }
 register(a){this.adapters.set(a.id,a)}
 registerExperimental(id,maxThrustN,torqueGain,label){this.adapters.set(id,{id,evidence:'experimental-simulation',step:ctx=>{
   const t=clamp(ctx.controls.throttle,0,1),capture=ctx.e47?.capture??0,residual=ctx.e47?.residual??1,coherence=clamp(.3+.9*capture-.05*Math.log10(1+residual),.15,1.2);
   const F=maxThrustN*t*coherence; const g=torqueGain*ctx.vehicle.massKg;
   return {forceBody:[F,0,-F*.04*ctx.controls.pitch],momentBody:[g*ctx.controls.roll,g*1.2*ctx.controls.pitch,g*.7*ctx.controls.yaw],receipt:{mode:'experimental-simulation',adapter:id,label,coherence}};
 }});}
 step(id,ctx){const a=this.adapters.get(id);if(!a)throw new Error(`Unknown propulsion adapter ${id}`);return a.step(ctx)}
}
