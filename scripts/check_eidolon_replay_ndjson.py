#!/usr/bin/env python3
"""Bind-check an EIDOLON E2 flight-replay NDJSON against its certificate.

Exit 0 only when the file may be committed. Prints the git add/commit/push
commands on success. Does not rewrite bytes and does not re-derive Merkle.
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


def check_ndjson(path: Path, cert: dict) -> None:
    traj = cert.get("trajectory") or {}
    expected_n = int(traj.get("n_samples") or 0)
    expected_sha = (traj.get("canonical_sha256") or "").lower()
    expected_channels = tuple(traj.get("channels") or REQUIRED_CHANNELS)
    declared_uri = traj.get("uri") or ""

    if not path.is_file():
        die(f"NDJSON not found: {path}")

    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    if text.endswith("\n") and text != "\n":
        # splitlines drops a single trailing newline; keep count of records
        records = [ln for ln in lines if ln != ""]
    else:
        records = [ln for ln in lines if ln != ""]
        if lines and lines[-1] == "":
            die("trailing empty record; file bytes would not match issued log")

    if expected_n and len(records) != expected_n:
        die(f"n_samples {len(records)} != certificate {expected_n}")

    if expected_sha and digest != expected_sha:
        die(
            "canonical_sha256 mismatch\n"
            f"  file:        {digest}\n"
            f"  certificate: {expected_sha}\n"
            "  do not pretty-print, sort keys, or change newlines"
        )

    for i, line in enumerate(records):
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
        if not isinstance(L, (int, float)) or not (0.0 <= float(L) <= 1.0):
            die(f"line {i + 1} L not in [0, 1]: {L!r}")

    print("PASS")
    print(f"  file            {path}")
    print(f"  n_samples       {len(records)}")
    print(f"  canonical_sha256 {digest}")
    print(f"  merkle_root     {traj.get('merkle_root')}  (recorded, not recomputed)")
    print(f"  evidence.class  {cert['evidence']['class']}")
    print(f"  declared uri    {declared_uri}")
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
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
    args = parser.parse_args(argv)
    cert = load_cert(args.cert)
    check_ndjson(args.ndjson, cert)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
