/** E47 sector observables, faithful to the attached Gamma polynomial and canonical workbench.
 * This models sector norms, not the full QGNN's noncommuting gates or a neural Hilbert encoding. */
export const VALUES = [0,2,6,12,20,30,42];
export const COUNTS = [1,9,25,28,27,22,13];
export const RHO = 15/17;
const G = VALUES.map(c => 1-((c-6)*(c-30))**2/99144);
const SCHEMA='E47-OBSERVATORY-REPLAY-1';
function finite(v,min,max,name){if(typeof v!=='number'||!Number.isFinite(v)||v<min||v>max)throw new Error(`${name} outside supported bounds.`);return v;}
function integer(v,min,max,name){finite(v,min,max,name);if(!Number.isInteger(v))throw new Error(`${name} must be an integer.`);return v;}
function random(seed){integer(seed,0,4294967295,'Seed');let s=seed>>>0;return ()=>{s=(s+0x6D2B79F5)>>>0;let t=s;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
function spectralConfig(c={}){return {seed:integer(c.seed??47,0,4294967295,'Seed'),selectedWeight:finite(c.selectedWeight??0.376,0,1,'Selected weight'),steps:integer(c.steps??80,0,300,'Steps'),angle:finite(c.angle??0,-Math.PI*2,Math.PI*2,'Angle')};}
export function createExperiment(config={}){return spectralRun(config);}
export function spectralRun(config={}){
 const inputs=spectralConfig(config),rng=random(inputs.seed);
 const weights=COUNTS.map(n=>Array.from({length:n},()=>-Math.log(Math.max(rng(),2**-32))).reduce((a,b)=>a+b,0));
 const selected=weights[2]+weights[5],other=weights.reduce((s,v,i)=>s+(i===2||i===5?0:v),0);
 weights.forEach((v,i)=>weights[i]=v*(i===2||i===5?inputs.selectedWeight/selected:(1-inputs.selectedWeight)/other));
 const records=[];
 for(let n=0;n<=inputs.steps;n++){
  const evolved=weights.map((w,i)=>w*G[i]**(2*n));
  const residual=evolved.reduce((s,w,i)=>s+(i===2||i===5?0:w),0),probability=inputs.selectedWeight+residual;
  records.push({n,error:Math.sqrt(residual),bound:Math.sqrt(1-inputs.selectedWeight)*RHO**n,probability,fidelity:inputs.selectedWeight>0?inputs.selectedWeight/probability:null,occupancy:probability>0?inputs.selectedWeight/probability:null,weights:evolved});
 }
 return {schema:'E47-OBSERVATORY-SPECTRAL-1',inputs,weights,kernelWeight:inputs.selectedWeight,kernel_weight:inputs.selectedWeight,rho:RHO,records,phase:inputs.angle,scope:'Seven-sector norm simulation. Angle is a norm-preserving phase and does not change sector probabilities. Not the full QGNN gate family.'};
}
/** Dataset entries are {x,y,label}; coordinates in [-1,1], label 0 or 1. */
export function makeDataset(kind='Circle',seed=47,count=128){
 if(!['Circle','XOR','Spiral','Linear'].includes(kind))throw new Error('Unknown dataset.');integer(count,8,512,'Dataset size');const rng=random(seed);
 return Array.from({length:count},(_,i)=>{let x,y,label;if(kind==='Spiral'){label=i%2;const r=0.08+0.9*rng(),a=r*5+label*Math.PI+(rng()-.5)*.25;x=r*Math.cos(a);y=r*Math.sin(a);}else{x=rng()*2-1;y=rng()*2-1;label=kind==='Circle'?Number(x*x+y*y<.48):kind==='XOR'?Number(x*y>0):Number(y>.55*x+.08);}return {x,y,label};});
}
export function createTrainer({dataset=makeDataset(),hidden=8,seed=47,learningRate=.22}={}){
 integer(hidden,2,32,'Hidden width');finite(learningRate,.001,2,'Learning rate');
 if(!Array.isArray(dataset)||dataset.length<8||dataset.length>512)throw new Error('Expected 8–512 training points.');
 const points=dataset.map(p=>({x:finite(p.x,-1,1,'x'),y:finite(p.y,-1,1,'y'),label:integer(p.label,0,1,'Label')})),rng=random(seed),scale=Math.sqrt(6/(hidden+2));
 return {dataset:points,hidden,seed,learningRate,epoch:0,w:Array.from({length:hidden},()=>[(rng()*2-1)*scale,(rng()*2-1)*scale]),b:Array(hidden).fill(0),v:Array.from({length:hidden},()=>rng()*2-1),bias:0};
}
const sigmoid=z=>1/(1+Math.exp(-Math.max(-40,Math.min(40,z))));
function forward(t,x,y){const h=t.w.map((w,i)=>Math.tanh(w[0]*x+w[1]*y+t.b[i]));return {h,p:sigmoid(h.reduce((s,v,i)=>s+v*t.v[i],t.bias))};}
export function predict(t,x,y){finite(x,-2,2,'x');finite(y,-2,2,'y');return forward(t,x,y).p;}
/** Full-batch analytic backprop, binary cross entropy objective. Mutates trainer. */
export function trainEpoch(t){
 if(t.epoch>=20000)throw new Error('Training epoch limit reached.');
 const dw=t.w.map(()=>[0,0]),db=t.b.map(()=>0),dv=t.v.map(()=>0);let dout=0;
 for(const {x,y,label} of t.dataset){const {h,p}=forward(t,x,y),d=p-label;dout+=d;h.forEach((a,i)=>{dv[i]+=d*a;const dh=d*t.v[i]*(1-a*a);dw[i][0]+=dh*x;dw[i][1]+=dh*y;db[i]+=dh;});}
 const rate=t.learningRate/t.dataset.length;t.w.forEach((w,i)=>{w[0]-=rate*dw[i][0];w[1]-=rate*dw[i][1];t.b[i]-=rate*db[i];t.v[i]-=rate*dv[i];});t.bias-=rate*dout;t.epoch++;return trainerMetrics(t);
}
export function trainerMetrics(t){let loss=0,mse=0,correct=0;for(const d of t.dataset){const p=forward(t,d.x,d.y).p;loss-=d.label*Math.log(Math.max(p,1e-15))+(1-d.label)*Math.log(Math.max(1-p,1e-15));mse+=(p-d.label)**2;correct+=Number(Number(p>=.5)===d.label);}const n=t.dataset.length;return {epoch:t.epoch,loss:loss/n,mse:mse/n,accuracy:correct/n};}
function keys(obj,allowed,name){if(!obj||typeof obj!=='object'||Array.isArray(obj)||Object.keys(obj).some(k=>!allowed.includes(k)))throw new Error(`Invalid ${name} fields.`);}
export function validateReplay(value){
 keys(value,['schema','spectral','neural','quantum','view'],'replay');if(value.schema!==SCHEMA)throw new Error('Unsupported replay schema.');
 keys(value.spectral,['seed','selectedWeight','steps','angle'],'spectral');const result={schema:SCHEMA,spectral:spectralConfig(value.spectral)};
 if(value.neural!==undefined){const n=value.neural;keys(n,['dataset','hidden','seed','learningRate','epochs'],'neural');if(!['Circle','XOR','Spiral','Linear'].includes(n.dataset))throw new Error('Unknown replay dataset.');result.neural={dataset:n.dataset,hidden:integer(n.hidden,2,32,'Hidden width'),seed:integer(n.seed,0,4294967295,'Seed'),learningRate:finite(n.learningRate,.001,2,'Learning rate'),epochs:integer(n.epochs,0,20000,'Epochs')};}
 if(value.quantum!==undefined){keys(value.quantum,['angles'],'quantum');const angles=value.quantum.angles;if(!Array.isArray(angles)||angles.length!==4)throw new Error('Quantum replay requires four angles.');result.quantum={angles:angles.map(a=>finite(a,-2*Math.PI,2*Math.PI,'Gate angle'))};}
 if(value.view!==undefined){if(!['city','signal','learn','evidence','atlas'].includes(value.view))throw new Error('Unknown replay view.');result.view=value.view;}return result;
}
export function encodeReplay(state){return encodeURIComponent(JSON.stringify(validateReplay(state)));}
export function decodeReplay(text){if(typeof text!=='string'||text.length>8192)throw new Error('Replay exceeds supported size.');return validateReplay(JSON.parse(text.startsWith('{')?text:decodeURIComponent(text)));}
