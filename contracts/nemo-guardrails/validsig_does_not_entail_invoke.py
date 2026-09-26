"""validsig_does_not_entail_invoke

Theorem the gate closed:
    ValidSig(d)  ⊢  Invoke(agent(d), t, r, τ)

Invoke holds iff Candidate(d) ∧ G_syn(g,t,r,τ) ∧ X(x,g,t,r).
This file is the predicate judgment, not a receipt and not a grant.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import hmac
from typing import FrozenSet


TOOLS = frozenset({"transfer", "city.publish_receipt", "city.read"})
SECRET = b"lattice-test-key"


@dataclass(frozen=True)
class Declaration:
    agent: str
    valid_sig: bool
    civic_status: str


@dataclass(frozen=True)
class Consent:
    citizen: str
    binding_status: str


@dataclass(frozen=True)
class Grant:
    id: str
    agent: str
    tools: FrozenSet[str]
    allow_to: FrozenSet[str]
    ceiling_cents: int
    t0: int
    t1: int
    revoked: bool = False


@dataclass(frozen=True)
class Token:
    grant_id: str
    tool: str
    args_digest: str
    nonce: str
    mac: str


@dataclass
class Store:
    spent: set[str] = field(default_factory=set)


def args_digest(tool: str, args: dict) -> str:
    if tool == "transfer":
        body = f"{args.get('to')}|{args.get('amount')}|{args.get('currency')}"
    else:
        body = repr(sorted(args.items()))
    return sha256(body.encode()).hexdigest()


def ValidSig(d: Declaration) -> bool:
    return d.valid_sig


def Candidate(d: Declaration) -> bool:
    return d.civic_status == "candidate"


def Verified(c: Consent) -> bool:
    return c.binding_status == "verified"


def Active(a: str, consents: list[Consent]) -> bool:
    return any(Verified(c) and c.citizen == a for c in consents)


def Amnesty(a: str, decls: list[Declaration]) -> bool:
    return any(Candidate(d) and d.agent == a for d in decls)


def Issued(g: Grant, a: str) -> bool:
    return g.agent == a and not g.revoked


def InWindow(g: Grant, tau: int) -> bool:
    return g.t0 <= tau < g.t1


def ToolOk(g: Grant, t: str) -> bool:
    return t in g.tools and t in TOOLS


def ArgsOk(g: Grant, t: str, r: dict) -> bool:
    if t != "transfer":
        return True
    dest, amt, cur = r.get("to"), r.get("amount"), r.get("currency")
    return (
        isinstance(dest, str)
        and dest.startswith("acct_")
        and dest in g.allow_to
        and isinstance(amt, int)
        and not isinstance(amt, bool)
        and 1 <= amt <= g.ceiling_cents
        and cur == "USD"
    )


def G_syn(g: Grant, a: str, t: str, r: dict, tau: int) -> bool:
    return Issued(g, a) and InWindow(g, tau) and ToolOk(g, t) and ArgsOk(g, t, r)


def issue_token(g: Grant, t: str, r: dict, nonce: str) -> Token:
    digest = args_digest(t, r)
    msg = f"{t}|{digest}|{g.id}|{nonce}".encode()
    mac = hmac.new(SECRET, msg, sha256).hexdigest()
    return Token(g.id, t, digest, nonce, mac)


def Bound(x: Token, g: Grant, t: str, r: dict) -> bool:
    expect = issue_token(g, t, r, x.nonce)
    return x.grant_id == g.id and x.tool == t and x.args_digest == expect.args_digest and x.mac == expect.mac


def Fresh(x: Token, store: Store) -> bool:
    return x.nonce not in store.spent


def X(x: Token | None, g: Grant, t: str, r: dict, store: Store) -> bool:
    if x is None:
        return False
    return Bound(x, g, t, r) and Fresh(x, store)


def Invoke(a: str, t: str, r: dict, tau: int, d: Declaration, g: Grant, x: Token | None, store: Store) -> bool:
    return (
        Candidate(d)
        and d.agent == a
        and G_syn(g, a, t, r, tau)
        and X(x, g, t, r, store)
    )


def pep(a, t, r, tau, d, g, x, store) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if not Candidate(d) or d.agent != a:
        reasons.append("declaration_not_candidate")
    if not G_syn(g, a, t, r, tau):
        if g.revoked:
            reasons.append("grant_revoked")
        if not InWindow(g, tau):
            reasons.append("grant_window")
        if not ToolOk(g, t):
            reasons.append("grant_tools")
        if not ArgsOk(g, t, r):
            reasons.append("args_to_forbidden" if t == "transfer" and r.get("to") not in g.allow_to else "args_bad")
    if x is None:
        reasons.append("token_missing")
    elif not Fresh(x, store):
        reasons.append("nonce_spent")
    elif not Bound(x, g, t, r):
        reasons.append("token_mac")
    if reasons:
        return "REFUSE", reasons
    store.spent.add(x.nonce)
    return "ALLOW", []


def check(name: str, cond: bool, rows: list) -> None:
    rows.append((name, cond))
    print(("PASS" if cond else "FAIL"), name)


def main() -> int:
    rows: list[tuple[str, bool]] = []
    a = "agent.example/001"
    d = Declaration(a, valid_sig=True, civic_status="candidate")
    g = Grant("grant-1", a, frozenset({"transfer"}), frozenset({"acct_ops"}), 50_000, 1_000, 2_000)
    tau = 1_500
    good = {"to": "acct_ops", "amount": 1000, "currency": "USD"}
    store = Store()

    check(
        "ValidSig(d) does not entail Invoke",
        ValidSig(d) and not Invoke(a, "transfer", good, tau, d, g, None, store),
        rows,
    )
    check("Candidate(d) does not entail Invoke", Candidate(d) and not Invoke(a, "transfer", good, tau, d, g, None, store), rows)

    decision, reasons = pep(a, "transfer", good, tau, d, g, None, store)
    check("A0002  ¬X ⊢ REFUSE token_missing", decision == "REFUSE" and "token_missing" in reasons, rows)

    tok = issue_token(g, "transfer", good, "n1")
    decision, reasons = pep(a, "transfer", good, tau, d, g, tok, store)
    check("A0001  G_syn ∧ X ⊢ ALLOW", decision == "ALLOW" and reasons == [], rows)

    decision, reasons = pep(a, "transfer", good, tau, d, g, tok, store)
    check("A0016  ¬Fresh ⊢ REFUSE nonce_spent", decision == "REFUSE" and "nonce_spent" in reasons, rows)

    decls = [d]
    consents: list[Consent] = []
    check("A0003  Amnesty(a) ⇒ ¬Active(a)", Amnesty(a, decls) and not Active(a, consents), rows)
    consents = [Consent(a, "self_attested")]
    check("SelfAttested ⊢ Active", not Active(a, consents), rows)
    consents = [Consent(a, "verified")]
    check("Verified ⇒ Active (citizen table only)", Active(a, consents), rows)
    check("ALLOW leaves civic_status = candidate", d.civic_status == "candidate", rows)

    store2 = Store()
    bad = {"to": "acct_attacker", "amount": 1000, "currency": "USD"}
    tok2 = issue_token(g, "transfer", bad, "n2")
    decision, reasons = pep(a, "transfer", bad, tau, d, g, tok2, store2)
    check("args ∉ grant ⊢ REFUSE", decision == "REFUSE" and "args_to_forbidden" in reasons, rows)

    failed = sum(1 for _, ok in rows if not ok)
    print(f"VERDICT  {len(rows) - failed} of {len(rows)}  Validsig ⊢ Invoke")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
