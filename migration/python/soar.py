#!/usr/bin/env python3
"""
SOAR — E47 Control, Programming & Restoration Lab
==================================================

SOAR is an evidence-typed computational laboratory built from the complete
supplied E47 / KKP prototype after error correction.

It keeps ALL major sections, but separates what is mathematically validated
from what is a computational proxy or proposed bridge.

Core validated algebra
----------------------
    V = V_2 ⊗ V_2 ⊗ V_2, dim(V)=125
    C = J_tot^2
    K = (C - 6I)(C - 30I)
    E47 = ker(K)
    rank(P47)=47
    rank(I-P47)=78

Validated restoration
---------------------
    Gamma_epsilon = I - epsilon K^2
    epsilon* = 1/99144
    rho* = 15/17

    ||(I-P47) Gamma^n psi||
      <= (15/17)^n ||(I-P47) psi||

Programmable-state section
--------------------------
The original scalar map

    psi -> P47 [phi^N psi / ||psi||]

is retained and explicitly diagnosed: after normalization it does not change
Hilbert-space direction, so it cannot by itself encode distinct programmed
states.

SOAR therefore also includes a separate, explicit PROPOSED OPERATOR BRIDGE:

    U_N = exp[-i N log(phi) G_E]
    G_E = P47 Jz_tot P47
    psi_N = U_N P47 psi

This produces an N-dependent norm-preserving transformation INSIDE E47.
It is a valid computational state-programming map. It is not, by itself,
a physical theory of programmable matter.

Synthetic propulsion / gravity section
--------------------------------------
The supplied formulas are retained as computational proxies:

    leakage = ||(I-P47) psi||
    F_proxy = leakage * c^2 * grad(N)

and a projected state satisfies zero E47 leakage. These facts do NOT derive
physical thrust, gravity nullification, Higgs decoupling, or inertial-mass
nullification.

Topology section
----------------
The original zero-density Skyrmion placeholder is rejected. SOAR includes a
correct lattice solid-angle topological-charge integrator and a standard
degree-one texture for independent validation. No E47 -> spatial texture map
is assumed.

Other retained sections
-----------------------
- centered Casimir probe <C - 18I>
- perturbation sensitivity
- active stabilizer
- constrained epsilon stability manifold
- telemetry
- machine self-test
- evidence-status ledger

Required dependency
-------------------
numpy

Optional UI dependency
----------------------
streamlit

Run
---
python soar.py --self-test
python soar.py --demo
streamlit run soar.py
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


# =============================================================================
# Constants
# =============================================================================

PHI = (1.0 + np.sqrt(5.0)) / 2.0

EXPECTED_CASIMIR_COUNTS = {
    0: 1,
    2: 9,
    6: 25,
    12: 28,
    20: 27,
    30: 22,
    42: 13,
}

K2_GAP = 11664.0
K2_MAX = 186624.0
EPSILON_STAR = 1.0 / 99144.0
RHO_STAR = 15.0 / 17.0


# =============================================================================
# Data containers
# =============================================================================

@dataclass(frozen=True)
class E47Model:
    Jx_tot: np.ndarray
    Jy_tot: np.ndarray
    Jz_tot: np.ndarray
    C: np.ndarray
    K: np.ndarray
    K2: np.ndarray
    P: np.ndarray
    Q: np.ndarray
    eigenvalues_C: np.ndarray
    epsilon_star: float
    rho_star: float
    k2_gap: float
    k2_max: float


@dataclass(frozen=True)
class TrajectoryPoint:
    step: int
    leakage_norm: float
    leakage_bound: float
    e47_weight: float
    complement_weight: float
    state_norm: float
    k2_energy: float


@dataclass(frozen=True)
class SoarRun:
    seed: int
    perturbation: float
    steps: int
    epsilon: float
    rho_bound: float
    initial_leakage: float
    final_leakage: float
    restoration_ratio: float
    verified: bool
    trajectory: tuple[TrajectoryPoint, ...]


# =============================================================================
# Linear algebra foundation
# =============================================================================

def normalize(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=complex)
    n = np.linalg.norm(v)
    if n == 0:
        raise ValueError("Cannot normalize zero vector.")
    return v / n


def spin_matrices(j: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if j < 0 or int(j) != j:
        raise ValueError("j must be a non-negative integer.")

    m = np.arange(j, -j - 1, -1, dtype=float)
    d = len(m)

    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((d, d), dtype=complex)

    for col in range(1, d):
        m_col = m[col]
        Jp[col - 1, col] = np.sqrt(
            j * (j + 1) - m_col * (m_col + 1)
        )

    Jm = Jp.conj().T
    Jx = 0.5 * (Jp + Jm)
    Jy = (Jp - Jm) / (2.0j)

    return Jx, Jy, Jz


def kron3(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    return np.kron(np.kron(A, B), C)


def build_e47_model() -> E47Model:
    Jx, Jy, Jz = spin_matrices(2)
    I5 = np.eye(5, dtype=complex)

    Jx_tot = (
        kron3(Jx, I5, I5)
        + kron3(I5, Jx, I5)
        + kron3(I5, I5, Jx)
    )
    Jy_tot = (
        kron3(Jy, I5, I5)
        + kron3(I5, Jy, I5)
        + kron3(I5, I5, Jy)
    )
    Jz_tot = (
        kron3(Jz, I5, I5)
        + kron3(I5, Jz, I5)
        + kron3(I5, I5, Jz)
    )

    C = (
        Jx_tot @ Jx_tot
        + Jy_tot @ Jy_tot
        + Jz_tot @ Jz_tot
    )
    C = 0.5 * (C + C.conj().T)

    I125 = np.eye(125, dtype=complex)
    K = (C - 6.0 * I125) @ (C - 30.0 * I125)
    K = 0.5 * (K + K.conj().T)
    K2 = K @ K

    vals, vecs = np.linalg.eigh(C)
    mask = (
        np.isclose(vals, 6.0, atol=1e-8, rtol=0.0)
        | np.isclose(vals, 30.0, atol=1e-8, rtol=0.0)
    )

    U = vecs[:, mask]
    P = U @ U.conj().T
    P = 0.5 * (P + P.conj().T)
    Q = I125 - P

    q = np.linalg.eigvalsh(K2)
    q = q[q > 1e-8]
    q_min = float(np.min(q))
    q_max = float(np.max(q))
    eps = 2.0 / (q_min + q_max)
    rho = (q_max - q_min) / (q_max + q_min)

    return E47Model(
        Jx_tot=Jx_tot,
        Jy_tot=Jy_tot,
        Jz_tot=Jz_tot,
        C=C,
        K=K,
        K2=K2,
        P=P,
        Q=Q,
        eigenvalues_C=vals,
        epsilon_star=eps,
        rho_star=rho,
        k2_gap=q_min,
        k2_max=q_max,
    )


# =============================================================================
# E47 geometry
# =============================================================================

def e47_leakage(psi: np.ndarray, model: E47Model) -> float:
    return float(np.linalg.norm(model.Q @ np.asarray(psi, dtype=complex)))


def e47_weight(psi: np.ndarray, model: E47Model) -> float:
    psi = np.asarray(psi, dtype=complex)
    n2 = float(np.linalg.norm(psi) ** 2)
    if n2 == 0:
        return 0.0
    return float(np.linalg.norm(model.P @ psi) ** 2 / n2)


def complement_weight(psi: np.ndarray, model: E47Model) -> float:
    psi = np.asarray(psi, dtype=complex)
    n2 = float(np.linalg.norm(psi) ** 2)
    if n2 == 0:
        return 0.0
    return float(np.linalg.norm(model.Q @ psi) ** 2 / n2)


def k2_energy(psi: np.ndarray, model: E47Model) -> float:
    psi = np.asarray(psi, dtype=complex)
    n2 = float(np.linalg.norm(psi) ** 2)
    if n2 == 0:
        return 0.0
    value = np.vdot(psi, model.K2 @ psi) / n2
    return float(np.real(value))


def random_state(rng: np.random.Generator) -> np.ndarray:
    return normalize(
        rng.normal(size=125) + 1j * rng.normal(size=125)
    )


def random_e47_state(
    model: E47Model,
    rng: np.random.Generator,
) -> np.ndarray:
    return normalize(model.P @ random_state(rng))


def random_complement_direction(
    model: E47Model,
    rng: np.random.Generator,
) -> np.ndarray:
    return normalize(model.Q @ random_state(rng))


def disturb_state(
    psi_e47: np.ndarray,
    model: E47Model,
    rng: np.random.Generator,
    magnitude: float,
) -> np.ndarray:
    if magnitude < 0:
        raise ValueError("magnitude must be non-negative.")
    eta = random_complement_direction(model, rng)
    return np.asarray(psi_e47, dtype=complex) + float(magnitude) * eta


# =============================================================================
# Restoration / active stabilizer
# =============================================================================

def gamma_operator(
    model: E47Model,
    epsilon: float | None = None,
) -> np.ndarray:
    if epsilon is None:
        epsilon = model.epsilon_star

    epsilon = float(epsilon)
    stability_limit = 2.0 / model.k2_max

    if not (0.0 < epsilon < stability_limit):
        raise ValueError(
            f"epsilon must satisfy 0 < epsilon < {stability_limit:.16g}"
        )

    return np.eye(125, dtype=complex) - epsilon * model.K2


def transverse_rho(
    model: E47Model,
    epsilon: float,
) -> float:
    q = np.linalg.eigvalsh(model.K2)
    q = q[q > 1e-8]
    return float(np.max(np.abs(1.0 - epsilon * q)))


def run_restoration(
    model: E47Model,
    *,
    seed: int = 470125,
    perturbation: float = 0.25,
    steps: int = 30,
    epsilon: float | None = None,
) -> SoarRun:
    if steps < 0:
        raise ValueError("steps must be non-negative.")

    if epsilon is None:
        epsilon = model.epsilon_star

    epsilon = float(epsilon)
    Gamma = gamma_operator(model, epsilon)
    rho = transverse_rho(model, epsilon)

    rng = np.random.default_rng(int(seed))
    base = random_e47_state(model, rng)
    psi = disturb_state(base, model, rng, perturbation)

    initial = e47_leakage(psi, model)
    trajectory: list[TrajectoryPoint] = []
    verified = True

    for step in range(steps + 1):
        leak = e47_leakage(psi, model)
        bound = initial * (rho ** step)

        if leak > bound + 1e-9:
            verified = False

        trajectory.append(
            TrajectoryPoint(
                step=step,
                leakage_norm=leak,
                leakage_bound=bound,
                e47_weight=e47_weight(psi, model),
                complement_weight=complement_weight(psi, model),
                state_norm=float(np.linalg.norm(psi)),
                k2_energy=k2_energy(psi, model),
            )
        )

        if step < steps:
            psi = Gamma @ psi

    final = trajectory[-1].leakage_norm
    ratio = 0.0 if initial == 0 else final / initial

    return SoarRun(
        seed=int(seed),
        perturbation=float(perturbation),
        steps=int(steps),
        epsilon=epsilon,
        rho_bound=rho,
        initial_leakage=initial,
        final_leakage=final,
        restoration_ratio=ratio,
        verified=verified,
        trajectory=tuple(trajectory),
    )


# =============================================================================
# "Programmable Matter" section
# =============================================================================

def original_phi_scalar_program(
    psi: np.ndarray,
    target_n: float,
    model: E47Model,
) -> np.ndarray:
    """
    Original supplied operation, retained exactly in mathematical meaning:

        P47 [phi^N psi / ||psi||]

    This changes magnitude by phi^N before projection but does not create
    an N-dependent normalized Hilbert-space direction.
    """
    psi = np.asarray(psi, dtype=complex)
    return model.P @ (
        (PHI ** float(target_n)) * psi / np.linalg.norm(psi)
    )


def phi_scalar_program_diagnostic(
    psi: np.ndarray,
    n_a: float,
    n_b: float,
    model: E47Model,
) -> dict[str, float | bool]:
    a = normalize(original_phi_scalar_program(psi, n_a, model))
    b = normalize(original_phi_scalar_program(psi, n_b, model))

    overlap = np.vdot(a, b)
    phase = np.exp(-1j * np.angle(overlap))
    direction_change = float(np.linalg.norm(a - phase * b))

    return {
        "n_a": float(n_a),
        "n_b": float(n_b),
        "direction_change_after_normalization": direction_change,
        "same_direction": bool(direction_change < 1e-10),
    }


def e47_programming_generator(model: E47Model) -> np.ndarray:
    """
    A concrete E47-preserving Hermitian generator.

    G_E = P47 Jz_tot P47

    This is a proposed computational bridge for state programming, not a
    physical matter-programming law.
    """
    G = model.P @ model.Jz_tot @ model.P
    return 0.5 * (G + G.conj().T)


def unitary_from_hermitian(
    G: np.ndarray,
    theta: float,
) -> np.ndarray:
    vals, vecs = np.linalg.eigh(
        0.5 * (G + G.conj().T)
    )
    phases = np.exp(-1j * float(theta) * vals)
    return (vecs * phases) @ vecs.conj().T


def program_e47_state(
    psi: np.ndarray,
    target_n: float,
    model: E47Model,
) -> np.ndarray:
    """
    Proposed executable operator bridge:

        theta_N = N log(phi)
        G_E = P47 Jz_tot P47
        U_N = exp(-i theta_N G_E)
        psi_N = U_N P47 psi

    This is a nontrivial N-dependent transformation inside E47.
    """
    psi_e = normalize(model.P @ np.asarray(psi, dtype=complex))
    theta_n = float(target_n) * np.log(PHI)
    U_n = unitary_from_hermitian(
        e47_programming_generator(model),
        theta_n,
    )
    return normalize(U_n @ psi_e)


def programming_audit(
    psi: np.ndarray,
    n_a: float,
    n_b: float,
    model: E47Model,
) -> dict[str, float | bool]:
    a = program_e47_state(psi, n_a, model)
    b = program_e47_state(psi, n_b, model)

    overlap = float(np.abs(np.vdot(a, b)) ** 2)
    leak_a = e47_leakage(a, model)
    leak_b = e47_leakage(b, model)

    # Group-law test: U(n_a)U(n_b) = U(n_a+n_b)
    G = e47_programming_generator(model)
    Ua = unitary_from_hermitian(G, n_a * np.log(PHI))
    Ub = unitary_from_hermitian(G, n_b * np.log(PHI))
    Uab = unitary_from_hermitian(G, (n_a + n_b) * np.log(PHI))
    group_residual = float(
        np.linalg.norm(Ua @ Ub - Uab, ord="fro")
    )

    return {
        "n_a": float(n_a),
        "n_b": float(n_b),
        "fidelity_between_programmed_states": overlap,
        "leakage_n_a": leak_a,
        "leakage_n_b": leak_b,
        "group_law_residual_fro": group_residual,
        "e47_preserved": bool(max(leak_a, leak_b) < 1e-10),
    }


# =============================================================================
# Supplied gravity / propulsion formulas retained as typed proxies
# =============================================================================

def projection_nullification_proxy(
    psi: np.ndarray,
    model: E47Model,
) -> dict[str, float | bool]:
    """
    Project psi into E47 and report the remaining E47 leakage.

    This is a subspace-nullification result only.
    """
    projected = model.P @ np.asarray(psi, dtype=complex)
    residual = e47_leakage(projected, model)

    return {
        "e47_leakage_after_projection": residual,
        "projection_nullified": bool(residual < 1e-10),
    }


def propulsion_proxy(
    psi: np.ndarray,
    model: E47Model,
    gradient_N: np.ndarray,
    c: float = 1.0,
) -> np.ndarray:
    """
    Supplied synthetic formula:

        F_proxy = leakage * c^2 * grad(N)

    No physical-force claim is made by this function.
    """
    return (
        e47_leakage(psi, model)
        * float(c) ** 2
        * np.asarray(gradient_N, dtype=float)
    )


# =============================================================================
# Centered Casimir / "mid-shaft" probe
# =============================================================================

def centered_casimir_probe(
    psi: np.ndarray,
    model: E47Model,
    center: float = 18.0,
) -> dict[str, float]:
    psi = normalize(psi)
    A = model.C - float(center) * np.eye(125, dtype=complex)
    mean = np.vdot(psi, A @ psi)
    second = np.vdot(psi, A @ (A @ psi))
    variance = float(np.real_if_close(second - mean * mean.conjugate()))

    return {
        "center": float(center),
        "expectation": float(np.real_if_close(mean)),
        "variance": max(0.0, variance),
    }


# =============================================================================
# Perturbation sensitivity
# =============================================================================

def sensitivity_audit(
    psi: np.ndarray,
    model: E47Model,
    perturbation: np.ndarray,
) -> dict[str, float | bool]:
    perturbation = np.asarray(perturbation, dtype=complex)

    lhs = float(
        np.linalg.norm(
            model.Q @ (psi + perturbation)
            - model.Q @ psi
        )
    )
    rhs = float(np.linalg.norm(perturbation))

    return {
        "projected_perturbation_norm": lhs,
        "perturbation_norm": rhs,
        "nonexpansive_ratio": 0.0 if rhs == 0 else lhs / rhs,
        "bound_verified": bool(lhs <= rhs + 1e-12),
    }


# =============================================================================
# Stability manifold and constrained control
# =============================================================================

def logarithmic_barrier(
    epsilon: float,
    epsilon_min: float,
    epsilon_max: float,
    mu: float = 1e-3,
) -> float:
    if not (epsilon_min < epsilon < epsilon_max):
        return float("inf")

    return float(
        -mu
        * (
            np.log(epsilon - epsilon_min)
            + np.log(epsilon_max - epsilon)
        )
    )


def stability_manifold(
    model: E47Model,
    samples: int = 200,
) -> dict[str, list[float] | float]:
    """
    Map the true control manifold rho(epsilon) over the stable interval.

    This replaces the original degenerate n-attractor scan.
    """
    if samples < 10:
        raise ValueError("samples must be >= 10.")

    limit = 2.0 / model.k2_max
    eps = np.linspace(
        limit / (samples + 1),
        limit * samples / (samples + 1),
        samples,
    )

    rho = np.array(
        [transverse_rho(model, float(e)) for e in eps]
    )

    idx = int(np.argmin(rho))

    return {
        "epsilon": eps.tolist(),
        "rho": rho.tolist(),
        "numeric_optimal_epsilon": float(eps[idx]),
        "numeric_optimal_rho": float(rho[idx]),
        "analytic_epsilon_star": model.epsilon_star,
        "analytic_rho_star": model.rho_star,
        "stability_limit": limit,
    }


# =============================================================================
# Topological charge
# =============================================================================

def _triangle_solid_angle(
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
) -> np.ndarray:
    numerator = np.einsum(
        "...i,...i->...",
        a,
        np.cross(b, c),
    )

    denominator = (
        1.0
        + np.einsum("...i,...i->...", a, b)
        + np.einsum("...i,...i->...", b, c)
        + np.einsum("...i,...i->...", c, a)
    )

    return 2.0 * np.arctan2(
        numerator,
        denominator,
    )


def lattice_topological_charge(
    texture: np.ndarray,
) -> float:
    texture = np.asarray(texture, dtype=float)

    if texture.ndim != 3 or texture.shape[-1] != 3:
        raise ValueError(
            "texture must have shape (Ny, Nx, 3)."
        )

    norms = np.linalg.norm(
        texture,
        axis=-1,
        keepdims=True,
    )

    if np.any(norms == 0):
        raise ValueError(
            "texture contains zero vectors."
        )

    n = texture / norms

    a = n[:-1, :-1]
    b = n[:-1, 1:]
    c = n[1:, 1:]
    d = n[1:, :-1]

    omega = (
        _triangle_solid_angle(a, b, c)
        + _triangle_solid_angle(a, c, d)
    )

    return float(
        np.sum(omega) / (4.0 * np.pi)
    )


def canonical_skyrmion_texture(
    grid_size: int = 201,
    extent: float = 8.0,
    scale: float = 1.0,
) -> np.ndarray:
    x = np.linspace(
        -extent,
        extent,
        grid_size,
    )
    y = np.linspace(
        -extent,
        extent,
        grid_size,
    )
    X, Y = np.meshgrid(
        x,
        y,
        indexing="xy",
    )

    r2 = X * X + Y * Y
    den = r2 + scale * scale

    return np.stack(
        [
            2.0 * scale * X / den,
            2.0 * scale * Y / den,
            (r2 - scale * scale) / den,
        ],
        axis=-1,
    )


# =============================================================================
# Telemetry
# =============================================================================

def write_telemetry(
    run: SoarRun,
    path: str | Path,
) -> Path:
    path = Path(path)

    rows = [
        asdict(point)
        for point in run.trajectory
    ]

    with path.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(rows[0].keys()),
        )
        writer.writeheader()
        writer.writerows(rows)

    return path


# =============================================================================
# Evidence ledger
# =============================================================================

def evidence_ledger() -> list[dict[str, str]]:
    return [
        {
            "module": "E47 carrier / Casimir / projector",
            "status": "VALIDATED",
            "scope": "finite-dimensional linear algebra",
        },
        {
            "module": "E47 leakage",
            "status": "VALIDATED",
            "scope": "distance to selected invariant subspace",
        },
        {
            "module": "Gamma restoration",
            "status": "VALIDATED",
            "scope": "deterministic nonunitary contraction map",
        },
        {
            "module": "Original phi^N scalar programming",
            "status": "NEGATIVE RESULT",
            "scope": "scalar rescaling is direction-degenerate after normalization",
        },
        {
            "module": "Operator state programming U_N",
            "status": "PROPOSED EXECUTABLE BRIDGE",
            "scope": "N-dependent unitary transformation within E47",
        },
        {
            "module": "Projection nullification",
            "status": "VALIDATED AS SUBSPACE STATEMENT",
            "scope": "P47 psi has zero E47-complement leakage",
        },
        {
            "module": "Propulsion formula",
            "status": "FORMAL PROXY",
            "scope": "computable vector; physical thrust not derived",
        },
        {
            "module": "Centered Casimir probe",
            "status": "VALIDATED WITH REINTERPRETATION",
            "scope": "spectral expectation / variance, not transition detector",
        },
        {
            "module": "Perturbation sensitivity",
            "status": "VALIDATED",
            "scope": "orthogonal projection non-expansiveness",
        },
        {
            "module": "Stability manifold",
            "status": "VALIDATED",
            "scope": "rho(epsilon) over the exact stable Euler interval",
        },
        {
            "module": "Lattice topological charge",
            "status": "VALIDATED INDEPENDENTLY",
            "scope": "explicit S2 texture only",
        },
        {
            "module": "E47 -> spatial Skyrmion bridge",
            "status": "OPEN",
            "scope": "no source-derived spatial texture map supplied",
        },
        {
            "module": "Gravity nullification / Higgs decoupling",
            "status": "OPEN PHYSICAL HYPOTHESIS",
            "scope": "requires an independently specified physical coupling model",
        },
        {
            "module": "Physical programmable matter",
            "status": "OPEN PHYSICAL HYPOTHESIS",
            "scope": "operator state programming does not itself establish matter reconfiguration",
        },
    ]


# =============================================================================
# Complete machine audit
# =============================================================================

def self_test(
    model: E47Model | None = None,
) -> dict[str, Any]:
    if model is None:
        model = build_e47_model()

    rounded = np.rint(
        model.eigenvalues_C
    ).astype(int)

    counts = {
        int(v): int(np.sum(rounded == v))
        for v in sorted(set(rounded.tolist()))
    }

    rank_p = int(
        round(np.trace(model.P).real)
    )
    rank_q = int(
        round(np.trace(model.Q).real)
    )

    p2 = float(
        np.linalg.norm(
            model.P @ model.P - model.P,
            ord="fro",
        )
    )
    pq = float(
        np.linalg.norm(
            model.P @ model.Q,
            ord="fro",
        )
    )
    kp = float(
        np.linalg.norm(
            model.K @ model.P,
            ord="fro",
        )
    )

    assert counts == EXPECTED_CASIMIR_COUNTS
    assert rank_p == 47
    assert rank_q == 78
    assert p2 < 1e-10
    assert pq < 1e-10
    assert kp < 1e-8

    assert np.isclose(
        model.k2_gap,
        K2_GAP,
        atol=1e-6,
    )
    assert np.isclose(
        model.k2_max,
        K2_MAX,
        atol=1e-6,
    )
    assert np.isclose(
        model.epsilon_star,
        EPSILON_STAR,
        atol=1e-15,
    )
    assert np.isclose(
        model.rho_star,
        RHO_STAR,
        atol=1e-12,
    )

    restoration = run_restoration(
        model,
        seed=470125,
        perturbation=0.25,
        steps=30,
    )

    assert restoration.verified
    assert (
        restoration.final_leakage
        < restoration.initial_leakage
    )

    rng = np.random.default_rng(470125)
    psi = random_state(rng)

    scalar_diag = phi_scalar_program_diagnostic(
        psi,
        10.0,
        45.0,
        model,
    )
    assert scalar_diag["same_direction"]

    program_diag = programming_audit(
        psi,
        10.0,
        45.0,
        model,
    )
    assert program_diag["e47_preserved"]
    assert program_diag["group_law_residual_fro"] < 1e-9

    null_diag = projection_nullification_proxy(
        psi,
        model,
    )
    assert null_diag["projection_nullified"]

    proxy = propulsion_proxy(
        psi,
        model,
        np.array([0.1, -0.05, 0.02]),
    )
    assert proxy.shape == (3,)
    assert np.all(np.isfinite(proxy))

    probe = centered_casimir_probe(
        psi,
        model,
    )
    assert np.isfinite(probe["expectation"])
    assert probe["variance"] >= 0.0

    delta = 1e-3 * (
        rng.normal(size=125)
        + 1j * rng.normal(size=125)
    )
    sensitivity = sensitivity_audit(
        psi,
        model,
        delta,
    )
    assert sensitivity["bound_verified"]

    manifold = stability_manifold(
        model,
        samples=501,
    )
    numeric_eps = manifold[
        "numeric_optimal_epsilon"
    ]
    numeric_rho = manifold[
        "numeric_optimal_rho"
    ]
    grid_step = (
        manifold["stability_limit"]
        / 502.0
    )

    assert (
        abs(numeric_eps - model.epsilon_star)
        <= 2.0 * grid_step
    )
    assert (
        numeric_rho
        <= model.rho_star + 0.01
    )

    texture = canonical_skyrmion_texture()
    q_top = lattice_topological_charge(
        texture
    )
    assert abs(abs(q_top) - 1.0) < 0.03

    return {
        "status": "PASS",
        "carrier_dimension": 125,
        "casimir_counts": counts,
        "rank_P47": rank_p,
        "rank_complement": rank_q,
        "projector_residual_fro": p2,
        "PQ_residual_fro": pq,
        "KP_residual_fro": kp,
        "K2_gap": model.k2_gap,
        "K2_max": model.k2_max,
        "epsilon_star": model.epsilon_star,
        "rho_star": model.rho_star,
        "restoration": {
            "initial_leakage":
                restoration.initial_leakage,
            "final_leakage":
                restoration.final_leakage,
            "ratio":
                restoration.restoration_ratio,
            "bound_verified":
                restoration.verified,
        },
        "original_phi_scalar_programming": scalar_diag,
        "operator_programming": program_diag,
        "projection_nullification": null_diag,
        "propulsion_proxy_vector": proxy.tolist(),
        "centered_casimir_probe": probe,
        "sensitivity": sensitivity,
        "stability_manifold": {
            "numeric_optimal_epsilon":
                numeric_eps,
            "numeric_optimal_rho":
                numeric_rho,
            "analytic_epsilon_star":
                model.epsilon_star,
            "analytic_rho_star":
                model.rho_star,
        },
        "independent_skyrmion_charge":
            q_top,
        "evidence_ledger":
            evidence_ledger(),
    }


# =============================================================================
# Streamlit app
# =============================================================================

def in_streamlit_context() -> bool:
    try:
        from streamlit.runtime.scriptrunner import (
            get_script_run_ctx,
        )
        return (
            get_script_run_ctx(
                suppress_warning=True
            )
            is not None
        )
    except Exception:
        return False


def render_streamlit() -> None:
    import streamlit as st

    st.set_page_config(
        page_title="Soar",
        page_icon="🪽",
        layout="wide",
    )

    st.title("Soar")
    st.caption(
        "E47 Control, Programming & Restoration Lab"
    )
    st.markdown(
        "**Question:** Can an invariant sector be "
        "restored and deliberately transformed without "
        "leaving itself?"
    )

    @st.cache_resource
    def cached_model() -> E47Model:
        return build_e47_model()

    model = cached_model()

    with st.sidebar:
        st.header("Global controls")

        seed = st.number_input(
            "Seed",
            min_value=0,
            max_value=2_147_483_647,
            value=470125,
            step=1,
        )

        perturbation = st.slider(
            "Disturbance magnitude",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.01,
        )

        steps = st.slider(
            "Restoration steps",
            min_value=1,
            max_value=80,
            value=30,
            step=1,
        )

        target_n = st.slider(
            "Programming index N",
            min_value=0.0,
            max_value=80.0,
            value=45.0,
            step=0.5,
        )

    restoration = run_restoration(
        model,
        seed=int(seed),
        perturbation=float(perturbation),
        steps=int(steps),
    )

    tabs = st.tabs(
        [
            "Restore",
            "Programmable Matter",
            "Propulsion / Gravity Proxy",
            "Spectral Probe",
            "Topology",
            "Stability Manifold",
            "Audit",
        ]
    )

    with tabs[0]:
        st.subheader(
            "Active invariant-sector restoration"
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("rank(P47)", "47")
        c2.metric(
            "Initial leakage",
            f"{restoration.initial_leakage:.6g}",
        )
        c3.metric(
            "Final leakage",
            f"{restoration.final_leakage:.6g}",
        )
        c4.metric(
            "Restoration ratio",
            f"{restoration.restoration_ratio:.3e}",
        )

        if restoration.verified:
            st.success(
                "Certified contraction bound verified."
            )
        else:
            st.error(
                "Contraction bound failed."
            )

        st.latex(
            r"\Gamma_{\epsilon_*}=I-\epsilon_*K^2,"
            r"\quad\epsilon_*=\frac{1}{99144},"
            r"\quad\rho_*=\frac{15}{17}"
        )

        rows = [
            asdict(point)
            for point in restoration.trajectory
        ]
        st.line_chart(
            {
                "observed leakage": [
                    row["leakage_norm"]
                    for row in rows
                ],
                "certified bound": [
                    row["leakage_bound"]
                    for row in rows
                ],
            }
        )

        st.dataframe(
            rows,
            use_container_width=True,
        )

    with tabs[1]:
        st.subheader(
            "Programmable Matter / state-programming module"
        )

        st.warning(
            "The original phi^N scalar operation is kept "
            "and diagnosed, not silently discarded."
        )

        rng = np.random.default_rng(int(seed))
        psi = random_state(rng)

        scalar_diag = (
            phi_scalar_program_diagnostic(
                psi,
                10.0,
                float(target_n),
                model,
            )
        )

        st.markdown(
            "**Original supplied scalar map**"
        )
        st.latex(
            r"\psi_N="
            r"P_{47}\frac{\phi^N\psi}{\|\psi\|}"
        )
        st.json(scalar_diag)

        st.markdown(
            "After normalization this scalar operation "
            "has no N-dependent direction. That is a "
            "machine-checkable negative result."
        )

        st.divider()

        st.markdown(
            "**Proposed executable operator bridge**"
        )
        st.latex(
            r"G_E=P_{47}J_z^{\mathrm{tot}}P_{47},"
            r"\qquad"
            r"U_N=e^{-iN\log(\phi)G_E}"
        )
        st.latex(
            r"\psi_N=U_NP_{47}\psi"
        )

        program_diag = programming_audit(
            psi,
            0.0,
            float(target_n),
            model,
        )

        st.json(program_diag)

        if program_diag["e47_preserved"]:
            st.success(
                "Programmed state remains inside E47."
            )

        st.caption(
            "This is a valid computational state-programming "
            "map. Physical programmable matter remains an "
            "open bridge."
        )

    with tabs[2]:
        st.subheader(
            "Supplied propulsion / gravity formulas"
        )

        rng = np.random.default_rng(int(seed))
        psi = random_state(rng)

        gradient = st.text_input(
            "Synthetic grad(N), comma-separated",
            value="0.1,-0.05,0.02",
        )

        try:
            grad = np.array(
                [
                    float(x.strip())
                    for x in gradient.split(",")
                ],
                dtype=float,
            )

            proxy = propulsion_proxy(
                psi,
                model,
                grad,
            )

            nullification = (
                projection_nullification_proxy(
                    psi,
                    model,
                )
            )

            st.markdown(
                "**Projection-nullification diagnostic**"
            )
            st.json(nullification)

            st.markdown(
                "**Synthetic propulsion proxy**"
            )
            st.latex(
                r"F_{\mathrm{proxy}}="
                r"\|(I-P_{47})\psi\|\,c^2\nabla N"
            )
            st.write(
                proxy.tolist()
            )
            st.metric(
                "Proxy-vector norm",
                f"{np.linalg.norm(proxy):.6g}",
            )

        except ValueError:
            st.error(
                "Enter a comma-separated numeric vector."
            )

        st.error(
            "Evidence boundary: zero E47 leakage is a "
            "subspace statement. The displayed proxy is not "
            "a derivation of physical gravity nullification, "
            "Higgs decoupling, inertial-mass nullification, "
            "or propulsion."
        )

    with tabs[3]:
        st.subheader(
            "Centered Casimir spectral probe"
        )

        rng = np.random.default_rng(int(seed))
        psi = random_state(rng)

        center = st.slider(
            "Spectral center",
            min_value=0.0,
            max_value=42.0,
            value=18.0,
            step=0.5,
        )

        result = centered_casimir_probe(
            psi,
            model,
            center=float(center),
        )

        st.json(result)

        counts = {
            int(v): int(
                np.sum(
                    np.rint(
                        model.eigenvalues_C
                    ).astype(int)
                    == v
                )
            )
            for v in EXPECTED_CASIMIR_COUNTS
        }

        st.write(
            "Casimir eigenspace counts:",
            counts,
        )

        st.caption(
            "The probe is a centered spectral expectation "
            "and variance. It is not automatically an "
            "edge-state or transition detector."
        )

    with tabs[4]:
        st.subheader(
            "Topological charge module"
        )

        grid_size = st.slider(
            "Texture grid",
            min_value=51,
            max_value=301,
            value=151,
            step=50,
        )

        texture = canonical_skyrmion_texture(
            grid_size=int(grid_size),
        )

        q_top = lattice_topological_charge(
            texture
        )

        st.metric(
            "Independent texture charge Q",
            f"{q_top:.6f}",
        )

        st.success(
            "Correct lattice solid-angle integrator active."
        )

        st.warning(
            "No E47-to-spatial-texture map is asserted. "
            "This module validates topological-charge "
            "machinery on an explicit texture only."
        )

    with tabs[5]:
        st.subheader(
            "Exact epsilon stability manifold"
        )

        manifold = stability_manifold(
            model,
            samples=300,
        )

        st.line_chart(
            {
                "rho(epsilon)": (
                    manifold["rho"]
                )
            }
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Analytic epsilon*",
            f"{model.epsilon_star:.10g}",
        )
        c2.metric(
            "Analytic rho*",
            f"{model.rho_star:.10g}",
        )
        c3.metric(
            "Stable epsilon ceiling",
            f"{2.0/model.k2_max:.10g}",
        )

        st.latex(
            r"\rho(\epsilon)="
            r"\max_{q\in\operatorname{spec}(K^2)\setminus\{0\}}"
            r"|1-\epsilon q|"
        )

        st.caption(
            "This replaces the former degenerate N-attractor "
            "scan with the actual control-stability manifold."
        )

    with tabs[6]:
        st.subheader(
            "Machine validation and evidence ledger"
        )

        report = self_test(model)

        st.json(report)

        st.dataframe(
            evidence_ledger(),
            use_container_width=True,
        )

        st.markdown(
            "**SOAR keeps the speculative sections visible, "
            "but typed.** A calculation is allowed to exist "
            "before its physical interpretation is established."
        )


# =============================================================================
# CLI
# =============================================================================

def demo() -> dict[str, Any]:
    model = build_e47_model()
    rng = np.random.default_rng(470125)
    psi = random_state(rng)

    run = run_restoration(
        model,
        seed=470125,
        perturbation=0.25,
        steps=30,
    )

    result = {
        "restoration": {
            "initial_leakage": run.initial_leakage,
            "final_leakage": run.final_leakage,
            "ratio": run.restoration_ratio,
            "verified": run.verified,
        },
        "phi_scalar_diagnostic":
            phi_scalar_program_diagnostic(
                psi,
                10.0,
                45.0,
                model,
            ),
        "operator_programming":
            programming_audit(
                psi,
                10.0,
                45.0,
                model,
            ),
        "projection_nullification":
            projection_nullification_proxy(
                psi,
                model,
            ),
        "propulsion_proxy":
            propulsion_proxy(
                psi,
                model,
                np.array([0.1, -0.05, 0.02]),
            ).tolist(),
        "centered_probe":
            centered_casimir_probe(
                psi,
                model,
            ),
        "skyrmion_charge":
            lattice_topological_charge(
                canonical_skyrmion_texture(
                    grid_size=151
                )
            ),
        "evidence":
            evidence_ledger(),
    }

    write_telemetry(
        run,
        "soar_telemetry.csv",
    )

    return result


def cli() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Soar: E47 control, programming, "
            "and restoration laboratory."
        )
    )

    parser.add_argument(
        "--self-test",
        action="store_true",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
    )

    args = parser.parse_args()

    if args.self_test:
        print(
            json.dumps(
                self_test(),
                indent=2,
            )
        )
        return

    if args.demo:
        print(
            json.dumps(
                demo(),
                indent=2,
            )
        )
        return

    print(
        "Run one of:\n"
        "  python soar.py --self-test\n"
        "  python soar.py --demo\n"
        "  streamlit run soar.py"
    )


if __name__ == "__main__":
    if in_streamlit_context():
        render_streamlit()
    else:
        cli()
