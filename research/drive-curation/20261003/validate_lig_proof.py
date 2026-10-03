#!/usr/bin/env python3
"""Independent numerical validation of the L_IG invariant-projection proof.

The script constructs the E47 carrier from spin-2 generators and validates the
finite-dimensional theorem used by L_IG. It does not treat Haar Monte Carlo,
coalgebraic terminology, dialect translations, or the N_inv/N_diff comparison
as substitutes for their respective formal or external proofs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import numpy as np


TOL = 2.0e-10
SEED = 0
HAAR_N = 10_000


def spin_generators(j: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return Hermitian Jx, Jy, Jz in the |j,m> basis."""
    m = np.arange(-j, j + 1, dtype=float)
    dim = m.size
    jp = np.zeros((dim, dim), dtype=complex)
    for col, magnetic in enumerate(m[:-1]):
        jp[col + 1, col] = np.sqrt(j * (j + 1) - magnetic * (magnetic + 1))
    jm = jp.conj().T
    jx = (jp + jm) / 2.0
    jy = (jp - jm) / (2.0j)
    jz = np.diag(m)
    return jx, jy, jz


def kron3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.kron(np.kron(a, b), c)


def carrier() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Construct V_2 tensor-cubed and its total Casimir C."""
    jx, jy, jz = spin_generators(2)
    ident = np.eye(5, dtype=complex)
    totals = []
    for generator in (jx, jy, jz):
        totals.append(
            kron3(generator, ident, ident)
            + kron3(ident, generator, ident)
            + kron3(ident, ident, generator)
        )
    c = sum((generator @ generator for generator in totals), start=np.zeros((125, 125), dtype=complex))
    return c, *totals


def projector_from_kernel(q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return the numerical orthogonal projector onto ker(q) and eigenvalues."""
    eigenvalues, eigenvectors = np.linalg.eigh(q)
    scale = max(1.0, float(np.max(np.abs(eigenvalues))))
    mask = np.abs(eigenvalues) <= 1.0e-9 * scale
    basis = eigenvectors[:, mask]
    p = basis @ basis.conj().T
    return p, eigenvalues


def operator_residual(a: np.ndarray) -> float:
    return float(np.linalg.norm(a, ord=2))


def coalgebra_step(x: np.ndarray, gamma: np.ndarray, p: np.ndarray) -> tuple[float, np.ndarray]:
    """One deterministic F(X)=R x X coalgebra step."""
    occupancy = float(np.real(np.vdot(x, p @ x)))
    return occupancy, gamma @ x


@dataclass
class Report:
    dimension: int
    casimir_spectrum: list[float]
    casimir_multiplicities: list[int]
    kernel_dimension: int
    projector_rank: int
    trace_projector: float
    projector_idempotence_residual: float
    projector_hermitian_residual: float
    annihilation_residual: float
    q_positive_min: float
    q_positive_max: float
    epsilon_max: float
    epsilon_star: float
    rho_star: float
    contraction_residual_n250: float
    coalgebra_limit_residual: float
    conjugacy_projector_residual: float
    conjugacy_observable_residual: float
    haar_mean: float
    haar_standard_deviation: float
    haar_standard_error: float
    haar_expected_mean: float
    haar_expected_variance: float
    haar_mean_z_score: float
    conditional_efficiency_ratio_at_1e3: float


