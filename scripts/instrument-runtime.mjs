import fs from 'node:fs';
import crypto from 'node:crypto';
import os from 'node:os';
import {execFileSync} from 'node:child_process';

export const RECEIPT_SCHEMA='CITY-INSTRUMENT-RECEIPT/1.0';
export const FAILURE_SCHEMA='CITY-INSTRUMENT-FAILURE/1.0';

function gitCommit(root){
  if(process.env.GITHUB_SHA) return process.env.GITHUB_SHA;
  try{return execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();}
  catch{return null;}
}

export function loadContract(path){
  const raw=fs.readFileSync(path);
  return {
    contract:JSON.parse(raw.toString('utf8')),
    hash:crypto.createHash('sha256').update(raw).digest('hex')
  };
}

export async function emitInstrumentReceipt({contractPath,root,benchmark=false,phase='smoke',run}){
  const {contract,hash}=loadContract(contractPath);
  const start=performance.now();
  let checks=[],metrics={},failure=null,status='PASS';
  try{
    ({checks,metrics}=await run(benchmark));
    if(!checks.every(c=>Boolean(c.pass))) throw new Error('one or more instrument checks failed');
  }catch(error){
    status='FAIL';
    failure={
      schema:FAILURE_SCHEMA,
      component_id:contract.id,
      version:contract.version,
      phase,
      error_type:error?.name||'Error',
      message:String(error?.message||error),
      recoverable:false,
      context:{entrypoint:contract.smoke.entrypoint}
    };
  }
  const receipt={
    schema:RECEIPT_SCHEMA,
    component_id:contract.id,
    version:contract.version,
    mode:benchmark?'benchmark':'smoke',
    status,
    timestamp_utc:new Date().toISOString(),
    duration_ms:Number((performance.now()-start).toFixed(3)),
    git_commit:gitCommit(root),
    contract_sha256:hash,
    runtime:{language:'javascript',node:process.version,platform:process.platform,arch:process.arch,hostname:os.hostname()},
    checks,metrics,failure
  };
  process.stdout.write(JSON.stringify(receipt)+'\n');
  return status==='PASS'?0:1;
}
