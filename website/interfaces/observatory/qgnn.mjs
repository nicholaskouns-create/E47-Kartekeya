/** Exact complex-vector simulation of four compressed Hermitian eigengates.
 * Static coefficients compiled from the attributed user attachment; no browser dependencies.
 * Coordinates refer to the attachment's retained eigenbasis, not physical torus-node addresses.
 */
export const SOURCE_SHA256='054c2d7e4b634c5f796c127d8452466c56fec9012ff86a1dfa6658ab7b2f04fb';
const N=47;
function real(x){return typeof x==='number'&&Number.isFinite(x)&&Math.abs(x)<1e8;}
function complex(z){return Array.isArray(z)&&z.length===2&&z.every(real);}
function matrix(a){return Array.isArray(a)&&a.length===N&&a.every(row=>Array.isArray(row)&&row.length===N&&row.every(complex));}
export function validateCarrier(data){
 if(!data||data.schema!=='E47-QGNN-CARRIER-1'||data.dimension!==N||data.source?.sha256!==SOURCE_SHA256)throw new Error('Unsupported or unattributed QGNN carrier data.');
 if(!Array.isArray(data.eigensystems)||data.eigensystems.length!==4||!data.eigensystems.every(s=>Array.isArray(s.eigenvalues)&&s.eigenvalues.length===N&&s.eigenvalues.every(real)&&matrix(s.vectors)))throw new Error('Invalid gate eigensystems.');
 if(!matrix(data.observable)||!Array.isArray(data.input)||data.input.length!==N||!data.input.every(complex))throw new Error('Invalid observable or input state.');
 const norm=data.input.reduce((s,[a,b])=>s+a*a+b*b,0);if(Math.abs(norm-1)>1e-10)throw new Error('Carrier input is not normalized.');
 if(!real(data.projectionProbability)||data.projectionProbability<=0||data.projectionProbability>1)throw new Error('Invalid input projection probability.');
 return data;
}
let cached;
export async function loadCarrier(){if(cached)return cached;const response=await fetch(new URL('./qgnn-data.json',import.meta.url));if(!response.ok)throw new Error('QGNN carrier data could not be loaded.');cached=validateCarrier(await response.json());return cached;}
/** angles: four finite radians, each bounded to [-2π,2π]. */
export function evolveCarrier(data,angles){
 validateCarrier(data);
 if(!Array.isArray(angles)||angles.length!==4||angles.some(a=>!real(a)||Math.abs(a)>2*Math.PI))throw new Error('Expected four finite gate angles within ±2π.');
 let state=data.input.map(z=>z.slice());
 for(let gate=0;gate<4;gate++){
  const {eigenvalues:e,vectors:v}=data.eigensystems[gate],coeff=Array.from({length:N},()=>[0,0]);
  // V† |ψ〉, diagonal exp(-iθλ), then V. Eigenvectors are matrix columns.
  for(let j=0;j<N;j++){let a=0,b=0;for(let i=0;i<N;i++){const [vr,vi]=v[i][j],[xr,xi]=state[i];a+=vr*xr+vi*xi;b+=vr*xi-vi*xr;}const co=Math.cos(angles[gate]*e[j]),si=Math.sin(angles[gate]*e[j]);coeff[j]=[a*co+b*si,b*co-a*si];}
  state=Array.from({length:N},(_,i)=>{let a=0,b=0;for(let j=0;j<N;j++){const [vr,vi]=v[i][j],[xr,xi]=coeff[j];a+=vr*xr-vi*xi;b+=vr*xi+vi*xr;}return [a,b];});
 }
 let expectation=0,imaginary=0;
 for(let i=0;i<N;i++){let a=0,b=0;for(let j=0;j<N;j++){const [or,oi]=data.observable[i][j],[xr,xi]=state[j];a+=or*xr-oi*xi;b+=or*xi+oi*xr;}const [xr,xi]=state[i];expectation+=xr*a+xi*b;imaginary+=xr*b-xi*a;}
 const probabilities=state.map(([a,b])=>a*a+b*b),norm=probabilities.reduce((s,v)=>s+v,0);
 return {expectation,norm,error:Math.abs(norm-1),imaginaryResidual:Math.abs(imaginary),probabilities,sourceSha256:data.source.sha256};
}
