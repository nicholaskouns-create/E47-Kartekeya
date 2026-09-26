import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {emitInstrumentReceipt} from '../../../scripts/instrument-runtime.mjs';

const ROOT=fileURLToPath(new URL('../../../',import.meta.url));
const HERE=fileURLToPath(new URL('./',import.meta.url));
const CONTRACT=path.join(HERE,'component.json');

async function run(benchmark){
  const index=fs.readFileSync(path.join(HERE,'index.html'),'utf8');
  const app=fs.readFileSync(path.join(HERE,'app.html'),'utf8');
  const bridge=fs.readFileSync(path.join(HERE,'aetheris-receipt-bridge.js'),'utf8');
  const matrix=fs.readFileSync(path.join(HERE,'matrix-cube-bridge.js'),'utf8');
  const loops=benchmark?1000:1;
  const t0=performance.now();
  let routeHits=0;
  for(let i=0;i<loops;i++) routeHits+=['skyrmion','eidolon','matrix'].filter(x=>(index+app).toLowerCase().includes(x)).length;
  const checks=[
    {name:'core_surface',pass:index.includes('CITY CORE')||index.includes('KOUNS CORE'),observed:true,expected:true},
    {name:'eidolon_local_route',pass:app.includes('../flight/eidolon/'),observed:app.includes('../flight/eidolon/'),expected:true},
    {name:'aetheris_receipt_bridge',pass:bridge.includes('aetheris')&&bridge.includes('receipt'),observed:true,expected:true},
    {name:'matrix_bridge',pass:matrix.length>100,observed:matrix.length,expected:'>100 bytes'}
  ];
  return {checks,metrics:{scan_iterations:loops,scan_ms:Number((performance.now()-t0).toFixed(3)),route_hits:routeHits,index_bytes:Buffer.byteLength(index)}};
}
process.exitCode=await emitInstrumentReceipt({contractPath:CONTRACT,root:ROOT,benchmark:process.argv.includes('--benchmark'),phase:'city-core',run});
