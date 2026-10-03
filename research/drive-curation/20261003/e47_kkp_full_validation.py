#!/usr/bin/env python3
"""
E47 / KKP FORMALISM — ERROR-CORRECTED FULL VALIDATION
=====================================================

Purpose
-------
Validate every mathematically executable component in the supplied E47/KKP
prototype, correct coding errors, and separate:

    1. exact / machine-checkable mathematics,
    2. computational proxy definitions,
    3. degenerate or invalid constructions,
    4. physical interpretations not established by the mathematics.

This file does NOT promote a computational proxy into a physical claim.

Key terminology corrections
---------------------------
- ||(I - P_E) psi|| is called E47 leakage / projection residual.
  It is not identified here with inertial mass or physical decoherence.
- leakage * c^2 * grad(N) is retained only as a declared synthetic proxy.
  It is not derived here as physical thrust.
- phi**n multiplication is a scalar rescaling. After normalization it does
  not change Hilbert-space direction, topology, or sector identity.
- the supplied Skyrmion density routine was a placeholder. A separate,
  mathematically valid lattice charge integrator is included only to validate
  that topological-charge machinery once an actual spatial texture is supplied.
- active restoration is implemented with the validated E47 contraction
      Gamma_epsilon = I - epsilon K^2
  rather than by changing an unrelated scalar recursion index n.

Outputs
-------
- e47_kkp_full_validation_report.json
- e47_stabilizer_telemetry.csv

Dependencies
------------
numpy
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


TOL = 1e-10
RNG = np.random.default_rng(470125)

REPORT_PATH = Path("e47_kkp_full_validation_report.json")
TELEMETRY_PATH = Path("e47_stabilizer_telemetry.csv")


def max_abs(a: np.ndarray) -> float:
    return float(np.max(np.abs(a))) if a.size else 0.0


def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n == 0:
        raise ValueError("Cannot normalize the zero vector.")
    return v / n


def record(
    report: list[dict[str, Any]],
    test_id: str,
    status: str,
    statement: str,
    **metrics: Any,
) -> None:
    report.append(
        {
            "id": test_id,
            "status": status,
            "statement": statement,
            "metrics": metrics,
        }
    )


# =============================================================================
# I. SPIN-2 / SU(2) FOUNDATION
# =============================================================================

def spin_matrices(j: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return Hermitian spin-j matrices Jx, Jy, Jz in descending-m basis."""
    if j < 0 or int(j) != j:
        raise ValueError("This validator expects a non-negative integer j.")

    m = np.arange(j, -j - 1, -1, dtype=float)
    d = m.size

    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((d, d), dtype=complex)

    # Basis order: |j>, |j-1>, ..., |-j>.
    # J_+ |m> = sqrt(j(j+1)-m(m+1)) |m+1>.
    for col in range(1, d):
        m_col = m[col]
        Jp[col - 1, col] = np.sqrt(j * (j + 1) - m_col * (m_col + 1))

    Jm = Jp.conj().T
    Jx = 0.5 * (Jp + Jm)
    Jy = (Jp - Jm) / (2.0j)

    return Jx, Jy, Jz


