/** Run with: node --test website/interfaces/emergent-spacetime/flow.test.mjs
 *
 * These tests check the browser module against the integers that
 * HalfOccupancy.lean and HalfOccupancy.v prove, so a drift in the JavaScript
 * cannot quietly disagree with the formal proofs.
 */
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  A_MAX, A_MIN, EPS_STAR_DENOMINATOR, KAPPA, OMEGA_C, RHO_STAR,
  agreesWithCanonicalLock, compareHalf, crossingTime, exactSignature,
  flowDerivatives, g00FromAcceleration, metric, occupancy, recoverBoundary,
  signature, signatureDataset, step, toNumber, trajectory, transitionStep,
} from './flow.mjs';

test('the flow starts at the coherence fraction 47/125', () => {
  assert.deepEqual(occupancy(0), { num: 47n, den: 125n });
  assert.equal(toNumber(OMEGA_C), 0.376);
});

test('the exact steps match the Lean and Coq theorems', () => {
  assert.deepEqual(occupancy(1), { num: 13583n, den: 31133n });
  assert.deepEqual(occupancy(2), { num: 3925487n, den: 7874237n });
  assert.deepEqual(occupancy(3), { num: 1134465743n, den: 2022934493n });
});

test('step 2 is still Euclidean and step 3 is Lorentzian', () => {
  assert.equal(compareHalf(occupancy(2)), -1);
  assert.equal(compareHalf(occupancy(3)), 1);
  assert.equal(exactSignature(occupancy(2)).code, '(4,0,0)');
  assert.equal(exactSignature(occupancy(3)).code, '(3,1,0)');
  assert.equal(transitionStep(), 3);
});

test('step 2 lands within 0.15 per cent of the critical point', () => {
  const { num, den } = occupancy(2);
  // 1/2 - p = (den - 2 num) / (2 den) = 23263/15748474
  assert.equal(den - 2n * num, 23263n);
  assert.equal(2n * den, 15748474n);
  assert.ok((den - 2n * num) * 10000n < 15n * (2n * den));
});

test('the log-odds is exactly geometric in the step number', () => {
  // u_n = u_0 * (289/225)^n, as integers with no rounding.
  for (let n = 0; n <= 6; n++) {
    const { num, den } = occupancy(n);
    assert.equal(num * 78n * 225n ** BigInt(n), (den - num) * 47n * 289n ** BigInt(n));
  }
});

test('the occupancy map is strictly increasing and stays in the unit interval', () => {
  let p = OMEGA_C;
  for (let n = 0; n < 40; n++) {
    const q = step(p);
    assert.ok(q.num * p.den > p.num * q.den, `not increasing at step ${n}`);
    assert.ok(q.num >= 0n && q.num <= q.den);
    p = q;
  }
});

test('kappa is the exact per-step log-odds slope', () => {
  assert.ok(Math.abs(2 * KAPPA - Math.log(289 / 225)) < 1e-15);
  assert.ok(Math.abs(KAPPA - Math.log(Number(RHO_STAR.den) / Number(RHO_STAR.num))) < 1e-15);
});

test('g00 is exactly a quarter of the occupancy acceleration', () => {
  for (const p of [0.05, 0.2, 0.37, 0.49, 0.5, 0.51, 0.8, 0.97]) {
    assert.ok(Math.abs(metric(p)[0] - g00FromAcceleration(p)) < 1e-18, `mismatch at p=${p}`);
  }
});

test('the signature turns exactly at half occupancy', () => {
  assert.equal(signature(0.25).code, '(4,0,0)');
  assert.equal(signature(0.5).code, '(3,0,1)');
  assert.equal(signature(0.75).code, '(3,1,0)');
  assert.equal(signature(1).code, '(3,0,1)');
  assert.equal(signature(0).code, '(0,0,4)');
});

test('the signature is constant on each side of half occupancy', () => {
  for (let i = 1; i < 500; i++) {
    const below = (0.5 * i) / 500;
    const above = 0.5 + (0.5 * i) / 500;
    assert.equal(signature(below).code, '(4,0,0)', `at p=${below}`);
    if (above < 1) assert.equal(signature(above).code, '(3,1,0)', `at p=${above}`);
  }
});

test('the spatial legs are isotropic and positive throughout', () => {
  for (const p of [0.1, 0.5, 0.9]) {
    const [, gx, gy, gz] = metric(p);
    assert.equal(gx, gy);
    assert.equal(gy, gz);
    assert.ok(gx > 0);
  }
});

