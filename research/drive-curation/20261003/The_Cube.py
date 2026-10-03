#!/usr/bin/env python3
"""
THE CUBE
========
A single-file Streamlit educational app for geometric computation across the
user's corpus: Professor's Cube / C5^3 permutation algebra, E47 spectral
projection, S3 bridge, HBr Morse formalism, hyperbolic-fractal / Buoy geometry,
and a 4D tesseract visualizer.

Run:
    pip install streamlit plotly numpy
    streamlit run The_Cube.py

Optional arbitrary 3x3 facelet solving:
    pip install kociemba

Self-test (does not require Streamlit or Plotly):
    python The_Cube.py --self-test

Evidence discipline:
- E47 finite-dimensional SU(2) construction and K^2 contraction are exact / E1
  numerical reconstruction targets.
- C5^3 Laplacian has a rank-one constant kernel. It is NOT E47. The exact shared
  bridge used here is the S3 factor-permutation symmetry on the common 125-state
  carrier.
- HBr is implemented as the corpus Morse oscillator / local coherence example.
- The 4D tesseract is an educational high-dimensional visualizer; it is not
  asserted to be a physical carrier for E47.
"""

from __future__ import annotations

import sys
import math
import itertools
import random
from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

APP_TITLE = "The Cube"
OMEGA_E47 = 47 / 125

# -----------------------------------------------------------------------------
# 1. Exact spin-2 SU(2) / E47 machinery
# -----------------------------------------------------------------------------

