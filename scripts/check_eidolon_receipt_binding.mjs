import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import {
  normalizeFlightReceipt,
  deriveFlightControl,
  EIDOLON_FLIGHT_RECEIPT_CONTRACT
} from '../website/interfaces/flight/aetheris-flight-binding.js';

test('normalizes the deployed eidolon-city-adapter receipt envelope', () => {
  const x = normalizeFlightReceipt({
    actor_code:'SOL',
    receipt:{id:'r-1',receipt_code:'AETHERIS-EIDOLON-SOL-1',status:'completed',created_at:'2026-09-18T00:00:00Z'},
    state_before_digest:'before',
    state_after_digest:'after',
    state:{step:7,last_interaction:{yaw:.5,pitch:-.25,roll:.2,throttle:.9,vertical:.1}}
  });
  assert.equal(x.schema,EIDOLON_FLIGHT_RECEIPT_CONTRACT.schema);
  assert.equal(x.receipt_code,'AETHERIS-EIDOLON-SOL-1');
  assert.equal(x.status,'completed');
  assert.equal(x.step,7);
  assert.equal(x.state_before_digest,'before');
  assert.equal(x.state_after_digest,'after');
  assert.equal(x.state_transition.step,7);
});

test('derives bounded flight controls from returned state', () => {
  const c = deriveFlightControl({last_interaction:{yaw:3,pitch:-2,roll:.2,throttle:1.5,vertical:-.4,speed:12}});
  assert.deepEqual(c,{yaw:1,pitch:-1,roll:.2,vertical:-.4,throttle:1,speed:12});
});

test('public EIDOLON routes through the receipt-bound flight shell', () => {
  const root=resolve(import.meta.dirname,'..');
  const app=readFileSync(resolve(root,'website/js/app.js'),'utf8');
  const core=readFileSync(resolve(root,'website/interfaces/kouns-core/app.html'),'utf8');
  const shell=readFileSync(resolve(root,'website/interfaces/flight/flight-shell.js'),'utf8');
  const eidolon=readFileSync(resolve(root,'website/interfaces/flight/eidolon/index.html'),'utf8');
  assert.match(app,/interfaces\/flight\/eidolon\//);
  assert.match(core,/\.\.\/flight\/eidolon\//);
  assert.match(shell,/createEidolonFlightReceiptBinding/);
  assert.match(shell,/receiptFlightBinding\?\.sample/);
  assert.match(shell,/EIDOLON:AETHERIS_STATE_TRANSITION|aetheris-flight-binding/);
  assert.match(eidolon,/eidolon-flight-lab\.nicholaskouns\.chatgpt\.site/);
});
