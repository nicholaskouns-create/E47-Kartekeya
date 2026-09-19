#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/"lab-manifest.json"
ALLOWED_MATURITY={"validated-core","research","experimental","prototype","archived"}
ALLOWED_EVIDENCE={"E0","E1","E2","E3","E4","H0"}

def fail(msg:str)->None:
    raise SystemExit(f"INSTRUMENT CONTRACT FAIL: {msg}")

def main()->None:
    lab=json.loads(LAB.read_text())
    components=lab["components"]
    seen=set()
    for item in components:
        cid=item["id"]
        contract_path=item.get("contract")
        if not contract_path:
            fail(f"{cid}: lab manifest missing contract path")
        path=ROOT/contract_path
        if not path.is_file():
            fail(f"{cid}: contract file missing: {contract_path}")
        c=json.loads(path.read_text())
        if c.get("schema")!="CITY-INSTRUMENT-CONTRACT/1.0":
            fail(f"{cid}: bad contract schema")
        if c.get("id")!=cid:
            fail(f"{cid}: contract id mismatch: {c.get('id')}")
        if cid in seen:
            fail(f"duplicate component id: {cid}")
        seen.add(cid)
        if c.get("maturity") not in ALLOWED_MATURITY:
            fail(f"{cid}: invalid maturity")
        if set(c.get("evidence",[]))-ALLOWED_EVIDENCE:
            fail(f"{cid}: invalid evidence class")
        if c.get("maturity")!=item.get("maturity"):
            fail(f"{cid}: maturity differs between lab manifest and component contract")
        if c.get("evidence")!=item.get("evidence"):
            fail(f"{cid}: evidence differs between lab manifest and component contract")
        if c.get("version")!=item.get("version"):
            fail(f"{cid}: version differs between lab manifest and component contract")
        version_file=path.parent/"VERSION"
        if not version_file.is_file():
            fail(f"{cid}: VERSION file missing")
        if version_file.read_text().strip()!=c["version"]:
            fail(f"{cid}: VERSION does not match component.json")
        smoke=ROOT/c["smoke"]["entrypoint"]
        if not smoke.is_file():
            fail(f"{cid}: smoke entrypoint missing: {smoke.relative_to(ROOT)}")
        if c["provenance"].get("receipt_schema")!="CITY-INSTRUMENT-RECEIPT/1.0":
            fail(f"{cid}: receipt schema mismatch")
        if c["telemetry"].get("failure_schema")!="CITY-INSTRUMENT-FAILURE/1.0":
            fail(f"{cid}: failure telemetry schema mismatch")
        if not c.get("boundaries"):
            fail(f"{cid}: evidence/runtime boundaries are missing")
        if contract_path.startswith("website/interfaces/"):
            index=path.parent/"index.html"
            if not index.is_file():
                fail(f"{cid}: browser instrument index.html is missing")
            html=index.read_text(encoding="utf-8")
            if "instrument-telemetry.js" not in html:
                fail(f"{cid}: live standardized failure telemetry hook is not installed")
            if c["version"] not in html:
                fail(f"{cid}: live surface does not expose its component version")
    print(f"INSTRUMENT CONTRACT PASS: {len(components)} autonomous instruments")

if __name__=="__main__":
    main()
