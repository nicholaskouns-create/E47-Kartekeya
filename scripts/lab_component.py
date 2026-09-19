#!/usr/bin/env python3
"""Uniform smoke, benchmark, provenance receipt, and failure telemetry for lab components."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"lab-manifest.json"

def now(): return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def load():
    m=json.loads(MANIFEST.read_text())
    return m,{c["id"]:c for c in m["components"]}
def contract(c): return json.loads((ROOT/c["contract_file"]).read_text())
def digest(paths):
    h=hashlib.sha256()
    for rel in paths:
        p=ROOT/rel
        if p.is_file():
            h.update(rel.encode()); h.update(p.read_bytes())
        elif p.is_dir():
            for f in sorted(x for x in p.rglob("*") if x.is_file() and "__pycache__" not in x.parts):
                h.update(str(f.relative_to(ROOT)).encode()); h.update(f.read_bytes())
    return h.hexdigest()
def emit_failure(c,op,t0,e):
    rec={"schema":"LAB-FAILURE-1.0","component":c["id"],"version":c["version"],"operation":op,"status":"fail","timestamp_utc":now(),"error_type":type(e).__name__,"message":str(e),"duration_ms":round((time.perf_counter()-t0)*1000,3)}
    print(json.dumps(rec,separators=(",",":")),file=sys.stderr)
def smoke(c):
    cfg=contract(c); p=ROOT/c["path"]
    if not p.exists(): raise FileNotFoundError(c["path"])
    ep=cfg["entrypoint"].split()[0]
    if ep.endswith(".html") and not (ROOT/ep).is_file(): raise FileNotFoundError(ep)
    for rel in cfg["provenance"]:
        if not (ROOT/rel).exists(): raise FileNotFoundError(rel)
    return {"path":c["path"],"entrypoint":cfg["entrypoint"],"provenance_items":len(cfg["provenance"]),"invariants_declared":len(cfg["invariants"])}
def benchmark(c):
    t=time.perf_counter(); detail=smoke(c)
    # Component-specific deterministic microbenchmarks. These measure software execution, not physical performance.
    if c["id"]=="e47-core":
        code="from e47.validation_results import run_all_validations,require_all_validations;r=run_all_validations();require_all_validations(r)"
        subprocess.run([sys.executable,"-c",code],cwd=ROOT,check=True,capture_output=True,text=True)
    elif c["id"]=="manta":
        code="import sys;sys.path.insert(0,'.');from src.manta.programmable_matter import MantaEngine;m=MantaEngine();[m.step() for _ in range(100)];assert m.telemetry()['geometry_nodes']==125"
        subprocess.run([sys.executable,"-c",code],cwd=ROOT,check=True,capture_output=True,text=True)
    elif c["id"]=="aetheris":
        code="import aetheris;assert aetheris.RUNTIME_VERSION"
        subprocess.run([sys.executable,"-c",code],cwd=ROOT,check=True,capture_output=True,text=True)
    detail["benchmark_ms"]=round((time.perf_counter()-t)*1000,3)
    detail["benchmark_scope"]="software microbenchmark; no physical-performance claim"
    return detail
def receipt(c):
    cfg=contract(c)
    return {"schema":"LAB-PROVENANCE-RECEIPT-1.0","component":c["id"],"version":c["version"],"kind":c["kind"],"maturity":c["maturity"],"evidence":c["evidence"],"timestamp_utc":now(),"source_digest_sha256":digest(cfg["provenance"]),"provenance":cfg["provenance"],"contract_file":c["contract_file"]}
def run_one(c,op):
    t=time.perf_counter()
    try:
        detail={"smoke":smoke,"benchmark":benchmark,"receipt":receipt}[op](c)
        out={"schema":"LAB-OPERATION-1.0","component":c["id"],"version":c["version"],"operation":op,"status":"pass","timestamp_utc":now(),"duration_ms":round((time.perf_counter()-t)*1000,3),"detail":detail}
        print(json.dumps(out,separators=(",",":")))
        return 0
    except Exception as e:
        emit_failure(c,op,t,e); return 1
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("operation",choices=["smoke","benchmark","receipt"])
    ap.add_argument("component",nargs="?",default=None)
    ap.add_argument("--all",action="store_true")
    a=ap.parse_args(); _,cs=load()
    if a.all:
        return max(run_one(c,a.operation) for c in cs.values())
    if not a.component or a.component not in cs:
        ap.error("provide a component id or --all")
    return run_one(cs[a.component],a.operation)
if __name__=="__main__": raise SystemExit(main())
