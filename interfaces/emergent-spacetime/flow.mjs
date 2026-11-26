/** Emergent Spacetime -- the occupancy flow and the metric signature.
 *
 * Exact integer arithmetic throughout. The occupancy after n filter steps is
 * carried as a BigInt numerator/denominator pair, so the browser computes the
 * same integers that HalfOccupancy.lean and HalfOccupancy.v prove, rather than
 * a float that drifts near the critical point.
 *
 * Physical content, in one line:
 *     g00 = kappa^2 p (1-p) (1-2p) = p'' / 4
 * so the metric signature is the sign of the occupancy acceleration, and it
 * turns at p = 1/2 -- the inflection of the flow. Nothing is tuned.
 *
 * Scope: this is the induced coframe metric of the filter's fixed-point flow.
 * It is not a solution of the Einstein equations and makes no claim about one.
 */

/** rho* = 15/17 is the minimax contraction rate off the kernel; rho*^2 = 225/289. */
export const RHO_STAR = Object.freeze({ num: 15n, den: 17n });
export const R_NUM = 225n;
export const R_DEN = 289n;

/** Omega_c = 47/125, the coherence fraction, used as the default start. */
export const OMEGA_C = Object.freeze({ num: 47n, den: 125n });

/** The continuum envelope of the exact map: 2*kappa is the log-odds slope. */
export const KAPPA = Math.log(17 / 15);

/** Dimensions, for the contract check against the canonical kernel lock. */
export const CARRIER_DIMENSION = 125;
export const KERNEL_DIMENSION = 47;
export const EPS_STAR_DENOMINATOR = 99144n;
export const A_MIN = 11664n;
export const A_MAX = 186624n;

function bigint(value, name) {
  if (typeof value !== 'bigint') throw new Error(`${name} must be a BigInt.`);
  return value;
}

/**
 * One filter step on the kernel occupancy p = ||P psi||^2 / ||psi||^2.
 *
 *     p |-> p / (p + (1-p) * 225/289)
 *
 * clears denominators to (a,b) |-> (289a, 289a + 225(b-a)).
 *
 * This is the WORST CASE. Off the kernel the filter has five distinct factors
 * and only the two equioscillation sectors (C = 12 and C = 42) contract as
 * slowly as rho*, so every other state reaches half occupancy at this step or
 * sooner. Treat the result as an upper bound on the transition step.
 */
export function step({ num, den }) {
  bigint(num, 'num');
  bigint(den, 'den');
  if (num < 0n || den <= 0n || num > den) throw new Error('Occupancy must lie in [0,1].');
  const a = R_DEN * num;
  return { num: a, den: a + R_NUM * (den - num) };
}

/** Occupancy after n steps, exactly. */
export function occupancy(n, start = OMEGA_C) {
  if (!Number.isInteger(n) || n < 0 || n > 4096) throw new Error('Step count outside supported bounds.');
  let p = { num: start.num, den: start.den };
  for (let i = 0; i < n; i++) p = step(p);
  return p;
}

/** Exact rational to a double, without losing the small gap near 1/2. */
export function toNumber({ num, den }) {
  const SCALE = 10n ** 18n;
  return Number((num * SCALE) / den) / 1e18;
}

/** Compare an exact occupancy with 1/2. Returns -1, 0 or +1. */
export function compareHalf({ num, den }) {
  const twice = 2n * num;
  return twice < den ? -1 : twice === den ? 0 : 1;
}

/**
 * The induced coframe metric, diagonal in the derived coframe.
 * g = diag(g00, 2p, 2p, 2p) with g00 = kappa^2 p(1-p)(1-2p).
 * The three spatial legs are equal because all three sit in the same C = 6
 * sector: (1/5) tr_V2(J_a J_b) = 2 delta_ab, verified in certificate.py.
 */
export function metric(p, kappa = KAPPA) {
  if (!Number.isFinite(p) || p < 0 || p > 1) throw new Error('Occupancy must lie in [0,1].');
  return [kappa * kappa * p * (1 - p) * (1 - 2 * p), 2 * p, 2 * p, 2 * p];
}

/** Flow speed and acceleration of the logistic envelope. */
export function flowDerivatives(p, kappa = KAPPA) {
  const pdot = 2 * kappa * p * (1 - p);
  return { pdot, pddot: 2 * kappa * pdot * (1 - 2 * p) };
}

/** g00 is exactly a quarter of the occupancy acceleration. */
export function g00FromAcceleration(p, kappa = KAPPA) {
  return flowDerivatives(p, kappa).pddot / 4;
}

const EUCLIDEAN = Object.freeze({ pos: 4, neg: 0, zero: 0, label: 'Euclidean', code: '(4,0,0)' });
const LORENTZIAN = Object.freeze({ pos: 3, neg: 1, zero: 0, label: 'Lorentzian', code: '(3,1,0)' });
const CRITICAL = Object.freeze({ pos: 3, neg: 0, zero: 1, label: 'degenerate', code: '(3,0,1)' });
const NULL_LEAF = Object.freeze({ pos: 0, neg: 0, zero: 4, label: 'wholly degenerate', code: '(0,0,4)' });

