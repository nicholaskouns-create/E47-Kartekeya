#!/usr/bin/env python3
"""DENSITY: Quantum Topography Visualised. Bundles SpectralEngine + TomographicVisualizer."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from spectral_engine import SpectralEngine
from tomographic_visualizer import (
    TomographicVisualizer,
    ANGLES_DEG,
    DOMAINS,
    radial_profile,
)

APP_TITLE = "DENSITY"
APP_SUBTITLE = "Quantum Topography Visualised"
APP_ID = "DENSITY / KKP-R / E47"


def _repo_artifacts() -> str:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "src").is_dir() and (p / "research").is_dir():
            d = p / "artifacts"
            d.mkdir(parents=True, exist_ok=True)
            return str(d)
    d = Path.cwd() / "artifacts"
    d.mkdir(parents=True, exist_ok=True)
    return str(d)


DEFAULT_OUT = _repo_artifacts()


class DensityApp:
    def __init__(self, n2: int = 97, n3: int = 49, n_iter: int = 8, out_dir: str = DEFAULT_OUT):
        self.spec = SpectralEngine()
        self.tomo = TomographicVisualizer(n2=n2, n3=n3, n_iter=n_iter, out_dir=out_dir)
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def run(self) -> "DensityApp":
        self.spec.validate()
        self.tomo.run()
        return self

    def report(self) -> str:
        s, t = self.spec, self.tomo
        m = t.metrics
        return "\n".join([
            f"{APP_TITLE}: {APP_SUBTITLE}",
            f"[ok] SPECTRAL ENGINE LOCKED",
            f"    dim H={s.dim_H}  dim E47={s.dim_kernel}  rank K={s.dim_complement}",
            f"    Omega_c={s.omega_c}=47/125  kappa={s.kappa:g}  rho=15/17",
            f"[ok] TOMOGRAPHY LOCKED",
            f"    grid {t.n2}x{t.n2} / {t.n3}^3   ART x {t.n_iter}",
            f"    rel L2={m['rel_l2']:.6f}  mass ratio={m['mass_ratio']:.6f}  MSE={m['mse']:.6e}",
        ])

    def render(self, filename: str = "Density_Quantum_Topography_Visualised.png") -> str:
        return self.tomo.render(filename)


def main() -> None:
    app = DensityApp().run()
    print(app.report())
    path = app.render()
    print(f"[ok] {path}")


if __name__ == "__main__":
    main()
