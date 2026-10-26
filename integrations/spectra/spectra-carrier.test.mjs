import test from "node:test";import assert from "node:assert/strict";
import {carrierIndex,carrierCoordinates,carrierQasm,parseSpectraQasm,decodeSpectraCounts} from "./spectra-carrier.mjs";
test("exact 125-state base-5 bijection",()=>{const s=new Set();for(let x=0;x<5;x++)for(let y=0;y<5;y++)for(let z=0;z<5;z++){const i=carrierIndex(x,y,z);s.add(i);assert.deepEqual(carrierCoordinates(i),[x,y,z]);}assert.equal(s.size,125);assert.equal(carrierIndex(2,1,3),58)});
test("QASM preparation and parse",()=>{const g=parseSpectraQasm(carrierQasm(58));assert.deepEqual(g.filter(v=>v.gate==="X").map(v=>v.targets[0]),[1,3,4,5]);assert.equal(g.filter(v=>v.gate==="MEASURE").length,7)});
test("unused register states are explicit leakage",()=>{assert.equal(decodeSpectraCounts({"1111101":2,"1111111":3}).leakageShots,5);assert.equal(decodeSpectraCounts({"0111010":7}).leakageShots,0)});
test("invalid and unknown statements rejected",()=>{assert.throws(()=>carrierIndex(1.2,0,0));assert.throws(()=>parseSpectraQasm(carrierQasm(0)+"\nswap q[0],q[1];"))});
