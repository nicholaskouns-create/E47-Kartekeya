import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {emitInstrumentReceipt} from '../../../scripts/instrument-runtime.mjs';

const ROOT=fileURLToPath(new URL('../../../',import.meta.url));
const HERE=fileURLToPath(new URL('./',import.meta.url));
const CONTRACT=path.join(HERE,'component.json');
const read=p=>fs.readFileSync(path.join(HERE,p),'utf8');

async function run(benchmark){
 const runtime=read('rt3/runtime3.js'),drive=read('rt3/e47-drive.js'),bus=read('rt3/engine-bus.js');
 const aero=read('rt3/aero.js'),gear=read('rt3/gear.js'),geodesy=read('rt3/geodesy.js');
 const provenance=JSON.parse(read('provenance.json'));
 const t0=performance.now();
 const child=spawnSync(process.execPath,['--test',path.join(ROOT,'scripts/check_skyrmion_rt3.cjs')],{cwd:ROOT,encoding:'utf8'});
 const testMs=performance.now()-t0;
 const checks=[
  {name:'runtime_version',pass:runtime.includes('SKYRMION-RUNTIME-3.0'),observed:'SKYRMION-RUNTIME-3.0',expected:'SKYRMION-RUNTIME-3.0'},
  {name:'regression_suite',pass:child.status===0,observed:child.status,expected:0},
  {name:'model_separation',pass:runtime.includes('evidence===\'conventional\'')&&runtime.includes('E47Drive'),observed:true,expected:true},
  {name:'kernel_from_canonical_lock',pass:drive.includes("from '../../shared/e47-lock.js'")&&!/const\s+CASIMIR\s*=/.test(drive),observed:true,expected:'imported, never restated'},
  {name:'wgs84_geodesy',pass:geodesy.includes('Somigliana')&&geodesy.includes('transportRateNed'),observed:true,expected:true},
  {name:'compressible_aero',pass:aero.includes('waveDrag')&&aero.includes('compressibility')&&aero.includes('groundEffect'),observed:true,expected:true},
  {name:'ground_contact_present',pass:gear.includes('weightOnWheels')&&gear.includes('springNpm'),observed:true,expected:true},
  {name:'engine_bus_binds_city',pass:['worldEngine','worldBinding','e47Lock','stargate','cityGeo','instrument'].every(k=>bus.includes(k)),observed:6,expected:6},
  {name:'provenance_schema',pass:provenance.schema==='CITY-INVARIANT/1.0',observed:provenance.schema,expected:'CITY-INVARIANT/1.0'}
 ];
 return {checks,metrics:{
  regression_test_ms:Number(testMs.toFixed(3)),
  runtime_bytes:Buffer.byteLength(runtime),
  module_count:fs.readdirSync(path.join(HERE,'rt3')).filter(f=>f.endsWith('.js')).length,
  benchmark:benchmark?'regression-suite-timed':'regression-suite',
  child_stdout_tail:(child.stdout||'').trim().split('\n').slice(-4)
 }};
}
process.exitCode=await emitInstrumentReceipt({contractPath:CONTRACT,root:ROOT,benchmark:process.argv.includes('--benchmark'),phase:'skyrmion-rt3-runtime',run});
