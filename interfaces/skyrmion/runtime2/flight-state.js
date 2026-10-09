import {norm,qNorm} from './math.js';
export function stateIssue(s){
 if(!s||!s.position||!s.controls)return 'Missing flight state';
 for(const [name,n] of [['velocityBody',3],['omegaBody',3],['quaternion',4]]){
  if(!Array.isArray(s[name])||s[name].length!==n||!s[name].every(Number.isFinite))return 'Non-finite '+name;
 }
 const p=s.position;
 if(![s.t,p.lat,p.lon,p.altitudeM,...['throttle','pitch','roll','yaw'].map(k=>s.controls[k])].every(Number.isFinite))return 'Non-finite coordinates or controls';
 if(Math.abs(p.lat)>90||Math.abs(p.lon)>180)return 'Coordinates outside WGS84 range';
 if(Math.abs(p.altitudeM)>1e8||norm(s.velocityBody)>1e5||norm(s.omegaBody)>100)return 'Numerical integration range exceeded';
 if(Math.abs(qNorm(s.quaternion)-1)>1e-6)return 'Invalid attitude quaternion';
 return null;
}
export const copyState=s=>structuredClone(s);
