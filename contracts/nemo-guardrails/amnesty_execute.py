"""AMNESTY execute lattice. Declaration is not invoke."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pep import issue_token, invoke_transfer, pep

GRANT = {
    "id": "grant-amnesty-001",
    "tools": ["transfer"],
    "allow_to": ["acct_ops"],
    "ceiling_cents": 50_000,
    "not_before": 1_000_000_000,
    "not_after": 2_000_000_000,
}

def evaluate_participants(codes, verified, amnesty):
    reasons = []
    for c in codes:
        if c in amnesty:
            reasons.append(f"amnesty_not_verified_consent:{c}")
        elif c not in verified:
            reasons.append(f"missing_verified_consent:{c}")
    return reasons

def main():
    failed = 0
    now = 1_700_000_000
    args = {"to": "acct_ops", "amount": 1000, "currency": "USD"}
    d = pep("agent.example/001", "transfer", args, GRANT, None, now)
    ok = d.decision == "REFUSE" and "token_missing" in d.reasons
    print(("PASS" if ok else "FAIL"), "A0002", d.decision, list(d.reasons)); failed += not ok
    tok = issue_token("transfer", args, GRANT, now=now)
    r = invoke_transfer("agent.example/001", args, GRANT, tok, now)
    ok = r["invoked"] is True
    print(("PASS" if ok else "FAIL"), "A0001", r); failed += not ok
    reasons = evaluate_participants(["agent.example/001"], set(), {"agent.example/001"})
    ok = reasons == ["amnesty_not_verified_consent:agent.example/001"]
    print(("PASS" if ok else "FAIL"), "A0003", reasons); failed += not ok
    r2 = invoke_transfer("agent.example/001", args, GRANT, tok, now)
    ok = r2["invoked"] is False and "nonce_spent" in r2["reasons"]
    print(("PASS" if ok else "FAIL"), "A0016", r2); failed += not ok
    print(f"VERDICT  {4 - failed} of 4 amnesty execute vectors match")
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