def kron3(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> np.ndarray:
    return np.kron(np.kron(A, B), C)


def build_e47() -> dict[str, np.ndarray]:
    """Construct the correct 125D total-spin Casimir, selector K, and P_E."""
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

    eigvals_C, eigvecs_C = np.linalg.eigh(C)
    ker_mask = (
        np.isclose(eigvals_C, 6.0, atol=1e-8, rtol=0.0)
        | np.isclose(eigvals_C, 30.0, atol=1e-8, rtol=0.0)
    )

    U_E = eigvecs_C[:, ker_mask]
    P_E = U_E @ U_E.conj().T
    P_E = 0.5 * (P_E + P_E.conj().T)
    Q_E = I125 - P_E

    return {
        "Jx": Jx,
        "Jy": Jy,
        "Jz": Jz,
        "Jx_tot": Jx_tot,
        "Jy_tot": Jy_tot,
        "Jz_tot": Jz_tot,
        "C": C,
        "K": K,
        "K2": K2,
        "P_E": P_E,
        "Q_E": Q_E,
        "eigvals_C": eigvals_C,
        "eigvecs_C": eigvecs_C,
    }


# =============================================================================
# II. E47 GEOMETRY AND COMPUTATIONAL PROXIES
# =============================================================================

def e47_leakage(psi: np.ndarray, P_E: np.ndarray) -> float:
    """Distance of psi from E47: ||(I-P_E) psi||_2."""
    psi = np.asarray(psi, dtype=complex)
    Q = np.eye(P_E.shape[0], dtype=complex) - P_E
    return float(np.linalg.norm(Q @ psi))


def e47_weight(psi: np.ndarray, P_E: np.ndarray) -> float:
    """Squared norm carried by E47, for normalized psi."""
    return float(np.linalg.norm(P_E @ psi) ** 2)


def synthetic_thrust_proxy(
    psi: np.ndarray,
    P_E: np.ndarray,
    gradient_N: np.ndarray,
    c: float = 1.0,
) -> np.ndarray:
    """
    Declared synthetic proxy retained from the prototype:

        proxy = leakage * c^2 * grad(N)

    This function makes NO physical thrust claim.
    """
    return e47_leakage(psi, P_E) * (c ** 2) * np.asarray(gradient_N, dtype=float)


def phi_scale_then_project(
    psi: np.ndarray,
    target_n: float,
    P_E: np.ndarray,
    phi: float = (1.0 + np.sqrt(5.0)) / 2.0,
) -> np.ndarray:
    """
    Preserve the original algebraic operation for diagnosis:

        P_E [ phi^n * psi / ||psi|| ]

    target_n changes only scalar magnitude before projection.
    """
    psi = np.asarray(psi, dtype=complex)
    if np.linalg.norm(psi) == 0:
        raise ValueError("psi must be nonzero.")
    return P_E @ ((phi ** target_n) * psi / np.linalg.norm(psi))


def centered_casimir_probe(psi: np.ndarray, C: np.ndarray, center: float = 18.0) -> complex:
    """
    Return <psi | (C-center*I) | psi> / <psi|psi>.

    This is a centered spectral expectation, not by itself an edge-state
    or transition detector.
    """
    psi = np.asarray(psi, dtype=complex)
    psi = normalize(psi)
    A = C - center * np.eye(C.shape[0], dtype=complex)
    return np.vdot(psi, A @ psi)


# =============================================================================
# III. VALIDATED E47 RESTORATION MAP
# =============================================================================

def optimal_e47_contraction(K2: np.ndarray) -> tuple[float, float, float, float]:
    """
    Return (q_min_positive, q_max, epsilon_star, rho_star) for
        Gamma = I - epsilon K^2.

    For a positive spectrum q in [q_min, q_max], the minimax Euler step is

        epsilon_star = 2/(q_min+q_max)

    with transverse contraction factor

        rho_star = (q_max-q_min)/(q_max+q_min).
    """
    q = np.linalg.eigvalsh(0.5 * (K2 + K2.conj().T))
    q_pos = q[q > 1e-8]
    q_min = float(np.min(q_pos))
    q_max = float(np.max(q_pos))
    eps_star = 2.0 / (q_min + q_max)
    rho_star = (q_max - q_min) / (q_max + q_min)
    return q_min, q_max, eps_star, rho_star


def e47_restore_step(psi: np.ndarray, K2: np.ndarray, epsilon: float) -> np.ndarray:
    """
    Apply one dissipative linear restoration step

        psi' = (I - epsilon K^2) psi.

    This is a mathematical contraction map, not unitary time evolution.
    """
    I = np.eye(K2.shape[0], dtype=complex)
    Gamma = I - epsilon * K2
    return Gamma @ psi


# =============================================================================
# IV. LOG-BARRIER: VALID SCALAR CONSTRAINT, NOT AN E47 COUPLING
# =============================================================================

def logarithmic_barrier(
    n: float,
    n_min: float = 1.0,
    n_max: float = 100.0,
    mu: float = 0.01,
) -> float:
    if not (n_min < n < n_max):
        return float("inf")
    return float(-mu * (np.log(n - n_min) + np.log(n_max - n)))


def logarithmic_barrier_grad(
    n: float,
    n_min: float = 1.0,
    n_max: float = 100.0,
    mu: float = 0.01,
) -> float:
    if not (n_min < n < n_max):
        raise ValueError("Barrier gradient is defined only inside the interval.")
    return float(
        -mu * (
            1.0 / (n - n_min)
            - 1.0 / (n_max - n)
        )
    )


def logarithmic_barrier_hessian(
    n: float,
    n_min: float = 1.0,
    n_max: float = 100.0,
    mu: float = 0.01,
) -> float:
    if not (n_min < n < n_max):
        raise ValueError("Barrier Hessian is defined only inside the interval.")
    return float(
        mu / (n - n_min) ** 2
        + mu / (n_max - n) ** 2
    )


# =============================================================================
# V. TOPOLOGICAL CHARGE: CORRECT INTEGRATOR, SEPARATE FROM E47
# =============================================================================

def _triangle_solid_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Oriented solid angle for unit vectors a,b,c on S^2."""
    numerator = np.einsum("...i,...i->...", a, np.cross(b, c))
    denominator = (
        1.0
        + np.einsum("...i,...i->...", a, b)
        + np.einsum("...i,...i->...", b, c)
        + np.einsum("...i,...i->...", c, a)
    )
    return 2.0 * np.arctan2(numerator, denominator)


def lattice_topological_charge(texture: np.ndarray) -> float:
    """
    Compute lattice degree / skyrmion charge of an explicit S^2 texture.

    texture shape: (Ny, Nx, 3)

    Each plaquette is split into two oriented triangles.
    """
    texture = np.asarray(texture, dtype=float)
    if texture.ndim != 3 or texture.shape[-1] != 3:
        raise ValueError("texture must have shape (Ny, Nx, 3).")

    norms = np.linalg.norm(texture, axis=-1, keepdims=True)
    if np.any(norms == 0):
        raise ValueError("texture contains zero vectors.")

    n = texture / norms

    a = n[:-1, :-1]
    b = n[:-1, 1:]
    c = n[1:, 1:]
    d = n[1:, :-1]

    omega = (
        _triangle_solid_angle(a, b, c)
        + _triangle_solid_angle(a, c, d)
    )

    return float(np.sum(omega) / (4.0 * np.pi))


def canonical_skyrmion_texture(
    grid_size: int = 201,
    extent: float = 8.0,
    scale: float = 1.0,
) -> np.ndarray:
    """
    Standard degree-1 stereographic texture on a finite square.

    This validates the charge integrator only.
    It is NOT derived from an E47 state.
    """
    x = np.linspace(-extent, extent, grid_size)
    y = np.linspace(-extent, extent, grid_size)
    X, Y = np.meshgrid(x, y, indexing="xy")

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
# VI. ORIGINAL CASIMIR BUG REPRODUCTION
# =============================================================================

def incorrect_elementwise_casimir() -> np.ndarray:
    """
    Reproduce the structural error from the final supplied snippet:
    elementwise **2 and omission of total-generator cross terms.
    """
    Jx, Jy, Jz = spin_matrices(2)
    I5 = np.eye(5, dtype=complex)

    C_bad = np.zeros((125, 125), dtype=complex)
    for Op in (Jx, Jy, Jz):
        C_bad += (
            kron3(Op, I5, I5) ** 2
            + kron3(I5, Op, I5) ** 2
            + kron3(I5, I5, Op) ** 2
        )

    return 0.5 * (C_bad + C_bad.conj().T)


# =============================================================================
# VII. FULL VALIDATION
# =============================================================================

def validate_all() -> dict[str, Any]:
    report: list[dict[str, Any]] = []

    data = build_e47()
    Jx = data["Jx"]
    Jy = data["Jy"]
    Jz = data["Jz"]
    Jx_tot = data["Jx_tot"]
    Jy_tot = data["Jy_tot"]
    Jz_tot = data["Jz_tot"]
    C = data["C"]
    K = data["K"]
    K2 = data["K2"]
    P = data["P_E"]
    Q = data["Q_E"]
    eigvals_C = data["eigvals_C"]

    I5 = np.eye(5, dtype=complex)
    I125 = np.eye(125, dtype=complex)

    # -------------------------------------------------------------------------
    # A. Single-spin SU(2)
    # -------------------------------------------------------------------------
    comm_xy = Jx @ Jy - Jy @ Jx - 1j * Jz
    comm_yz = Jy @ Jz - Jz @ Jy - 1j * Jx
    comm_zx = Jz @ Jx - Jx @ Jz - 1j * Jy
    single_J2 = Jx @ Jx + Jy @ Jy + Jz @ Jz

    su2_residual = max(
        max_abs(comm_xy),
        max_abs(comm_yz),
        max_abs(comm_zx),
        max_abs(single_J2 - 6.0 * I5),
    )

    assert su2_residual < TOL
    record(
        report,
        "SU2-SPIN2",
        "PASS",
        "Spin-2 matrices satisfy the SU(2) commutators and J^2=6I.",
        max_residual=su2_residual,
    )

    # -------------------------------------------------------------------------
    # B. Tensor cube and total Casimir
    # -------------------------------------------------------------------------
    assert C.shape == (125, 125)
    total_comm_residual = max(
        max_abs(Jx_tot @ Jy_tot - Jy_tot @ Jx_tot - 1j * Jz_tot),
        max_abs(Jy_tot @ Jz_tot - Jz_tot @ Jy_tot - 1j * Jx_tot),
        max_abs(Jz_tot @ Jx_tot - Jx_tot @ Jz_tot - 1j * Jy_tot),
    )
    herm_C = max_abs(C - C.conj().T)

    assert total_comm_residual < 1e-9
    assert herm_C < TOL

    record(
        report,
        "CARRIER-125",
        "PASS",
        "V2 tensor V2 tensor V2 has dimension 125 and the total generators satisfy SU(2).",
        dimension=125,
        total_commutator_residual=total_comm_residual,
        casimir_hermiticity_residual=herm_C,
    )

    expected_counts = {
        0: 1,
        2: 9,
        6: 25,
        12: 28,
        20: 27,
        30: 22,
        42: 13,
    }

    rounded = np.rint(eigvals_C).astype(int)
    observed_counts = {
        int(v): int(np.sum(rounded == v))
        for v in sorted(set(rounded.tolist()))
    }

    max_round_error = float(np.max(np.abs(eigvals_C - rounded)))
    assert observed_counts == expected_counts
    assert max_round_error < 1e-9

    record(
        report,
        "CASIMIR-SPECTRUM",
        "PASS",
        "Total Casimir spectrum and eigenspace dimensions match the exact spin-coupling decomposition.",
        eigenvalue_counts=observed_counts,
        max_eigenvalue_roundoff=max_round_error,
    )

    # -------------------------------------------------------------------------
    # C. K, E47 projector, complement
    # -------------------------------------------------------------------------
    rank_P = int(round(np.trace(P).real))
    rank_Q = int(round(np.trace(Q).real))

    projector_residual = max_abs(P @ P - P)
    projector_herm = max_abs(P - P.conj().T)
    complement_residual = max_abs(Q @ Q - Q)
    pq_residual = max_abs(P @ Q)
    kp_residual = max_abs(K @ P)

    assert rank_P == 47
    assert rank_Q == 78
    assert projector_residual < 1e-10
    assert projector_herm < 1e-10
    assert complement_residual < 1e-10
    assert pq_residual < 1e-10
    assert kp_residual < 1e-8

    record(
        report,
        "E47-PROJECTOR",
        "PASS",
        "E47 = eigenspace(C,6) direct-sum eigenspace(C,30) has rank 47; P is Hermitian/idempotent and KP≈0.",
        rank_P=rank_P,
        rank_Q=rank_Q,
        P2_minus_P=projector_residual,
        P_hermiticity=projector_herm,
        PQ=pq_residual,
        KP=kp_residual,
    )

    # -------------------------------------------------------------------------
    # D. K^2 spectrum and optimal contraction
    # -------------------------------------------------------------------------
    q_min, q_max, eps_star, rho_star = optimal_e47_contraction(K2)

    assert np.isclose(q_min, 11664.0, atol=1e-6)
    assert np.isclose(q_max, 186624.0, atol=1e-6)
    assert np.isclose(eps_star, 1.0 / 99144.0, atol=1e-15)
    assert np.isclose(rho_star, 15.0 / 17.0, atol=1e-12)

    Gamma = I125 - eps_star * K2
    gamma_preserves_P = max_abs(Gamma @ P - P)
    p_gamma = max_abs(P @ Gamma - P)

    transverse = np.linalg.eigvalsh(
        0.5 * (Q @ Gamma @ Q + (Q @ Gamma @ Q).conj().T)
    )
    nonzero_transverse = transverse[np.abs(transverse) > 1e-9]
    observed_rho = float(np.max(np.abs(nonzero_transverse)))

    assert gamma_preserves_P < 1e-8
    assert p_gamma < 1e-8
    assert observed_rho <= rho_star + 1e-10

    record(
        report,
        "E47-CONTRACTION",
        "PASS",
        "Gamma = I - epsilon*K^2 preserves E47 and contracts the complement; the minimax step is epsilon*=1/99144 with rho*=15/17.",
        K2_gap=q_min,
        K2_max=q_max,
        epsilon_star=eps_star,
        rho_star=rho_star,
        observed_transverse_operator_radius=observed_rho,
        GammaP_minus_P=gamma_preserves_P,
        PGamma_minus_P=p_gamma,
    )

    # -------------------------------------------------------------------------
    # E. State decomposition and terminology correction
    # -------------------------------------------------------------------------
    psi = normalize(
        RNG.normal(size=125)
        + 1j * RNG.normal(size=125)
    )

    psi_E = P @ psi
    psi_perp = Q @ psi
    pythagorean_residual = abs(
        np.linalg.norm(psi) ** 2
        - np.linalg.norm(psi_E) ** 2
        - np.linalg.norm(psi_perp) ** 2
    )
    leakage = e47_leakage(psi, P)

    assert pythagorean_residual < 1e-10
    assert np.isclose(leakage, np.linalg.norm(psi_perp), atol=1e-12)

    record(
        report,
        "LEAKAGE-GEOMETRY",
        "PASS",
        "||(I-P)psi|| is the exact Hilbert-space distance from psi to E47 for an orthogonal projector.",
        leakage_norm=leakage,
        e47_weight=e47_weight(psi, P),
        pythagorean_residual=pythagorean_residual,
    )

    record(
        report,
        "INERTIAL-MASS-INTERPRETATION",
        "NOT_VALIDATED",
        "The supplied quantity called 'inertial mass' equals E47 leakage by definition, but no physical mass or Higgs-decoupling law is derived by the projector mathematics.",
        computational_proxy=leakage,
    )

    grad_N = np.array([0.1, -0.05, 0.02])
    thrust_proxy = synthetic_thrust_proxy(psi, P, grad_N, c=1.0)

    record(
        report,
        "THRUST-PROXY",
        "FORMAL_PROXY",
        "leakage*c^2*grad(N) is internally computable exactly as declared, but physical thrust/propulsion is not validated by this definition.",
        gradient_N=grad_N.tolist(),
        proxy_vector=thrust_proxy.tolist(),
        proxy_norm=float(np.linalg.norm(thrust_proxy)),
    )

    record(
        report,
        "GRAVITY-NULLIFICATION",
        "NOT_VALIDATED",
        "P psi = psi implies zero E47 leakage only. It does not establish gravitational or inertial nullification.",
    )

    record(
        report,
        "DECOHERENCE-TERMINOLOGY",
        "NOT_VALIDATED",
        "Projection leakage is mathematically defined. Calling it physical quantum decoherence requires a specified quantum channel/noise model and is not established here.",
    )

    # -------------------------------------------------------------------------
    # F. phi^n modulation degeneracy
    # -------------------------------------------------------------------------
    test_indices = [10.0, 45.0, 80.0]
    projected = [phi_scale_then_project(psi, n, P) for n in test_indices]
    normalized_projected = [normalize(v) for v in projected]

    direction_residuals = []
    for v in normalized_projected[1:]:
        phase = np.vdot(normalized_projected[0], v)
        aligned = v * np.exp(-1j * np.angle(phase))
        direction_residuals.append(float(np.linalg.norm(aligned - normalized_projected[0])))

    post_projection_residuals = [
        float(np.linalg.norm(Q @ normalize(v)))
        for v in projected
    ]

    max_direction_change = max(direction_residuals)
    max_post_projection_residual = max(post_projection_residuals)

    assert max_direction_change < 1e-10
    assert max_post_projection_residual < 1e-5

    record(
        report,
        "PHI-INDEX-SCALING",
        "REJECTED_AS_STRUCTURAL_MAP",
        "Multiplication by phi^n changes only global amplitude. After normalization, all tested n give the same projected Hilbert-space direction; n therefore does not encode a distinct sector or matter configuration in the supplied map.",
        tested_indices=test_indices,
        max_normalized_direction_change=max_direction_change,
        max_post_projection_leakage=max_post_projection_residual,
    )

    # n-attractor degeneracy: the original scan minimizes a quantity that is
    # already zero after projection.
    n_range = np.linspace(10.0, 80.0, 50)
    n_residuals = []
    for n in n_range:
        state_n = phi_scale_then_project(psi, float(n), P)
        n_residuals.append(float(np.linalg.norm(Q @ normalize(state_n))))

    record(
        report,
        "RECURSIVE-INDEX-ATTRACTOR",
        "REJECTED_AS_IDENTIFIABLE",
        "The proposed n-attractor scan is degenerate because every P-projected state lies in E47 for every n. Numerical minima can only reflect roundoff/scale, not a unique structural optimum.",
        residual_min=float(np.min(n_residuals)),
        residual_max=float(np.max(n_residuals)),
        n_count=len(n_residuals),
    )

    # -------------------------------------------------------------------------
    # G. Centered Casimir probe
    # -------------------------------------------------------------------------
    probe = centered_casimir_probe(psi, C, center=18.0)
    assert abs(probe.imag) < 1e-10
    assert -18.0 - 1e-10 <= probe.real <= 24.0 + 1e-10

    record(
        report,
        "CASIMIR-CENTERED-PROBE",
        "PASS_WITH_REINTERPRETATION",
        "<psi|(C-18I)|psi> is a valid real centered spectral expectation. It is not, by itself, a transition or edge-state detector.",
        value_real=float(probe.real),
        value_imag=float(probe.imag),
        spectral_bounds=[-18.0, 24.0],
    )

    # -------------------------------------------------------------------------
    # H. Perturbation sensitivity
    # -------------------------------------------------------------------------
    delta = 1e-3 * (
        RNG.normal(size=125)
        + 1j * RNG.normal(size=125)
    )
    leakage_change_vector = Q @ (psi + delta) - Q @ psi
    lhs = float(np.linalg.norm(leakage_change_vector))
    rhs = float(np.linalg.norm(delta))

    assert lhs <= rhs + 1e-12

    record(
        report,
        "PROJECTOR-SENSITIVITY",
        "PASS",
        "Orthogonal projection is non-expansive: ||Q(psi+delta)-Q psi|| <= ||delta||.",
        projected_perturbation_norm=lhs,
        perturbation_norm=rhs,
        ratio=lhs / rhs,
    )

    # -------------------------------------------------------------------------
    # I. Active E47 restoration: corrected controller
    # -------------------------------------------------------------------------
    psi_kernel = normalize(P @ (
        RNG.normal(size=125) + 1j * RNG.normal(size=125)
    ))
    perturbation = Q @ (
        RNG.normal(size=125) + 1j * RNG.normal(size=125)
    )
    perturbation = 0.25 * normalize(perturbation)

    psi_perturbed = psi_kernel + perturbation
    initial_leakage = float(np.linalg.norm(Q @ psi_perturbed))

    state = psi_perturbed.copy()
    telemetry = []

    for step in range(21):
        leak = float(np.linalg.norm(Q @ state))
        telemetry.append(
            {
                "step": step,
                "leakage_norm": leak,
                "e47_component_norm": float(np.linalg.norm(P @ state)),
                "state_norm": float(np.linalg.norm(state)),
            }
        )

        bound = (rho_star ** step) * initial_leakage
        assert leak <= bound + 1e-9

        if step < 20:
            state = e47_restore_step(state, K2, eps_star)

    final_leakage = float(np.linalg.norm(Q @ state))

    assert final_leakage < initial_leakage

    record(
        report,
        "ACTIVE-E47-STABILIZER",
        "PASS",
        "The error-corrected stabilizer acts on the state itself via Gamma=I-epsilon*K^2 and contracts E47 leakage with the certified rho*=15/17 bound.",
        initial_leakage=initial_leakage,
        final_leakage=final_leakage,
        steps=20,
        certified_bound=(rho_star ** 20) * initial_leakage,
    )

    with TELEMETRY_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "step",
                "leakage_norm",
                "e47_component_norm",
                "state_norm",
            ],
        )
        writer.writeheader()
        writer.writerows(telemetry)

    record(
        report,
        "TELEMETRY",
        "PASS",
        "Telemetry now logs actual E47 restoration observables rather than labeling a synthetic proxy as thrust.",
        rows=len(telemetry),
        columns=[
            "step",
            "leakage_norm",
            "e47_component_norm",
            "state_norm",
        ],
    )

    # -------------------------------------------------------------------------
    # J. Barrier validation
    # -------------------------------------------------------------------------
    interior = np.linspace(1.5, 99.5, 200)
    hessians = np.array([logarithmic_barrier_hessian(float(n)) for n in interior])
    assert np.all(hessians > 0.0)

    near_left = logarithmic_barrier(1.0 + 1e-9)
    center_barrier = logarithmic_barrier(50.5)
    near_right = logarithmic_barrier(100.0 - 1e-9)

    assert near_left > center_barrier
    assert near_right > center_barrier

    record(
        report,
        "LOG-BARRIER",
        "PASS_AS_SCALAR_CONSTRAINT",
        "The logarithmic barrier is convex on (n_min,n_max) and diverges toward the boundaries. It does not stabilize E47 unless n is given an independently defined coupling to the state dynamics.",
        min_hessian=float(np.min(hessians)),
        center_value=center_barrier,
        near_left_value=near_left,
        near_right_value=near_right,
        center_gradient=logarithmic_barrier_grad(50.5),
    )

    # -------------------------------------------------------------------------
    # K. Skyrmion / topology
    # -------------------------------------------------------------------------
    record(
        report,
        "E47-TO-SKYRMION-MAP",
        "NOT_EXECUTABLE",
        "The supplied code never defines a map from a 125D E47 state to a spatial S^2 texture n(x,y). Therefore an E47-derived Pontryagin/skyrmion charge cannot be validated from the supplied formalism.",
    )

    texture = canonical_skyrmion_texture(
        grid_size=201,
        extent=8.0,
        scale=1.0,
    )
    Q_top = lattice_topological_charge(texture)

    assert abs(abs(Q_top) - 1.0) < 0.03

    record(
        report,
        "LATTICE-TOPOLOGICAL-CHARGE",
        "PASS_INDEPENDENT_DEMONSTRATION",
        "A corrected solid-angle lattice integrator recovers unit topological charge on a standard explicit skyrmion texture. This validates the integrator, not an E47-to-texture bridge.",
        computed_charge=Q_top,
        absolute_charge_error=abs(abs(Q_top) - 1.0),
        grid_size=201,
        extent=8.0,
    )

    record(
        report,
        "ORIGINAL-ZERO-TEXTURE-QUANTIZATION",
        "REJECTED_AS_TRIVIAL",
        "The supplied placeholder returned an all-zero density, so Q=0 and the integer test passed tautologically. That is not evidence for a Q=1 skyrmion sector.",
    )

    # -------------------------------------------------------------------------
    # L. Explicitly reject the erroneous final Casimir construction
    # -------------------------------------------------------------------------
    C_bad = incorrect_elementwise_casimir()
    bad_distance = float(np.linalg.norm(C_bad - C, ord="fro"))
    bad_vals = np.linalg.eigvalsh(C_bad)
    bad_rounded = np.rint(bad_vals).astype(int)
    bad_counts = {
        int(v): int(np.sum(bad_rounded == v))
        for v in sorted(set(bad_rounded.tolist()))
    }

    assert bad_distance > 1.0
    assert bad_counts != expected_counts

    record(
        report,
        "FINAL-SNIPPET-CASIMIR",
        "REJECTED_AND_CORRECTED",
        "The final supplied Casimir builder used elementwise **2 and omitted cross terms from (J1+J2+J3)^2. The correct total-generator construction is used everywhere in this validator.",
        frobenius_distance_from_correct_C=bad_distance,
        incorrect_rounded_spectrum_counts=bad_counts,
    )

    # -------------------------------------------------------------------------
    # M. Physical-claim boundary
    # -------------------------------------------------------------------------
    for test_id, statement in [
        (
            "HIGGS-DECOUPLING",
            "No Higgs-sector coupling, Lagrangian, or Standard Model mass map is specified, so Higgs decoupling is not validated.",
        ),
        (
            "PHYSICAL-PROPULSION",
            "No physical force law, spacetime dynamics, energy-momentum balance, dimensions, or experimental data derive the synthetic thrust proxy as propulsion.",
        ),
        (
            "MATTER-PROGRAMMING",
            "Scalar phi^n rescaling plus projection does not reconfigure topology or matter; an n-dependent operator or independently derived state map would be required.",
        ),
        (
            "GRAVITATIONAL-COUPLING",
            "No metric, stress-energy tensor, Newtonian gravitational field, or coupling law connects E47 leakage to gravity in the supplied executable formalism.",
        ),
        (
            "SOVEREIGN-SUBSPACE-LANGUAGE",
            "E47 is mathematically a selected invariant subspace. 'Sovereign' is interpretive terminology, not an additional theorem.",
        ),
    ]:
        record(report, test_id, "NOT_VALIDATED", statement)

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    status_counts: dict[str, int] = {}
    for item in report:
        status_counts[item["status"]] = status_counts.get(item["status"], 0) + 1

    summary = {
        "overall": "RIGOROUS_CORE_PASS_WITH_INTERPRETATION_BOUNDARIES",
        "status_counts": status_counts,
        "validated_core": [
            "spin-2 SU(2) algebra",
            "125-dimensional tensor cube",
            "total Casimir spectrum",
            "E47 rank-47 projector",
            "78-dimensional orthogonal complement",
            "K and K^2 spectral data",
            "optimal E47 contraction Gamma=I-epsilon*K^2",
            "orthogonal-projection leakage geometry",
            "projector perturbation sensitivity bound",
            "state-space restoration / leakage contraction",
            "log-barrier scalar convexity",
            "independent lattice topological-charge integrator",
        ],
        "rejected_or_unresolved": [
            "physical inertial-mass interpretation of leakage",
            "gravity nullification",
            "physical thrust / propulsion",
            "matter programming by scalar phi^n rescaling",
            "unique recursion-index attractor",
            "physical decoherence without a quantum channel",
            "E47-to-skyrmion spatial texture bridge",
            "original all-zero texture quantization test",
            "original final elementwise-square Casimir builder",
        ],
    }

    full_report = {
        "summary": summary,
        "tests": report,
    }

    REPORT_PATH.write_text(
        json.dumps(full_report, indent=2),
        encoding="utf-8",
    )

    return full_report


if __name__ == "__main__":
    result = validate_all()

    print("=== E47 / KKP FULL VALIDATION ===")
    print("Overall:", result["summary"]["overall"])
    print("Status counts:")
    for key, value in sorted(result["summary"]["status_counts"].items()):
        print(f"  {key}: {value}")

    print("\nSelected machine-validated facts:")
    for item in result["tests"]:
        if item["status"] in {
            "PASS",
            "PASS_WITH_REINTERPRETATION",
            "PASS_AS_SCALAR_CONSTRAINT",
            "PASS_INDEPENDENT_DEMONSTRATION",
        }:
            print(f"  [{item['status']}] {item['id']}: {item['statement']}")

    print("\nBoundary findings:")
    for item in result["tests"]:
        if item["status"] in {
            "NOT_VALIDATED",
            "NOT_EXECUTABLE",
            "REJECTED_AS_STRUCTURAL_MAP",
            "REJECTED_AS_IDENTIFIABLE",
            "REJECTED_AS_TRIVIAL",
            "REJECTED_AND_CORRECTED",
            "FORMAL_PROXY",
        }:
            print(f"  [{item['status']}] {item['id']}: {item['statement']}")

    print(f"\nWrote: {REPORT_PATH}")
    print(f"Wrote: {TELEMETRY_PATH}")
