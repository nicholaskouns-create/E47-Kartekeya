import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {emitInstrumentReceipt} from '../../../scripts/instrument-runtime.mjs';

const here=resolve(import.meta.dirname);
const root=resolve(here,'../../..');
const contractPath=resolve(here,'component.json');

async function run(){
  const html=readFileSync(resolve(here,'index.html'),'utf8');
  const model=readFileSync(resolve(here,'manta-model.js'),'utf8');
  const contract=JSON.parse(readFileSync(contractPath,'utf8'));
  const checks=[
    ['contract',contract.id==='manta-flight-lab'&&contract.version==='1.1.0'],
    ['6dof',model.includes('SixDOFPhysics')&&model.includes('FIXED_STEP_HZ=120')],
    ['aero-coupling',model.includes('const CL=')&&model.includes('const CD=')&&model.includes('const Cm=')],
    ['mass-properties',model.includes('inertia=[')&&model.includes('c.mdot=-fuelFlow')],
    ['actuator-bounds',model.includes('MORPH_AXES')&&model.includes('boundHits')],
    ['energy',model.includes('this.energyJ += power*dt')],
    ['ab-mission',model.includes('this.stepCase(this.morphCase,cmd);this.stepCase(this.baseCase,cmd)')],
    ['ui',html.includes('id="run"')&&html.includes('>FLY</button>')&&html.includes('id="baseline"')&&html.includes('id="data"')]
  ].map(([name,pass])=>({name,pass}));
  return {checks,metrics:{inspection:'source-contract',model_bytes:Buffer.byteLength(model)}};
}

process.exitCode=await emitInstrumentReceipt({
  contractPath,root,benchmark:process.argv.includes('--benchmark'),phase:'manta-source-contract',run
});
