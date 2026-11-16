// SKYRMION RT3 · E47 experimental drive.
// Spectrum and epsilon come from the generated canonical lock, never from literals
// typed into a runtime, so the browser cannot drift from src/e47.
import {CASIMIR,MULT,ROOTS,N,EPS,OMEGA_C,DIM_E47} from '../../shared/e47-lock.js';
import {clamp} from './math.js';

const spectrum=[];
for(let j=0;j<CASIMIR.length;j++)for(let i=0;i<MULT[j];i++)spectrum.push(CASIMIR[j]);
const k2=spectrum.map(c=>{let k=1;for(const root of ROOTS)k*=(c-root);return k*k});
const inKernel=spectrum.map(c=>ROOTS.includes(c));

export const DRIVES=Object.freeze({
 eidolon_scalar:{maxThrustN:180000,torqueGain:1.25,label:'scalar-coherence'},
 manta_morph:{maxThrustN:145000,torqueGain:1.65,label:'programmable-matter/spectral-morph'},
 skyrmion_coherence:{maxThrustN:205000,torqueGain:1.45,label:'coherence-propulsion'},
 syntax_jacob:{maxThrustN:220000,torqueGain:1.05,label:'coherence/inertial'}
});

export class E47Drive{
 constructor(driveId){
  const spec=DRIVES[driveId];
  if(!spec)throw new Error('Unknown drive '+driveId);
  this.spec=spec;this.driveId=driveId;
  this.schema='RT3-E47-DRIVE-1.0';this.lock='E47-LOCK-FROM-SRC-E47';
  this.state=new Float64Array(N);this.iterations=0;this.seed(47);
 }
 seed(seed=47){
  let n=0;
  for(let i=0;i<N;i++){
   const v=Math.sin((i+1)*(seed+1)*.731)+.31*Math.cos((i+3)*(seed+7)*.173);
   this.state[i]=v;n+=v*v;
  }
  n=Math.sqrt(n)||1;
  for(let i=0;i<N;i++)this.state[i]/=n;
  this.iterations=0;return this.snapshot();
 }
 reset(){return this.seed(47)}
 step(signal={},dt=1/120){
  const drive=1e-4*((signal.controlNorm||0)+Math.sin(signal.alpha||0)+Math.cos(signal.mach||0));
  let n=0;
  for(let i=0;i<N;i++){
   this.state[i]=(this.state[i]+drive)*(1-EPS*k2[i]);
   n+=this.state[i]*this.state[i];
  }
  n=Math.sqrt(n)||1;
  for(let i=0;i<N;i++)this.state[i]/=n;
  this.iterations++;return this.snapshot();
 }
 snapshot(){
  let total=0,cap=0,res=0;
  for(let i=0;i<N;i++){
   const p=this.state[i]*this.state[i];
   total+=p;if(inKernel[i])cap+=p;res+=k2[i]*p;
  }
  const t=total||1;
  return {schema:this.schema,lock:this.lock,epsilon:EPS,omegaC:OMEGA_C,kernelDim:DIM_E47,carrier:N,
   capture:cap/t,residual:Math.sqrt(res/t),iterations:this.iterations};
 }
 // Gravity stays active and the aerodynamic load is exactly zero: an experimental
 // craft cannot borrow lift it has not earned.
 forces(state,mass,inertia,snapshot=this.snapshot()){
  const s=this.spec,c=state.controls;
  const coherence=clamp(.3+.9*snapshot.capture-.05*Math.log10(1+snapshot.residual),.15,1.2);
  const F=s.maxThrustN*c.throttle*coherence,g=s.torqueGain*mass;
  return {
   forceBody:[F,0,-F*.04*c.pitch],
   momentBody:[g*c.roll,g*1.2*c.pitch,g*.7*c.yaw].map((m,i)=>m-1.8*inertia[i]*state.omegaBody[i]),
   receipt:{mode:'experimental-simulation',drive:this.driveId,label:s.label,coherence,
    scope:'Simulation assumption. Coherence is a thrust multiplier, not a probability, and not a physical claim.'}
  };
 }
}
