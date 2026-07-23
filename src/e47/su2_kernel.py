"""Canonical E47 SU(2) kernel algebra and validation.

This module builds the canonical spin-2 three-body carrier

    V = V₂ ⊗ V₂ ⊗ V₂,

constructs the total SU(2) Casimir operator

    C = Jx_total² + Jy_total² + Jz_total²,

and defines the canonical E47 kernel operator

    K = (C - 6I)(C - 30I).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import qutip as qt


CANONICAL_SINGLE_SPIN = 2.0
SINGLE_REPRESENTATION_DIMENSION = 5
EXPECTED_CARRIER_DIMENSION = 125
EXPECTED_KERNEL_DIMENSION = 47
EXPECTED_COHERENCE_FRACTION = EXPECTED_KERNEL_DIMENSION / EXPECTED_CARRIER_DIMENSION
EXPECTED_K2_SPECTRAL_GAP = 11_664
EXPECTED_K2_MAX_EIGENVALUE = 186_624
CASIMIR_ROOTS = (6.0, 30.0)


@dataclass(frozen=True)
class E47Operators:
    """Canonical SU(2) operators for the E47 construction."""

    single_spin: float
    single_dimension: int
    carrier_dimension: int
    identity_total: qt.Qobj
    total_jx: qt.Qobj
    total_jy: qt.Qobj
    total_jz: qt.Qobj
    casimir: qt.Qobj
    kernel: qt.Qobj
    kernel_squared: qt.Qobj


@dataclass(frozen=True)
class KernelValidation:
    """Structured validation output for the canonical E47 kernel."""

    inputs: dict[str, Any]
    results: dict[str, Any]
    tolerances: dict[str, float]
    checks: dict[str, dict[str, Any]]
    status: str


def build_e47_operators() -> E47Operators:
    """Construct the canonical SU(2) operators on V₂ ⊗ V₂ ⊗ V₂."""

    jx, jy, jz = qt.jmat(CANONICAL_SINGLE_SPIN)
    identity_single = qt.qeye(SINGLE_REPRESENTATION_DIMENSION)
    identity_total = qt.tensor(identity_single, identity_single, identity_single)

    total_jx = (
        qt.tensor(jx, identity_single, identity_single)
        + qt.tensor(identity_single, jx, identity_single)
        + qt.tensor(identity_single, identity_single, jx)
    )
    total_jy = (
        qt.tensor(jy, identity_single, identity_single)
        + qt.tensor(identity_single, jy, identity_single)
        + qt.tensor(identity_single, identity_single, jy)
    )
    total_jz = (
        qt.tensor(jz, identity_single, identity_single)
        + qt.tensor(identity_single, jz, identity_single)
        + qt.tensor(identity_single, identity_single, jz)
    )

    casimir = total_jx * total_jx + total_jy * total_jy + total_jz * total_jz
    casimir = 0.5 * (casimir + casimir.dag())

    kernel = (casimir - CASIMIR_ROOTS[0] * identity_total) * (
        casimir - CASIMIR_ROOTS[1] * identity_total
    )
    kernel = 0.5 * (kernel + kernel.dag())

    kernel_squared = kernel * kernel
    kernel_squared = 0.5 * (kernel_squared + kernel_squared.dag())

    return E47Operators(
        single_spin=CANONICAL_SINGLE_SPIN,
        single_dimension=SINGLE_REPRESENTATION_DIMENSION,
        carrier_dimension=identity_total.shape[0],
        identity_total=identity_total,
        total_jx=total_jx,
        total_jy=total_jy,
        total_jz=total_jz,
        casimir=casimir,
        kernel=kernel,
        kernel_squared=kernel_squared,
    )


def validate_e47_kernel(
    operators: E47Operators | None = None,
    *,
    kernel_tolerance: float = 1e-8,
    hermiticity_tolerance: float = 1e-10,
) -> KernelValidation:
    """Validate the canonical E47 SU(2) kernel construction."""

    if kernel_tolerance <= 0.0:
        raise ValueError("Parameter kernel_tolerance must be positive.")

    if hermiticity_tolerance <= 0.0:
        raise ValueError("Parameter hermiticity_tolerance must be positive.")

    if operators is None:
        operators = build_e47_operators()

    casimir_hermiticity_error = float((operators.casimir - operators.casimir.dag()).norm())
    kernel_hermiticity_error = float((operators.kernel - operators.kernel.dag()).norm())
    kernel_squared_hermiticity_error = float(
        (operators.kernel_squared - operators.kernel_squared.dag()).norm()
    )

    k2_eigenvalues = np.sort(
        np.real_if_close(operators.kernel_squared.eigenenergies()).astype(float)
    )
    zero_mask = np.abs(k2_eigenvalues) <= kernel_tolerance
    kernel_dimension = int(np.count_nonzero(zero_mask))
    positive_eigenvalues = k2_eigenvalues[~zero_mask]
    if positive_eigenvalues.size:
        spectral_gap = int(round(float(positive_eigenvalues[0])))
    else:
        spectral_gap = 0
    k2_max_eigenvalue = int(round(float(k2_eigenvalues[-1])))
    coherence_fraction = kernel_dimension / operators.carrier_dimension

    checks: dict[str, dict[str, Any]] = {
        "carrier_dimension": {
            "description": "The canonical carrier has dimension 125.",
            "expected": EXPECTED_CARRIER_DIMENSION,
            "computed": operators.carrier_dimension,
            "pass": operators.carrier_dimension == EXPECTED_CARRIER_DIMENSION,
        },
        "casimir_hermiticity": {
            "description": "The total Casimir operator is Hermitian.",
            "expected": 0.0,
            "computed": casimir_hermiticity_error,
            "pass": casimir_hermiticity_error < hermiticity_tolerance,
        },
        "kernel_hermiticity": {
            "description": "The canonical kernel operator is Hermitian.",
            "expected": 0.0,
            "computed": kernel_hermiticity_error,
            "pass": kernel_hermiticity_error < hermiticity_tolerance,
        },
        "kernel_squared_hermiticity": {
            "description": "K² is Hermitian.",
            "expected": 0.0,
            "computed": kernel_squared_hermiticity_error,
            "pass": kernel_squared_hermiticity_error < hermiticity_tolerance,
        },
        "kernel_dimension": {
            "description": "The zero eigenspace of K² has dimension 47.",
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": kernel_dimension,
            "pass": kernel_dimension == EXPECTED_KERNEL_DIMENSION,
        },
        "coherence_fraction": {
            "description": "The kernel occupies exactly 47/125 of the carrier.",
            "expected": EXPECTED_COHERENCE_FRACTION,
            "computed": coherence_fraction,
            "absolute_error": abs(coherence_fraction - EXPECTED_COHERENCE_FRACTION),
            "pass": abs(coherence_fraction - EXPECTED_COHERENCE_FRACTION) < kernel_tolerance,
        },
        "k2_spectral_gap": {
            "description": "The smallest non-zero eigenvalue of K² is 11664.",
            "expected": EXPECTED_K2_SPECTRAL_GAP,
            "computed": spectral_gap,
            "pass": abs(spectral_gap - EXPECTED_K2_SPECTRAL_GAP) < kernel_tolerance,
        },
        "k2_max_eigenvalue": {
            "description": "The largest eigenvalue of K² is 186624.",
            "expected": EXPECTED_K2_MAX_EIGENVALUE,
            "computed": k2_max_eigenvalue,
            "pass": abs(k2_max_eigenvalue - EXPECTED_K2_MAX_EIGENVALUE) < kernel_tolerance,
        },
    }

    all_passed = all(bool(check["pass"]) for check in checks.values())

    return KernelValidation(
        inputs={
            "carrier": "V₂ ⊗ V₂ ⊗ V₂",
            "single_spin": CANONICAL_SINGLE_SPIN,
            "kernel_definition": "K = (C - 6I)(C - 30I)",
            "casimir_definition": "C = Jx_total² + Jy_total² + Jz_total²",
        },
        results={
            "carrier_dimension": operators.carrier_dimension,
            "kernel_dimension": kernel_dimension,
            "coherence_fraction": coherence_fraction,
            "k2_spectral_gap": spectral_gap,
            "k2_max_eigenvalue": k2_max_eigenvalue,
            "k2_eigenvalues": [int(round(float(value))) for value in k2_eigenvalues],
        },
        tolerances={
            "kernel_tolerance": kernel_tolerance,
            "hermiticity_tolerance": hermiticity_tolerance,
        },
        checks=checks,
        status="pass" if all_passed else "fail",
    )


def require_valid_e47_kernel(
    validation: KernelValidation,
) -> None:
    """Raise SystemExit if any kernel check failed."""

    if validation.status != "pass":
        failed = [
            name for name, check in validation.checks.items() if not bool(check["pass"])
        ]
        raise SystemExit(
            "Canonical E47 kernel validation failed: " + ", ".join(failed)
        )


__all__ = [
    "CASIMIR_ROOTS",
    "EXPECTED_CARRIER_DIMENSION",
    "EXPECTED_COHERENCE_FRACTION",
    "EXPECTED_K2_MAX_EIGENVALUE",
    "EXPECTED_K2_SPECTRAL_GAP",
    "EXPECTED_KERNEL_DIMENSION",
    "E47Operators",
    "KernelValidation",
    "build_e47_operators",
    "require_valid_e47_kernel",
    "validate_e47_kernel",
]
