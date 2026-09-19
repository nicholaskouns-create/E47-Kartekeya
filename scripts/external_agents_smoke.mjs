#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root=path.resolve(path.dirname(new URL(import.meta.url).pathname),'..');
const manifestPath=path.join(root,'city','external-agents','CITY-EXTERNAL-AGENTS-1.0.json');
const m=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const fail=(msg)=>{console.error('CITY EXTERNAL AGENTS FAIL:',msg);process.exitCode=1};

if(m.schema!=='CITY-EXTERNAL-AGENTS/1.0') fail('schema');
if(m.contract!=='CITY-EXTERNAL-AGENTS-1.0') fail('contract');
if(m.workers?.length!==5) fail('expected five external workers');
if(m.sovereignty?.citizen_runtime_instances_expected!==15) fail('citizen invariant');
if(m.sovereignty?.external_workers_are_citizens!==false) fail('external/citizen separation');
const codes=new Set(m.workers.map(w=>w.code));
if(codes.size!==5 || [...codes].some(c=>!c.startsWith('EXT-'))) fail('worker codes');
for(const w of m.workers){
  if(!w.schedule||!w.target||!w.mission) fail('incomplete worker '+w.code);
}
for(const p of [
  'website/interfaces/external-agents/index.html',
  '.github/workflows/city-external-agents.yml'
]){
  if(!fs.existsSync(path.join(root,p))) fail('missing '+p);
}
if(!process.exitCode) console.log('CITY EXTERNAL AGENTS PASS: 5 external workers / 15 sovereign citizens');
