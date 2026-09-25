"""Error-corrected Native Variational Quantum Eigensolver (N-VQE).

The historical golden-ratio Babylonian recursion is retained as a classical
Heron/Newton map. Quantum status begins only after an explicit Hilbert space
and self-adjoint Hamiltonian are supplied.

Exact E47 Hilbert-space specialization
--------------------------------------
H_N-VQE = K^2
E_N-VQE(psi) = <psi|K^2|psi> = ||K psi||^2 >= 0
Ground(H_N-VQE) = ker(K) = E47

A 125 -> 128 isometric statevector lift is also provided. The three padding
states receive a positive penalty, so the 7-qubit Hamiltonian retains exactly
the same 47-dimensional ground space.

Scope
-----
This module proves and validates finite-dimensional spectral and statevector
statements only. It does not establish consciousness, biological quantum
computation, physical hardware implementation, or universal cross-domain
cognition claims.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
import qutip as qt

from .su2_kernel import (
    CANONICAL_K2_MAX_EIGENVALUE,
    CANONICAL_SPECTRAL_GAP,
    E47_DIMENSION,
    E47Operators,
    build_e47_operators,
)

OPTIMAL_EPSILON: Final[float] = 1.0 / 99144.0
OPTIMAL_TRANSIENT_BOUND: Final[float] = 15.0 / 17.0
PHI: Final[float] = (1.0 + np.sqrt(5.0)) / 2.0
HERON_SEED: Final[float] = PHI ** -5
HERON_FIXED_POINT: Final[float] = PHI ** (-5.0 / 2.0)
SEVEN_QUBIT_DIMENSION: Final[int] = 128



@dataclass(frozen=True)
class SevenQubitSample:
    tau: float
    energy: float
    ground_weight: float


def heron_step(x: float, *, seed: float = HERON_SEED) -> float:
    """One positive Heron/Newton step for x^2 = seed.

    T(x) = 1/2 (x + seed/x). This map is classical. For seed > 0 and x > 0
    its unique positive fixed point is sqrt(seed).
    """
    if seed <= 0 or x <= 0:
        raise ValueError("seed and x must be positive")
    return 0.5 * (float(x) + float(seed) / float(x))


def heron_error_identity_residual(x: float, *, seed: float = HERON_SEED) -> float:
    """Residual of e_next = e^2/(2x), the exact quadratic error identity."""
    if seed <= 0 or x <= 0:
        raise ValueError("seed and x must be positive")
    target = float(np.sqrt(seed))
    lhs = heron_step(x, seed=seed) - target
    rhs = (float(x) - target) ** 2 / (2.0 * float(x))
    return abs(lhs - rhs)


def seven_qubit_hamiltonian(
    operators: E47Operators | None = None,
    *,
    padding_penalty: float = CANONICAL_K2_MAX_EIGENVALUE,
) -> qt.Qobj:
    """Embed K^2 into 7 qubits while penalizing the three unused basis states.

    H_128 = K^2 ⊕ padding_penalty * I_3.

    The embedding is a dense statevector/Hilbert-space construction, not a
    claim of locality or a hardware-native seven-qubit interaction graph.
    """
    if padding_penalty <= 0:
        raise ValueError("padding_penalty must be positive")
    ops = operators or build_e47_operators()
    dense = np.zeros((SEVEN_QUBIT_DIMENSION, SEVEN_QUBIT_DIMENSION), dtype=complex)
    dense[:125, :125] = ops.kernel_squared.full()
    dense[125:, 125:] = float(padding_penalty) * np.eye(3)
    return qt.Qobj(dense, dims=[[2] * 7, [2] * 7])


def simulate_seven_qubit_imaginary_time(
    operators: E47Operators | None = None,
    *,
    taus: tuple[float, ...] = (0.0, 1.0, 2.0, 4.0, 8.0, 12.0),
    seed: int = 20260925,
) -> tuple[SevenQubitSample, ...]:
    """Normalized imaginary-time statevector simulation on the 7-qubit lift.

    Evolution uses exp[-tau H/gap], where tau is dimensionless. Imaginary
    time is non-unitary and is used here as a ground-space projection
    simulation, not as physical real-time evolution.
    """
    if any(tau < 0 for tau in taus):
        raise ValueError("taus must be nonnegative")

    h = seven_qubit_hamiltonian(operators).full()
    eigenvalues, eigenvectors = np.linalg.eigh(h)
    ground_mask = np.abs(eigenvalues) < 1e-8
    positive = eigenvalues[~ground_mask]
    gap = float(np.min(positive))

    rng = np.random.default_rng(seed)
    psi0 = rng.normal(size=SEVEN_QUBIT_DIMENSION) + 1j * rng.normal(
        size=SEVEN_QUBIT_DIMENSION
    )
    psi0 = psi0 / np.linalg.norm(psi0)
    coeff = eigenvectors.conj().T @ psi0
    p_ground = eigenvectors[:, ground_mask] @ eigenvectors[:, ground_mask].conj().T

    samples: list[SevenQubitSample] = []
    for tau in taus:
        psi = eigenvectors @ (np.exp(-float(tau) * eigenvalues / gap) * coeff)
        psi = psi / np.linalg.norm(psi)
        energy = float(np.real(np.vdot(psi, h @ psi)))
        ground_weight = float(np.real(np.vdot(psi, p_ground @ psi)))
        samples.append(
            SevenQubitSample(
                tau=float(tau),
                energy=energy,
                ground_weight=ground_weight,
            )
        )
    return tuple(samples)

@dataclass(frozen=True)
class NVEValidation:
    status: str
    ground_energy: float
    ground_dimension: int
    spectral_gap: float
    max_eigenvalue: float
    projector_residual: float
    contraction_spectral_radius: float
    checks: dict[str, bool]


def _normalized(state: qt.Qobj) -> qt.Qobj:
    norm = float(state.norm())
    if norm == 0:
        raise ValueError("state must be nonzero")
    return state / norm


def rayleigh_energy(state: qt.Qobj, hamiltonian: qt.Qobj) -> float:
    """Return the normalized Rayleigh quotient <psi|H|psi>."""
    psi = _normalized(state)
    value = qt.expect(hamiltonian, psi)
    return float(np.real_if_close(value))


def eigen_residual(state: qt.Qobj, hamiltonian: qt.Qobj) -> float:
    """Return ||H psi - E psi|| for normalized psi.

    A zero residual certifies that the state is an eigenvector. A stationary
    point in an arbitrary restricted parameterization does not imply this
    residual vanishes.
    """
    psi = _normalized(state)
    energy = rayleigh_energy(psi, hamiltonian)
    return float((hamiltonian * psi - energy * psi).norm())


def e47_nve_energy(
    state: qt.Qobj,
    operators: E47Operators | None = None,
) -> float:
    """Exact E47 objective E_NVE = <psi|K^2|psi> = ||K psi||^2."""
    ops = operators or build_e47_operators()
    return rayleigh_energy(state, ops.kernel_squared)


def construct_e47_ground_projector(
    operators: E47Operators | None = None,
    *,
    tolerance: float = 1e-9,
) -> qt.Qobj:
    """Construct the orthogonal projector onto the zero eigenspace of K^2."""
    ops = operators or build_e47_operators()
    eigenvalues, eigenstates = ops.kernel_squared.eigenstates()
    ground = [
        ket
        for value, ket in zip(eigenvalues, eigenstates)
        if abs(float(np.real(value))) < tolerance
    ]
    if not ground:
        raise RuntimeError("K^2 has no detected ground eigenspace")
    projector = sum((ket * ket.dag() for ket in ground), 0 * ops.identity_total)
    return projector


def e47_continuous_flow(
    state: qt.Qobj,
    time: float,
    operators: E47Operators | None = None,
) -> qt.Qobj:
    """Apply exp(-t K^2) to a state."""
    if time < 0:
        raise ValueError("time must be nonnegative")
    ops = operators or build_e47_operators()
    return (-float(time) * ops.kernel_squared).expm() * state


def e47_discrete_flow(
    state: qt.Qobj,
    steps: int,
    operators: E47Operators | None = None,
    *,
    epsilon: float = OPTIMAL_EPSILON,
) -> qt.Qobj:
    """Apply Gamma^n where Gamma = I - epsilon K^2."""
    if steps < 0:
        raise ValueError("steps must be nonnegative")
    ops = operators or build_e47_operators()
    gamma = ops.identity_total - float(epsilon) * ops.kernel_squared
    evolved = state
    for _ in range(int(steps)):
        evolved = gamma * evolved
    return evolved


def validate_e47_nve(
    operators: E47Operators | None = None,
    *,
    tolerance: float = 1e-8,
) -> NVEValidation:
    """Validate the exact E47 NVE theorem directly from K^2."""
    ops = operators or build_e47_operators()
    eigenvalues = np.sort(np.real(ops.kernel_squared.eigenenergies()))
    zero_mask = np.abs(eigenvalues) < tolerance
    positive = eigenvalues[~zero_mask]

    ground_energy = float(np.min(eigenvalues))
    ground_dimension = int(np.sum(zero_mask))
    spectral_gap = float(np.min(positive))
    max_eigenvalue = float(np.max(eigenvalues))

    projector = construct_e47_ground_projector(ops, tolerance=tolerance)
    projector_residual = float((ops.kernel_squared * projector).norm())

    contraction_spectral_radius = max(
        abs(1.0 - OPTIMAL_EPSILON * float(value))
        for value in positive
    )

    checks = {
        "positive_semidefinite": ground_energy >= -tolerance,
        "ground_energy_zero": abs(ground_energy) < tolerance,
        "ground_dimension_47": ground_dimension == E47_DIMENSION,
        "gap_11664": abs(spectral_gap - CANONICAL_SPECTRAL_GAP) < tolerance,
        "max_186624": abs(max_eigenvalue - CANONICAL_K2_MAX_EIGENVALUE) < tolerance,
        "ground_projector_annihilated": projector_residual < tolerance,
        "optimal_transient_15_over_17": abs(
            contraction_spectral_radius - OPTIMAL_TRANSIENT_BOUND
        ) < tolerance,
    }

    return NVEValidation(
        status="pass" if all(checks.values()) else "fail",
        ground_energy=ground_energy,
        ground_dimension=ground_dimension,
        spectral_gap=spectral_gap,
        max_eigenvalue=max_eigenvalue,
        projector_residual=projector_residual,
        contraction_spectral_radius=contraction_spectral_radius,
        checks=checks,
    )


__all__ = [
    "HERON_FIXED_POINT",
    "HERON_SEED",
    "NVEValidation",
    "PHI",
    "SEVEN_QUBIT_DIMENSION",
    "SevenQubitSample",
    "OPTIMAL_EPSILON",
    "OPTIMAL_TRANSIENT_BOUND",
    "construct_e47_ground_projector",
    "heron_error_identity_residual",
    "heron_step",
    "e47_continuous_flow",
    "e47_discrete_flow",
    "e47_nve_energy",
    "eigen_residual",
    "rayleigh_energy",
    "seven_qubit_hamiltonian",
    "simulate_seven_qubit_imaginary_time",
    "validate_e47_nve",
]
