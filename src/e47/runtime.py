"""Wire spectral engine, intertwiners, Chevalley lock, Eidolon ODE, tomography."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VAL = REPO / "research" / "e47" / "validation"
EID = REPO / "src" / "eidolon"
for p in (str(VAL), str(EID), str(REPO / "src" / "e47"), str(REPO / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)


def load_stack() -> dict:
    from spectral_engine import SpectralEngine
    from intertwiners import N_UNITS, lock as lock_intertwiners
    from chevalley import FAIL, PASS, verify
    from eidolon_engine import Craft, EidolonEngine, assert_lock
    from tomographic_visualizer import TomographicVisualizer, _lock_spectrum

    spec = SpectralEngine()
    spec.validate()
    assert_lock()
    _lock_spectrum()
    lock_intertwiners()
    PASS.clear()
    FAIL.clear()
    verify()
    return {
        "spectral": spec,
        "n_units": N_UNITS,
        "eidolon": EidolonEngine,
        "craft": Craft,
        "tomo": TomographicVisualizer,
        "omega_c": spec.omega_c,
        "dim_e47": spec.dim_kernel,
    }


def smoke() -> None:
    stack = load_stack()
    spec = stack["spectral"]
    eng = stack["eidolon"](stack["craft"](mode="acquire"), dt=1.0, duration=4.0).run()
    print(f"SPECTRAL  dim H={spec.dim_H}  dim E47={spec.dim_kernel}  Ω_c={spec.omega_c}")
    print(f"INTERTWINERS  n={stack['n_units']}")
    print(f"EIDOLON  L={eng.lock():.6f}  samples={len(eng.history)}")
    print("STACK LOCKED")


if __name__ == "__main__":
    smoke()
