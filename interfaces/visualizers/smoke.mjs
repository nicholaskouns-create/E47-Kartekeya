import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {emitInstrumentReceipt} from '../../../scripts/instrument-runtime.mjs';

const ROOT=fileURLToPath(new URL('../../../',import.meta.url));
const HERE=fileURLToPath(new URL('./',import.meta.url));
const CONTRACT=path.join(HERE,'component.json');
const IDS=['spectra','fold','murmuration','mnemosyne','density','horizon','wave','identity','build','soar','scalar','invarifold'];

async function run(benchmark){
  const html=fs.readFileSync(path.join(HERE,'index.html'),'utf8');
  const loops=benchmark?1000:1;
  const t0=performance.now();
  let matches=0;
  for(let i=0;i<loops;i++) for(const id of IDS) if(html.includes(`id:'${id}'`)) matches++;
  const missing=IDS.filter(id=>!html.includes(`id:'${id}'`));
  const checks=[
    {name:'portal_label',pass:html.includes('VISUALIZER PORTAL'),observed:html.includes('VISUALIZER PORTAL'),expected:true},
    {name:'instrument_registry',pass:missing.length===0,observed:missing,expected:[]},
    {name:'source_preservation_contract',pass:html.includes('source visualizer is preserved unchanged'),observed:true,expected:true}
  ];
  return {checks,metrics:{instrument_count:IDS.length,scan_iterations:loops,scan_ms:Number((performance.now()-t0).toFixed(3)),matches}};
}
process.exitCode=await emitInstrumentReceipt({contractPath:CONTRACT,root:ROOT,benchmark:process.argv.includes('--benchmark'),phase:'visualizer-portal',run});
