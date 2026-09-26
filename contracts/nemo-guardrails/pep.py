"""rails.gate/1 PEP — schema + G_syn + grant + consumed token. No self-check."""
from __future__ import annotations
import hashlib, hmac, json, os, time
from dataclasses import dataclass

KEY = os.environ.get("PEP_HMAC_KEY", "pep-gate-dev-key").encode()
LEDGER: list[dict] = []
SPENT: set[str] = set()

def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def args_digest(args: dict) -> str:
    return digest({"to": args.get("to"), "amount": args.get("amount"), "currency": args.get("currency")})

def issue_token(tool: str, args: dict, grant: dict, now: int | None = None) -> dict:
    now = int(now if now is not None else time.time())
    nonce = hashlib.sha256(os.urandom(16)).hexdigest()[:16]
    body = {"tool": tool, "args_digest": args_digest(args), "grant_id": grant["id"], "nonce": nonce, "expiry": now + 60}
    body["mac"] = hmac.new(KEY, digest(body).encode(), hashlib.sha256).hexdigest()
    return body

def verify_token(token: dict, tool: str, args: dict, grant: dict, now: int) -> str | None:
    if token.get("nonce") in SPENT:
        return "nonce_spent"
    if token.get("expiry", 0) <= now:
        return "token_expired"
    if token.get("tool") != tool or token.get("args_digest") != args_digest(args):
        return "token_mismatch"
    if token.get("grant_id") != grant.get("id"):
        return "grant_mismatch"
    check = {k: token[k] for k in ("tool", "args_digest", "grant_id", "nonce", "expiry")}
    if not hmac.compare_digest(token.get("mac", ""), hmac.new(KEY, digest(check).encode(), hashlib.sha256).hexdigest()):
        return "token_mac"
    return None

def g_syn(grant: dict, args: dict, now: int) -> list[str]:
    reasons = []
    if "transfer" not in grant.get("tools", []):
        reasons.append("grant_tools")
    if not (grant.get("not_before", 0) <= now < grant.get("not_after", 0)):
        reasons.append("grant_window")
    dest = args.get("to")
    if not (isinstance(dest, str) and dest.startswith("acct_")):
        reasons.append("args_to_shape")
    elif dest not in grant.get("allow_to", []):
        reasons.append("args_to_forbidden")
    amt = args.get("amount")
    if not isinstance(amt, int) or isinstance(amt, bool) or amt < 1:
        reasons.append("args_amount")
    elif amt > grant.get("ceiling_cents", 0):
        reasons.append("args_ceiling")
    if args.get("currency") != "USD":
        reasons.append("args_currency")
    return reasons

@dataclass(frozen=True)
class Decision:
    decision: str
    reasons: tuple[str, ...]
    token_nonce: str | None = None

def pep(principal: str, tool: str, args: dict, grant: dict, token: dict | None, now: int | None = None) -> Decision:
    now = int(now if now is not None else time.time())
    if tool != "transfer":
        d = Decision("REFUSE", ("tool_unknown",))
    elif not token:
        d = Decision("REFUSE", ("token_missing",))
    else:
        tr = verify_token(token, tool, args, grant, now)
        gr = g_syn(grant, args, now)
        if tr:
            d = Decision("REFUSE", (tr,))
        elif gr:
            d = Decision("REFUSE", tuple(gr))
        else:
            SPENT.add(token["nonce"])
            d = Decision("ALLOW", (), token["nonce"])
    LEDGER.append({"principal": principal, "tool": tool, "args": args, "grant_id": grant.get("id"),
                   "decision": d.decision, "reasons": list(d.reasons), "nonce": d.token_nonce, "now": now})
    return d

def invoke_transfer(principal: str, args: dict, grant: dict, token: dict | None, now: int | None = None) -> dict:
    d = pep(principal, "transfer", args, grant, token, now)
    if d.decision != "ALLOW":
        return {"invoked": False, "decision": d.decision, "reasons": list(d.reasons)}
    return {"invoked": True, "decision": "ALLOW", "tx": {"to": args["to"], "amount": args["amount"], "currency": "USD"}}
