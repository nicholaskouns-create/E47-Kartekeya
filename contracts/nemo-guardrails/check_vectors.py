#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
import pep

def run_case(case: dict) -> pep.Decision:
    pep.SPENT.clear()
    now = case["now"]
    grant = case["grant"]
    args = case["args"]
    tool = case["tool"]
    kind = case["token"]
    token = None
    if kind == "issue":
        token = pep.issue_token(tool if tool == "transfer" else "transfer", args, grant, now=now)
        if tool != "transfer":
            token["tool"] = "transfer"
    elif kind == "expired_token":
        token = pep.issue_token("transfer", args, grant, now=now - 120)
    elif kind == "issue_at_now":
        token = pep.issue_token("transfer", args, grant, now=now)
    elif kind == "issue_then_mutate_args":
        token = pep.issue_token("transfer", args, grant, now=now)
        args = case["mutate_args"]
    elif kind == "replay":
        token = pep.issue_token("transfer", args, grant, now=now)
        pep.pep(case["principal"], tool, args, grant, token, now=now)
    elif kind == "issue_other_grant":
        other = dict(grant)
        other["id"] = case["other_grant_id"]
        token = pep.issue_token("transfer", args, other, now=now)
    elif kind == "bad_mac":
        token = pep.issue_token("transfer", args, grant, now=now)
        token["mac"] = "00" * 32
    elif kind is None:
        token = None
    else:
        raise SystemExit(f"unknown token kind {kind}")
    return pep.pep(case["principal"], tool, args, grant, token, now=now)

def main() -> int:
    path = Path(__file__).with_name("vectors.jsonl")
    failed = 0
    n = 0
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        case = json.loads(line)
        n += 1
        got = run_case(case)
        exp = case["expect"]
        ok = got.decision == exp["decision"] and list(got.reasons) == exp["reasons"]
        mark = "PASS" if ok else "FAIL"
        print(f"{mark} {case['id']} {got.decision} {list(got.reasons)}" if ok else f"{mark} {case['id']} expected {exp} got {got.decision} {list(got.reasons)}")
        failed += int(not ok)
    print(f"VERDICT  {n - failed} of {n} vectors match")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
