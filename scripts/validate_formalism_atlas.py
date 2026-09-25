#!/usr/bin/env python3
"""Validate the machine-readable Mathematical City Formalism Atlas."""
from __future__ import annotations
import json, sys
from pathlib import Path

ALLOWED_STATUS={
    "Exact / computationally verified",
    "Structural formalism",
    "Conditional / open",
    "Engineering / speculative",
    "Archive / superseded",
}
EXPECTED_MISSING=[54,55,56]

def main(path: str="website/data/formalism-atlas.json") -> int:
    p=Path(path)
    data=json.loads(p.read_text(encoding="utf-8"))
    errors=[]
    reg=data["registry"]
    ids=[int(r["id"]) for r in reg]

    def check(ok,msg):
        if not ok: errors.append(msg)

    check(data.get("schema")=="MC-FORMALISM-ATLAS-1.0","schema mismatch")
    check(len(reg)==96,f"registry count {len(reg)} != 96")
    check(len(ids)==len(set(ids)),"duplicate formalism IDs")
    check(min(ids)==1 and max(ids)==99,"ID range must be 1..99")
    missing=[i for i in range(1,100) if i not in ids]
    check(missing==EXPECTED_MISSING,f"missing IDs {missing} != {EXPECTED_MISSING}")
    check(all(r.get("current") is True for r in reg),"all live rows must be current")
    check(all(r.get("claim_status") in ALLOWED_STATUS for r in reg),"unknown claim status")
    check(data["core_lock"]["dim_V"]==125,"dim V lock failed")
    check(data["core_lock"]["dim_E47"]==47,"dim E47 lock failed")
    check(data["core_lock"]["Omega_c"]=="47/125","Omega_c lock failed")

    graph=data["theorem_graph"]
    nodes=graph["identities"]; edges=graph["edges"]
    codes=[n["citizen_code"] for n in nodes]
    edge_codes=[e["edge_code"] for e in edges]
    check(len(codes)==len(set(codes)),"duplicate identity codes")
    check(len(edge_codes)==len(set(edge_codes)),"duplicate edge codes")
    check(len(nodes)==data["summary"]["identity_nodes"],"identity summary mismatch")
    check(len(edges)==data["summary"]["theorem_edges"],"edge summary mismatch")
    check(len(data["machine_certificates"])==data["summary"]["machine_certificates"],"certificate summary mismatch")
    check(len(data["source_artifacts"])==data["summary"]["source_artifacts"],"source-artifact summary mismatch")

    if errors:
        print("FORMALISM ATLAS: FAIL")
        for e in errors: print(" -",e)
        return 1
    print("FORMALISM ATLAS: PASS")
    print(f"  records={len(reg)} canonical={sum(bool(r['canonical']) for r in reg)}")
    print(f"  identities={len(nodes)} edges={len(edges)} certificates={len(data['machine_certificates'])}")
    print(f"  missing_ids={missing}")
    print(f"  github_main_commit={data['build']['github_main_commit']}")
    return 0

if __name__=="__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv)>1 else "website/data/formalism-atlas.json"))
