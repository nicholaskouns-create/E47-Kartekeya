"""Shared receipt/telemetry helper for autonomous Python instruments."""
from __future__ import annotations
import hashlib, json, os, platform, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

RECEIPT_SCHEMA="CITY-INSTRUMENT-RECEIPT/1.0"
FAILURE_SCHEMA="CITY-INSTRUMENT-FAILURE/1.0"

def _git_commit(root: Path) -> str | None:
    env=os.getenv("GITHUB_SHA")
    if env:
        return env
    try:
        return subprocess.check_output(
            ["git","rev-parse","HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None

def load_contract(path: Path) -> tuple[dict[str,Any], str]:
    raw=path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()

def emit_instrument_receipt(
    contract_path: Path,
    root: Path,
    run: Callable[[bool], tuple[list[dict[str,Any]], dict[str,Any]]],
    *,
    benchmark: bool=False,
    phase: str="smoke",
) -> int:
    contract, contract_hash=load_contract(contract_path)
    start=time.perf_counter()
    failure=None
    checks:list[dict[str,Any]]=[]
    metrics:dict[str,Any]={}
    status="PASS"
    try:
        checks, metrics=run(benchmark)
        if not all(bool(c.get("pass")) for c in checks):
            raise AssertionError("one or more instrument checks failed")
    except Exception as exc:
        status="FAIL"
        failure={
            "schema":FAILURE_SCHEMA,
            "component_id":contract["id"],
            "version":contract["version"],
            "phase":phase,
            "error_type":type(exc).__name__,
            "message":str(exc),
            "recoverable":False,
            "context":{"entrypoint":contract["smoke"]["entrypoint"]},
        }
    receipt={
        "schema":RECEIPT_SCHEMA,
        "component_id":contract["id"],
        "version":contract["version"],
        "mode":"benchmark" if benchmark else "smoke",
        "status":status,
        "timestamp_utc":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "duration_ms":round((time.perf_counter()-start)*1000,3),
        "git_commit":_git_commit(root),
        "contract_sha256":contract_hash,
        "runtime":{
            "language":"python",
            "python":platform.python_version(),
            "implementation":platform.python_implementation(),
            "platform":platform.platform(),
        },
        "checks":checks,
        "metrics":metrics,
        "failure":failure,
    }
    def _default(value):
        item=getattr(value,"item",None)
        if callable(item):
            try:return item()
            except Exception:pass
        return str(value)
    print(json.dumps(receipt, sort_keys=True, default=_default))
    return 0 if status=="PASS" else 1
