// SKYRMION RT3 · compressible aerodynamics with separation hysteresis and ground effect.
// Body axes: x forward, y right, z down. Positive pilot pitch is nose-up.
import {clamp,qRotateInv} from './math.js';

// Prandtl-Glauert below the drag divergence Mach, Ackeret above it, blended across
// the transonic band. beta is floored so the correction stays finite at M = 1.
export function compressibility(mach,claIncompressible=2*Math.PI){
 const m=Math.max(0,mach),beta=Math.sqrt(Math.max(.04,Math.abs(1-m*m)));
 const sup=M=>(4/Math.sqrt(Math.max(.04,M*M-1)))/claIncompressible;
 if(m<.8)return {beta,liftFactor:1/beta,regime:'subsonic'};
 if(m>1.2)return {beta,liftFactor:sup(m),regime:'supersonic'};
 // Transonic: smoothstep between Prandtl-Glauert at M 0.8 and Ackeret at M 1.2 so
 // the lift slope peaks near drag divergence and falls after, with nothing
 // discontinuous crossing M = 1.
 const t=(m-.8)/.4,blend=t*t*(3-2*t);
 return {beta,liftFactor:(1/Math.sqrt(.36))*(1-blend)+sup(1.2)*blend,regime:'transonic'};
}
// Lock's fourth-power law for the drag rise above the critical Mach, rolling over
// into the supersonic decay. Without this an SR-71 accelerates like a cartoon.
export function waveDrag(mach,machCrit,peak){
 if(mach<=machCrit)return 0;
 const MREF=1.05;
 if(mach<MREF)return Math.min(peak,20*Math.pow(mach-machCrit,4));
 // Anchored at the peak so the supersonic decay is continuous with the rise.
 return peak*Math.sqrt(MREF*MREF-1)/Math.sqrt(Math.max(.05,mach*mach-1));
}
// Wieselsberger: the ground shortens the trailing vortex system, cutting induced drag.
export function groundEffect(heightM,span){
 const r=Math.max(.02,heightM/Math.max(1,span));
 if(r>1.1)return {inducedFactor:1,liftFactor:1,active:false};
 const x=16*r*16*r;
 return {inducedFactor:x/(1+x),liftFactor:1+.08*clamp(1-r,0,1),active:true};
}
// Separation state with hysteresis: flow detaches at a higher angle than it
// reattaches, which is why a stall has to be flown out of rather than eased out of.
export class SeparationState{
 constructor(){this.value=0}
 step(alpha,alphaStall,dt){
  const a=Math.abs(alpha);
  const onset=alphaStall,reattach=alphaStall*.82;
  const target=this.value>.5
   ? clamp((a-reattach)/(onset*.45),0,1)
   : clamp((a-onset)/(onset*.35),0,1);
  const tau=target>this.value?.14:.42;
  this.value+=(target-this.value)*(1-Math.exp(-dt/tau));
  return this.value;
 }
 reset(){this.value=0;return this}
}

export class AeroModel{
 constructor(vehicle){this.vehicle=vehicle;this.separation=new SeparationState();this.schema='RT3-AERO-1.1'}
 reset(){this.separation.reset()}
 // dt is optional: the integrator calls this many times per step and must not
 // advance hysteresis on every stage, so separation is advanced by the runtime.
 forces(state,env,{groundHeightM=1e6,massKg=null}={}){
  const v=this.vehicle,a=v.aero,ctl=state.controls;
  const windBody=qRotateInv(state.quaternion,env.windNed||[0,0,0]);
  const u=state.velocityBody[0]-windBody[0],w2=state.velocityBody[1]-windBody[1],w=state.velocityBody[2]-windBody[2];
  const V=Math.max(.1,Math.hypot(u,w2,w));
  const alpha=Math.atan2(w,u),beta=Math.asin(clamp(w2/V,-1,1));
  const mach=V/env.speedOfSound,qbar=.5*env.density*V*V;
  const S=v.wing.area,b=v.wing.span,c=v.wing.chord;
  const comp=compressibility(mach,a.CLa);
  const ge=groundEffect(groundHeightM,b);
  const sep=this.separation.value;
  const flap=ctl.flap??0,brake=ctl.brake??0,gear=ctl.gear??0;

  // Lift: linear range scaled by compressibility and ground effect, faded out by
  // the separation state rather than by a hard cut at a stall angle.
  const alphaLin=clamp(alpha,-v.limits.alpha,v.limits.alpha);
  const CLclean=(a.CL0+a.CLa*comp.liftFactor*alphaLin+a.CLde*ctl.pitch+(a.CLflap??.9)*flap);
  const CL=CLclean*(1-.62*sep)*ge.liftFactor;

  // Drag: parasite, induced, wave, sideslip, separated bluff-body, and configuration.
  const CDi=a.k*ge.inducedFactor*CL*CL;
  const CDw=waveDrag(mach,a.machCrit??.82,a.waveDragPeak??.028);
  const CD=a.CD0+CDi+CDw+.04*beta*beta+1.25*sep*Math.sin(alpha)**2
   +(a.CDflap??.055)*flap+(a.CDbrake??.09)*brake+(a.CDgear??.022)*gear;
  const CY=a.CyBeta*beta+a.CyDr*ctl.yaw;

  const L=qbar*S*CL,D=qbar*S*CD,Y=qbar*S*CY;
  const ca=Math.cos(alpha),sa=Math.sin(alpha);
  const [p,q,r]=state.omegaBody,Vd=2*V;
  // Damping derivatives are non-dimensionalised on half-span / half-chord per
  // convention; they are what make the airframe feel like it has inertia in air.
  const Cl=a.Clp*p*b/Vd+a.ClDa*ctl.roll+(a.ClBeta??-.08)*beta;
  const Cm=a.Cm0+a.Cma*comp.liftFactor*alphaLin-a.CmDe*ctl.pitch+a.Cmq*q*c/Vd
   -.18*sep*Math.sign(alpha)-(a.Cmflap??.05)*flap;
  const Cn=a.Cnr*r*b/Vd+a.CnDr*ctl.yaw+(a.CnBeta??.11)*beta;

  return {
   forceBody:[-D*ca+L*sa,Y,-D*sa-L*ca],
   momentBody:[qbar*S*b*Cl,qbar*S*c*Cm,qbar*S*b*Cn],
   alpha,beta,mach,qbar,CL,CD,V,
   separation:sep,regime:comp.regime,groundEffect:ge.active,waveDrag:CDw,
   loadFactor:L/Math.max(1,(massKg??v.dryMassKg)*env.gravity)
  };
 }
}
