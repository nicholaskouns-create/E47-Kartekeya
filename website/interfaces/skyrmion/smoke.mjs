import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {emitInstrumentReceipt} from '../../../scripts/instrument-runtime.mjs';

const ROOT=fileURLToPath(new URL('../../../',import.meta.url));
const HERE=fileURLToPath(new URL('./',import.meta.url));
const CONTRACT=path.join(HERE,'component.json');

async function run(benchmark){
  const runtime=fs.readFileSync(path.join(HERE,'runtime2/runtime2.js'),'utf8');
  const provenance=JSON.parse(fs.readFileSync(path.join(HERE,'provenance.json'),'utf8'));
  const baseline=JSON.parse(fs.readFileSync(path.join(HERE,'runtime2-smoke-20260919.json'),'utf8'));
  const t0=performance.now();
  const child=spawnSync(process.execPath,['--test',path.join(ROOT,'scripts/check_skyrmion_runtime.cjs')],{cwd:ROOT,encoding:'utf8'});
  const testMs=performance.now()-t0;
  const checks=[
    {name:'runtime_version',pass:runtime.includes('SKYRMION-RUNTIME-2.2'),observed:'SKYRMION-RUNTIME-2.2',expected:'SKYRMION-RUNTIME-2.2'},
    {name:'model_separation',pass:runtime.includes('ConventionalFlightModel')&&runtime.includes('ExperimentalFlightModel'),observed:true,expected:true},
    {name:'runtime_regression_suite',pass:child.status===0,observed:child.status,expected:0},
    {name:'provenance_schema',pass:typeof provenance.schema==='string',observed:provenance.schema,expected:'declared provenance schema'},
    {name:'baseline_smoke_present',pass:baseline!==null&&typeof baseline==='object',observed:true,expected:true}
  ];
  return {checks,metrics:{
    regression_test_ms:Number(testMs.toFixed(3)),
    runtime_bytes:Buffer.byteLength(runtime),
    benchmark:benchmark?'regression-suite-timed':'regression-suite',
    child_stdout_tail:(child.stdout||'').trim().split('\n').slice(-4)
  }};
}

process.exitCode=await emitInstrumentReceipt({contractPath:CONTRACT,root:ROOT,benchmark:process.argv.includes('--benchmark'),phase:'skyrmion-runtime',run});
