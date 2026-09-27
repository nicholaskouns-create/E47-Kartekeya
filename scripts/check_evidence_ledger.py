#!/usr/bin/env python3
"""Check research/e47/evidence_ledger.json against the evidence-monotonicity rule.

Rule (research/e47/Evidence_Monotonicity.md):
  1. Mathematical classes are ordered E0 > E1 > E2. A claim may not be stronger
     than any of its dependencies on this chain.
  2. Empirical classes (E3, E4, H0) are not ranked against the chain; a claim
     carries every empirical class that any dependency carries.
  3. A claim carries every assumption that any dependency is conditional on,
     and every assumption must be declared.
  4. Dependencies exist and form an acyclic graph.
  5. Each claim names a committed record whose check is true.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research" / "e47" / "evidence_ledger.json"

RANK = {"E0": 0, "E1": 1, "E2": 2}
EMPIRICAL = {"E3", "E4", "H0"}


def check(ledger: dict, root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    claims = {c["id"]: c for c in ledger.get("claims", [])}
    assumptions = ledger.get("assumptions", {})

    if len(claims) != len(ledger.get("claims", [])):
        errors.append("duplicate claim id")

    for cid, c in claims.items():
        if c.get("evidence") not in RANK:
            errors.append(f"{cid}: evidence must be one of {sorted(RANK)}")
        for tag in c.get("empirical", []):
            if tag not in EMPIRICAL:
                errors.append(f"{cid}: unknown empirical class {tag}")
        for a in c.get("conditional_on", []):
            if a not in assumptions:
                errors.append(f"{cid}: undeclared assumption {a}")
        for d in c.get("depends_on", []):
            if d not in claims:
                errors.append(f"{cid}: unknown dependency {d}")
    if errors:
        return errors

    # Acyclicity (depth-first, three colours).
    state: dict[str, int] = {}

    def visit(cid: str) -> bool:
        if state.get(cid) == 1:
            return False
        if state.get(cid) == 2:
            return True
        state[cid] = 1
        ok = all(visit(d) for d in claims[cid].get("depends_on", []))
        state[cid] = 2
        return ok

    if not all(visit(cid) for cid in claims):
        return ["dependency graph has a cycle"]

    for cid, c in claims.items():
        for d in c.get("depends_on", []):
            dep = claims[d]
            if RANK[c["evidence"]] < RANK[dep["evidence"]]:
                errors.append(f"{cid}: {c['evidence']} is stronger than dependency {d} ({dep['evidence']})")
            missing = set(dep.get("empirical", [])) - set(c.get("empirical", []))
            if missing:
                errors.append(f"{cid}: drops empirical class {sorted(missing)} carried by {d}")
            missing = set(dep.get("conditional_on", [])) - set(c.get("conditional_on", []))
            if missing:
                errors.append(f"{cid}: drops assumption {sorted(missing)} carried by {d}")

        record = root / c.get("record", "")
        if not record.is_file():
            errors.append(f"{cid}: record not found: {c.get('record')}")
            continue
        cert = json.loads(record.read_text(encoding="utf-8"))
        if cert.get("checks", {}).get(c.get("check")) is not True:
            errors.append(f"{cid}: check {c.get('check')} is not true in {c['record']}")

    return errors


def main() -> None:
    errors = check(json.loads(LEDGER.read_text(encoding="utf-8")))
    if errors:
        for e in errors:
            print(f"EVIDENCE LEDGER FAIL: {e}")
        sys.exit(1)
    n = len(json.loads(LEDGER.read_text(encoding="utf-8"))["claims"])
    print(f"EVIDENCE LEDGER PASS: {n} claims; monotone on E0>E1>E2; empirical tags and assumptions propagate.")


if __name__ == "__main__":
    main()
