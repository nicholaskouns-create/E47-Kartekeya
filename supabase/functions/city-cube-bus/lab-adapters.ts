/** Numerical companions to MC-OCTET-PACKET-1.0; neither is a packet stage. */
export class LabError extends Error {
  status: number;
  constructor(status: number, message: string) { super(message); this.status = status; }
}
type Matrix = number[][];
function matrix(value: unknown, rows?: number, columns?: number): Matrix {
  if (!Array.isArray(value) || !value.length || value.length > 256 ||
      (rows !== undefined && value.length !== rows)) throw new LabError(400, "invalid state row count");
  const width = columns ?? (Array.isArray(value[0]) ? value[0].length : 0);
  if (width < 1 || width > 16 || !value.every(row => Array.isArray(row) && row.length === width &&
      row.every(v => typeof v === "number" && Number.isFinite(v) && Math.abs(v) <= 1e6)))
    throw new LabError(400, "state must be a finite rectangular numeric array (absolute values <= 1e6)");
  return value.map(row => row.slice());
}
const norm2 = (a: Matrix) => a.reduce((s, row) => s + row.reduce((t, v) => t + v * v, 0), 0);
const sub = (a: Matrix, b: Matrix) => a.map((row, i) => row.map((v, j) => v - b[i][j]));
const combine = (a: Matrix, b: Matrix, scale: number) => a.map((row, i) => row.map((v, j) => v + scale * b[i][j]));

/** C on |m1,m2,m3>, m_i = 2,1,0,-1,-2; complex values are [real,imag]. */
export function casimir(state: Matrix): Matrix {
  const out = Array.from({length: 125}, () => [0, 0]);
  for (let i = 0; i < 125; i++) {
    const digits = [Math.floor(i / 25), Math.floor(i / 5) % 5, i % 5];
    const m = digits.map(d => 2 - d), strides = [25, 5, 1];
    const diagonal = 18 + 2 * (m[0]*m[1] + m[0]*m[2] + m[1]*m[2]);
    for (let c = 0; c < 2; c++) out[i][c] += diagonal * state[i][c];
    for (let a = 0; a < 3; a++) for (let b = a + 1; b < 3; b++) {
      for (const sign of [-1, 1]) {
        if (Math.abs(m[a] + sign) > 2 || Math.abs(m[b] - sign) > 2) continue;
        const target = i - sign * strides[a] + sign * strides[b];
        const coefficient = Math.sqrt((6 - m[a]*(m[a]+sign)) * (6 - m[b]*(m[b]-sign)));
        for (let c = 0; c < 2; c++) out[target][c] += coefficient * state[i][c];
      }
    }
  }
  return out;
}
function kernel(state: Matrix): Matrix {
  const c = casimir(state), cc = casimir(c);
  return state.map((row, i) => row.map((v, j) => cc[i][j] - 36*c[i][j] + 180*v));
}
function project(state: Matrix): Matrix {
  const spectrum = [0, 2, 6, 12, 20, 30, 42];
  const parts = [6, 30].map(root => {
    let p = state.map(row => row.slice());
    for (const eigenvalue of spectrum.filter(v => v !== root)) {
      const cp = casimir(p);
      p = p.map((row, i) => row.map((v, j) => (cp[i][j] - eigenvalue*v)/(root-eigenvalue)));
    }
    return p;
  });
  return combine(parts[0], parts[1], 1);
}
export function runLab(module: string, input: any, steps: number) {
  if (!Number.isInteger(steps) || steps < 1 || steps > 200) throw new LabError(400, "steps must be an integer from 1 to 200");
  if (module === "BUILD") {
    let positions = matrix(input?.positions);
    const alpha = input?.alpha;
    if (typeof alpha !== "number" || !Number.isFinite(alpha) || alpha <= 0 || alpha >= 2)
      throw new LabError(400, "BUILD alpha must be strictly between 0 and 2");
    const centroid = positions[0].map((_, j) => positions.reduce((s, row) => s + row[j], 0)/positions.length);
    const dispersion = (p: Matrix) => norm2(p.map(row => row.map((v, j) => v-centroid[j])));
    const initial = dispersion(positions), telemetry = [{step: 0, dispersion: initial, predicted_dispersion: initial}];
    for (let step = 1; step <= steps; step++) {
      positions = positions.map(row => row.map((v, j) => centroid[j] + (1-alpha)*(v-centroid[j])));
      telemetry.push({step, dispersion: dispersion(positions), predicted_dispersion: initial*(1-alpha)**(2*step)});
    }
    return {module, model: "centroid-affine-v1", state: {positions, alpha}, centroid, telemetry};
  }
  if (module === "SOAR") {
    let amplitudes = matrix(input?.amplitudes, 125, 2);
    if (input?.basis !== "spin2-tensor3-descending-m") throw new LabError(400, "SOAR requires basis spin2-tensor3-descending-m");
    const p = project(amplitudes), initialLeakage = Math.sqrt(norm2(sub(amplitudes, p)));
    const measure = (step: number) => {
      const k = kernel(amplitudes), n2 = norm2(amplitudes), complementWeight = norm2(sub(amplitudes, project(amplitudes)));
      return {step, norm: Math.sqrt(n2), leakage: Math.sqrt(complementWeight),
        leakage_bound: initialLeakage*(15/17)**step, complement_weight: complementWeight,
        normalized_e47_weight: n2 === 0 ? null : norm2(project(amplitudes))/n2, k2_energy: norm2(k)};
    };
    const telemetry = [measure(0)];
    for (let step = 1; step <= steps; step++) {
      amplitudes = combine(amplitudes, kernel(kernel(amplitudes)), -1/99144);
      telemetry.push(measure(step));
    }
    return {module, model: "e47-k2-restoration-v1", state: {amplitudes, basis: input.basis},
      epsilon: 1/99144, complement_rate: 15/17, telemetry};
  }
  throw new LabError(400, "lab module must be BUILD or SOAR");
}

