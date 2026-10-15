from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import threading

UTC = timezone.utc
_SPEND = threading.Lock()


@dataclass(frozen=True)
class Grant:
    principal: str
    task: str
    tool: str
    args_digest: str
    issued_at: datetime
    expires_at: datetime
    nonce: str
    signature: str


def digest_args(args: str) -> str:
    return hashlib.sha256(args.encode()).hexdigest()


def sign(secret: bytes, principal: str, task: str, tool: str, args_digest: str,
         issued_at: datetime, expires_at: datetime, nonce: str) -> str:
    # A JSON array keeps every field boundary explicit: no delimiter inside a
    # field can move bytes from one field into the next.
    payload = json.dumps([
        principal, task, tool, args_digest,
        issued_at.isoformat(), expires_at.isoformat(), nonce,
    ], separators=(",", ":"), ensure_ascii=True).encode()
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def issue(secret: bytes, principal: str, task: str, tool: str, args: str,
          nonce: str, ttl_seconds: int = 300, now: datetime | None = None) -> Grant:
    now = now or datetime.now(UTC)
    exp = now + timedelta(seconds=ttl_seconds)
    d = digest_args(args)
    return Grant(principal, task, tool, d, now, exp, nonce,
                 sign(secret, principal, task, tool, d, now, exp, nonce))


def authorize(secret: bytes, grant: Grant, *, principal: str, task: str,
              tool: str, args: str, now: datetime, active_principals: set[str],
              spent_nonces: set[str]) -> bool:
    if principal not in active_principals:
        return False
    if grant.principal != principal or grant.task != task or grant.tool != tool:
        return False
    if digest_args(args) != grant.args_digest:
        return False
    if not (grant.issued_at <= now <= grant.expires_at):
        return False
    if not isinstance(grant.signature, str):
        return False
    expected = sign(secret, grant.principal, grant.task, grant.tool,
                    grant.args_digest, grant.issued_at, grant.expires_at, grant.nonce)
    if not hmac.compare_digest(expected.encode(), grant.signature.encode()):
        return False
    with _SPEND:
        if grant.nonce in spent_nonces:
            return False
        spent_nonces.add(grant.nonce)
    return True


def run_tests() -> None:
    secret = b"authorization-invariant-reference-key"
    t0 = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
    passed = []

    def ok(name, value):
        assert value, name
        passed.append(name)
        print(f"PASS {name}")

    g = issue(secret, "alice", "task-A", "exec", "echo safe", "n1", now=t0)
    spent = set()
    ok("valid grant", authorize(secret, g, principal="alice", task="task-A", tool="exec", args="echo safe", now=t0, active_principals={"alice"}, spent_nonces=spent))
    ok("replay rejected", not authorize(secret, g, principal="alice", task="task-A", tool="exec", args="echo safe", now=t0, active_principals={"alice"}, spent_nonces=spent))

    cases = [
        ("cross-task approval reuse", dict(principal="alice", task="task-B", tool="exec", args="echo safe", now=t0, active_principals={"alice"}, spent_nonces=set())),
        ("cross-principal access", dict(principal="bob", task="task-A", tool="exec", args="echo safe", now=t0, active_principals={"alice","bob"}, spent_nonces=set())),
        ("inactive principal", dict(principal="alice", task="task-A", tool="exec", args="echo safe", now=t0, active_principals=set(), spent_nonces=set())),
        ("tool mismatch", dict(principal="alice", task="task-A", tool="network", args="echo safe", now=t0, active_principals={"alice"}, spent_nonces=set())),
        ("argument mismatch", dict(principal="alice", task="task-A", tool="exec", args="cat secret", now=t0, active_principals={"alice"}, spent_nonces=set())),
        ("expired grant", dict(principal="alice", task="task-A", tool="exec", args="echo safe", now=t0 + timedelta(hours=1), active_principals={"alice"}, spent_nonces=set())),
        ("pre-issued use", dict(principal="alice", task="task-A", tool="exec", args="echo safe", now=t0 - timedelta(seconds=1), active_principals={"alice"}, spent_nonces=set())),
    ]
    for name, kwargs in cases:
        ok(name, not authorize(secret, g, **kwargs))

    tampered = Grant(**{**g.__dict__, "signature": "0" * 64})
    ok("signature tamper", not authorize(secret, tampered, principal="alice", task="task-A", tool="exec", args="echo safe", now=t0, active_principals={"alice"}, spent_nonces=set()))

    # A grant signed for principal "bob|x" on task "t" cannot be relabelled as
    # principal "bob" on task "x|t": the signed encoding fixes every field boundary.
    g2 = issue(secret, "bob|x", "t", "exec", "echo safe", "n2", now=t0)
    relabelled = Grant(**{**g2.__dict__, "principal": "bob", "task": "x|t"})
    ok("field-boundary forgery rejected", not authorize(secret, relabelled, principal="bob", task="x|t", tool="exec", args="echo safe", now=t0, active_principals={"bob"}, spent_nonces=set()))

    # Evidence must be the exact signature string. Truthy look-alikes are refused, never coerced.
    g4 = issue(secret, "alice", "task-A", "exec", "echo safe", "n4", now=t0)
    for value in (True, 1, "true", {"ok": True}):
        look_alike = Grant(**{**g4.__dict__, "signature": value})
        ok(f"look-alike evidence {value!r} refused", not authorize(secret, look_alike, principal="alice", task="task-A", tool="exec", args="echo safe", now=t0, active_principals={"alice"}, spent_nonces=set()))

    # A syntactically valid signature observes a grant; it does not invoke without full binding.
    g3 = issue(secret, "alice", "task-A", "exec", "echo safe", "n3", now=t0)
    observed_sig_valid = hmac.compare_digest(g3.signature, sign(secret, g3.principal, g3.task, g3.tool, g3.args_digest, g3.issued_at, g3.expires_at, g3.nonce))
    ok("valid signature alone is not invocation", observed_sig_valid and not authorize(secret, g3, principal="alice", task="wrong-task", tool="exec", args="echo safe", now=t0, active_principals={"alice"}, spent_nonces=set()))

    print(f"{len(passed)}/{len(passed)} PASS")


if __name__ == "__main__":
    run_tests()
