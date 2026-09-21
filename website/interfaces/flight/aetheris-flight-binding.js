// Bind AETHERIS receipt state transitions into the GitHub-owned EIDOLON flight loop.
// This consumes state; it does not promote evidence class or invent solver outputs.
export const EIDOLON_FLIGHT_RECEIPT_CONTRACT = Object.freeze({
  schema: "EIDOLON-AETHERIS-FLIGHT/1.0",
  grammar: "CITY-INVARIANT 1.0",
  operator: "AETHERIS receipt/state_transition -> EIDOLON frame state",
  invariant: "Receipt application preserves provenance/evidence and never promotes canonical status."
});

export const AETHERIS_RECEIPT_STORAGE_KEY = "city:aetheris:last-receipt";

const isObject = x => !!x && typeof x === "object" && !Array.isArray(x);
const numberOr = (value, fallback = 0) => Number.isFinite(Number(value)) ? Number(value) : fallback;
const clamp = (value, lo, hi) => Math.max(lo, Math.min(hi, numberOr(value)));

function pickState(raw, receipt) {
  return raw?.state ??
    raw?.state_transition ??
    raw?.output_packet?.state_transition ??
    raw?.envelope?.state ??
    raw?.envelope?.state_transition ??
    raw?.envelope?.output_packet?.state_transition ??
    raw?.raw?.state ??
    raw?.raw?.state_transition ??
    raw?.raw?.output_packet?.state_transition ??
    receipt?.state ??
    receipt?.state_transition ??
    receipt?.output_packet?.state_transition ??
    null;
}

export function normalizeFlightReceipt(raw) {
  if (!isObject(raw)) return null;
  const receipt = isObject(raw.receipt) ? raw.receipt :
    isObject(raw.raw?.receipt) ? raw.raw.receipt :
    isObject(raw.raw) ? raw.raw :
    raw;
  const state = pickState(raw, receipt);
  const status = receipt?.status ?? raw.status ?? "RECEIVED";
  const receiptCode = receipt?.receipt_code ?? receipt?.id ?? raw.receipt_code ?? raw.id ?? null;
  const evidence = receipt?.evidence_class ?? raw.evidence_class ?? raw.evidence ?? "SOURCE-DEFINED";
  const step = state?.step ?? raw.step ?? receipt?.step ?? null;
  return {
    schema: EIDOLON_FLIGHT_RECEIPT_CONTRACT.schema,
    receipt,
    receipt_code: receiptCode,
    status,
    evidence,
    step,
    state_transition: isObject(state) ? state : null,
    state_before_digest: raw.state_before_digest ?? receipt?.state_before_digest ?? null,
    state_after_digest: raw.state_after_digest ?? receipt?.state_after_digest ?? null,
    timestamp: raw.timestamp ?? receipt?.created_at ?? receipt?.timestamp ?? new Date().toISOString()
  };
}

function readAxis(source, aliases, fallback = 0) {
  for (const key of aliases) {
    if (source?.[key] !== undefined) return numberOr(source[key], fallback);
  }
  return fallback;
}

export function deriveFlightControl(state) {
  if (!isObject(state)) return { yaw:0, pitch:0, roll:0, vertical:0, throttle:0, speed:0 };
  const interaction = isObject(state.last_interaction) ? state.last_interaction :
    isObject(state.interaction) ? state.interaction :
    isObject(state.controls) ? state.controls :
    state;
  const axes = isObject(interaction.axes) ? interaction.axes : {};
  return {
    yaw: clamp(readAxis(interaction, ["yaw","heading_delta"], readAxis(axes, ["yaw","x"])), -1, 1),
    pitch: clamp(readAxis(interaction, ["pitch"], readAxis(axes, ["pitch","y"])), -1, 1),
    roll: clamp(readAxis(interaction, ["roll"], readAxis(axes, ["roll","rx"])), -1, 1),
    vertical: clamp(readAxis(interaction, ["vertical","climb","lift"], readAxis(axes, ["vertical","ry"])), -1, 1),
    throttle: clamp(readAxis(interaction, ["throttle","power"], readAxis(axes, ["throttle"])), 0, 1),
    speed: Math.max(0, readAxis(interaction, ["speed","velocity","airspeed"], 0))
  };
}

export function createEidolonFlightReceiptBinding({ sim, onApply } = {}) {
  let current = null;

  const forward = normalized => {
    if (!normalized) return;
    try {
      sim?.contentWindow?.postMessage({
        type: "EIDOLON:AETHERIS_STATE_TRANSITION",
        schema: EIDOLON_FLIGHT_RECEIPT_CONTRACT.schema,
        receipt: {
          receipt_code: normalized.receipt_code,
          status: normalized.status,
          evidence: normalized.evidence,
          step: normalized.step,
          state_before_digest: normalized.state_before_digest,
          state_after_digest: normalized.state_after_digest
        },
        state_transition: normalized.state_transition,
        control: deriveFlightControl(normalized.state_transition)
      }, "*");
    } catch {}
  };

  const consume = raw => {
    const normalized = normalizeFlightReceipt(raw);
    if (!normalized) return null;
    current = {
      ...normalized,
      control: deriveFlightControl(normalized.state_transition)
    };
    forward(current);
    onApply?.(current);
    return current;
  };

  const message = event => {
    const data = event?.data;
    if (!isObject(data)) return;
    if (data.type === "EIDOLON:AETHERIS_STATE_TRANSITION") return;
    if (
      data.type === "aetheris.receipt" ||
      data.kind === "aetheris.receipt" ||
      data.receipt ||
      data.certificate ||
      data.state_transition
    ) consume(data);
  };

  const storage = event => {
    if (event.key !== AETHERIS_RECEIPT_STORAGE_KEY || !event.newValue) return;
    try { consume(JSON.parse(event.newValue)); } catch {}
  };

  window.addEventListener("message", message);
  window.addEventListener("storage", storage);
  sim?.addEventListener?.("load", () => forward(current));

  try {
    const prior = JSON.parse(localStorage.getItem(AETHERIS_RECEIPT_STORAGE_KEY) || "null");
    if (prior) consume(prior);
  } catch {}

  return {
    consume,
    sample: () => current,
    replay: () => forward(current),
    destroy() {
      window.removeEventListener("message", message);
      window.removeEventListener("storage", storage);
    }
  };
}
