// SKYRMION RT3 · landing gear and ground contact.
// RT2 had no ground interaction at all, so the aircraft could only ever be in the
// air. This is the module that makes takeoff, touchdown and rollout exist.
import {clamp,cross,qRotate,qRotateInv,norm} from './math.js';

export class GearModel{
 constructor(vehicle){
  this.vehicle=vehicle;this.schema='RT3-GEAR-1.0';
  this.wheels=(vehicle.gear||[]).map(w=>({...w,compression:0,onGround:false}));
  this.weightOnWheels=false;this.maxCompression=0;this.touchdownRateMps=0;this.wasAirborne=true;
 }
 reset(){this.wheels.forEach(w=>{w.compression=0;w.onGround=false});this.weightOnWheels=false;this.wasAirborne=true;this.touchdownRateMps=0}
 // Lowest point of the extended gear below the CG, used for clearance readouts.
 lowestPointM(state,extension=1){
  let lowest=0;
  for(const w of this.wheels){
   const ned=qRotate(state.quaternion,[w.x,w.y,w.z*extension]);
   lowest=Math.max(lowest,ned[2]+w.radius);
  }
  return lowest;
 }
 forces(state,env,{groundElevationM=0,velocityNed=[0,0,0]}={}){
  const ctl=state.controls,extension=clamp(ctl.gear??0,0,1);
  const result={forceBody:[0,0,0],momentBody:[0,0,0],weightOnWheels:false,maxCompression:0,contacts:0,struts:[]};
  if(extension<=.02)
   {this.wheels.forEach(w=>{w.compression=0;w.onGround=false});this.weightOnWheels=false;return result}
  const v=this.vehicle,q=state.quaternion;
  let anyContact=false,maxComp=0;
  for(const w of this.wheels){
   const offsetBody=[w.x,w.y,w.z*extension];
   const offsetNed=qRotate(q,offsetBody);
   const wheelAltitude=state.position.altitudeM-offsetNed[2];
   const contactAltitude=groundElevationM+w.radius;
   const compression=contactAltitude-wheelAltitude;
   if(compression<=0){w.compression=0;w.onGround=false;continue}
   w.onGround=true;anyContact=true;
   w.compression=Math.min(compression,w.travel);
   maxComp=Math.max(maxComp,w.compression);
   // Wheel velocity in NED includes the rotational term about the CG.
   const wheelVelNed=velocityNed.map((c,i)=>c+qRotate(q,cross(state.omegaBody,offsetBody))[i]);
   const sink=wheelVelNed[2]; // positive is descending
   // Strut: spring plus damper, damping only while compressing hard, and never
   // pulling the aircraft down.
   const spring=w.springNpm*w.compression;
   const damper=w.damperNspm*Math.max(-w.travel*4,sink);
   let up=spring+damper;
   // Bottoming out stiffens sharply rather than passing through the ground.
   if(compression>w.travel)up+=w.springNpm*8*(compression-w.travel);
   up=Math.max(0,up);
   // Friction in the ground plane. Longitudinal is rolling plus braking, lateral
   // resists scrubbing; both are capped by the available normal load.
   const track=[wheelVelNed[0],wheelVelNed[1]];
   const heading=qRotate(q,[1,0,0]),hMag=Math.hypot(heading[0],heading[1])||1;
   const fwd=[heading[0]/hMag,heading[1]/hMag],side=[-fwd[1],fwd[0]];
   const vFwd=track[0]*fwd[0]+track[1]*fwd[1],vSide=track[0]*side[0]+track[1]*side[1];
   const muRoll=w.braked?(w.muRoll+(w.muBrake-w.muRoll)*clamp(ctl.wheelBrake??0,0,1)):w.muRoll;
   const steer=w.steerable?(ctl.yaw??0)*(v.steerLimitRad??.52):0;
   const fFwd=-Math.sign(vFwd)*Math.min(muRoll*up,Math.abs(vFwd)*up*.6);
   const fSide=-Math.sign(vSide)*Math.min(w.muSide*up,Math.abs(vSide)*up*1.4)+Math.sin(steer)*up*w.muSide*.35;
   const forceNed=[fFwd*fwd[0]+fSide*side[0],fFwd*fwd[1]+fSide*side[1],-up];
   const forceBody=qRotateInv(q,forceNed);
   const momentBody=cross(offsetBody,forceBody);
   for(let i=0;i<3;i++){result.forceBody[i]+=forceBody[i];result.momentBody[i]+=momentBody[i]}
   result.contacts++;
   result.struts.push({id:w.id,compression:w.compression,loadN:up});
  }
  if(anyContact&&this.wasAirborne){this.touchdownRateMps=Math.max(0,velocityNed[2]);this.wasAirborne=false}
  if(!anyContact)this.wasAirborne=true;
  this.weightOnWheels=anyContact;this.maxCompression=maxComp;
  result.weightOnWheels=anyContact;result.maxCompression=maxComp;
  return result;
 }
}
