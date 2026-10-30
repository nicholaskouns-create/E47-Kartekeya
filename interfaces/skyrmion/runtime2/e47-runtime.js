import {CASIMIR, MULT, ROOTS, N, EPS, OMEGA_C} from "../../shared/e47-lock.js";

const spectrum = [];
for (let j = 0; j < CASIMIR.length; j++) {
  for (let i = 0; i < MULT[j]; i++) spectrum.push(CASIMIR[j]);
}
const k2 = spectrum.map((c) => {
  let k = 1;
  for (const root of ROOTS) k *= (c - root);
  return k * k;
});

export class E47Runtime {
  constructor() {
    this.schema = "E47-RUNTIME-BROWSER-2.0";
    this.lock = "E47-LOCK-FROM-SRC-E47";
    this.state = new Float64Array(N);
    this.seed(47);
    this.iterations = 0;
  }
  seed(seed = 47) {
    let n = 0;
    for (let i = 0; i < N; i++) {
      const v = Math.sin((i + 1) * (seed + 1) * 0.731) + 0.31 * Math.cos((i + 3) * (seed + 7) * 0.173);
      this.state[i] = v;
      n += v * v;
    }
    n = Math.sqrt(n) || 1;
    for (let i = 0; i < N; i++) this.state[i] /= n;
    this.iterations = 0;
    return this.snapshot();
  }
  inject(signal) {
    const s = signal || {};
    for (let i = 0; i < N; i++) {
      const drive = 1e-4 * (Math.sin((i + 1) * (s.alpha || 0)) + Math.cos((i + 3) * (s.mach || 0)) + (s.controlNorm || 0));
      this.state[i] += drive;
    }
  }
  step(signal) {
    this.inject(signal);
    let n = 0;
    for (let i = 0; i < N; i++) {
      this.state[i] *= (1 - EPS * k2[i]);
      n += this.state[i] * this.state[i];
    }
    n = Math.sqrt(n) || 1;
    for (let i = 0; i < N; i++) this.state[i] /= n;
    this.iterations++;
    return this.snapshot();
  }
  snapshot() {
    let total = 0, cap = 0, res = 0;
    for (let i = 0; i < N; i++) {
      const p = this.state[i] * this.state[i];
      total += p;
      if (ROOTS.includes(spectrum[i])) cap += p;
      res += k2[i] * p;
    }
    return {
      schema: this.schema,
      lock: this.lock,
      epsilon: EPS,
      omegaC: OMEGA_C,
      capture: cap / (total || 1),
      residual: Math.sqrt(res / (total || 1)),
      iterations: this.iterations
    };
  }
}
