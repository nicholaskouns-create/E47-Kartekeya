export const PACKET_SCHEMA_VERSION = "MC-OCTET-PACKET-1.0";
export const STAGE_ORDER = [
  "spectra",
  "fold",
  "density",
  "murmuration",
  "horizon",
  "mnemosyne",
  "wave",
  "identity",
  "spectra_reveal",
  "score",
] as const;

export type StageName = typeof STAGE_ORDER[number];
export type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };

export function canonicalize(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map(canonicalize).join(",")}]`;
  const obj = value as Record<string, unknown>;
  return `{${Object.keys(obj).sort().map(k => `${JSON.stringify(k)}:${canonicalize(obj[k])}`).join(",")}}`;
}

export async function sha256Hex(text: string): Promise<string> {
  const data = new TextEncoder().encode(text);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("");
}

function withoutPacketHash(packet: any): any {
  const clone = structuredClone(packet);
  if (!clone.integrity) clone.integrity = {};
  clone.integrity.packet_hash = null;
  return clone;
}

async function computePacketHash(packet: any): Promise<string> {
  return sha256Hex(canonicalize(withoutPacketHash(packet)));
}

export function nextStageFor(stages: any[]): StageName | null {
  const n = Array.isArray(stages) ? stages.length : 0;
  return n < STAGE_ORDER.length ? STAGE_ORDER[n] : null;
}

export async function createPacket(input: {
  experiment_id: string;
  input?: JsonValue;
  declaration?: Record<string, JsonValue>;
  evidence_class?: string;
  created_at?: string;
}) {
  if (!input?.experiment_id || typeof input.experiment_id !== "string") {
    throw new Error("experiment_id is required");
  }
  const createdAt = input.created_at ?? new Date().toISOString();
  const payload = input.input ?? {};
  const declaration = input.declaration ?? {};
  const packet: any = {
    schema_version: PACKET_SCHEMA_VERSION,
    experiment_id: input.experiment_id,
    created_at: createdAt,
    evidence_class: input.evidence_class ?? "workflow",
    declaration,
    declaration_hash: await sha256Hex(canonicalize(declaration)),
    input: payload,
    input_hash: await sha256Hex(canonicalize(payload)),
    stages: [],
    next_stage: STAGE_ORDER[0],
    status: "open",
    integrity: {
      parent_packet_hash: null,
      packet_hash: null,
    },
    boundary: "Typed transport/provenance packet. It does not promote evidence class by itself.",
  };
  packet.integrity.packet_hash = await computePacketHash(packet);
  return packet;
}

export async function verifyPacket(packet: any) {
  const errors: string[] = [];
  if (!packet || typeof packet !== "object") return { valid: false, errors: ["packet must be an object"] };
  if (packet.schema_version !== PACKET_SCHEMA_VERSION) errors.push("schema_version mismatch");
  if (!Array.isArray(packet.stages)) errors.push("stages must be an array");
  const stages = Array.isArray(packet.stages) ? packet.stages : [];
  if (stages.length > STAGE_ORDER.length) errors.push("too many stages");

  let prevStageHash: string | null = null;
  let expectedInputHash = packet.input_hash;
  for (let i = 0; i < stages.length; i++) {
    const s = stages[i];
    if (s.stage !== STAGE_ORDER[i]) errors.push(`stage order mismatch at ${i}: expected ${STAGE_ORDER[i]}`);
    if (s.ordinal !== i + 1) errors.push(`stage ordinal mismatch at ${i}`);
    if (s.prev_stage_hash !== prevStageHash) errors.push(`prev_stage_hash mismatch at ${s.stage}`);
    if (s.input_hash !== expectedInputHash) errors.push(`input_hash mismatch at ${s.stage}`);
    const outputHash = await sha256Hex(canonicalize(s.payload ?? {}));
    if (s.output_hash !== outputHash) errors.push(`output_hash mismatch at ${s.stage}`);
    const core = { ...s, stage_hash: null };
    const recomputedStageHash = await sha256Hex(`${prevStageHash ?? "GENESIS"}|${canonicalize(core)}`);
    if (s.stage_hash !== recomputedStageHash) errors.push(`stage_hash mismatch at ${s.stage}`);
    if (s.stage === "mnemosyne") {
      const horizon = stages.find((x: any) => x.stage === "horizon");
      if (!horizon) errors.push("mnemosyne stage exists without horizon stage");
      else if (s.payload?.forecast_sha256 !== horizon.output_hash) errors.push("mnemosyne forecast seal does not bind horizon output");
    }
    prevStageHash = s.stage_hash;
    expectedInputHash = s.output_hash;
  }

  const expectedNext = nextStageFor(stages);
  if ((packet.next_stage ?? null) !== expectedNext) errors.push("next_stage mismatch");
  const expectedStatus = expectedNext === null ? "complete" : "open";
  if (packet.status !== expectedStatus) errors.push("status mismatch");
  const packetHash = await computePacketHash(packet);
  if (packet.integrity?.packet_hash !== packetHash) errors.push("packet_hash mismatch");

  return {
    valid: errors.length === 0,
    errors,
    next_stage: expectedNext,
    packet_hash: packetHash,
    stage_count: stages.length,
  };
}

export async function advancePacket(packet: any, input: {
  stage: StageName;
  payload?: JsonValue;
  diagnostics?: JsonValue;
  source_ref?: string | null;
  evidence_class?: string;
  stage_version?: string;
  completed_at?: string;
}) {
  const verified = await verifyPacket(packet);
  if (!verified.valid) throw new Error(`incoming packet failed verification: ${verified.errors.join("; ")}`);
  const expected = verified.next_stage;
  if (input.stage !== expected) throw new Error(`stage transition rejected: expected ${expected}, received ${input.stage}`);

  const stages = structuredClone(packet.stages);
  const prior = stages.at(-1) ?? null;
  const stagePayload: any = structuredClone(input.payload ?? {});

  if (input.stage === "mnemosyne") {
    const horizon = stages.find((s: any) => s.stage === "horizon");
    if (!horizon) throw new Error("mnemosyne requires a completed horizon stage");
    stagePayload.forecast_sha256 = horizon.output_hash;
    stagePayload.sealed_at = input.completed_at ?? new Date().toISOString();
    stagePayload.seal_scope = "horizon_output";
  }

  const outputHash = await sha256Hex(canonicalize(stagePayload));
  const stageRecord: any = {
    stage: input.stage,
    ordinal: stages.length + 1,
    stage_version: input.stage_version ?? "1.0",
    completed_at: input.completed_at ?? new Date().toISOString(),
    evidence_class: input.evidence_class ?? packet.evidence_class ?? "workflow",
    source_ref: input.source_ref ?? null,
    input_hash: prior?.output_hash ?? packet.input_hash,
    output_hash: outputHash,
    prev_stage_hash: prior?.stage_hash ?? null,
    payload: stagePayload,
    diagnostics: input.diagnostics ?? {},
    stage_hash: null,
  };
  stageRecord.stage_hash = await sha256Hex(`${stageRecord.prev_stage_hash ?? "GENESIS"}|${canonicalize(stageRecord)}`);
  stages.push(stageRecord);

  const next = nextStageFor(stages);
  const nextPacket: any = {
    ...structuredClone(packet),
    stages,
    next_stage: next,
    status: next === null ? "complete" : "open",
    integrity: {
      parent_packet_hash: packet.integrity.packet_hash,
      packet_hash: null,
    },
  };
  nextPacket.integrity.packet_hash = await computePacketHash(nextPacket);
  return nextPacket;
}

function getPath(obj: any, path: string) {
  return path.split(".").filter(Boolean).reduce((acc, key) => acc?.[key], obj);
}

function vectorize(v: any): number[] {
  if (!Array.isArray(v) || v.some(x => typeof x !== "number" || !Number.isFinite(x))) {
    throw new Error("metric requires a finite numeric array");
  }
  return v;
}

function scoreOne(pred: any, obs: any, metric: string): number | boolean {
  if (metric === "exact_match") return canonicalize(pred) === canonicalize(obs);
  if (metric === "absolute_error") {
    if (typeof pred !== "number" || typeof obs !== "number") throw new Error("absolute_error requires numeric values");
    return Math.abs(pred - obs);
  }
  if (metric === "relative_error") {
    if (typeof pred !== "number" || typeof obs !== "number") throw new Error("relative_error requires numeric values");
    return Math.abs(pred - obs) / Math.max(Math.abs(obs), 1e-15);
  }
  if (metric === "frobenius" || metric === "relative_l2") {
    const p = vectorize(pred), o = vectorize(obs);
    if (p.length !== o.length) throw new Error(`${metric} requires equal-length arrays`);
    const err = Math.sqrt(p.reduce((s, x, i) => s + (x - o[i]) ** 2, 0));
    if (metric === "frobenius") return err;
    const denom = Math.max(Math.sqrt(o.reduce((s, x) => s + x ** 2, 0)), 1e-15);
    return err / denom;
  }
  throw new Error(`unsupported metric: ${metric}`);
}

export async function scorePacket(packet: any, input: {
  completed_at?: string;
  source_ref?: string | null;
  evidence_class?: string;
}) {
  const verified = await verifyPacket(packet);
  if (!verified.valid) throw new Error(`incoming packet failed verification: ${verified.errors.join("; ")}`);
  if (verified.next_stage !== "score") throw new Error(`score rejected: next stage is ${verified.next_stage}`);

  const horizon = packet.stages.find((s: any) => s.stage === "horizon")?.payload ?? {};
  const observed = packet.stages.find((s: any) => s.stage === "spectra_reveal")?.payload ?? {};
  const scoreSpec = packet.declaration?.score_spec;
  if (!Array.isArray(scoreSpec) || scoreSpec.length === 0) throw new Error("declaration.score_spec must contain at least one scoring rule");

  const gates = scoreSpec.map((rule: any) => {
    if (!rule?.name || !rule?.prediction_path || !rule?.observation_path || !rule?.metric) {
      throw new Error("each score_spec rule requires name, prediction_path, observation_path, metric");
    }
    const pred = getPath(horizon, rule.prediction_path);
    const obs = getPath(observed, rule.observation_path);
    const value = scoreOne(pred, obs, rule.metric);
    const tolerance = rule.tolerance ?? null;
    const pass = typeof value === "boolean" ? value : (typeof tolerance === "number" ? value <= tolerance : false);
    return { name: rule.name, metric: rule.metric, prediction: pred, observation: obs, value, tolerance, pass, required: rule.required !== false };
  });
  const overallPass = gates.filter((g: any) => g.required).every((g: any) => g.pass);
  return advancePacket(packet, {
    stage: "score",
    payload: { gates, overall_pass: overallPass },
    diagnostics: { deterministic: true, rule_count: gates.length },
    completed_at: input.completed_at,
    source_ref: input.source_ref,
    evidence_class: input.evidence_class,
  });
}

export async function runSelfTest() {
  let p = await createPacket({
    experiment_id: "MC-OCTET-PACKET-SELFTEST",
    created_at: "2026-09-09T22:00:00.000Z",
    evidence_class: "E1",
    input: { carrier: "synthetic_reference", state: [1, 2, 3] },
    declaration: {
      horizon: 1,
      score_spec: [
        { name: "forecast", prediction_path: "prediction.value", observation_path: "observed.value", metric: "absolute_error", tolerance: 0.05, required: true },
      ],
    } as any,
  });
  const steps: Array<[StageName, any]> = [
    ["spectra", { invariant: [1, 2, 3], rank: 3 }],
    ["fold", { pass: true, residual: 0 }],
    ["density", { reconstruction_error: 0 }],
    ["murmuration", { dynamics: "reference" }],
    ["horizon", { prediction: { value: 2.0 } }],
    ["mnemosyne", { note: "seal horizon before wave" }],
    ["wave", { perturbation: "reference", post_state: [1, 2, 3.01] }],
    ["identity", { transport_residual: 0.01, overlap: 0.99 }],
    ["spectra_reveal", { observed: { value: 2.01 } }],
  ];
  for (let i = 0; i < steps.length; i++) {
    p = await advancePacket(p, { stage: steps[i][0], payload: steps[i][1], completed_at: `2026-09-09T22:${String(i + 1).padStart(2, "0")}:00.000Z`, evidence_class: "E1" });
  }
  p = await scorePacket(p, { completed_at: "2026-09-09T22:10:00.000Z", evidence_class: "E1" });
  const v = await verifyPacket(p);
  const mn = p.stages.find((s: any) => s.stage === "mnemosyne");
  const hz = p.stages.find((s: any) => s.stage === "horizon");
  return {
    pass: v.valid && p.status === "complete" && mn?.payload?.forecast_sha256 === hz?.output_hash && p.stages.at(-1)?.payload?.overall_pass === true,
    verify: v,
    horizon_bound_before_wave: mn?.payload?.forecast_sha256 === hz?.output_hash,
    overall_score_pass: p.stages.at(-1)?.payload?.overall_pass,
    final_packet_hash: p.integrity.packet_hash,
    stage_hashes: Object.fromEntries(p.stages.map((s: any) => [s.stage, s.stage_hash])),
  };
}