/** Signature of the metric, counted from a diagonal with a tolerance. */
export function signature(p, tol = 1e-15) {
  const g = metric(p);
  const pos = g.filter((v) => v > tol).length;
  const neg = g.filter((v) => v < -tol).length;
  if (pos === 0 && neg === 0) return NULL_LEAF;
  if (pos === 4) return EUCLIDEAN;
  if (neg === 1) return LORENTZIAN;
  return CRITICAL;
}

/** Signature read off the exact rational, with no float anywhere near 1/2. */
export function exactSignature(p) {
  const c = compareHalf(p);
  if (p.num === 0n) return NULL_LEAF;
  if (c < 0) return EUCLIDEAN;
  if (c === 0) return CRITICAL;
  return p.num === p.den ? CRITICAL : LORENTZIAN;
}

/** The first step at which the envelope is Lorentzian. */
export function transitionStep(start = OMEGA_C, limit = 4096) {
  let p = { num: start.num, den: start.den };
  for (let n = 0; n <= limit; n++) {
    if (compareHalf(p) > 0) return n;
    p = step(p);
  }
  throw new Error('No transition within the supported step budget.');
}

/** The continuum crossing time, ln((1-p0)/p0) / 2kappa. Generally not an integer. */
export function crossingTime(start = OMEGA_C) {
  const p0 = toNumber(start);
  if (p0 <= 0 || p0 >= 1) throw new Error('Start must lie strictly inside (0,1).');
  return Math.log((1 - p0) / p0) / (2 * KAPPA);
}

/** The whole trajectory, exact and as doubles, with signature at each step. */
export function trajectory(steps = 8, start = OMEGA_C) {
  if (!Number.isInteger(steps) || steps < 0 || steps > 512) throw new Error('Steps outside supported bounds.');
  const rows = [];
  let p = { num: start.num, den: start.den };
  for (let n = 0; n <= steps; n++) {
    const value = toNumber(p);
    const sig = exactSignature(p);
    rows.push({
      step: n,
      exact: `${p.num}/${p.den}`,
      value,
      signature: sig,
      g00: metric(value)[0],
      pddotOverFour: g00FromAcceleration(value),
    });
    p = step(p);
  }
  return rows;
}

/**
 * Verify the derived constants against the canonical kernel contract, so the
 * page cannot render a number that disagrees with src/e47. Pass the object
 * returned by loadCanonicalE47(); throws on any mismatch.
 */
export function agreesWithCanonicalLock(lock) {
  const k = lock?.canonical;
  const expected = {
    carrier_dimension: CARRIER_DIMENSION,
    kernel_dimension: KERNEL_DIMENSION,
    coherence_fraction: `${OMEGA_C.num}/${OMEGA_C.den}`,
    epsilon_star: `1/${EPS_STAR_DENOMINATOR}`,
    rho_star: `${RHO_STAR.num}/${RHO_STAR.den}`,
    q_gap: Number(A_MIN),
    q_max: Number(A_MAX),
  };
  const mismatched = Object.entries(expected).filter(([key, value]) => k?.[key] !== value);
  if (mismatched.length) {
    throw new Error(`Derived constants disagree with the canonical lock: ${mismatched.map(([key]) => key).join(', ')}`);
  }
  if (JSON.stringify(k.casimir_roots) !== '[6,30]') throw new Error('Canonical selector roots are not [6,30].');
  return true;
}

/**
 * Training points for the Observatory neural lab. The classifier is shown only
 * indirect observables -- the flow speed and the centred occupancy -- and never
 * the number 1/2, so the boundary it settles on is recovered from samples
 * rather than supplied. Coordinates are in [-1,1] and labels in {0,1}, which is
 * what createTrainer() accepts.
 */
export function signatureDataset(count = 160, seed = 47) {
  if (!Number.isInteger(count) || count < 8 || count > 512) throw new Error('Dataset size outside supported bounds.');
  let s = seed >>> 0;
  const rand = () => {
    s = (s + 0x6d2b79f5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  const maxSpeed = 2 * KAPPA * 0.25;
  return Array.from({ length: count }, () => {
    const p = 0.02 + 0.96 * rand();
    return {
      x: 2 * p - 1,
      y: Math.max(-1, Math.min(1, (flowDerivatives(p).pdot / maxSpeed) * 2 - 1)),
      label: p > 0.5 ? 1 : 0,
    };
  });
}

/**
 * Recover the classifier's decision boundary in occupancy, by bisecting its
 * output along the occupancy axis. `predictAt` takes an occupancy and returns
 * a probability. Returns the occupancy where the probability crosses 1/2.
 */
export function recoverBoundary(predictAt, iterations = 48) {
  let lo = 0.0;
  let hi = 1.0;
  if ((predictAt(lo) - 0.5) * (predictAt(hi) - 0.5) > 0) return null;
  for (let i = 0; i < iterations; i++) {
    const mid = (lo + hi) / 2;
    if ((predictAt(lo) - 0.5) * (predictAt(mid) - 0.5) <= 0) hi = mid;
    else lo = mid;
  }
  return (lo + hi) / 2;
}
