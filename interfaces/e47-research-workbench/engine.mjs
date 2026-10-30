/** Seven-sector observables for the canonical E47 construction. No phase reconstruction. */
export const VERSION='1.0.0';
export const VALUES=[0,2,6,12,20,30,42];
export const COUNTS=[1,9,25,28,27,22,13];
export const Q=VALUES.map(c=>((c-6)*(c-30))**2);
export const GAP=11664, QMAX=186624, EPSILON=1/99144;
export function normalize(weights){
  if(!Array.isArray(weights)||weights.length!==7||weights.some(w=>typeof w!=='number'||!Number.isFinite(w)||w<0))throw new Error('Provide seven finite, nonnegative sector weights.');
  const sum=weights.reduce((a,b)=>a+b,0);
  if(!(sum>0)&&Number.isFinite(sum))throw new Error('At least one sector must have positive weight.');
  if(!Number.isFinite(sum))throw new Error('Weight total exceeds the supported range.');
  return weights.map(w=>w/sum);
}
export function seededWeights(seed){
  if(!Number.isInteger(seed)||seed<0||seed>4294967295)throw new Error('Seed must be an integer from 0 to 4294967295.');
  // mulberry32 + exponential complex-Gaussian squared magnitudes in a Casimir eigenbasis.
  let s=seed>>>0;
  const random=()=>{s=(s+0x6D2B79F5)>>>0;let t=s;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};
  return normalize(COUNTS.map(count=>Array.from({length:count},()=>-Math.log(Math.max(random(),2**-32))).reduce((a,b)=>a+b,0)));
}
export function simulate({weights=COUNTS,steps=220,epsilon=EPSILON,mode='discrete',horizon=15}={}){
  const w=normalize(weights);
  if(!Number.isInteger(steps)||steps<1||steps>1000)throw new Error('Steps must be an integer from 1 to 1000.');
  if(!['discrete','continuous'].includes(mode))throw new Error('Unknown evolution mode.');
  if(!Number.isFinite(epsilon)||epsilon<=0||epsilon>=2/QMAX)throw new Error('Step must satisfy 0 < ε < 2/q_max.');
  if(!Number.isFinite(horizon)||horizon<=0||horizon>100)throw new Error('Horizon must lie between 0 and 100, excluding zero.');
  const a=w[2]+w[5],rho=Math.max(...Q.filter(q=>q>0).map(q=>Math.abs(1-epsilon*q))),records=[];
  for(let n=0;n<=steps;n++){
    const tau=mode==='continuous'?n*horizon/steps:n*epsilon*GAP;
    const evolved=w.map((weight,i)=>weight*(mode==='discrete'?Math.pow(1-epsilon*Q[i],2*n):Math.exp(-2*Q[i]*tau/GAP)));
    const b=evolved.reduce((sum,x,i)=>sum+(Q[i]>0?x:0),0),probability=a+b;
    const occupancy=probability>0?a/probability:null;
    const numerator=evolved.reduce((sum,x,i)=>sum+x*Q[i],0);
    const effective=b>0?numerator/b:null;
    records.push({n,tau,error:Math.sqrt(b),bound:Math.sqrt(Math.max(0,1-a))*(mode==='discrete'?rho**n:Math.exp(-tau)),probability,occupancy,fidelity:a>0?occupancy:null,lambda_eff:effective,energy:probability>0?numerator/probability:null,occupancy_derivative_tau:effective!==null&&occupancy!==null?2*effective/GAP*occupancy*(1-occupancy):null});
  }
  return {schema:'E47-WORKBENCH-RUN-1.0',version:VERSION,evidence:'E2',inputs:{weights:w,steps,epsilon,mode,horizon},rho,kernel_weight:a,records,scope:'Sector norm observables; conditional fidelity is undefined for zero selected weight.'};
}
export function importRun(text){
  if(text.length>2_000_000)throw new Error('Run file exceeds 2 MB.');
  const run=JSON.parse(text);
  if(run.schema!=='E47-WORKBENCH-RUN-1.0'||run.version!==VERSION||!run.inputs)throw new Error('Unsupported experiment schema or version.');
  return simulate(run.inputs); // Recompute; never trust imported results or executable content.
}
export function runCSV(run){
  const keys=['n','tau','error','bound','probability','occupancy','fidelity','lambda_eff','energy','occupancy_derivative_tau'];
  return [keys.join(','),...run.records.map(r=>keys.map(k=>r[k]??'').join(','))].join('\n')+'\n';
}
export function runMarkdown(run){
  const last=run.records.at(-1),f=x=>x===null?'undefined':Number(x).toPrecision(8);
  return `# E47 Research WorkBench experiment\n\nEvidence: E2 (numerical model). Version: ${VERSION}.\n\nMode: ${run.inputs.mode}; samples: ${run.inputs.steps}; epsilon: ${run.inputs.epsilon}; horizon: ${run.inputs.horizon}.\n\nInitial selected weight: ${f(run.kernel_weight)}. Final error: ${f(last.error)}. Bound: ${f(last.bound)}. Conditional occupancy: ${f(last.occupancy)}.\n\nSector weights: ${JSON.stringify(run.inputs.weights)}\n\n${run.scope}\n\nImport the matching JSON receipt to reproduce the displayed observables. Workspace links are navigation links, not live synchronization.\n`;
}
