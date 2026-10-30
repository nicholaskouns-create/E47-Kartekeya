import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {validateCarrier,evolveCarrier,SOURCE_SHA256} from './qgnn.mjs';
const data=JSON.parse(await readFile(new URL('./qgnn-data.json',import.meta.url),'utf8'));
test('browser exact eigengates match independent Python expectations and populations',()=>{for(const f of data.fixtures){const out=evolveCarrier(data,f.angles);assert.ok(Math.abs(out.expectation-f.expectation)<1e-10);assert.ok(Math.abs(out.norm-f.norm)<1e-10);assert.ok(out.error<1e-10);assert.ok(out.imaginaryResidual<1e-10);out.probabilities.forEach((p,i)=>assert.ok(Math.abs(p-f.probabilities[i])<1e-10));}});
test('unitary gate sweep preserves norm and bounded observable expectation',()=>{for(let n=0;n<20;n++){const out=evolveCarrier(data,Array.from({length:4},(_,i)=>Math.sin(n+i)*Math.PI*2));assert.ok(Math.abs(out.norm-1)<1e-10);assert.ok(Math.abs(out.expectation)<=1+1e-10);assert.ok(out.probabilities.every(x=>x>=0));}assert.equal(data.source.sha256,SOURCE_SHA256);});
test('reject malformed coefficients, attribution and unsupported gate controls',()=>{assert.throws(()=>evolveCarrier(data,[0,0,0]));assert.throws(()=>evolveCarrier(data,[0,0,NaN,0]));assert.throws(()=>evolveCarrier(data,[0,0,0,99]));const bad=structuredClone(data);bad.eigensystems[0].vectors[0][0][0]=Infinity;assert.throws(()=>validateCarrier(bad));assert.throws(()=>validateCarrier({...data,source:{sha256:'bad'}}));assert.throws(()=>validateCarrier({...data,input:data.input.slice(1)}));});
