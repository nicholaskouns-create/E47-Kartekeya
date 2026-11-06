#!/usr/bin/env node
import fs from 'node:fs'; import vm from 'node:vm'; import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../website/interfaces/matrix/mps-worker.js',import.meta.url),'utf8');
function run(data){let result;const ctx={Float64Array,Math,Number,Array,console,postMessage:x=>{result=x}};vm.createContext(ctx);vm.runInContext(source,ctx);ctx.onmessage({data});return result}
for(const n of [2,3,4,5,6,7,8]){const chi=1<<Math.floor(n/2);const x=run({n,layers:4,phi:.7,chi,validate:true});assert.equal(x.engine,'two-site-mps');assert.equal(x.backend,'web-worker-js');assert.equal(x.validation.mode,'exact-equivalence');assert.ok(x.validation.relative_l2<1e-9,`n=${n} err=${x.validation.relative_l2}`);assert.ok(Math.abs(x.norm-1)<1e-9)}
const t=run({n:8,layers:8,phi:.7,chi:2,validate:true});assert.equal(t.validation.mode,'controlled-truncation');assert.equal(t.validation.pass,true);assert.ok(t.validation.relative_l2<=t.truncation.state_error_bound+1e-9);assert.ok(Math.abs(t.norm-t.truncation.retained_norm2)<1e-9);assert.ok(t.discard>0);
// Both entanglers must match a dense oracle, including odd-size registers.
for(const n of [3,6,7]){const x=run({n,layers:5,phi:.37,chi:1<<Math.floor(n/2),entangler:'chain',validate:true});assert.equal(x.validation.pass,true);assert.ok(x.validation.relative_l2<1e-9)}
// Canonical sweeps preserve the physical state and discarded weight is actual norm loss.
{
 const ctx={Float64Array,Math,Number,Array,console,postMessage(){},assert};vm.createContext(ctx);vm.runInContext(source,ctx);
 vm.runInContext(`{
  const m=init(6);for(let k=0;k<5;k++){for(let q=0;q<6;q++){m[q]=one(m[q],H());m[q]=one(m[q],R(.7));}for(let q=k%2;q<5;q+=2){centerBond(m,q);const [a,b]=two(m[q],m[q+1],CNOT,8);m[q]=a;m[q+1]=b;}}
  const norm=v=>v.reduce((s,z)=>s+a2(z),0),before=dense(m);centerBond(m,2);const gauged=dense(m);
  assert.ok(Math.sqrt(before.reduce((s,z,i)=>s+a2(add(z,scale(gauged[i],-1))),0))<1e-10);
  const [a,b,t]=two(m[2],m[3],CNOT,1);m[2]=a;m[3]=b;
  assert.ok(t.discarded>1e-5);assert.ok(Math.abs(norm(dense(m))-norm(before)*(1-t.discarded))<1e-10);
 }`,ctx);
}
const z=run({n:6,layers:4,phi:.7,chi:8,validate:false,noise:'trajectory',g1:.03,gphi:.04,seed:47125});assert.equal(z.ok,true);assert.equal(z.noise.model,'amplitude-damping+phase-flip-trajectory');assert.equal(z.noise.seed,47125);assert.ok(Math.abs(z.norm-1)<1e-9);const z2=run({n:6,layers:4,phi:.7,chi:8,validate:false,noise:'trajectory',g1:.03,gphi:.04,seed:47125});assert.equal(JSON.stringify(z.statevector),JSON.stringify(z2.statevector));const too=run({n:17,layers:1,phi:.7,chi:2,noise:'trajectory'});assert.equal(too.ok,false);
console.log(JSON.stringify({status:'PASS',exact_registers:'n=2..8',tolerance:1e-9,truncation_case:{n:8,chi:2,relative_l2:t.validation.relative_l2,discarded_weight:t.discard}},null,2));
