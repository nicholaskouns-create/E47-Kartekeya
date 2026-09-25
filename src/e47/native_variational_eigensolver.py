"""Error-corrected Native Variational Eigensolver (NVE).

Generic variational claims are kept separate from the exact E47 specialization.

Exact E47 specialization
------------------------
H_NVE = K^2
E_NVE(psi) = <psi|K^2|psi> = ||K psi||^2 >= 0
Ground(H_NVE) = ker(K) = E47

Scope
-----
This module proves and validates finite-dimensional spectral statements only.
It does not establish consciousness, physical quantum hardware, or universal
cross-domain cognition claims.
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
    return (gamma ** int(steps)) * state


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

    gamma = ops.identity_total - OPTIMAL_EPSILON * ops.kernel_squared
    gamma_eigs = np.real(gamma.eigenenergies())
    transient = [
        abs(float(value))
        for value, k2_value in zip(gamma_eigs, eigenvalues)
        if abs(float(k2_value)) >= tolerance
    ]
    contraction_spectral_radius = max(transient)

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
    "NVEValidation",
    "OPTIMAL_EPSILON",
    "OPTIMAL_TRANSIENT_BOUND",
    "construct_e47_ground_projector",
    "e47_continuous_flow",
    "e47_discrete_flow",
    "e47_nve_energy",
    "eigen_residual",
    "rayleigh_energy",
    "validate_e47_nve",
]
