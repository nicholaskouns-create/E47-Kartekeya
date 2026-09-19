from __future__ import annotations
import argparse, time
from pathlib import Path
from scripts.instrument_runtime import emit_instrument_receipt
from .model import StatePacket
from .modules import IdentityModule
from .runtime import AetherisRuntime, RUNTIME_VERSION

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=Path(__file__).with_name("component.json")

def execute_once():
    runtime=AetherisRuntime()
    runtime.register(IdentityModule())
    packet=StatePacket(kind="instrument.smoke",payload={"x":7,"runtime":RUNTIME_VERSION})
    return runtime.execute(packet,["aetheris.identity"],run_label="component-smoke")

def run(benchmark: bool):
    first=execute_once()
    second=execute_once()
    iterations=250 if benchmark else 1
    t0=time.perf_counter()
    for _ in range(iterations):
        execute_once()
    elapsed=time.perf_counter()-t0
    checks=[
        {"name":"certificate_status","pass":first.certificate.status=="PASS","observed":first.certificate.status,"expected":"PASS"},
        {"name":"deterministic_certificate","pass":first.certificate.digest==second.certificate.digest,"observed":first.certificate.digest,"expected":second.certificate.digest},
        {"name":"runtime_version","pass":RUNTIME_VERSION=="0.1.0","observed":RUNTIME_VERSION,"expected":"0.1.0"}
    ]
    metrics={
        "pipeline":["aetheris.identity"],
        "iterations":iterations,
        "executions_per_second":round(iterations/elapsed,3) if elapsed else None,
        "certificate_digest":first.certificate.digest
    }
    return checks,metrics

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--benchmark",action="store_true")
    args=ap.parse_args()
    raise SystemExit(emit_instrument_receipt(CONTRACT,ROOT,run,benchmark=args.benchmark,phase="aetheris-runtime"))

if __name__=="__main__":
    main()
