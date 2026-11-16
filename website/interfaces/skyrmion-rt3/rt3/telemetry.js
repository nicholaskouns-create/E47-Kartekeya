// SKYRMION RT3 · state validation and proof receipts.
import {norm,qNorm} from './math.js';

export function stateIssue(s){
 if(!s||!s.position||!s.controls)return 'Missing flight state';
 for(const [name,n] of [['velocityBody',3],['omegaBody',3],['quaternion',4]])
  if(!Array.isArray(s[name])||s[name].length!==n||!s[name].every(Number.isFinite))return 'Non-finite '+name;
 const p=s.position;
 const scalars=[s.t,p.lat,p.lon,p.altitudeM,
  ...['throttle','pitch','roll','yaw','flap','gear','brake','afterburner'].map(k=>s.controls[k])];
 if(!scalars.every(Number.isFinite))return 'Non-finite coordinates or controls';
 if(Math.abs(p.lat)>90||Math.abs(p.lon)>180)return 'Coordinates outside WGS84 range';
 if(p.altitudeM<-500||p.altitudeM>1e6)return 'Altitude outside modelled range';
 if(norm(s.velocityBody)>1e5||norm(s.omegaBody)>100)return 'Numerical integration range exceeded';
 if(Math.abs(qNorm(s.quaternion)-1)>1e-6)return 'Invalid attitude quaternion';
 return null;
}
export const copyState=s=>structuredClone(s);

export class ProofTelemetry{
 constructor(){this.schema='SKYRMION-PROOF-TELEMETRY-3.0';this.sequence=0;this.failures=0;this.last=null}
 inspect({state,vehicle,mass,env,e47,propulsion,gear,fixedStepHz,fault=null,integrator=null}){
  const conventional=vehicle.evidence==='conventional';
  const checks={
   finite:[...state.velocityBody,...state.quaternion,...state.omegaBody,
    state.position.lat,state.position.lon,state.position.altitudeM].every(Number.isFinite),
   numericalState:!stateIssue(state)&&!fault,
   quaternion:Math.abs(qNorm(state.quaternion)-1)<1e-6,
   positiveMass:mass.massKg>0,
   massConservation:mass.fuelKg>=0&&mass.fuelKg<=(vehicle.fuelCapacityKg??0)+1e-9,
   fixedStep:fixedStepHz>=60&&fixedStepHz<=480,
   // The isolation boundary, re-checked every step rather than asserted once.
   evidenceBoundary:conventional
    ? propulsion?.receipt?.mode==='conventional'&&e47===null
    : propulsion?.receipt?.mode==='experimental-simulation',
   craftIdentity:state.vehicleId===vehicle.id,
   atmosphere:env.density>0&&env.speedOfSound>0&&env.gravity>9.5&&env.gravity<9.9
  };
  if(!conventional)checks.e47=!!e47&&Number.isFinite(e47.capture)&&e47.capture>=0&&e47.capture<=1;
  if(conventional)checks.gearIsolation=!gear||gear.weightOnWheels===(gear.contacts>0);
  const pass=Object.values(checks).every(Boolean);
  if(!pass)this.failures++;
  return this.last={
   schema:this.schema,sequence:++this.sequence,t:state.t,pass,failures:this.failures,checks,
   scope:'Numerical integrity and model isolation. Not an aircraft performance certificate and not a physical claim.',
   fault,vehicle:{id:vehicle.id,evidence:vehicle.evidence,model:vehicle.model},
   mass:{totalKg:mass.massKg,fuelKg:mass.fuelKg},
   world:{density:env.density,gravity:env.gravity,temperatureK:env.temperatureK},
   integrator,e47,speedMps:norm(state.velocityBody),propulsion:propulsion?.receipt??null
  };
 }
}
