import {clamp,norm,qFromEuler,qRotateInv} from './math.js';

export const ENGINES=Object.freeze({
 f100:{maxThrustN:129000,factor:({mach})=>clamp(1-.035*Math.max(0,mach-1),.72,1.08)},
 j58:{maxThrustN:290000,factor:({mach})=>clamp(.58+.22*mach,.55,1.38)},
 x15_rocket:{maxThrustN:254000,factor:({world})=>clamp(1+.12*(1-world.density/1.225),1,1.13)}
});

// Body axes: x forward, y right, z down. Positive pilot pitch means nose up.
// CmDe describes elevator deflection; delta_e = -pilot_pitch.
export class ConventionalFlightModel{
 constructor(vehicle){
  if(vehicle.evidence!=='conventional'||!ENGINES[vehicle.propulsion])throw new Error('Conventional model requires an aerodynamic vehicle');
  this.vehicle=vehicle;this.kind='conventional';this.e47=null;
 }
 propulsion(state,world){
  const engine=ENGINES[this.vehicle.propulsion],mach=norm(state.velocityBody)/world.speedOfSound;
  return {forceBody:[engine.maxThrustN*state.controls.throttle*engine.factor({mach,world}),0,0],momentBody:[0,0,0],receipt:{mode:this.kind,engine:this.vehicle.propulsion}};
 }
 aerodynamic(state,world){
  const vehicle=this.vehicle,wind=qRotateInv(state.quaternion,world.windNed||[0,0,0]);
  const [u,v,w]=state.velocityBody.map((x,i)=>x-wind[i]),V=Math.max(.1,Math.hypot(u,v,w));
  const alpha=Math.atan2(w,u),beta=Math.asin(clamp(v/V,-1,1));
  const qbar=.5*world.density*V*V,S=vehicle.wing.area,b=vehicle.wing.span,c=vehicle.wing.chord,a=vehicle.aero,ctl=state.controls;
  // Smooth stall extension keeps the linear derivatives local to attached flow.
  const al=clamp(alpha,-vehicle.limits.alpha,vehicle.limits.alpha),stall=Math.max(0,Math.cos(alpha))**2;
  const CL=(a.CL0+a.CLa*al+.72*ctl.pitch)*stall;
  const CD=a.CD0+a.k*CL*CL+.04*beta*beta+1.2*Math.sin(alpha)**2;
  const CY=a.CyBeta*beta+a.CyDr*ctl.yaw;
  const L=qbar*S*CL,D=qbar*S*CD,Y=qbar*S*CY,ca=Math.cos(alpha),sa=Math.sin(alpha);
  const [p,q,r]=state.omegaBody;
  const Cl=a.Clp*p*b/(2*V)+a.ClDa*ctl.roll;
  const Cm=a.Cm0+a.Cma*al-a.CmDe*ctl.pitch+(a.Cmq??-8)*q*c/(2*V);
  const Cn=a.Cnr*r*b/(2*V)+a.CnDr*ctl.yaw;
  return {forceBody:[-D*ca+L*sa,Y,-D*sa-L*ca],momentBody:[qbar*S*b*Cl,qbar*S*c*Cm,qbar*S*b*Cn],alpha,beta,qbar,mach:V/world.speedOfSound};
 }
 trim(state,world,heading=0){
  const v=this.vehicle,a=v.aero,V=norm(state.velocityBody),qS=.5*world.density*V*V*v.wing.area;
  const pitchAt=alpha=>(a.Cm0+a.Cma*alpha)/a.CmDe;
  const balance=alpha=>{
   const CL=(a.CL0+a.CLa*alpha+.72*pitchAt(alpha))*Math.cos(alpha)**2;
   const CD=a.CD0+a.k*CL*CL+1.2*Math.sin(alpha)**2;
   return qS*(CL+CD*Math.tan(alpha))-v.massKg*world.gravity;
  };
  let lo=-.15,hi=Math.min(.4,v.limits.alpha);
  for(let i=0;i<60;i++){const mid=(lo+hi)/2;if(balance(mid)>0)hi=mid;else lo=mid;}
  const alpha=(lo+hi)/2,pitch=clamp(pitchAt(alpha),-1,1);
  state.quaternion=qFromEuler(0,alpha,heading);state.velocityBody=[V*Math.cos(alpha),0,V*Math.sin(alpha)];state.controls.pitch=pitch;
  const aero=this.aerodynamic(state,world),D=-(aero.forceBody[0]*Math.cos(alpha)+aero.forceBody[2]*Math.sin(alpha));
  const engine=ENGINES[v.propulsion],maxThrust=engine.maxThrustN*engine.factor({mach:V/world.speedOfSound,world});
  const throttle=clamp(D/(Math.cos(alpha)*maxThrust),0,1);state.controls.throttle=throttle;
  state.last={alpha:aero.alpha,beta:aero.beta,mach:aero.mach,qbar:aero.qbar};
  this.trimState={alpha,pitch,throttle};return this.trimState;
 }
 controls(state,cmd,dt,world){
  const f=this.vehicle.fcs||{},V=Math.max(1,norm(state.velocityBody)),qbar=.5*world.density*V*V;
  const authority=clamp(22000/Math.max(8000,qbar),.34,1),[p,q,r]=state.omegaBody,beta=state.last.beta;
  const coordinated=cmd.roll*(f.coordination??.08)*clamp(V/140,0,1);
  const targets={
   roll:clamp(cmd.roll*(f.rollGain??.8)*authority-p*(f.rollDamp??.2),-1,1),
   pitch:clamp((this.trimState?.pitch||0)+cmd.pitch*(f.pitchGain??.75)*authority-q*(f.pitchDamp??.24),-1,1),
   yaw:clamp(cmd.yaw*(f.yawGain??.35)*authority+coordinated+beta*(f.betaDamp??1.25)-r*(f.yawDamp??.8),-.58,.58),
   throttle:cmd.throttle
  };
  for(const axis of ['roll','pitch','yaw','throttle'])state.controls[axis]+=clamp(targets[axis]-state.controls[axis],-(f[axis+'Rate']??1.8)*dt,(f[axis+'Rate']??1.8)*dt);
 }
 step(physics,state,world,dt,cmd){
  this.controls(state,cmd,dt,world);
  physics.step(this.vehicle,state,world,dt,s=>({aero:this.aerodynamic(s,world),propulsion:this.propulsion(s,world)}));
  return {propulsion:this.propulsion(state,world),e47:null};
 }
}
