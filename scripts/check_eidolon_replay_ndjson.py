#!/usr/bin/env python3
"""Bind-check an EIDOLON E2 flight-replay NDJSON against its certificate.

The certificate binds the records, not the bytes of a file:

  canonical record   JSON with sorted keys and no insignificant whitespace
  canonical_sha256   SHA-256 of the canonical JSON array of all records
  merkle_root        SHA-256 Merkle root over the records in order:
                     leaf = SHA-256(canonical record), parent = SHA-256(left || right),
                     an unpaired node is paired with itself

The NDJSON holds one canonical record per line. Both bindings are recomputed here.

Exit 0 only when the file may be committed. Prints the git add/commit/push
commands on success. Does not rewrite bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REQUIRED_CHANNELS = ("t", "W", "L", "m_eff", "mode", "lab_mode")


def die(msg: str, code: int = 1) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(code)


def canonical(obj, ensure_ascii: bool = False) -> str:
    """Canonical JSON: sorted keys, no insignificant whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=ensure_ascii)


def canonical_sha256(records: list[dict]) -> str:
    return hashlib.sha256(canonical(records).encode("utf-8")).hexdigest()


def merkle_root(records: list[dict]) -> str:
    level = [hashlib.sha256(canonical(r).encode("utf-8")).digest() for r in records]
    if not level:
        return hashlib.sha256(b"").hexdigest()
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [hashlib.sha256(level[i] + level[i + 1]).digest() for i in range(0, len(level), 2)]
    return level[0].hex()


def load_cert(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        die(f"certificate not found: {path}")
    except json.JSONDecodeError as exc:
        die(f"certificate is not JSON: {path} ({exc})")
    if data.get("evidence", {}).get("class") != "E2":
        die("certificate evidence.class is not E2; refuse to bind a replay log")
    return data


def check_ndjson(path: Path, cert: dict) -> dict:
    """Return the recomputed bindings; exit non-zero unless the log matches the certificate."""
    traj = cert.get("trajectory") or {}
    expected_n = int(traj.get("n_samples") or 0)
    expected_sha = (traj.get("canonical_sha256") or "").lower()
    expected_root = (traj.get("merkle_root") or "").lower()
    expected_channels = tuple(traj.get("channels") or REQUIRED_CHANNELS)

    if not path.is_file():
        die(f"NDJSON not found: {path}")

    raw = path.read_bytes()
    records = []
    for i, line in enumerate(raw.decode("utf-8").splitlines()):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            die(f"line {i + 1} is not JSON: {exc}")
        if not isinstance(row, dict):
            die(f"line {i + 1} is not an object")
        missing = [c for c in expected_channels if c not in row]
        if missing:
            die(f"line {i + 1} missing channels: {missing}")
        L = row.get("L")
        if isinstance(L, bool) or not isinstance(L, (int, float)) or not (0.0 <= float(L) <= 1.0):
            die(f"line {i + 1} L not in [0, 1]: {L!r}")
        if line != canonical(row):
            die(f"line {i + 1} is not a canonical record (sorted keys, no whitespace)")
        records.append(row)

    if expected_n and len(records) != expected_n:
        die(f"n_samples {len(records)} != certificate {expected_n}")

    sha = canonical_sha256(records)
    if expected_sha and sha != expected_sha:
        die(
            "canonical_sha256 mismatch\n"
            f"  records:     {sha}\n"
            f"  certificate: {expected_sha}"
        )

    root = merkle_root(records)
    if expected_root and root != expected_root:
        die(
            "merkle_root mismatch\n"
            f"  records:     {root}\n"
            f"  certificate: {expected_root}"
        )

    return {
        "n_samples": len(records),
        "canonical_sha256": sha,
        "merkle_root": root,
        "file_sha256": hashlib.sha256(raw).hexdigest(),
    }


def signature_status(cert: dict) -> tuple[bool, str]:
    """Check signature.payload_sha256 and, when possible, the Ed25519 signature.

    The signed payload is the canonical JSON of the certificate without its
    signature object. Non-ASCII text is tried both raw and escaped.
    """
    sig = cert.get("signature") or {}
    recorded = (sig.get("payload_sha256") or "").lower()
    if not recorded:
        return False, "no signature.payload_sha256 recorded"
    body = {k: v for k, v in cert.items() if k != "signature"}
    for escape in (False, True):
        payload = canonical(body, ensure_ascii=escape).encode("utf-8")
        if hashlib.sha256(payload).hexdigest() == recorded:
            break
    else:
        return False, "payload_sha256 is not reproduced by the canonical certificate without its signature"
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.serialization import load_pem_public_key
    except ImportError:
        return False, "payload_sha256 reproduced; Ed25519 not checked (install 'cryptography')"
    try:
        key = load_pem_public_key(sig["public_key_pem"].encode("ascii"))
        key.verify(bytes.fromhex(sig["signature_hex"]), payload)
    except (InvalidSignature, KeyError, ValueError):
        return False, "payload_sha256 reproduced; the Ed25519 signature does not verify"
    return True, "Ed25519 signature verifies over the canonical payload"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--cert",
        default="artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json",
        type=Path,
    )
    parser.add_argument(
        "--ndjson",
        default="trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson",
        type=Path,
    )
    parser.add_argument(
        "--require-signature",
        action="store_true",
        help="also fail unless the certificate signature verifies",
    )
    args = parser.parse_args(argv)
    cert = load_cert(args.cert)
    report = check_ndjson(args.ndjson, cert)
    signed, signature_note = signature_status(cert)
    path = args.ndjson

    print("PASS")
    print(f"  file             {path}")
    print(f"  n_samples        {report['n_samples']}")
    print(f"  canonical_sha256 {report['canonical_sha256']}  (recomputed)")
    print(f"  merkle_root      {report['merkle_root']}  (recomputed)")
    print(f"  file sha256      {report['file_sha256']}")
    print(f"  evidence.class   {cert['evidence']['class']}")
    print(f"  declared uri     {(cert.get('trajectory') or {}).get('uri') or ''}")
    print(f"  signature        {'VERIFIED' if signed else 'UNVERIFIED'}: {signature_note}")
    if args.require_signature and not signed:
        die(f"signature required: {signature_note}")
    print()
    print("Commit commands (run from the repository root):")
    print()
    print(f"git add {path.as_posix()}")
    mirror = Path("website/data") / path.as_posix()
    print(f"git add {mirror.as_posix()}   # if a Pages mirror exists")
    print()
    print("git commit -m \"$(cat <<'EOF'")
    print(f"Add {cert.get('certificate_id')} trajectory NDJSON.")
    print()
    print(f"Merkle-bound to {cert.get('certificate_id', 'the replay certificate')}.")
    print("Evidence class locked at E2. No promotion of game rules.")
    print("EOF")
    print(')"')
    print()
    print("git push origin main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