def spin_matrices(j: int = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return Jx, Jy, Jz in descending m basis for integer/half-integer j."""
    m = np.arange(j, -j - 1, -1, dtype=float)
    d = len(m)
    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((d, d), dtype=complex)
    # basis indices: m[i] > m[i+1]. Raising maps |m> -> |m+1>.
    for col, mm in enumerate(m):
        mp = mm + 1
        if mp > j:
            continue
        rows = np.where(np.isclose(m, mp))[0]
        if rows.size:
            row = int(rows[0])
            Jp[row, col] = math.sqrt(j * (j + 1) - mm * (mm + 1))
    Jm = Jp.conj().T
    Jx = (Jp + Jm) / 2
    Jy = (Jp - Jm) / (2j)
    return Jx, Jy, Jz


def kron3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.kron(np.kron(a, b), c)


@lru_cache(maxsize=1)
def e47_system() -> Dict[str, np.ndarray | float | List[Tuple[float, int]]]:
    Jx, Jy, Jz = spin_matrices(2)
    I5 = np.eye(5, dtype=complex)
    Jtot = []
    for J in (Jx, Jy, Jz):
        Jtot.append(kron3(J, I5, I5) + kron3(I5, J, I5) + kron3(I5, I5, J))
    C = sum(J @ J for J in Jtot)
    C = (C + C.conj().T) / 2
    I = np.eye(125, dtype=complex)
    K = (C - 6 * I) @ (C - 30 * I)
    K = (K + K.conj().T) / 2
    K2 = K @ K
    w, U = np.linalg.eigh(C)
    mask = np.isclose(w, 6.0, atol=1e-8) | np.isclose(w, 30.0, atol=1e-8)
    V = U[:, mask]
    P47 = V @ V.conj().T
    P47 = (P47 + P47.conj().T) / 2
    spec = []
    for val in [0, 2, 6, 12, 20, 30, 42]:
        spec.append((float(val), int(np.sum(np.isclose(w, val, atol=1e-8)))))
    k2_vals = np.linalg.eigvalsh(K2)
    pos = k2_vals[k2_vals > 1e-7]
    return {
        "C": C,
        "K": K,
        "K2": K2,
        "P47": P47,
        "casimir_spectrum": spec,
        "rank": float(np.real(np.trace(P47))),
        "gap": float(pos.min()),
        "norm_k2": float(k2_vals.max()),
    }


def optimal_e47_epsilon() -> float:
    """Canonical minimax step from the E47 spectrum: 1/99144."""
    return 1 / 99144


def e47_contraction_curve(steps: int = 80, seed: int = 47) -> Tuple[np.ndarray, np.ndarray]:
    sys47 = e47_system()
    K2 = sys47["K2"]
    P = sys47["P47"]
    eps = optimal_e47_epsilon()
    rng = np.random.default_rng(seed)
    x0 = rng.normal(size=125) + 1j * rng.normal(size=125)
    x0 = x0 / np.linalg.norm(x0)
    target = P @ x0
    x = x0.copy()
    errs = [np.linalg.norm(x - target)]
    for _ in range(steps):
        x = x - eps * (K2 @ x)
        errs.append(np.linalg.norm(x - target))
    return np.arange(steps + 1), np.array(errs)


# -----------------------------------------------------------------------------
# 2. C5^3 carrier, Laplacian, Professor's Cube moves
# -----------------------------------------------------------------------------

def idx5(x: int, y: int, z: int) -> int:
    return 25 * x + 5 * y + z


def unidx5(i: int) -> Tuple[int, int, int]:
    return i // 25, (i % 25) // 5, i % 5


@lru_cache(maxsize=1)
def c5_laplacian() -> np.ndarray:
    A = np.zeros((5, 5), dtype=float)
    for i in range(5):
        A[i, (i - 1) % 5] = 1
        A[i, (i + 1) % 5] = 1
    L5 = 2 * np.eye(5) - A
    I5 = np.eye(5)
    return np.kron(np.kron(L5, I5), I5) + np.kron(np.kron(I5, L5), I5) + np.kron(np.kron(I5, I5), L5)


def _rot2(a: int, b: int, direction: int) -> Tuple[int, int]:
    """Quarter-turn around center 2 on a 0..4 coordinate square."""
    # +1: (a,b)->(b,4-a), -1 inverse.
    return (b, 4 - a) if direction > 0 else (4 - b, a)


def rotate_point_layer(p: Tuple[int, int, int], axis: str, layer: int, direction: int) -> Tuple[int, int, int]:
    x, y, z = p
    if axis == "x" and x == layer:
        y, z = _rot2(y, z, direction)
    elif axis == "y" and y == layer:
        z, x = _rot2(z, x, direction)
    elif axis == "z" and z == layer:
        x, y = _rot2(x, y, direction)
    return x, y, z


# Canonical 15 quarter-turn labels used by the user's Professor's Cube formalism.
MOVE_SPECS: Dict[str, Tuple[str, int, int]] = {
    "R": ("x", 4, +1), "R2": ("x", 3, +1), "M": ("x", 2, -1), "L2": ("x", 1, -1), "L": ("x", 0, -1),
    "U": ("y", 4, +1), "U2": ("y", 3, +1), "E": ("y", 2, -1), "D2": ("y", 1, -1), "D": ("y", 0, -1),
    "F": ("z", 4, +1), "F2": ("z", 3, +1), "S": ("z", 2, +1), "B2": ("z", 1, -1), "B": ("z", 0, -1),
}


def move_permutation(name: str, inverse: bool = False) -> np.ndarray:
    axis, layer, direction = MOVE_SPECS[name]
    if inverse:
        direction *= -1
    perm = np.empty(125, dtype=int)
    for i in range(125):
        p2 = rotate_point_layer(unidx5(i), axis, layer, direction)
        perm[i] = idx5(*p2)
    return perm


def permutation_matrix(perm: np.ndarray) -> np.ndarray:
    P = np.zeros((len(perm), len(perm)), dtype=float)
    # state at old i moves to new perm[i]
    P[perm, np.arange(len(perm))] = 1.0
    return P


def apply_move_to_labels(labels: np.ndarray, name: str, inverse: bool = False) -> np.ndarray:
    perm = move_permutation(name, inverse=inverse)
    out = np.empty_like(labels)
    out[perm] = labels
    return out


def inverse_word(word: Sequence[str]) -> List[Tuple[str, bool]]:
    return [(name, True) for name in reversed(word)]


def apply_word_labels(word: Sequence[Tuple[str, bool]], labels: np.ndarray | None = None) -> np.ndarray:
    if labels is None:
        labels = np.arange(125)
    state = labels.copy()
    for name, inv in word:
        state = apply_move_to_labels(state, name, inverse=inv)
    return state


def parse_professor_word(text: str) -> List[Tuple[str, bool]]:
    """Parse canonical move word. Apostrophe means inverse. R2 is an inner-layer label, not 180°."""
    toks = [t.strip() for t in text.replace(",", " ").split() if t.strip()]
    out = []
    for tok in toks:
        inv = tok.endswith("'")
        name = tok[:-1] if inv else tok
        if name not in MOVE_SPECS:
            raise ValueError(f"Unknown move {tok!r}. Allowed: {', '.join(MOVE_SPECS)} plus apostrophe for inverse.")
        out.append((name, inv))
    return out


def format_word(word: Sequence[Tuple[str, bool]]) -> str:
    return " ".join(name + ("'" if inv else "") for name, inv in word)


def professor_scramble(length: int = 14, seed: int | None = None) -> List[Tuple[str, bool]]:
    rng = random.Random(seed)
    names = list(MOVE_SPECS)
    out: List[Tuple[str, bool]] = []
    last_axis = None
    for _ in range(length):
        candidates = [n for n in names if MOVE_SPECS[n][0] != last_axis] or names
        n = rng.choice(candidates)
        out.append((n, bool(rng.getrandbits(1))))
        last_axis = MOVE_SPECS[n][0]
    return out


# -----------------------------------------------------------------------------
# 3. S3 factor-permutation bridge
# -----------------------------------------------------------------------------

def factor_perm_map(sigma: Tuple[int, int, int]) -> np.ndarray:
    """Permutation of coordinates/factors. sigma gives output coordinate source order."""
    perm = np.empty(125, dtype=int)
    for i in range(125):
        p = unidx5(i)
        q = (p[sigma[0]], p[sigma[1]], p[sigma[2]])
        perm[i] = idx5(*q)
    return perm


def all_s3_permutation_matrices() -> List[np.ndarray]:
    return [permutation_matrix(factor_perm_map(s)) for s in itertools.permutations((0, 1, 2))]


@lru_cache(maxsize=1)
def s3_projectors() -> Dict[str, np.ndarray]:
    mats = all_s3_permutation_matrices()
    Psym = sum(mats) / 6.0
    # parity sign for permutations
    def parity(s):
        inv = sum(1 for i in range(3) for j in range(i + 1, 3) if s[i] > s[j])
        return -1 if inv % 2 else 1
    Panti = np.zeros((125, 125), dtype=float)
    for s, M in zip(itertools.permutations((0, 1, 2)), mats):
        Panti += parity(s) * M / 6.0
    Pstd = np.eye(125) - Psym - Panti
    return {"sym": Psym, "anti": Panti, "std": Pstd}


def bridge_diagnostics() -> Dict[str, float]:
    e = e47_system()
    C = np.real_if_close(e["C"])
    P47 = np.real_if_close(e["P47"])
    L = c5_laplacian()
    U = all_s3_permutation_matrices()[1:]
    commC = max(np.linalg.norm(C @ u - u @ C, 2) for u in U)
    commL = max(np.linalg.norm(L @ u - u @ L, 2) for u in U)
    commP = max(np.linalg.norm(P47 @ u - u @ P47, 2) for u in U)
    Psym = s3_projectors()["sym"]
    # C=6 spectral projector from eigendecomposition
    w, V = np.linalg.eigh(np.real_if_close(C))
    V6 = V[:, np.isclose(w, 6, atol=1e-8)]
    P6 = V6 @ V6.T
    Pcan = P6 @ Psym
    Pcan = (Pcan + Pcan.T) / 2
    rank_can = int(np.sum(np.linalg.eigvalsh(Pcan) > 0.5))
    return {"[C,S3]": float(commC), "[L,S3]": float(commL), "[P47,S3]": float(commP), "rank_Pcan": rank_can}


# -----------------------------------------------------------------------------
# 4. HBr Morse oscillator / local coherence formalism
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class HBrParameters:
    D_e_eV: float = 3.79
    E0_eV: float = 0.164
    omega_e_cm: float = 2648.975
    omega_exe_cm: float = 45.2175
    r_e_A: float = 1.414  # display/reference equilibrium bond length; adjustable in app
    a_invA: float = 1.80  # visualization stiffness; adjustable in app


def hbr_quantities(p: HBrParameters = HBrParameters()) -> Dict[str, float]:
    local = p.E0_eV / p.D_e_eV
    margin = (p.D_e_eV - p.E0_eV) / p.E0_eV
    phi = (1 + math.sqrt(5)) / 2
    psi_univ = phi ** -2
    r_univ = 78 / 47
    omega_c = 1 / (1 + r_univ)
    return {
        "Omega_HBr": local,
        "r_HBr": margin,
        "phi": phi,
        "psi_univ": psi_univ,
        "r_univ": r_univ,
        "Omega_c": omega_c,
    }


def morse_potential(r_A: np.ndarray, p: HBrParameters) -> np.ndarray:
    return p.D_e_eV * (1 - np.exp(-p.a_invA * (r_A - p.r_e_A))) ** 2


def morse_levels_cm(n: np.ndarray, p: HBrParameters) -> np.ndarray:
    q = n + 0.5
    return p.omega_e_cm * q - p.omega_exe_cm * q**2


# -----------------------------------------------------------------------------
# 5. Hyperbolic geometry, fractal recursion, Buoy residual
# -----------------------------------------------------------------------------

def poincare_distance(z: complex, w: complex, kappa: float = 1.0) -> float:
    ratio = abs((z - w) / (1 - np.conj(z) * w))
    ratio = min(max(float(ratio), 0.0), 1 - 1e-14)
    return (2 / kappa) * np.arctanh(ratio)


def disk_isometry(z: complex, a: complex, theta: float = 0.0) -> complex:
    """Orientation-preserving Poincare disk isometry."""
    return np.exp(1j * theta) * (z - a) / (1 - np.conj(a) * z)


def fractal_points(depth: int = 7, ratio: float = 0.36) -> np.ndarray:
    """A bounded 3-map recursive set inside the disk, used as an educational scale-semigroup visualizer."""
    centers = 0.52 * np.exp(1j * np.array([0, 2*np.pi/3, 4*np.pi/3]))
    pts = np.array([0j])
    for _ in range(depth):
        pts = np.concatenate([c + ratio * pts for c in centers])
    return pts[np.abs(pts) < 0.995]


def buoy_error_bound(eta: float, q: float, n: int) -> float:
    if not (0 <= q < 1):
        return float("inf")
    return eta * (1 - q**n) / (1 - q)


# -----------------------------------------------------------------------------
# 6. 4D tesseract geometry
# -----------------------------------------------------------------------------

def tesseract_vertices() -> np.ndarray:
    return np.array(list(itertools.product((-1.0, 1.0), repeat=4)), dtype=float)


def tesseract_edges() -> List[Tuple[int, int]]:
    V = tesseract_vertices()
    edges = []
    for i in range(len(V)):
        for j in range(i + 1, len(V)):
            if np.sum(V[i] != V[j]) == 1:
                edges.append((i, j))
    return edges


def rot4(theta: float, plane: Tuple[int, int]) -> np.ndarray:
    R = np.eye(4)
    i, j = plane
    c, s = np.cos(theta), np.sin(theta)
    R[i, i] = c; R[j, j] = c
    R[i, j] = -s; R[j, i] = s
    return R


def tesseract_projection(theta: float) -> np.ndarray:
    V = tesseract_vertices()
    R = rot4(theta, (0, 3)) @ rot4(0.73 * theta, (1, 2)) @ rot4(0.37 * theta, (0, 1))
    X = V @ R.T
    # perspective 4D -> 3D
    d = 3.2
    denom = d - X[:, 3]
    return X[:, :3] / denom[:, None]


# -----------------------------------------------------------------------------
# 7. Self-test certificate
# -----------------------------------------------------------------------------

def self_test(verbose: bool = True) -> Dict[str, object]:
    checks = []
    e = e47_system()
    P = e["P47"]; K = e["K"]; K2 = e["K2"]
    checks.append(("E47 rank 47", abs(np.trace(P).real - 47) < 1e-8, float(np.trace(P).real)))
    checks.append(("P47 idempotent", np.linalg.norm(P @ P - P) < 1e-10, float(np.linalg.norm(P @ P - P))))
    checks.append(("K annihilates P47", np.linalg.norm(K @ P) < 1e-9, float(np.linalg.norm(K @ P))))
    checks.append(("K2 gap 11664", abs(float(e["gap"]) - 11664) < 1e-5, float(e["gap"])))
    checks.append(("K2 norm 186624", abs(float(e["norm_k2"]) - 186624) < 1e-4, float(e["norm_k2"])))

    L = c5_laplacian()
    vals = np.linalg.eigvalsh(L)
    checks.append(("C5^3 kernel rank 1", int(np.sum(np.isclose(vals, 0, atol=1e-9))) == 1, int(np.sum(np.isclose(vals, 0, atol=1e-9)))))
    expected_gap = (5 - math.sqrt(5)) / 2
    pos = vals[vals > 1e-9]
    checks.append(("C5^3 gap", abs(pos.min() - expected_gap) < 1e-10, float(pos.min())))

    defect_norms = []
    for name in MOVE_SPECS:
        Q = permutation_matrix(move_permutation(name))
        checks.append((f"{name} orthogonal", np.linalg.norm(Q.T @ Q - np.eye(125)) < 1e-12, float(np.linalg.norm(Q.T @ Q - np.eye(125)))))
        checks.append((f"{name} order four", np.linalg.norm(np.linalg.matrix_power(Q, 4) - np.eye(125)) < 1e-12, float(np.linalg.norm(np.linalg.matrix_power(Q, 4) - np.eye(125)))))
        defect_norms.append(np.linalg.norm(Q.T @ L @ Q - L, 2))
    checks.append(("Layer defect spectral norm 2sqrt2", max(abs(d - 2*math.sqrt(2)) for d in defect_norms) < 1e-9, float(max(defect_norms))))

    bd = bridge_diagnostics()
    checks.append(("S3 commutes with C", bd["[C,S3]"] < 1e-10, bd["[C,S3]"]))
    checks.append(("S3 commutes with L", bd["[L,S3]"] < 1e-10, bd["[L,S3]"]))
    checks.append(("S3 commutes with P47", bd["[P47,S3]"] < 1e-10, bd["[P47,S3]"]))
    checks.append(("Canonical rank-5 descendant", bd["rank_Pcan"] == 5, bd["rank_Pcan"]))

    h = hbr_quantities()
    checks.append(("HBr exact ratio 82/1895", abs(h["Omega_HBr"] - 82/1895) < 1e-15, h["Omega_HBr"]))
    checks.append(("Universal ratio 47/125", abs(h["Omega_c"] - 47/125) < 1e-15, h["Omega_c"]))

    z, w = 0.17+0.11j, -0.27+0.19j
    a, th = 0.13-0.08j, 0.42
    d0 = poincare_distance(z, w)
    d1 = poincare_distance(disk_isometry(z, a, th), disk_isometry(w, a, th))
    checks.append(("Poincare isometry invariance", abs(d0-d1) < 1e-12, abs(d0-d1)))

    V4 = tesseract_vertices(); E4 = tesseract_edges()
    checks.append(("Tesseract 16 vertices", len(V4) == 16, len(V4)))
    checks.append(("Tesseract 32 edges", len(E4) == 32, len(E4)))

    passed = all(ok for _, ok, _ in checks)
    result = {"status": "PASS" if passed else "FAIL", "passed": sum(ok for _, ok, _ in checks), "total": len(checks), "checks": checks}
    if verbose:
        print("="*72)
        print("THE CUBE · SELF-TEST CERTIFICATE")
        print("="*72)
        for name, ok, val in checks:
            print(f"[{'PASS' if ok else 'FAIL'}] {name}: {val}")
        print("-"*72)
        print(f"STATUS: {result['status']} · {result['passed']}/{result['total']} checks")
    return result

# -----------------------------------------------------------------------------
# 8. Gradio application
# -----------------------------------------------------------------------------

def _plotly():
    import plotly.graph_objects as go
    return go


def professor_solver_figure(text: str):
    go = _plotly()
    word = parse_professor_word(text)
    sol = [(n, not inv) for n, inv in reversed(word)]
    solved = apply_word_labels(word + sol)
    residual = int(np.sum(solved != np.arange(125)))
    coords = np.array([unidx5(i) for i in range(125)], dtype=float)
    sequence = word + sol
    labels = np.arange(125)
    states = [labels.copy()]
    for n, inv in sequence:
        labels = apply_move_to_labels(labels, n, inv)
        states.append(labels.copy())
    frames = []
    for k, labels_k in enumerate(states):
        frames.append(go.Frame(
            data=[go.Scatter3d(
                x=coords[:, 0], y=coords[:, 1], z=coords[:, 2], mode="markers",
                marker=dict(size=6, color=labels_k, colorscale="Turbo", cmin=0, cmax=124, opacity=.92),
                text=[f"position {i} · cubie {int(labels_k[i])}" for i in range(125)],
                hoverinfo="text")], name=str(k)))
    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        height=620, margin=dict(l=0, r=0, t=30, b=0),
        scene=dict(aspectmode="cube", xaxis_title="x", yaxis_title="y", zaxis_title="z"),
        updatemenus=[dict(type="buttons", showactive=False, buttons=[
            dict(label="▶ Scramble + solve", method="animate",
                 args=[None, {"frame": {"duration": 180, "redraw": True}, "fromcurrent": True,
                              "transition": {"duration": 0}}]),
            dict(label="⏸ Pause", method="animate",
                 args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
        ])],
        sliders=[dict(
            steps=[dict(method="animate", args=[[str(i)], {"mode": "immediate",
                                                            "frame": {"duration": 0, "redraw": True}}],
                        label=str(i)) for i in range(len(frames))],
            currentvalue={"prefix": "step "})]
    )
    return "Solution: " + format_word(sol), f"Exact return residual: {residual}", fig


def random_scramble_text(length: int, seed: int) -> str:
    return format_word(professor_scramble(int(length), int(seed)))


def carrier_figure(move: str, inverse: bool):
    go = _plotly()
    perm = move_permutation(move, bool(inverse))
    coords0 = np.array([unidx5(i) for i in range(125)], float)
    coords1 = np.array([unidx5(perm[i]) for i in range(125)], float)
    frames = []
    for t in np.linspace(0, 1, 20):
        xyz = (1 - t) * coords0 + t * coords1
        frames.append(go.Frame(data=[go.Scatter3d(
            x=xyz[:, 0], y=xyz[:, 1], z=xyz[:, 2], mode="markers",
            marker=dict(size=6, color=np.arange(125), colorscale="Viridis"))], name=f"{t:.2f}"))
    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        height=600, scene=dict(aspectmode="cube"), margin=dict(l=0, r=0, t=20, b=0),
        updatemenus=[dict(type="buttons", buttons=[
            dict(label="▶ quarter-turn", method="animate",
                 args=[None, {"frame": {"duration": 45, "redraw": True},
                              "transition": {"duration": 0}}])])])
    L = c5_laplacian()
    Q = permutation_matrix(perm)
    d2 = np.linalg.norm(Q.T @ L @ Q - L, 2)
    stats = f"dim carrier = 125 · dim ker L = 1 · gap = {(5-math.sqrt(5))/2:.6f} · ||QᵀLQ-L||₂ = {d2:.6f}"
    return fig, stats


def e47_figures(seed: int):
    go = _plotly()
    e = e47_system()
    spec = e["casimir_spectrum"]
    vals = [x for x, _ in spec]
    mult = [m for _, m in spec]
    f1 = go.Figure(go.Bar(x=[str(v) for v in vals], y=mult, text=mult, textposition="outside"))
    f1.update_layout(height=380, xaxis_title="Casimir eigenvalue λ", yaxis_title="multiplicity",
                     title="C = J_tot² spectrum on V₂⊗³")
    steps, errs = e47_contraction_curve(100, int(seed))
    f2 = go.Figure(go.Scatter(x=steps, y=errs, mode="lines+markers", marker=dict(size=3)))
    f2.update_yaxes(type="log", title="||Γⁿx - P₄₇x||₂")
    f2.update_xaxes(title="iteration n")
    f2.update_layout(height=380, title="E47 contraction · ε*=1/99144 · target factor 15/17")
    stats = f"rank P47 = {e['rank']:.0f} · K² gap = {e['gap']:.0f} · ||K²|| = {e['norm_k2']:.0f} · Ωc = {OMEGA_E47:.3f}"
    return f1, f2, stats


def bridge_figure():
    go = _plotly()
    bd = bridge_diagnostics()
    vals = [bd["[C,S3]"], bd["[L,S3]"], bd["[P47,S3]"]]
    floor = 1e-18
    f = go.Figure(go.Bar(x=["[C,S3]", "[L,S3]", "[P47,S3]"], y=[max(v, floor) for v in vals]))
    f.update_yaxes(type="log", title="max operator-norm residual")
    f.update_layout(height=390)
    stats = f"Cube kernel = 1 · E47 kernel = 47 · rank(P6 Psym) = {bd['rank_Pcan']}"
    return f, stats


def hbr_figure(De: float, E0: float, re: float, aa: float):
    go = _plotly()
    p = HBrParameters(D_e_eV=float(De), E0_eV=float(E0), r_e_A=float(re), a_invA=float(aa))
    h = hbr_quantities(p)
    rr = np.linspace(max(.2, re - 1.0), re + 2.2, 500)
    V = morse_potential(rr, p)
    f = go.Figure()
    f.add_trace(go.Scatter(x=rr, y=V, name="Morse V(r)", mode="lines"))
    f.add_hline(y=E0, annotation_text="E₀")
    f.add_hline(y=De, annotation_text="Dₑ")
    f.update_layout(height=470, xaxis_title="bond coordinate r (Å)", yaxis_title="energy (eV)")
    stats = f"Ω_HBr = {h['Omega_HBr']:.8f} · local margin = {h['r_HBr']:.5f} · Ωc = {h['Omega_c']:.6f}"
    return f, stats


def hfbg_figure(depth: int, ratio: float, eta: float, q: float, n: int):
    go = _plotly()
    pts = fractal_points(int(depth), float(ratio))
    ang = np.linspace(0, 2 * np.pi, 500)
    f = go.Figure()
    f.add_trace(go.Scatter(x=np.cos(ang), y=np.sin(ang), mode="lines", name="Poincaré boundary"))
    f.add_trace(go.Scatter(x=pts.real, y=pts.imag, mode="markers",
                           marker=dict(size=5, color=np.abs(pts), colorscale="Plasma"), name="recursive set"))
    f.update_layout(height=520, yaxis=dict(scaleanchor="x", scaleratio=1),
                    xaxis_title="Re z", yaxis_title="Im z")
    z, w = 0.17 + 0.11j, -0.27 + 0.19j
    a, th = 0.13 - 0.08j, .42
    resid = abs(poincare_distance(z, w) -
                poincare_distance(disk_isometry(z, a, th), disk_isometry(w, a, th)))
    bound = buoy_error_bound(float(eta), float(q), int(n))
    stats = f"Buoy error tube = {bound:.6f} · Poincaré isometry residual = {resid:.3e}"
    return f, stats


def tesseract_figure():
    go = _plotly()
    edges = tesseract_edges()
    frames = []
    for k, th in enumerate(np.linspace(0, 2 * np.pi, 72)):
        X = tesseract_projection(th)
        xs, ys, zs = [], [], []
        for i, j in edges:
            xs += [X[i, 0], X[j, 0], None]
            ys += [X[i, 1], X[j, 1], None]
            zs += [X[i, 2], X[j, 2], None]
        frames.append(go.Frame(data=[
            go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(width=5), hoverinfo="skip"),
            go.Scatter3d(x=X[:, 0], y=X[:, 1], z=X[:, 2], mode="markers",
                         marker=dict(size=7, color=np.arange(16), colorscale="Turbo"))], name=str(k)))
    fig = go.Figure(data=frames[0].data, frames=frames)
    fig.update_layout(
        height=620, scene=dict(aspectmode="cube"), margin=dict(l=0, r=0, t=20, b=0),
        updatemenus=[dict(type="buttons", buttons=[
            dict(label="▶ Rotate in 4D", method="animate",
                 args=[None, {"frame": {"duration": 55, "redraw": True},
                              "transition": {"duration": 0}, "fromcurrent": True}]),
            dict(label="⏸", method="animate",
                 args=[[None], {"mode": "immediate", "frame": {"duration": 0}}])])])
    return fig


def certificate_markdown():
    r = self_test(verbose=False)
    lines = [f"# {r['status']} · {r['passed']}/{r['total']} checks", ""]
    for name, ok, val in r["checks"]:
        lines.append(("✅" if ok else "❌") + f" **{name}** · `{val}`")
    return "\n".join(lines)


def build_app():
    import gradio as gr
    css = """
    .gradio-container {max-width: 1500px !important;}
    .hero {border-radius:24px;padding:22px 26px;background:linear-gradient(135deg,#0b1025,#15162e);color:white;border:1px solid #383c78;margin-bottom:12px}
    .hero h1 {font-size:46px;margin:0 0 4px 0;letter-spacing:-1px}
    .hero p {font-size:17px;opacity:.86}
    """
    with gr.Blocks(title=APP_TITLE, css=css) as demo:
        gr.HTML("""<div class='hero'><div>GEOMETRIC COMPUTATION · 125 → 47 · QUANTUM → MACRO</div><h1>🧊 The Cube</h1><p>An animated Rubik / Professor's Cube solver-laboratory for E47, S3 symmetry, HBr Morse structure, hyperbolic-fractal Buoy dynamics and 4D tesseract projection.</p></div>""")
        seed = gr.Number(value=47, precision=0, label="Random seed")

        with gr.Tabs():
            with gr.Tab("🧩 Solve"):
                gr.Markdown("## Professor's Cube inverse-word solver\nExact group inversion on the canonical fifteen 5×5×5 layer-turn permutations.")
                with gr.Row():
                    slen = gr.Slider(1, 30, value=12, step=1, label="Scramble length")
                    sbtn = gr.Button("🎲 Generate scramble")
                    word = gr.Textbox(value="R U F M S E L2' D2", label="Canonical move word")
                sol = gr.Textbox(label="Solution")
                resid = gr.Textbox(label="Residual")
                plot = gr.Plot(label="Scramble + solve animation")
                sbtn.click(random_scramble_text, [slen, seed], word)
                gr.Button("Solve / refresh animation").click(professor_solver_figure, word, [sol, resid, plot])

            with gr.Tab("🧱 125 carrier"):
                gr.Markdown(r"""## Common 125-state carrier
\(\Sigma_5^3=\{0,1,2,3,4\}^3,\quad \pi(x,y,z)=25x+5y+z\).

The cube and E47 share ambient dimension and factor organization, not the same kernel.""")
                with gr.Row():
                    move = gr.Dropdown(list(MOVE_SPECS), value="R", label="Quarter-turn")
                    inv = gr.Checkbox(value=False, label="Inverse")
                    cbtn = gr.Button("Animate")
                cp = gr.Plot()
                cs = gr.Textbox(label="Operator diagnostics")
                cbtn.click(carrier_figure, [move, inv], [cp, cs])

            with gr.Tab("⚛️ E47"):
                gr.Markdown(r"""## E47 spectral selector
\(V=V_2^{\otimes3}\), \(K=(C-6I)(C-30I)\), \(E_{47}=\ker K\), \(P_{47}=P_6+P_{30}\), \(\Omega_c=47/125\).

Validated contraction: \(\Gamma_\varepsilon=I-\varepsilon K^2\to P_{47}\).""")
                ebtn = gr.Button("Reconstruct E47")
                with gr.Row():
                    ep1 = gr.Plot()
                    ep2 = gr.Plot()
                est = gr.Textbox(label="E47 diagnostics")
                ebtn.click(e47_figures, seed, [ep1, ep2, est])

            with gr.Tab("🔀 S3 bridge"):
                gr.Markdown(r"""## One carrier, two operators, one exact S3 bridge
\([C,U_\sigma]=[L,U_\sigma]=[P_{47},U_\sigma]=0\).

\(\ker L\) has dimension 1, while \(E_{47}\) has dimension 47.""")
                bbtn = gr.Button("Compute bridge residuals")
                bp = gr.Plot()
                bst = gr.Textbox(label="Bridge diagnostics")
                bbtn.click(bridge_figure, [], [bp, bst])

            with gr.Tab("🧪 HBr"):
                gr.Markdown(r"""## Hydrogen bromide Morse formalism
\(V(r)=D_e(1-e^{-a(r-r_e)})^2\), \(\Omega_{HBr}=E_0/D_e\).""")
                with gr.Row():
                    De = gr.Number(value=3.79, label="Dₑ (eV)")
                    E0 = gr.Number(value=.164, label="E₀ (eV)")
                    re = gr.Slider(.8, 2.5, value=1.414, step=.001, label="rₑ (Å)")
                    aa = gr.Slider(.5, 4, value=1.8, step=.01, label="a (Å⁻¹)")
                hbtn = gr.Button("Plot Morse well")
                hp = gr.Plot()
                hst = gr.Textbox(label="HBr diagnostics")
                hbtn.click(hbr_figure, [De, E0, re, aa], [hp, hst])
                gr.Markdown(r"""Corpus bridge displayed separately: \(\psi_{univ}=\phi^{-2}\), \(r_{univ}=78/47\), \(\Omega_c=1/(1+r_{univ})=47/125\).""")

            with gr.Tab("🌀 HFBG-47"):
                gr.Markdown(r"""## Hyperbolic–Fractal Buoy Group Representation lens
\(G_H=PSU(1,1)\cong PSL(2,\mathbb R)\). Buoy residual: \(\eta=\sup_x\|\pi F(x)-B\pi(x)\|\).""")
                with gr.Row():
                    depth = gr.Slider(2, 8, value=6, step=1, label="Fractal depth")
                    ratio = gr.Slider(.2, .43, value=.34, step=.01, label="recursive ratio")
                    eta = gr.Slider(0, .2, value=.03, step=.005, label="η")
                    q = gr.Slider(.05, .95, value=.65, step=.05, label="q")
                    nn = gr.Slider(1, 100, value=20, step=1, label="n")
                fbtn = gr.Button("Render HFBG-47")
                fp = gr.Plot()
                fst = gr.Textbox(label="HFBG diagnostics")
                fbtn.click(hfbg_figure, [depth, ratio, eta, q, nn], [fp, fst])

            with gr.Tab("💠 Tesseract"):
                gr.Markdown("## E47 tesseract section\n4D→3D projection visualizer beside the certified finite E47 selector. It is a visual teaching model, not a physical-carrier claim.")
                tbtn = gr.Button("Build rotating tesseract")
                tp = gr.Plot()
                tbtn.click(tesseract_figure, [], tp)
                gr.Markdown(r"""\(\mathbb R^4\to\mathbb R^3\) (display) versus \(V_2^{\otimes3}\xrightarrow{K}E_{47}\xrightarrow{P_{47}}E_{47}\) (certified finite core).""")

            with gr.Tab("🌍 Quantum → Macro"):
                gr.Markdown(r"""## Geometric computation atlas
**Molecular quantum** → HBr Morse well  
**Representation** → \(SU(2)\) spin-2 triple tensor  
**Selection** → \(K=(C-6I)(C-30I)\) and \(E_{47}\)  
**Contraction** → \(I-\varepsilon K^2\to P_{47}\)  
**Discrete geometry** → Professor's Cube / \(C_5^3\)  
**Group bridge** → shared \(S_3\) factor symmetry  
**Curved + fractal** → HFBG-47 / Buoy intertwining  
**Higher-dimensional** → tesseract projection  
**Macroscopic operator dynamics** → \(x_{n+1}=(I-\varepsilon\mathcal L)x_n\)

**Teaching motif:** carrier → operator → symmetry → invariant → projection → cross-scale map.""")

            with gr.Tab("✅ Certificate"):
                certbtn = gr.Button("Run 47-check certificate")
                cert = gr.Markdown()
                certbtn.click(certificate_markdown, [], cert)

        gr.Markdown("**The Cube** keeps the cube Laplacian, E47 projector, HBr molecular ratio, HFBG-47 geometry and tesseract display as distinct mathematical layers with explicit bridges.")
    return demo


def run_app() -> None:
    demo = build_app()
    demo.launch()


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        r = self_test(verbose=True)
        raise SystemExit(0 if r["status"] == "PASS" else 1)
    if "--no-launch" in sys.argv:
        build_app()
        print("THE CUBE · Gradio app constructed successfully")
    else:
        run_app()
