"""Canonical SU(2) kernel operators for the E47 construction.

This module builds the three-spin Hilbert space

    V = V₂ ⊗ V₂ ⊗ V₂,    dim(V) = 125,

the total Casimir C of SU(2), and the spectral-kernel operator

    K = (C - 6I)(C - 30I).

The kernel of K is E₄₇:

    dim ker(K) = 47,

corresponding to total-spin sectors J=2 (C=6) and J=5 (C=30).

All operators are returned as qutip Qobj instances so that they
compose correctly with the projector and semigroup modules.

Scope
-----
This module validates algebraic and spectral properties of the
canonical E47 kernel operator. It does not establish experimental,
physical, or hardware validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import numpy as np
import qutip as qt

# ── canonical constants ────────────────────────────────────────────

EXPECTED_KERNEL_DIMENSION: Final[int] = 47
EXPECTED_CARRIER_DIMENSION: Final[int] = 125
EXPECTED_COHERENCE_FRACTION: Final[float] = 47 / 125

# spec(K²) for V₂^⊗3 (distinct eigenvalues)
EXPECTED_K2_EIGENVALUES: Final[tuple[int, ...]] = (
    0,
    11_664,
    12_544,
    19_600,
    32_400,
    186_624,
)

EXPECTED_K2_SPECTRAL_GAP: Final[int] = 11_664
EXPECTED_K2_NORM: Final[int] = 186_624

# Casimir eigenvalues that define the kernel: C|J⟩ = J(J+1)|J⟩
_KERNEL_CASIMIR_VALUES: Final[tuple[int, ...]] = (6, 30)


# ── dataclasses ───────────────────────────────────────────────────

@dataclass(frozen=True)
class E47Operators:
    """Canonical SU(2) operators for the E47 construction.

    Attributes
    ----------
    casimir : qt.Qobj
        Total Casimir operator C on V₂⊗V₂⊗V₂.
    kernel : qt.Qobj
        Spectral kernel K = (C - 6I)(C - 30I).
    kernel_squared : qt.Qobj
        K² (Hermitian, positive semidefinite).
    identity_total : qt.Qobj
        Identity on V₂⊗V₂⊗V₂.
    carrier_dimension : int
        dim(V) = 125.
    """

    casimir: qt.Qobj
    kernel: qt.Qobj
    kernel_squared: qt.Qobj
    identity_total: qt.Qobj
    carrier_dimension: int


@dataclass(frozen=True)
class KernelValidation:
    """Structured validation output for the E47 kernel operator."""

    inputs: dict[str, Any]
    results: dict[str, Any]
    tolerances: dict[str, float]
    checks: dict[str, dict[str, Any]]
    status: str


# ── construction ──────────────────────────────────────────────────

def build_e47_operators() -> E47Operators:
    """Construct the canonical SU(2) operators for the E47 kernel.

    Builds the tensor-product Hilbert space V₂⊗V₂⊗V₂ (dim=125)
    and the total angular-momentum Casimir

        C = (J^tot)² = Σ_{a∈{x,y,z}} (J_a⊗I⊗I + I⊗J_a⊗I + I⊗I⊗J_a)²,

    then forms the spectral kernel

        K = (C - 6I)(C - 30I).

    Returns
    -------
    E47Operators
        Immutable container of all canonical operators.
    """

    j: float = 2.0
    Jx, Jy, Jz = qt.jmat(j, "x"), qt.jmat(j, "y"), qt.jmat(j, "z")
    I = qt.qeye(int(2 * j + 1))

    # Total angular-momentum components
    Jx_tot = qt.tensor(Jx, I, I) + qt.tensor(I, Jx, I) + qt.tensor(I, I, Jx)
    Jy_tot = qt.tensor(Jy, I, I) + qt.tensor(I, Jy, I) + qt.tensor(I, I, Jy)
    Jz_tot = qt.tensor(Jz, I, I) + qt.tensor(I, Jz, I) + qt.tensor(I, I, Jz)

    # Total Casimir
    casimir = Jx_tot**2 + Jy_tot**2 + Jz_tot**2
    casimir = 0.5 * (casimir + casimir.dag())

    identity_total = qt.tensor(I, I, I)

    # Spectral kernel K = (C − 6I)(C − 30I)
    kernel = (casimir - 6 * identity_total) * (casimir - 30 * identity_total)
    kernel = 0.5 * (kernel + kernel.dag())

    kernel_squared = kernel * kernel
    kernel_squared = 0.5 * (kernel_squared + kernel_squared.dag())

    return E47Operators(
        casimir=casimir,
        kernel=kernel,
        kernel_squared=kernel_squared,
        identity_total=identity_total,
        carrier_dimension=int(casimir.shape[0]),
    )


# ── validation ────────────────────────────────────────────────────

def validate_e47_kernel(
    operators: E47Operators | None = None,
    *,
    hermiticity_tolerance: float = 1e-10,
    casimir_tolerance: float = 1e-8,
    kernel_tolerance: float = 1e-6,
    k2_tolerance: float = 1e-6,
    dimension_tolerance: float = 1e-8,
) -> KernelValidation:
    """Validate the canonical E47 kernel operator.

    Checks include:

    - carrier dimension equals 125;
    - kernel dimension equals 47;
    - coherence fraction 47/125;
    - C is Hermitian;
    - K is Hermitian;
    - K² is Hermitian and positive semidefinite;
    - K² spectral gap is 11664;
    - K² operator norm is 186624.

    Parameters
    ----------
    operators
        Operators from ``build_e47_operators``. Built automatically if omitted.
    hermiticity_tolerance
        Maximum allowed Hermiticity residual for C and K.
    casimir_tolerance
        Tolerance for identifying Casimir eigenvalue sectors.
    kernel_tolerance
        Threshold for classifying K eigenvalues as zero.
    k2_tolerance
        Threshold for classifying K² eigenvalues as zero.
    dimension_tolerance
        Tolerance for trace-based dimension checks.

    Returns
    -------
    KernelValidation
        Structured validation record.
    """

    if operators is None:
        operators = build_e47_operators()

    tolerance_values = {
        "hermiticity_tolerance": hermiticity_tolerance,
        "casimir_tolerance": casimir_tolerance,
        "kernel_tolerance": kernel_tolerance,
        "k2_tolerance": k2_tolerance,
        "dimension_tolerance": dimension_tolerance,
    }

    for name, value in tolerance_values.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive.")

    # ── spectral analysis of K² ──────────────────────────────────

    k2_eigenvalues = np.sort(
        np.real_if_close(
            operators.kernel_squared.eigenenergies()
        ).astype(float)
    )

    zero_mask = np.abs(k2_eigenvalues) < k2_tolerance
    kernel_dimension = int(np.sum(zero_mask))
    positive_eigenvalues = k2_eigenvalues[~zero_mask]
    spectral_gap = (
        float(positive_eigenvalues[0])
        if positive_eigenvalues.size
        else 0.0
    )
    k2_max = float(k2_eigenvalues[-1])
    k2_min = float(k2_eigenvalues[0])

    coherence_fraction = kernel_dimension / operators.carrier_dimension

    # ── Hermiticity ──────────────────────────────────────────────

    casimir_hermiticity_error = float(
        (operators.casimir - operators.casimir.dag()).norm()
    )
    kernel_hermiticity_error = float(
        (operators.kernel - operators.kernel.dag()).norm()
    )
    k2_hermiticity_error = float(
        (operators.kernel_squared - operators.kernel_squared.dag()).norm()
    )

    # ── K eigenvalue analysis ────────────────────────────────────

    kernel_eigenvalues = np.sort(
        np.real_if_close(
            operators.kernel.eigenenergies()
        ).astype(float)
    )
    kernel_zero_count = int(
        np.sum(np.abs(kernel_eigenvalues) < kernel_tolerance)
    )

    # ── checks ───────────────────────────────────────────────────

    checks: dict[str, dict[str, Any]] = {
        "carrier_dimension": {
            "description": "The carrier space V₂⊗V₂⊗V₂ has dimension 125.",
            "expected": EXPECTED_CARRIER_DIMENSION,
            "computed": operators.carrier_dimension,
            "pass": operators.carrier_dimension == EXPECTED_CARRIER_DIMENSION,
        },
        "kernel_dimension": {
            "description": "ker(K) has dimension 47.",
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": kernel_dimension,
            "pass": kernel_dimension == EXPECTED_KERNEL_DIMENSION,
        },
        "coherence_fraction": {
            "description": "Coherence fraction is 47/125.",
            "expected": EXPECTED_COHERENCE_FRACTION,
            "computed": coherence_fraction,
            "absolute_error": abs(coherence_fraction - EXPECTED_COHERENCE_FRACTION),
            "pass": abs(
                coherence_fraction - EXPECTED_COHERENCE_FRACTION
            ) < dimension_tolerance,
        },
        "casimir_hermiticity": {
            "description": "C is Hermitian: C† = C.",
            "expected": 0.0,
            "computed": casimir_hermiticity_error,
            "pass": casimir_hermiticity_error < hermiticity_tolerance,
        },
        "kernel_hermiticity": {
            "description": "K is Hermitian: K† = K.",
            "expected": 0.0,
            "computed": kernel_hermiticity_error,
            "pass": kernel_hermiticity_error < hermiticity_tolerance,
        },
        "k2_hermiticity": {
            "description": "K² is Hermitian.",
            "expected": 0.0,
            "computed": k2_hermiticity_error,
            "pass": k2_hermiticity_error < hermiticity_tolerance,
        },
        "k2_positive_semidefinite": {
            "description": "K² is positive semidefinite: min eigenvalue ≥ 0.",
            "expected": 0.0,
            "computed": k2_min,
            "pass": k2_min >= -k2_tolerance,
        },
        "k2_spectral_gap": {
            "description": "K² spectral gap equals 11664.",
            "expected": EXPECTED_K2_SPECTRAL_GAP,
            "computed": spectral_gap,
            "absolute_error": abs(spectral_gap - EXPECTED_K2_SPECTRAL_GAP),
            "pass": abs(spectral_gap - EXPECTED_K2_SPECTRAL_GAP) < k2_tolerance,
        },
        "k2_operator_norm": {
            "description": "K² operator norm equals 186624.",
            "expected": EXPECTED_K2_NORM,
            "computed": k2_max,
            "absolute_error": abs(k2_max - EXPECTED_K2_NORM),
            "pass": abs(k2_max - EXPECTED_K2_NORM) < k2_tolerance,
        },
        "kernel_zero_count": {
            "description": "K has exactly 47 zero eigenvalues.",
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": kernel_zero_count,
            "pass": kernel_zero_count == EXPECTED_KERNEL_DIMENSION,
        },
    }

    all_passed = all(bool(check["pass"]) for check in checks.values())

    results: dict[str, Any] = {
        "carrier_dimension": operators.carrier_dimension,
        "kernel_dimension": kernel_dimension,
        "coherence_fraction": coherence_fraction,
        "k2_spectral_gap": spectral_gap,
        "k2_operator_norm": k2_max,
        "k2_min_eigenvalue": k2_min,
        "casimir_hermiticity_error": casimir_hermiticity_error,
        "kernel_hermiticity_error": kernel_hermiticity_error,
        "k2_hermiticity_error": k2_hermiticity_error,
        "kernel_zero_count": kernel_zero_count,
    }

    return KernelValidation(
        inputs={
            "carrier": "V₂ ⊗ V₂ ⊗ V₂",
            "casimir": "C = (J^tot)²",
            "kernel": "K = (C − 6I)(C − 30I)",
            "expected_kernel_dimension": EXPECTED_KERNEL_DIMENSION,
        },
        results=results,
        tolerances=tolerance_values,
        checks=checks,
        status="pass" if all_passed else "fail",
    )


def require_valid_e47_kernel(
    validation: KernelValidation,
) -> None:
    """Raise SystemExit if any kernel check failed."""

    if validation.status != "pass":
        failed = [
            name
            for name, check in validation.checks.items()
            if not bool(check["pass"])
        ]
        raise SystemExit(
            "Canonical E47 kernel validation failed: " + ", ".join(failed)
        )


# ── module self-test ──────────────────────────────────────────────

if __name__ == "__main__":
    ops = build_e47_operators()
    val = validate_e47_kernel(ops)
    require_valid_e47_kernel(val)
    print("Canonical E47 kernel validation PASSED.")
    print(f"  carrier_dimension = {val.results['carrier_dimension']}")
    print(f"  kernel_dimension  = {val.results['kernel_dimension']}")
    print(f"  k2_spectral_gap   = {val.results['k2_spectral_gap']}")


__all__ = [
    "E47Operators",
    "KernelValidation",
    "EXPECTED_CARRIER_DIMENSION",
    "EXPECTED_K2_NORM",
    "EXPECTED_K2_SPECTRAL_GAP",
    "EXPECTED_KERNEL_DIMENSION",
    "build_e47_operators",
    "require_valid_e47_kernel",
    "validate_e47_kernel",
]
