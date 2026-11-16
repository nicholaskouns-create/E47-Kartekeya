// SKYRMION RT3 · propulsion with spool dynamics and fuel accounting.
import {clamp} from './math.js';
const RHO0=1.225;

// An engine does not answer the throttle instantly. N1 lags, and it lags harder
// spooling up than down, which is most of what makes throttle handling feel real.
export class Spool{
 constructor({idle=.07,spoolUp=2.6,spoolDown=1.4}={}){
  Object.assign(this,{idle,spoolUp,spoolDown});this.n1=idle;
 }
 step(command,dt){
  const target=clamp(Math.max(this.idle,command),0,1);
  const tau=target>this.n1?this.spoolUp:this.spoolDown;
  this.n1+=(target-this.n1)*(1-Math.exp(-dt/tau));
  return this.n1;
 }
 reset(value=this.idle){this.n1=value;return this.n1}
}

export const ENGINES=Object.freeze({
 // Afterburning turbofan. Thrust falls with density and with Mach past the fan's
 // best operating point; the afterburner is a multiplier on the dry rating.
 f100:{kind:'afterburning-turbofan',maxThrustN:79000,afterburnerN:129000,tsfc:2.1e-5,abTsfc:5.4e-5,
  factor:({mach,density})=>Math.pow(clamp(density/RHO0,1e-4,1),.72)*clamp(1-.035*Math.max(0,mach-1)+.18*Math.min(mach,.9),.55,1.42)},
 // Ram-compression turbojet: thrust climbs steeply with Mach, which is the whole
 // reason an SR-71 is efficient only where it is fast.
 j58:{kind:'ram-turbojet',maxThrustN:145000,afterburnerN:290000,tsfc:2.4e-5,abTsfc:5.0e-5,
  // Calibrated to two public anchors: full static sea-level rating, and roughly
  // 89 kN installed at Mach 3.0 near 24 km, which is where the airframe cruises.
  // The cap is the inlet limit that kept the aircraft from over-thrusting down low.
  factor:({mach,density})=>clamp(Math.pow(clamp(density/RHO0,1e-5,1),.765)*(1+.9*mach),.02,1.25)},
 // Rocket: no air needed, so thrust rises slightly as back pressure falls.
 x15_rocket:{kind:'rocket',maxThrustN:254000,afterburnerN:254000,tsfc:3.1e-4,abTsfc:3.1e-4,
  factor:({pressurePa})=>clamp(1+.13*(1-clamp(pressurePa/101325,0,1)),1,1.13),airbreathing:false}
});

export class PropulsionModel{
 constructor(vehicle){
  const spec=ENGINES[vehicle.propulsion];
  if(!spec)throw new Error('Unknown engine '+vehicle.propulsion);
  this.vehicle=vehicle;this.spec=spec;this.spool=new Spool(vehicle.spool||{});
  this.schema='RT3-PROPULSION-1.1';this.fuelFlow=0;
 }
 reset(){this.spool.reset();this.fuelFlow=0}
 // Called once per integrator step by the runtime, not per stage.
 advance(throttleCommand,dt){return this.spool.step(throttleCommand,dt)}
 forces(state,env,fuelKg){
  const s=this.spec,ctl=state.controls,n1=this.spool.n1;
  const dry=s.maxThrustN,ab=s.afterburnerN;
  const burner=clamp(ctl.afterburner??0,0,1);
  const rating=dry+(ab-dry)*burner;
  const available=fuelKg>0?rating*n1*s.factor({mach:env.mach??0,density:env.density,pressurePa:env.pressurePa}):0;
  // Ram drag: an airbreathing engine must accelerate the air it swallows.
  const ramDrag=s.airbreathing===false?0:available*.035*clamp((env.mach??0)/3,0,1);
  const thrust=Math.max(0,available-ramDrag);
  const tsfc=s.tsfc+(s.abTsfc-s.tsfc)*burner;
  this.fuelFlow=fuelKg>0?thrust*tsfc:0;
  return {
   forceBody:[thrust,0,0],momentBody:[0,0,0],
   receipt:{mode:'conventional',engine:this.vehicle.propulsion,kind:s.kind,n1,afterburner:burner,thrustN:thrust,fuelFlowKgs:this.fuelFlow}
  };
 }
}

// Fuel burn changes mass and, because fuel sits out in the wings, inertia with it.
export class MassModel{
 constructor(vehicle){
  this.vehicle=vehicle;this.fuelKg=vehicle.fuelCapacityKg??0;this.schema='RT3-MASS-1.0';
 }
 reset(fraction=1){this.fuelKg=(this.vehicle.fuelCapacityKg??0)*clamp(fraction,0,1);return this.fuelKg}
 burn(flowKgs,dt){this.fuelKg=Math.max(0,this.fuelKg-flowKgs*dt);return this.fuelKg}
 get massKg(){return this.vehicle.dryMassKg+this.fuelKg}
 get inertia(){
  const v=this.vehicle,full=v.fuelCapacityKg||1,frac=this.fuelKg/full;
  // Roll inertia is the most fuel-sensitive axis on a wet wing; pitch and yaw less so.
  const gain=[.42,.18,.20];
  return v.dryInertia.map((I,i)=>I*(1+gain[i]*frac));
 }
 get fuelFraction(){return (this.vehicle.fuelCapacityKg||0)>0?this.fuelKg/this.vehicle.fuelCapacityKg:0}
}
