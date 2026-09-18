#!/usr/bin/env node
import assert from'node:assert/strict';import{makeCity125,idx,xyz,applyPacket,applyPermutation,route,browserWitness}from'../website/js/city-125-runtime.js';
let c=makeCity125();assert.equal(c.length,125);for(let i=0;i<125;i++)assert.equal(idx(...xyz(i)),i);
applyPacket(c,{object:'test',operator:'identity',invariant:'address',witness:{ok:true},evidence:'E1',provenance:{test:true},next_action:'spectra',addresses:[0,62,124]});assert.equal(c.filter(x=>x.state).length,3);
let p=Array.from({length:125},(_,i)=>124-i),d=applyPermutation(c,p);assert.equal(d[124].source,'test');assert.equal(d[62].source,'test');assert.equal(d[0].source,'test');
assert.throws(()=>applyPacket(c,{object:'bad'}));let routes=[{id:'spectra',accepts:['structure']}];assert.equal(route({next_action:'structure'},routes).id,'spectra');
let w=browserWitness(c);assert.equal(w.carrier,125);assert.equal(w.base5,true);console.log(JSON.stringify({status:'PASS',addresses:125,bijection:'pi<->xyz',typed_packet:true,permutation:true,routing:true},null,2));