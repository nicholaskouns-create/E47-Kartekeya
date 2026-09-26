"""Map a PEP decision to CITY-INSTRUMENT-RECEIPT/1.0.\n\nReceipt status is the harness result, not a permission.\ninvoked is a separate field. PASS never authorizes invoke.\n"""
from __future__ import annotations
import hashlib, json, time
from pathlib import Path
from pep import Decision, digest

SCHEMA = "CITY-INSTRUMENT-RECEIPT/1.0"

def receipt(component_id: str, decision: Decision, invoked: bool, git_commit: str | None = None) -> dict:
    contract = Path(__file__).with_name("rails.gate-1.contract.json")
    raw = contract.read_bytes() if contract.exists() else b"{}"
    return {
        "schema": SCHEMA,
        "component_id": component_id,
        "version": "1.0.0",
        "mode": "smoke",
        "status": "PASS" if decision.decision in {"ALLOW", "REFUSE"} and isinstance(decision.reasons, tuple) else "FAIL",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": 0,
        "git_commit": git_commit,
        "contract_sha256": hashlib.sha256(raw).hexdigest(),
        "runtime": {"pep": "rails.gate/1", "invoked": invoked, "decision": decision.decision},
        "checks": [{"name": "g_syn_x_token", "decision": decision.decision, "reasons": list(decision.reasons)}],
        "metrics": {"nonce_bound": decision.token_nonce is not None},
        "failure": None if invoked or decision.decision == "REFUSE" else {"reasons": list(decision.reasons)},
        "permission": {
            "note": "status PASS is not a grant. invoke requires decision ALLOW and an unspent token.",
            "allowed_to_invoke": bool(invoked and decision.decision == "ALLOW"),
        },
    }

def write_receipt(path: Path, rec: dict) -> None:
    path.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    path.with_suffix(".sha256").write_text(digest(rec) + "\n")
