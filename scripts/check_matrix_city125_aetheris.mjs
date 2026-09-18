#!/usr/bin/env node
import assert from'node:assert/strict';import{instantiateMatrixCityAdapter}from'../website/js/matrix-city125-aetheris.js';
let receipts=0;const a=instantiateMatrixCityAdapter({emitReceipt:async p=>({id:'r'+(++receipts),evidence:p.evidence})});
const v=Array.from({length:125},(_,i)=>i===0?[1,0]:[0,0]);
const x=await a.ingest({statevector:v,circuit:{lift:{name:'test-explicit-125'}},e47Witness:{e47_weight:.2,projected_weights:Array.from({length:125},(_,i)=>i<47?1:0)}});
assert.equal(x.cells.length,125);assert.equal(x.city.receipts,125);assert.equal(x.city.e47_cells,47);assert.equal(x.packet.invariant.representation_separation,true);assert.equal(x.packet.invariant.human_promotion_gate,true);assert.equal(x.packet.next_action,'aetheris');assert.equal(receipts,1);
await assert.rejects(()=>a.ingest({statevector:[[1,0]],circuit:{}}));
console.log(JSON.stringify({status:'PASS',contract:'MATRIX-CITY125-E47-AETHERIS-1.0',addresses:125,e47_marked:47,receipt:'PASS',promotion_gate:'retained'},null,2));