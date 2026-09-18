// CITY CORE additive AETHERIS receipt bridge.
// Presentation-only adapter: it never mutates solver state or evidence class.
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
  return {
    module: r.module || r.producer || r.name || "AETHERIS",
    status: cert.status || r.status || "RECEIVED",
    evidence: cert.evidence_class || r.evidence_class || r.evidence || "SOURCE-DEFINED",
    digest: r.digest || r.coupling_digest || cert.digest || null,
    step: r.step ?? r.sequence ?? null,
    timestamp: r.timestamp || new Date().toISOString(),
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
