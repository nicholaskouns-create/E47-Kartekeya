import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const src=fs.readFileSync(path.join(HERE,'world-engine.js'),'utf8');
const bindingSrc=fs.readFileSync(path.join(HERE,'world-binding.js'),'utf8');
const mod=await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64'));
const a=mod.generateWorldCell({lat:36.1699,lon:-115.1398,span:12000,samples:33,seed:470125,timestamp:Date.UTC(2026,8,19,20)});
const b=mod.generateWorldCell({lat:36.1699,lon:-115.1398,span:12000,samples:33,seed:470125,timestamp:Date.UTC(2026,8,19,20)});
const same=a.terrain.heights.length===b.terrain.heights.length&&a.terrain.heights.every((v,i)=>v===b.terrain.heights[i]);
const finite=[a.terrain.min,a.terrain.max,a.terrain.centerElevation,a.weather.cloudCover,a.lighting.daylight].every(Number.isFinite);
const checks=[
 ['schema',a.schema==='CITY-WORLD-CELL-1.0'],
 ['deterministic',same],
 ['finite',finite],
 ['terrain_nonflat',a.terrain.max>a.terrain.min],
 ['biome',typeof a.biome.id==='string'&&a.biome.id.length>0],
 ['wgs84_state',mod.createWorldState({lat:36.1699,lon:-115.1398}).schema==='CITY-WORLD-STATE-1.0'],
 ['shared_binding',bindingSrc.includes('CITY-WORLD-BINDING-1.0')&&bindingSrc.includes('CITY:WORLD')&&bindingSrc.includes('BroadcastChannel')]
];
for(const [name,pass] of checks)console.log((pass?'PASS':'FAIL')+' '+name);
if(checks.some(([,p])=>!p))process.exitCode=1;
