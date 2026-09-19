from __future__ import annotations
import argparse
from pathlib import Path
from scripts.instrument_runtime import emit_instrument_receipt
from .validation_results import run_all_validations

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=Path(__file__).with_name("component.json")

def run(benchmark: bool):
    results=run_all_validations()
    summary=results.summarize()
    checks=[
        {"name":"aggregate_validation","pass":bool(results.valid),"observed":bool(results.valid),"expected":True},
        {"name":"carrier_dimension","pass":results.qutip_validation.carrier_dimension==125,"observed":results.qutip_validation.carrier_dimension,"expected":125},
        {"name":"kernel_dimension","pass":results.qutip_validation.kernel_dimension==47,"observed":results.qutip_validation.kernel_dimension,"expected":47},
        {"name":"k2_spectral_gap","pass":results.qutip_validation.k2_spectral_gap==11664,"observed":results.qutip_validation.k2_spectral_gap,"expected":11664},
    ]
    metrics={
        "projector_rank":summary["projector_rank"],
        "projector_trace":summary["projector_trace"],
        "coherence_fraction":summary["coherence_fraction"],
        "benchmark_scope":"full-five-layer-validation" if benchmark else "full-five-layer-validation"
    }
    return checks,metrics

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--benchmark",action="store_true")
    args=ap.parse_args()
    raise SystemExit(emit_instrument_receipt(CONTRACT,ROOT,run,benchmark=args.benchmark,phase="e47-validation"))

if __name__=="__main__":
    main()
