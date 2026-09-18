#!/usr/bin/env node
import fs from 'node:fs'; import vm from 'node:vm'; import assert from 'node:assert/strict';
const source=fs.readFileSync(new URL('../website/interfaces/matrix/mps-worker.js',import.meta.url),'utf8');
function run(data){let result;const ctx={Float64Array,Math,Number,Array,console,postMessage:x=>{result=x}};vm.createContext(ctx);vm.runInContext(source,ctx);ctx.onmessage({data});return result}
for(const n of [2,3,4,5,6,7,8]){const chi=1<<Math.floor(n/2);const x=run({n,layers:4,phi:.7,chi,validate:true});assert.equal(x.engine,'two-site-mps');assert.equal(x.backend,'web-worker-js');assert.equal(x.validation.mode,'exact-equivalence');assert.ok(x.validation.relative_l2<1e-9,`n=${n} err=${x.validation.relative_l2}`);assert.ok(Math.abs(x.norm-1)<1e-9)}
const t=run({n:8,layers:8,phi:.7,chi:2,validate:true});assert.equal(t.validation.mode,'controlled-truncation');assert.ok(Number.isFinite(t.validation.relative_l2));assert.ok(t.discard>=0);
console.log(JSON.stringify({status:'PASS',exact_registers:'n=2..8',tolerance:1e-9,truncation_case:{n:8,chi:2,relative_l2:t.validation.relative_l2,discarded_weight:t.discard}},null,2));