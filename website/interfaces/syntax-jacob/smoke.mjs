import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {emitInstrumentReceipt} from '../../../scripts/instrument-runtime.mjs';

const ROOT=fileURLToPath(new URL('../../../',import.meta.url));
const HERE=fileURLToPath(new URL('./',import.meta.url));
const CONTRACT=path.join(HERE,'component.json');

async function run(benchmark){
  const app=fs.readFileSync(path.join(HERE,'app.js'),'utf8');
  const html=fs.readFileSync(path.join(HERE,'index.html'),'utf8');
  const prov=JSON.parse(fs.readFileSync(path.join(HERE,'provenance.json'),'utf8'));
  const loops=benchmark?500:1;
  const t0=performance.now();
  let hits=0;
  for(let i=0;i<loops;i++) hits+=['syntax-jacob-ephemeris','matrix-cube-adapter','aetheris.receipt'].filter(x=>app.includes(x)).length;
  const scanMs=performance.now()-t0;
  const checks=[
    {name:'surface',pass:html.includes('Syntax Jacob'),observed:html.includes('Syntax Jacob'),expected:true},
    {name:'server_side_ephemeris',pass:app.includes('city-app-host/syntax-jacob-ephemeris'),observed:true,expected:true},
    {name:'no_direct_jpl_fetch',pass:!(/fetch\(['"]https:\/\/ssd(?:-api)?\.jpl\.nasa\.gov/.test(app)),observed:false,expected:false},
    {name:'provenance_version',pass:prov.schema==='SYNTAX-JACOB-PROVENANCE-1.1',observed:prov.schema,expected:'SYNTAX-JACOB-PROVENANCE-1.1'},
    {name:'physical_claim_boundary',pass:prov.runtime?.propulsion_lab?.physical_claim==='none',observed:prov.runtime?.propulsion_lab?.physical_claim,expected:'none'}
  ];
  return {checks,metrics:{scan_iterations:loops,scan_ms:Number(scanMs.toFixed(3)),token_hits:hits,app_bytes:Buffer.byteLength(app)}};
}

process.exitCode=await emitInstrumentReceipt({contractPath:CONTRACT,root:ROOT,benchmark:process.argv.includes('--benchmark'),phase:'syntax-jacob-runtime',run});
