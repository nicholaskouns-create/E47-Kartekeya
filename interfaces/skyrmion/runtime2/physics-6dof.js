import {cross,qMul,qNormalize,qRotate,qRotateInv} from './math.js';
// Shared rigid-body kinematics only. Each flight model supplies its own loads.
export class SixDOFPhysics{
 constructor(){this.schema='SKYRMION-6DOF-2.1'}
 createState(vehicle,{lat=36.1699,lon=-115.1398,altitudeM=3600,speedMps=216,heading=0}={}){return {t:0,position:{lat,lon,altitudeM},velocityBody:[speedMps,0,0],quaternion:[Math.cos(heading/2),0,0,Math.sin(heading/2)],omegaBody:[0,0,0],controls:{throttle:.72,pitch:0,roll:0,yaw:0},vehicleId:vehicle.id,accelBody:[0,0,0],last:{alpha:0,beta:0,mach:0,qbar:0}}}
 step(vehicle,state,world,dt,loads){
  const mass=vehicle.massKg,I=vehicle.inertia;
  const initial=[...state.velocityBody,...state.omegaBody,...state.quaternion];
  const derivative=x=>{
   const s={...state,velocityBody:x.slice(0,3),omegaBody:x.slice(3,6),quaternion:qNormalize(x.slice(6))};
   const {aero,propulsion}=loads(s),omega=s.omegaBody;
   const gBody=qRotateInv(s.quaternion,[0,0,world.gravity*mass]);
   const coriolis=cross(omega,s.velocityBody),gyro=cross(omega,omega.map((v,i)=>I[i]*v));
   const acc=gBody.map((g,i)=>(g+aero.forceBody[i]+propulsion.forceBody[i])/mass-coriolis[i]);
   const angular=omega.map((_,i)=>(aero.momentBody[i]+propulsion.momentBody[i]-gyro[i])/I[i]);
   return [...acc,...angular,...qMul(s.quaternion,[0,...omega]).map(v=>v*.5)];
  };
  // RK4 avoids the artificial energy gain of Euler integration in rotating axes.
  const offset=(k,f)=>initial.map((v,i)=>v+dt*f*k[i]);
  const a=derivative(initial),b=derivative(offset(a,.5)),c=derivative(offset(b,.5)),d=derivative(offset(c,1));
  const next=initial.map((v,i)=>v+dt*(a[i]+2*b[i]+2*c[i]+d[i])/6);
  state.velocityBody=next.slice(0,3);state.omegaBody=next.slice(3,6);state.quaternion=qNormalize(next.slice(6));
  state.accelBody=derivative([...state.velocityBody,...state.omegaBody,...state.quaternion]).slice(0,3);state.t+=dt;
  const {alpha,beta,mach,qbar}=loads(state).aero;state.last={alpha,beta,mach,qbar};return state;
 }
 velocityNed(state){return qRotate(state.quaternion,state.velocityBody)}
}
