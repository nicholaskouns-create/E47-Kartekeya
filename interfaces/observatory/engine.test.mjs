import test from 'node:test';
import assert from 'node:assert/strict';
import {spectralRun,makeDataset,createTrainer,trainEpoch,trainerMetrics,encodeReplay,decodeReplay,validateReplay,RHO} from './engine.mjs';
test('exact contraction bounds, retained weight and zero projection semantics',()=>{
 for(const a of [0,.01,.376,1]){const r=spectralRun({seed:47,selectedWeight:a,steps:220});assert.equal(r.rho,15/17);for(const row of r.records){assert.ok(row.error<=row.bound+1e-14);assert.ok(row.probability>=a-1e-14&&row.probability<=1+1e-14);assert.ok(Math.abs(row.weights[2]+row.weights[5]-a)<1e-14);}assert.ok(Math.abs(r.records.at(-1).probability-a)<1e-14);if(a===0)assert.equal(r.records[0].fidelity,null);}
 assert.ok(spectralRun({selectedWeight:.2}).records.at(-1).probability<spectralRun({selectedWeight:.8}).records.at(-1).probability);
});
test('phase preserves norms and seeding is reproducible',()=>{const a=spectralRun({seed:3,angle:0}),b=spectralRun({seed:3,angle:2});assert.deepEqual(a.records,b.records);assert.deepEqual(makeDataset('Spiral',47),makeDataset('Spiral',47));});
test('real neural backprop improves all four datasets',()=>{for(const kind of ['Circle','XOR','Spiral','Linear']){const t=createTrainer({dataset:makeDataset(kind),hidden:12,learningRate:.4});const before=trainerMetrics(t);for(let i=0;i<1800;i++)trainEpoch(t);const after=trainerMetrics(t);assert.ok(after.loss<before.loss*.8,`${kind}: ${before.loss} -> ${after.loss}`);assert.ok(after.mse<before.mse);assert.ok(after.accuracy>=.7,kind);}});
test('replay is bounded, canonical and recomputable',()=>{const state={schema:'E47-OBSERVATORY-REPLAY-1',spectral:{seed:47,selectedWeight:.4,steps:80,angle:1},neural:{dataset:'XOR',hidden:8,seed:47,learningRate:.22,epochs:40},view:'learn'};assert.deepEqual(decodeReplay(encodeReplay(state)),state);assert.deepEqual(spectralRun(decodeReplay(encodeReplay(state)).spectral),spectralRun(state.spectral));assert.throws(()=>validateReplay({...state,extra:'bad'}));assert.throws(()=>decodeReplay('x'.repeat(8193)));assert.throws(()=>validateReplay({...state,neural:{...state.neural,epochs:20001}}));});
test('reject nonfinite, out of range and malformed inputs',()=>{for(const selectedWeight of [NaN,Infinity,-1,2,'0.4'])assert.throws(()=>spectralRun({selectedWeight}));assert.throws(()=>spectralRun({seed:-1}));assert.throws(()=>spectralRun({steps:3.5}));assert.throws(()=>makeDataset('Unknown'));assert.throws(()=>createTrainer({dataset:Array(8).fill({x:0,y:0,label:2})}));assert.equal(RHO,15/17);});
test('analytic backprop matches independent central finite differences',()=>{
 const t=createTrainer({dataset:makeDataset('XOR',9,16),hidden:4,seed:9,learningRate:.1});
 const before=structuredClone(t),h=1e-5,parameters=[];
 for(let i=0;i<t.hidden;i++){parameters.push(['w',i,0],['w',i,1],['b',i],['v',i]);}parameters.push(['bias']);
 function get(o,path){return path.reduce((a,k)=>a[k],o);}function put(o,path,v){let target=o;for(const k of path.slice(0,-1))target=target[k];target[path.at(-1)]=v;}
 const numerical=parameters.map(path=>{const plus=structuredClone(before),minus=structuredClone(before),value=get(before,path);put(plus,path,value+h);put(minus,path,value-h);return (trainerMetrics(plus).loss-trainerMetrics(minus).loss)/(2*h);});
 trainEpoch(t);parameters.forEach((path,i)=>assert.ok(Math.abs((get(before,path)-get(t,path))/t.learningRate-numerical[i])<1e-8,JSON.stringify(path)));
});
test('optional exact-gate replay preserves four bounded angles and rejects malformed gates',()=>{
 const state={schema:'E47-OBSERVATORY-REPLAY-1',spectral:{seed:47,selectedWeight:.376,steps:80,angle:0},quantum:{angles:[.34,-.27,.21,.48]}};
 assert.deepEqual(decodeReplay(encodeReplay(state)),state);
 for(const angles of [[0,0,0],[0,0,0,0,0],[0,0,NaN,0],[0,0,Infinity,0],[0,0,0,2*Math.PI+.01],[0,0,'1',0]])assert.throws(()=>validateReplay({...state,quantum:{angles}}));
 assert.throws(()=>validateReplay({...state,quantum:{angles:[0,0,0,0],extra:true}}));
});
