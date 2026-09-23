#!/usr/bin/env python3
"""KKP-R tomographic visualizer. Locked spectrum + ART + P47 gate."""
from __future__ import annotations
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List
import numpy as np
from scipy.ndimage import rotate, gaussian_filter

OMEGA_C = 47.0 / 125.0
DIM_H, DIM_E47, DIM_PERP = 125, 47, 78
P47_NORMALIZER = 1_814_400.0
SPINS = np.array([0, 1, 2, 3, 4, 5, 6], dtype=int)
MULTIPLICITIES = np.array([1, 3, 5, 4, 3, 2, 1], dtype=int)
SECTOR_DIMS = MULTIPLICITIES * (2 * SPINS + 1)
CASIMIR = SPINS * (SPINS + 1)
MU = (CASIMIR - 6) * (CASIMIR - 30)
KERNEL_MASK = MU == 0
DOMAINS: List[str] = ["RAND/Policy", "Defense", "MITRE", "Space", "Health", "AI", "Resilience", "Public Safety"]
ANGLES_DEG = np.arange(0.0, 360.0, 45.0)

def P_47(C):
    C = np.asarray(C, dtype=float)
    return (C - 31.0) * C * (C - 2.0) * (C - 12.0) * (C - 20.0) * (C - 42.0) / P47_NORMALIZER

def _lock_spectrum() -> None:
    assert DIM_H == 125 and DIM_E47 == 47 and DIM_PERP == 78
    assert np.array_equal(SECTOR_DIMS, [1, 9, 25, 28, 27, 22, 13])
    assert int(np.sum(SECTOR_DIMS[KERNEL_MASK])) == 47
    assert abs(OMEGA_C - 0.376) < 1e-12
    assert np.allclose(P_47(CASIMIR.astype(float)), [0, 0, 1, 0, 0, 1, 0])


def lambda_p47_matrix() -> np.ndarray:
    """Full 125x125 tomographic P47 gate from the canonical Lambda binding."""
    from e47.lexical_spine import canonical_lambda_matrix
    return canonical_lambda_matrix()


def project_e47_state(state) -> np.ndarray:
    """Apply the canonical full-state tomographic gate without changing ART logic."""
    from e47.lexical_spine import project_e47_state as _project
    return _project(state)

def _grid2(n: int):
    c = (n - 1) / 2.0
    y, x = np.indices((n, n), dtype=float)
    x, y = (x - c) / c, (y - c) / c
    return x, y, np.sqrt(x * x + y * y)

def _grid3(n: int):
    c = (n - 1) / 2.0
    z, y, x = np.indices((n, n, n), dtype=float)
    x, y, z = (x - c) / c, (y - c) / c, (z - c) / c
    return x, y, z, np.sqrt(x * x + y * y + z * z)

def coherence_phantom_2d(n: int = 129, seed: int = 47) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x, y, r = _grid2(n)
    core = OMEGA_C * np.exp(-(r / 0.22) ** 2)
    ring = 0.18 * np.exp(-((r - 0.48) / 0.06) ** 2)
    beads = np.zeros((n, n), dtype=float)
    for k, ang in enumerate(ANGLES_DEG):
        th = np.deg2rad(ang)
        cx, cy = 0.48 * np.cos(th), 0.48 * np.sin(th)
        amp = 0.10 + 0.08 * (SECTOR_DIMS[k % len(SECTOR_DIMS)] / 28.0)
        beads += amp * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (0.055 ** 2))
    speckle = gaussian_filter(0.04 * rng.standard_normal((n, n)), sigma=1.2) * (r < 0.92)
    return np.clip((core + ring + beads + speckle) * (r <= 1.0), 0.0, None)

def coherence_volume_3d(n: int = 65, seed: int = 47) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x, y, z, r = _grid3(n)
    rho = np.sqrt(x * x + y * y)
    core = OMEGA_C * np.exp(-(r / 0.24) ** 2)
    torus = 0.16 * np.exp(-(((rho - 0.46) ** 2 + z ** 2) / (0.07 ** 2)))
    beads = np.zeros((n, n, n), dtype=float)
    for k, ang in enumerate(ANGLES_DEG):
        th = np.deg2rad(ang)
        cx, cy = 0.46 * np.cos(th), 0.46 * np.sin(th)
        amp = 0.09 + 0.07 * (SECTOR_DIMS[k % len(SECTOR_DIMS)] / 28.0)
        d2 = (x - cx) ** 2 + (y - cy) ** 2 + (z - 0.08 * np.sin(2 * th)) ** 2
        beads += amp * np.exp(-d2 / (0.06 ** 2))
    speckle = gaussian_filter(0.03 * rng.standard_normal((n, n, n)), sigma=0.9)
    return np.clip((core + torus + beads + speckle) * (r <= 1.0), 0.0, None)