test('the flow decelerates exactly past half occupancy', () => {
  assert.ok(flowDerivatives(0.3).pddot > 0);
  assert.ok(Math.abs(flowDerivatives(0.5).pddot) < 1e-18);
  assert.ok(flowDerivatives(0.7).pddot < 0);
});

test('the continuum crossing time from 47/125 sits between steps 2 and 3', () => {
  const t = crossingTime();
  assert.ok(t > 2 && t < 3, `n* = ${t}`);
  assert.ok(Math.abs(t - 2.023604) < 1e-5);
});

test('later starts cross sooner, and never later than the envelope', () => {
  assert.ok(transitionStep({ num: 1n, den: 100n }) > transitionStep(OMEGA_C));
  assert.equal(transitionStep({ num: 2n, den: 5n }), 2);
  // Starting exactly AT half occupancy the metric is degenerate (3,0,1), not
  // Lorentzian, so the first Lorentzian step is 1 and not 0.
  assert.equal(exactSignature({ num: 1n, den: 2n }).code, '(3,0,1)');
  assert.equal(transitionStep({ num: 1n, den: 2n }), 1);
});

test('the trajectory reports the exact rational beside the float', () => {
  const rows = trajectory(4);
  assert.equal(rows.length, 5);
  assert.equal(rows[2].exact, '3925487/7874237');
  assert.equal(rows[3].signature.label, 'Lorentzian');
  assert.ok(Math.abs(rows[2].g00 - rows[2].pddotOverFour) < 1e-18);
});

test('the canonical lock contract is enforced, not assumed', () => {
  const good = {
    canonical: {
      carrier_dimension: 125, kernel_dimension: 47, coherence_fraction: '47/125',
      epsilon_star: `1/${EPS_STAR_DENOMINATOR}`, rho_star: '15/17',
      q_gap: Number(A_MIN), q_max: Number(A_MAX), casimir_roots: [6, 30],
    },
  };
  assert.equal(agreesWithCanonicalLock(good), true);
  for (const [key, value] of [['rho_star', '14/17'], ['kernel_dimension', 46], ['q_max', 1]]) {
    const bad = { canonical: { ...good.canonical, [key]: value } };
    assert.throws(() => agreesWithCanonicalLock(bad), /disagree with the canonical lock/);
  }
  const roots = { canonical: { ...good.canonical, casimir_roots: [6, 29] } };
  assert.throws(() => agreesWithCanonicalLock(roots), /selector roots/);
});

test('A has condition number exactly 16 off the kernel', () => {
  assert.equal(A_MAX, 16n * A_MIN);
});

test('the minimax step is forced by equioscillation', () => {
  assert.equal(2n * EPS_STAR_DENOMINATOR, A_MIN + A_MAX);
  assert.equal((EPS_STAR_DENOMINATOR - A_MIN) * 17n, 15n * EPS_STAR_DENOMINATOR);
  assert.equal((EPS_STAR_DENOMINATOR - A_MAX) * 17n, -(15n * EPS_STAR_DENOMINATOR));
});

test('the dataset is valid trainer input and never leaks the constant', () => {
  const data = signatureDataset(128);
  assert.equal(data.length, 128);
  for (const d of data) {
    assert.ok(d.x >= -1 && d.x <= 1);
    assert.ok(d.y >= -1 && d.y <= 1);
    assert.ok(d.label === 0 || d.label === 1);
  }
  assert.ok(data.some((d) => d.label === 1) && data.some((d) => d.label === 0));
  const source = signatureDataset.toString();
  assert.doesNotMatch(source, /0\.5\b(?!\s*\?)/, 'the dataset builder must not hand the net the boundary');
});

test('boundary recovery finds a known crossing', () => {
  const found = recoverBoundary((p) => (p < 0.42 ? 0.1 : 0.9));
  assert.ok(Math.abs(found - 0.42) < 1e-6, `recovered ${found}`);
  assert.equal(recoverBoundary(() => 0.9), null);
});

test('inputs outside the unit interval are refused, not clamped', () => {
  assert.throws(() => metric(1.2));
  assert.throws(() => metric(-0.1));
  assert.throws(() => occupancy(-1));
  assert.throws(() => step({ num: 3n, den: 2n }));
  assert.throws(() => step({ num: 1, den: 2 }), /BigInt/);
  assert.throws(() => signatureDataset(4));
});
