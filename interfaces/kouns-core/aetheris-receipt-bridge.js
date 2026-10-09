// CITY CORE additive AETHERIS receipt bridge.
// Normalizes and persists receipt envelopes without mutating solver state or evidence class.
// Returned state transitions are preserved so the EIDOLON flight loop can consume them.
export const CITY_AETHERIS_RECEIPT_BRIDGE = Object.freeze({
  grammar: "CITY-INVARIANT 1.0",
  object: "CITY CORE / EIDOLON AETHERIS receipt viewer",
  operator: "AETHERIS receipt -> postMessage/storage -> normalized viewer telemetry",
  invariant: "Receipt visualization does not alter solver state, timestep, evidence class, provenance, or canonical status.",
  evidence: "presentation adapter; underlying receipt retains its own evidence class",
  provenance: "CITY-COMMONS-SIM-FORGE / PR #40 / commit 6b3651ef073383e1ccb6ad2b618becb8e142ec1a",
  next_action: "Connect producers incrementally; retain human promotion gate."
});

const KEY = "city:aetheris:last-receipt";

function validReceipt(x) {
  return x && typeof x === "object" &&
    (x.kind === "aetheris.receipt" || x.type === "aetheris.receipt" || x.certificate || x.receipt);
}

export function normalizeReceipt(raw) {
  if (!validReceipt(raw)) return null;
  const r = raw.receipt || raw;
  const cert = r.certificate || {};
  const stateTransition =
    raw.state ??
    raw.state_transition ??
    raw.output_packet?.state_transition ??
    r.state ??
    r.state_transition ??
    r.output_packet?.state_transition ??
    null;
  return {
    module: r.module || r.producer || r.name || "AETHERIS",
    status: cert.status || r.status || "RECEIVED",
    evidence: cert.evidence_class || r.evidence_class || r.evidence || "SOURCE-DEFINED",
    digest: r.digest || r.coupling_digest || cert.digest || raw.state_after_digest || null,
    step: stateTransition?.step ?? r.step ?? r.sequence ?? null,
    timestamp: r.timestamp || r.created_at || new Date().toISOString(),
    state_transition: stateTransition,
    state_before_digest: raw.state_before_digest ?? r.state_before_digest ?? null,
    state_after_digest: raw.state_after_digest ?? r.state_after_digest ?? null,
    envelope: raw,
    raw: r
  };
}

export function createAetherisReceiptBridge({ onReceipt } = {}) {
  const emit = raw => {
    const receipt = normalizeReceipt(raw);
    if (!receipt) return null;
    try { localStorage.setItem(KEY, JSON.stringify(receipt)); } catch {}
    onReceipt?.(receipt);
    return receipt;
  };
  const message = event => {
    // Instruments may publish typed receipts without gaining control of CITY CORE.
    emit(event.data);
  };
  window.addEventListener("message", message);
  window.addEventListener("storage", e => {
    if (e.key === KEY && e.newValue) {
      try { onReceipt?.(JSON.parse(e.newValue)); } catch {}
    }
  });
  try {
    const prior = JSON.parse(localStorage.getItem(KEY) || "null");
    if (prior) onReceipt?.(prior);
  } catch {}
  return { emit, destroy: () => window.removeEventListener("message", message) };
}
