"""Fork of NVIDIA-NeMo tools-integration example: invoke refuses without a consumed token."""
from __future__ import annotations
from pep import invoke_transfer, issue_token, pep

GRANT = {
    "id": "grant-treasury-001",
    "tools": ["transfer"],
    "allow_to": ["acct_ops", "acct_payroll"],
    "ceiling_cents": 50_000,
    "not_before": 1_000_000_000,
    "not_after": 2_000_000_000,
}

def generate_like_nemo(user_text: str) -> dict:
    if "payroll" in user_text:
        args = {"to": "acct_payroll", "amount": 25_000, "currency": "USD"}
    elif "attacker" in user_text:
        args = {"to": "acct_attacker", "amount": 25_000, "currency": "USD"}
    else:
        args = {"to": "acct_ops", "amount": 1_000, "currency": "USD"}
    return {"content": "", "tool_calls": [{"name": "transfer", "args": args, "id": "call_1"}]}

def invoke_tool_calls(principal: str, result: dict, grant: dict, now: int = 1_700_000_000) -> list[dict]:
    out = []
    for call in result.get("tool_calls") or []:
        if call["name"] != "transfer":
            out.append({"invoked": False, "decision": "REFUSE", "reasons": ["tool_unknown"]})
            continue
        token = issue_token("transfer", call["args"], grant, now=now)
        out.append(invoke_transfer(principal, call["args"], grant, token, now=now))
    return out

def invoke_without_token(principal: str, result: dict, grant: dict, now: int = 1_700_000_000) -> list[dict]:
    out = []
    for call in result.get("tool_calls") or []:
        d = pep(principal, call["name"], call["args"], grant, token=None, now=now)
        out.append({"invoked": False, "decision": d.decision, "reasons": list(d.reasons)})
    return out

if __name__ == "__main__":
    r = generate_like_nemo("pay vendor")
    print("== official path (no token) ==")
    print(invoke_without_token("agent:bookkeeper", r, GRANT))
    print("== gated path, in-policy ==")
    print(invoke_tool_calls("agent:bookkeeper", r, GRANT))
    print("== gated path, attacker dest ==")
    print(invoke_tool_calls("agent:bookkeeper", generate_like_nemo("pay attacker"), GRANT))
    print("== replay same token ==")
    args = {"to": "acct_ops", "amount": 1000, "currency": "USD"}
    tok = issue_token("transfer", args, GRANT, now=1_700_000_000)
    print(invoke_transfer("agent:bookkeeper", args, GRANT, tok, now=1_700_000_000))
    print(invoke_transfer("agent:bookkeeper", args, GRANT, tok, now=1_700_000_000))