function canonical(value: any): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value !== null && typeof value === "object") return `{${Object.keys(value).sort().map(k => `${JSON.stringify(k)}:${canonical(value[k])}`).join(",")}}`;
  return JSON.stringify(value);
}
export async function digest(value: unknown) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical(value)));
  return Array.from(new Uint8Array(bytes), v => v.toString(16).padStart(2, "0")).join("");
}
/** Called inside the existing owner-checked, row-locked bus transaction. */
export async function prepareLabRun(body: any, binding: any) {
  if (body.expected_bus_head !== binding.bus_head_hash) throw new LabError(409, "expected_bus_head is required and must match; reload experiment before retrying");
  const module = body.module;
  if (module !== "BUILD" && module !== "SOAR") throw new LabError(400, "lab module must be BUILD or SOAR");
  if (body.mode !== "start" && body.mode !== "resume") throw new LabError(400, "mode must be start or resume");
  const previous = binding.metadata?.lab_states?.[module];
  if (body.mode === "resume" && !previous) throw new LabError(409, "no saved state for this lab");
  if (body.mode === "resume" && body.input !== undefined) throw new LabError(400, "resume uses saved state; omit input");
  const input = body.mode === "resume" ? previous.state : body.input;
  const result = runLab(module, input, body.steps ?? 1);
  const startStep = body.mode === "resume" ? previous.total_steps : 0;
  const output_hash = await digest(result.state);
  const checkpoint = {adapter_version: 1, model: result.model, state: result.state,
    total_steps: startStep + (body.steps ?? 1), output_hash};
  const details = {adapter_version: 1, mode: body.mode, source_ref: String(body.source_ref ?? "").slice(0,2048),
    evidence_class: "numerical-demonstration", start_step: startStep, end_step: checkpoint.total_steps,
    input, input_hash: await digest(input), output_hash, result,
    boundary: "Companion run preserves packet stage, packet hash, evidence class, and Cube state."};
  return {module, checkpoint, details};
}