def main() -> None:
    c, *_ = carrier()
    q_target = (c - 6.0 * np.eye(125)) @ (c - 30.0 * np.eye(125))
    q = q_target.conj().T @ q_target
    k = q_target

    c_values, c_vectors = np.linalg.eigh(c)
    rounded = np.rint(c_values).astype(int)
    spectrum, counts = np.unique(rounded, return_counts=True)

    p, q_values = projector_from_kernel(q)
    q_nonzero = q_values[q_values > 1.0e-7]
    q_min = float(np.min(q_nonzero))
    q_max = float(np.max(q_nonzero))
    epsilon_max = 2.0 / q_max
    epsilon_star = 2.0 / (q_min + q_max)
    rho_star = (q_max - q_min) / (q_max + q_min)
    gamma = np.eye(125) - epsilon_star * q

    gamma_n = np.linalg.matrix_power(gamma, 250)
    contraction_residual = operator_residual(gamma_n - p)

    rng = np.random.default_rng(SEED)
    x = rng.normal(size=125) + 1.0j * rng.normal(size=125)
    x /= np.linalg.norm(x)
    x_limit = x.copy()
    observations = []
    for _ in range(250):
        observation, x_limit = coalgebra_step(x_limit, gamma, p)
        observations.append(observation)
    coalgebra_limit_residual = float(np.linalg.norm(x_limit - p @ x))

    # Orthogonal conjugacy: a concrete bisimulation-preserving transformation.
    real_basis = rng.normal(size=(125, 125))
    u, _ = np.linalg.qr(real_basis)
    k_conjugate = u @ k.real @ u.T
    q_conjugate = k_conjugate.T @ k_conjugate
    p_conjugate_expected = u @ p.real @ u.T
    p_conjugate, _ = projector_from_kernel(q_conjugate)
    x_real = x.real
    x_conjugate = u @ x_real
    conjugacy_projector_residual = operator_residual(p_conjugate - p_conjugate_expected)
    original_observation = float(x_real @ p.real @ x_real)
    conjugate_observation = float(x_conjugate @ p_conjugate @ x_conjugate)
    conjugacy_observable_residual = abs(original_observation - conjugate_observation)
    assert operator_residual(k_conjugate @ p_conjugate) < 1.0e-8

    # Haar-random complex pure-state occupancy test.
    haar = rng.normal(size=(HAAR_N, 125)) + 1.0j * rng.normal(size=(HAAR_N, 125))
    haar /= np.linalg.norm(haar, axis=1, keepdims=True)
    projected = haar @ p
    occupancies = np.real(np.sum(projected.conj() * haar, axis=1))
    haar_mean = float(np.mean(occupancies))
    haar_sd = float(np.std(occupancies, ddof=1))
    haar_se = haar_sd / np.sqrt(HAAR_N)
    expected_mean = 47.0 / 125.0
    expected_variance = (47.0 * (125.0 - 47.0)) / (125.0**2 * 126.0)
    haar_z = (haar_mean - expected_mean) / haar_se

    conditional_ratio = 1.0 / (1.0e-3**2 * np.log(1.0e3))

    report = Report(
        dimension=c.shape[0],
        casimir_spectrum=spectrum.astype(float).tolist(),
        casimir_multiplicities=counts.astype(int).tolist(),
        kernel_dimension=int(np.rint(np.trace(p).real)),
        projector_rank=int(np.linalg.matrix_rank(p, tol=1.0e-8)),
        trace_projector=float(np.trace(p).real),
        projector_idempotence_residual=operator_residual(p @ p - p),
        projector_hermitian_residual=operator_residual(p.conj().T - p),
        annihilation_residual=operator_residual(k @ p),
        q_positive_min=q_min,
        q_positive_max=q_max,
        epsilon_max=epsilon_max,
        epsilon_star=epsilon_star,
        rho_star=rho_star,
        contraction_residual_n250=contraction_residual,
        coalgebra_limit_residual=coalgebra_limit_residual,
        conjugacy_projector_residual=conjugacy_projector_residual,
        conjugacy_observable_residual=conjugacy_observable_residual,
        haar_mean=haar_mean,
        haar_standard_deviation=haar_sd,
        haar_standard_error=haar_se,
        haar_expected_mean=expected_mean,
        haar_expected_variance=expected_variance,
        haar_mean_z_score=float(haar_z),
        conditional_efficiency_ratio_at_1e3=float(conditional_ratio),
    )

    assert report.dimension == 125
    assert report.casimir_spectrum == [0.0, 2.0, 6.0, 12.0, 20.0, 30.0, 42.0]
    assert report.casimir_multiplicities == [1, 9, 25, 28, 27, 22, 13]
    assert report.kernel_dimension == 47
    assert report.projector_rank == 47
    assert abs(report.trace_projector - 47.0) < 1.0e-8
    assert report.projector_idempotence_residual < TOL
    assert report.projector_hermitian_residual < TOL
    assert report.annihilation_residual < 1.0e-8
    assert abs(report.epsilon_max - 1.0 / 93312.0) < 1.0e-10
    assert abs(report.epsilon_star - 1.0 / 99144.0) < 1.0e-10
    assert abs(report.rho_star - 15.0 / 17.0) < 1.0e-10
    assert report.contraction_residual_n250 < 1.0e-10
    assert report.coalgebra_limit_residual < 1.0e-10
    assert report.conjugacy_observable_residual < 1.0e-10
    assert abs(report.haar_mean - report.haar_expected_mean) < 6.0 * report.haar_standard_error
    assert abs(report.haar_standard_deviation**2 - report.haar_expected_variance) < 5.0e-4

    print(json.dumps(asdict(report), indent=2))
    print("VALIDATION: PASS")
    print("STATUS: E0 finite-dimensional theorem numerically reconstructed; Haar result is E2 support.")
    print("PENDING: external E3 N_inv versus N_diff benchmark and formal dialect certificates.")


if __name__ == "__main__":
    main()
