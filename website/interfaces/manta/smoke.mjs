import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {resolve} from 'node:path';
const root=resolve(import.meta.dirname);const html=readFileSync(resolve(root,'index.html'),'utf8'),model=readFileSync(resolve(root,'manta-model.js'),'utf8'),contract=JSON.parse(readFileSync(resolve(root,'component.json'),'utf8'));
const checks=[
 ['contract',contract.id==='manta-flight-lab'&&contract.version==='1.0.0'],
 ['6dof',model.includes('SixDOFPhysics')&&model.includes('FIXED_STEP_HZ=120')],
 ['aero-coupling',model.includes('const CL=')&&model.includes('const CD=')&&model.includes('const Cm=')],
 ['mass-properties',model.includes('inertia=[')&&model.includes('c.mdot=-fuelFlow')],
 ['actuator-bounds',model.includes('MORPH_AXES')&&model.includes('boundHits')],
 ['energy',model.includes('this.energyJ += power*dt')],
 ['ab-mission',model.includes('this.stepCase(this.morphCase,cmd);this.stepCase(this.baseCase,cmd)')],
 ['ui',html.includes('RUN A/B')&&html.includes('EXPORT RECEIPT')]
];for(const [name,pass] of checks)assert.ok(pass,name);console.log(JSON.stringify({schema:'MANTA-SMOKE-1.0',result:'PASS',checks:checks.map(([name,pass])=>({name,pass}))},null,2));
