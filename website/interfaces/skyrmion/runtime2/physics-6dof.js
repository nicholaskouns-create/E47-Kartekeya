import {clamp,cross,qMul,qNormalize,qRotate,qRotateInv,norm} from './math.js';
export class SixDOFPhysics{
 constructor(){this.schema='SKYRMION-6DOF-2.0'}
 createState(vehicle,{lat=36.1699,lon=-115.1398,altitudeM=3600,speedMps=216,heading=0}={}){return {t:0,position:{lat,lon,altitudeM},velocityBody:[speedMps,0,0],quaternion:[Math.cos(heading/2),0,0,Math.sin(heading/2)],omegaBody:[0,0,0],controls:{throttle:.72,pitch:0,roll:0,yaw:0},vehicleId:vehicle.id,accelBody:[0,0,0],last:{alpha:0,beta:0,mach:0,qbar:0}}}
 aerodynamic(vehicle,state,world){
  if(vehicle.evidence!=='conventional')return {forceBody:[0,0,0],momentBody:[0,0,0],alpha:0,beta:0,qbar:0,mach:norm(state.velocityBody)/world.speedOfSound};
  const [u,v,w]=state.velocityBody,V=Math.max(1,norm(state.velocityBody)),alpha=Math.atan2(w,Math.max(.1,u)),beta=Math.asin(clamp(v/V,-1,1));
  const qbar=.5*world.density*V*V,S=vehicle.wing.area,b=vehicle.wing.span,c=vehicle.wing.chord,a=vehicle.aero,ctl=state.controls;
  const CL=a.CL0+a.CLa*alpha+.72*ctl.pitch,CD=a.CD0+a.k*CL*CL+.04*beta*beta,CY=a.CyBeta*beta+a.CyDr*ctl.yaw;
  const L=qbar*S*CL,D=qbar*S*CD,Y=qbar*S*CY;
  const ca=Math.cos(alpha),sa=Math.sin(alpha);const Fx=-D*ca+L*sa,Fz=-D*sa-L*ca;
  const p=state.omegaBody[0],q=state.omegaBody[1],r=state.omegaBody[2];
  const Cl=a.Clp*(p*b/(2*V))+a.ClDa*ctl.roll, Cm=a.Cm0+a.Cma*alpha+a.CmDe*ctl.pitch, Cn=a.Cnr*(r*b/(2*V))+a.CnDr*ctl.yaw;
  return {forceBody:[Fx,Y,Fz],momentBody:[qbar*S*b*Cl,qbar*S*c*Cm,qbar*S*b*Cn],alpha,beta,qbar,mach:V/world.speedOfSound};
 }
 step(vehicle,state,world,propulsion,dt){
  const aero=this.aerodynamic(vehicle,state,world),mass=vehicle.massKg,I=vehicle.inertia;
  const gNed=[0,0,world.gravity*mass],gBody=qRotateInv(state.quaternion,gNed);
  const F=[aero.forceBody[0]+propulsion.forceBody[0]+gBody[0],aero.forceBody[1]+propulsion.forceBody[1]+gBody[1],aero.forceBody[2]+propulsion.forceBody[2]+gBody[2]];
  const omega=state.omegaBody,Iw=[I[0]*omega[0],I[1]*omega[1],I[2]*omega[2]],gyro=cross(omega,Iw),M=propulsion.momentBody.map((v,i)=>v+aero.momentBody[i]);
  const acc=[F[0]/mass-(omega[1]*state.velocityBody[2]-omega[2]*state.velocityBody[1]),F[1]/mass-(omega[2]*state.velocityBody[0]-omega[0]*state.velocityBody[2]),F[2]/mass-(omega[0]*state.velocityBody[1]-omega[1]*state.velocityBody[0])];
  for(let i=0;i<3;i++)state.velocityBody[i]+=acc[i]*dt;
  for(let i=0;i<3;i++)state.omegaBody[i]+=(M[i]-gyro[i])/I[i]*dt;
  const qdot=qMul(state.quaternion,[0,...state.omegaBody]).map(v=>.5*v);state.quaternion=qNormalize(state.quaternion.map((v,i)=>v+qdot[i]*dt));
  state.accelBody=acc;state.t+=dt;state.last={alpha:aero.alpha,beta:aero.beta,mach:aero.mach,qbar:aero.qbar};
  return state;
 }
 velocityNed(state){return qRotate(state.quaternion,state.velocityBody)}
}
