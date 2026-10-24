import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {simulate,importRun,seededWeights,runCSV,EPSILON,Q,GAP,QMAX} from './engine.mjs';

test('browser observables agree with independent Python bundle',async()=>{
 const bundle=JSON.parse(await readFile(new URL('./data.json',import.meta.url),'utf8'));
 const run=simulate(bundle.reference_run.inputs);
 for(let i=0;i<run.records.length;i++)for(const key of ['error','bound','probability','occupancy','fidelity','energy','lambda_eff']){
  assert.ok(Math.abs(run.records[i][key]-bundle.reference_run.records[i][key])<1e-8,`${i}:${key}`);
 }
});
test('a single complement eigenmode has exact analytic decay',()=>{
 const w=[0,1,0,0,0,0,0],d=simulate({weights:w,steps:20}),c=simulate({weights:w,steps:20,mode:'continuous',horizon:2});
 for(const r of d.records)assert.ok(Math.abs(r.error-Math.abs(1-EPSILON*Q[1])**r.n)<1e-14);
 for(const r of c.records){assert.ok(Math.abs(r.error-Math.exp(-Q[1]*r.tau/GAP))<1e-14);assert.equal(r.fidelity,null);}
});
test('selected-only and underflow have explicit valid states',()=>{
 for(const r of simulate({weights:[0,0,1,0,0,0,0]}).records){assert.equal(r.error,0);assert.equal(r.fidelity,1);}
 const last=simulate({weights:[0,0,0,0,0,0,1],mode:'continuous',horizon:100}).records.at(-1);
 assert.equal(last.occupancy,null);assert.equal(last.fidelity,null);
});
test('occupancy derivative satisfies the continuous flow identity',()=>{
 const r=simulate({mode:'continuous',steps:1000,horizon:1});
 for(let i=1;i<999;i++){
  const estimate=(r.records[i+1].occupancy-r.records[i-1].occupancy)/.002;
  assert.ok(Math.abs(estimate-r.records[i].occupancy_derivative_tau)<1e-4);
 }
});
test('malformed imports and unsafe parameters fail before calculation',()=>{
 for(const weights of [[0,0,0,0,0,0,0],[1,2],[NaN,1,1,1,1,1,1],[-1,1,1,1,1,1,1],[Infinity,0,0,0,0,0,0]])assert.throws(()=>simulate({weights}));
 for(const steps of [0,1001,1.5,true,'220'])assert.throws(()=>simulate({steps}));
 for(const epsilon of [0,2/QMAX,Infinity,NaN])assert.throws(()=>simulate({epsilon}));
 assert.throws(()=>simulate({horizon:101}));assert.throws(()=>importRun('{"schema":"other"}'));
 assert.throws(()=>importRun(' '.repeat(2_000_001)));
 assert.throws(()=>seededWeights(-1));
});
test('receipt imports recompute tampered results and replay arbitrary valid steps',()=>{
 const run=simulate({epsilon:.7*EPSILON,weights:seededWeights(47)}),serialized=JSON.parse(JSON.stringify(run));serialized.records[0].error=999;
 assert.deepEqual(importRun(JSON.stringify(serialized)),run);
 assert.deepEqual(seededWeights(47),seededWeights(47));assert.notDeepEqual(seededWeights(47),seededWeights(48));
 assert.equal(runCSV(run).split('\n').length,223);
});
