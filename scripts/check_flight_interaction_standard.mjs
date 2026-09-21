import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const read=p=>fs.readFileSync(new URL('../'+p,import.meta.url),'utf8');
const contract=JSON.parse(read('website/interfaces/shared/flight-interaction-contract.json'));

test('CITY-FLIGHT-INTERACTION 2.4 contract is pinned',async()=>{
  assert.equal(contract.schema,'CITY-FLIGHT-INTERACTION/2.4');
  const mod=await import('../website/interfaces/shared/flight-interaction-standard.js');
  assert.equal(mod.CITY_FLIGHT_INTERACTION.schema,contract.schema);
  assert.equal(mod.CITY_FLIGHT_INTERACTION.version,'2.4.0');
});

test('four native flight surfaces bind the common interaction grammar',()=>{
  const sky=read('website/interfaces/skyrmion/runtime2/bootstrap.js');
  const manta=read('website/interfaces/manta/manual-controls.js');
  const eidolon=read('website/interfaces/flight/eidolon/index.html');
  const syntax=read('website/interfaces/syntax-jacob/app.js');
  assert.match(sky,/installFlightInteractionStandard/);
  assert.match(sky,/cameraModes:\['CHASE','WING','ORBIT'\]/);
  assert.match(manta,/installFlightInteractionStandard/);
  assert.match(manta,/MantaABRuntime\.prototype\.step/);
  assert.match(eidolon,/skyrmion\/\?vehicle=eidolon/);
  assert.match(syntax,/installFlightInteractionStandard/);
  assert.match(syntax,/cameraModes:\['COMET','EARTH','SYSTEM','FREE'\]/);
});

test('physics boundaries remain distinct underneath the shared controls',()=>{
  const exp=read('website/interfaces/skyrmion/runtime2/experimental-model.js');
  const prop=read('website/interfaces/skyrmion/runtime2/propulsion-registry.js');
  const manta=read('website/interfaces/manta/manta-model.js');
  const syntax=read('website/interfaces/syntax-jacob/app.js');
  assert.match(exp,/eidolon_scalar/);
  assert.match(prop,/manta_morph/);
  assert.match(prop,/syntax_jacob/);
  assert.match(manta,/FIXED_STEP_HZ=120/);
  assert.match(syntax,/EPHEMERIS_ENDPOINT/);
});

test('rendering grammar includes vehicle-in-world HUD, reticle, touch stick and camera cycle',()=>{
  const shared=read('website/interfaces/shared/flight-interaction-standard.js');
  const terrain=read('website/interfaces/skyrmion/terrain-3d.js');
  assert.match(shared,/cfs-reticle/);
  assert.match(shared,/cfs-stick/);
  assert.match(shared,/k==='c'/);
  assert.match(shared,/\^\[1-7\]\$/);
  assert.match(terrain,/cameraMode==='WING'/);
  assert.match(terrain,/cameraMode==='ORBIT'/);
});
