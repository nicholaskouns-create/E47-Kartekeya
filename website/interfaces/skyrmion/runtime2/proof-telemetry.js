import {qNorm,norm} from './math.js';
import {stateIssue} from './flight-state.js';
export class ProofTelemetry{
 constructor(){this.schema='SKYRMION-PROOF-TELEMETRY-2.1';this.sequence=0;this.failures=0;this.last=null}
 inspect({state,vehicle,world,e47,propulsion,fixedStepHz,fault=null}){
  const conventional=vehicle.evidence==='conventional';
  const checks={finite:[...state.velocityBody,...state.quaternion,...state.omegaBody,state.position.lat,state.position.lon,state.position.altitudeM].every(Number.isFinite),numericalState:!stateIssue(state)&&!fault,quaternion:Math.abs(qNorm(state.quaternion)-1)<1e-6,positiveMass:vehicle.massKg>0,fixedStep:fixedStepHz>=60&&fixedStepHz<=240,evidenceBoundary:conventional?propulsion.receipt?.mode==='conventional'&&e47===null:propulsion.receipt?.mode==='experimental-simulation',craftIdentity:state.vehicleId===vehicle.id};
  if(!conventional)checks.e47=!!e47&&Number.isFinite(e47.capture)&&e47.capture>=0&&e47.capture<=1;
  const pass=Object.values(checks).every(Boolean);if(!pass)this.failures++;
  return this.last={schema:this.schema,sequence:++this.sequence,t:state.t,pass,failures:this.failures,checks,scope:'Numerical integrity and model isolation; not an aircraft performance certificate',fault,vehicle:{id:vehicle.id,evidence:vehicle.evidence,model:vehicle.model},world:{density:world.density,gravity:world.gravity},e47,speedMps:norm(state.velocityBody),propulsion:propulsion.receipt};
 }
}