def radon_forward(image, angles_deg):
    sino = np.empty((len(angles_deg), image.shape[0]), dtype=float)
    for i, ang in enumerate(angles_deg):
        sino[i] = rotate(image, -ang, reshape=False, order=3, mode="constant", cval=0.0).sum(axis=0)
    return sino

def art_reconstruct(sino, angles_deg, n_iter=12, relax=0.35):
    n = sino.shape[1]
    recon = np.zeros((n, n), dtype=float)
    for _ in range(n_iter):
        acc = np.zeros_like(recon)
        for i, ang in enumerate(angles_deg):
            rot = rotate(recon, -ang, reshape=False, order=3, mode="constant", cval=0.0)
            rot = rot + (relax * (sino[i] - rot.sum(axis=0)) / float(n))[None, :]
            acc += rotate(rot, ang, reshape=False, order=3, mode="constant", cval=0.0)
        recon = np.clip(acc / len(angles_deg), 0.0, None)
    return recon

def coherence_gate(field, threshold=OMEGA_C):
    return field * (1.0 / (1.0 + np.exp(-18.0 * (field - threshold))))

def radial_profile(field, nbins=48):
    _, _, r = _grid2(field.shape[0])
    bins = np.linspace(0.0, 1.0, nbins + 1)
    idx = np.digitize(r.ravel(), bins) - 1
    f = field.ravel()
    prof = np.array([f[idx == i].mean() if np.any(idx == i) else 0.0 for i in range(nbins)])
    return 0.5 * (bins[:-1] + bins[1:]), prof

def quality_metrics(truth, recon, gated):
    nrm = float(np.linalg.norm(truth)) + 1e-12
    return {"mse": float(np.mean((recon - truth) ** 2)), "rel_l2": float(np.linalg.norm(recon - truth) / nrm), "mass_ratio": float(recon.sum() / (truth.sum() + 1e-12)), "omega_c": OMEGA_C, "dim_E47": float(DIM_E47), "dim_H": float(DIM_H)}

@dataclass
class TomographicVisualizer:
    n2: int = 129
    n3: int = 65
    n_iter: int = 12
    seed: int = 47
    out_dir: str = ""
    truth_2d: np.ndarray = field(init=False, repr=False)
    volume: np.ndarray = field(init=False, repr=False)
    sino: np.ndarray = field(init=False, repr=False)
    recon: np.ndarray = field(init=False, repr=False)
    gated: np.ndarray = field(init=False, repr=False)
    metrics: Dict[str, float] = field(init=False, default_factory=dict)
    def __post_init__(self) -> None:
        _lock_spectrum()
        if not self.out_dir:
            here = Path(__file__).resolve()
            out = None
            for p in here.parents:
                if (p / "src").is_dir() and (p / "research").is_dir():
                    out = p / "artifacts"
                    break
            self.out_dir = str(out or (Path.cwd() / "artifacts"))
        os.makedirs(self.out_dir, exist_ok=True)
    def run(self) -> "TomographicVisualizer":
        self.truth_2d = coherence_phantom_2d(self.n2, seed=self.seed)
        self.volume = coherence_volume_3d(self.n3, seed=self.seed)
        self.sino = radon_forward(self.truth_2d, ANGLES_DEG)
        recon_angles = np.linspace(0.0, 180.0, 24, endpoint=False)
        recon = art_reconstruct(radon_forward(self.truth_2d, recon_angles), recon_angles, n_iter=self.n_iter, relax=0.55)
        self.recon = recon * (float(self.truth_2d.max()) / (float(recon.max()) + 1e-12))
        self.gated = coherence_gate(self.recon)
        self.metrics = quality_metrics(self.truth_2d, self.recon, self.gated)
        return self
    def slices_3d(self):
        v, c = self.volume, self.volume.shape[0] // 2
        return {"XY": v[c, :, :], "XZ": v[:, c, :], "YZ": v[:, :, c]}
    def report(self) -> str:
        m = self.metrics
        return f"[ok] TOMO LOCKED  Omega_c={OMEGA_C}  relL2={m.get('rel_l2', float('nan')):.6f}"
    def render(self, filename: str = "KKP_R_Tomographic_Visualizer.png") -> str:
        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(2, 3, figsize=(12, 8), facecolor="#0B0F19")
        panels = [(self.truth_2d, "truth"), (self.recon, "ART"), (self.gated, "P47 gate"), (self.slices_3d()["XY"], "XY"), (self.sino, "sinogram"), (np.abs(self.recon - self.truth_2d), "residual")]
        for ax, (img, title) in zip(axes.ravel(), panels):
            ax.imshow(img, origin="lower", cmap="magma"); ax.set_title(title, color="#E2E8F0"); ax.set_xticks([]); ax.set_yticks([]); ax.set_facecolor("#111827")
        path = os.path.join(self.out_dir, filename)
        fig.savefig(path, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
        return path

def run_visualizer(**kwargs):
    eng = TomographicVisualizer(**kwargs).run()
    print(eng.report()); print("[ok] wrote", eng.render()); return eng

if __name__ == "__main__":
    run_visualizer()
