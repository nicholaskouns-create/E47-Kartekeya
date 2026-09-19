from __future__ import annotations
import argparse, time
from pathlib import Path
import numpy as np
from scripts.instrument_runtime import emit_instrument_receipt
from . import MANTA_VERSION
from .programmable_matter import MantaEngine, MorphMode, PilotInput

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=Path(__file__).with_name("component.json")

def run(benchmark: bool):
    engine=MantaEngine(seed=470125)
    pilot=PilotInput(pitch=.1,roll=.15,morph=.55)
    initial=engine.telemetry()
    steps=300 if benchmark else 8
    t0=time.perf_counter()
    for _ in range(steps):
        engine.step(pilot,MorphMode.TRANSITION)
    elapsed=time.perf_counter()-t0
    final=engine.telemetry()
    geometry=engine.geometry()
    checks=[
        {"name":"version","pass":MANTA_VERSION=="0.1.0","observed":MANTA_VERSION,"expected":"0.1.0"},
        {"name":"carrier_dimension","pass":final["carrier_dimension"]==125,"observed":final["carrier_dimension"],"expected":125},
        {"name":"kernel_dimension","pass":final["kernel_dimension"]==47,"observed":final["kernel_dimension"],"expected":47},
        {"name":"geometry_nodes","pass":geometry.shape==(125,3),"observed":list(geometry.shape),"expected":[125,3]},
        {"name":"finite_geometry","pass":bool(np.isfinite(geometry).all()),"observed":bool(np.isfinite(geometry).all()),"expected":True},
        {"name":"capture_non_decreasing","pass":final["e47_capture"]>=initial["e47_capture"]-1e-12,"observed":final["e47_capture"],"expected":f">={initial['e47_capture']}"}
    ]
    metrics={
        "steps":steps,
        "steps_per_second":round(steps/elapsed,3) if elapsed else None,
        "initial_capture":initial["e47_capture"],
        "final_capture":final["e47_capture"],
        "residual":final["residual"],
        "geometry_nodes":final["geometry_nodes"]
    }
    return checks,metrics

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--benchmark",action="store_true")
    args=ap.parse_args()
    raise SystemExit(emit_instrument_receipt(CONTRACT,ROOT,run,benchmark=args.benchmark,phase="manta-simulation"))

if __name__=="__main__":
    main()
