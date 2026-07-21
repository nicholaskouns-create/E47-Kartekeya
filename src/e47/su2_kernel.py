"""SU(2) Casimir kernel operators for the canonical E47 construction.

This module constructs the total SU(2) Casimir operator C and the spectral
kernel operator

    K = (C - 6I)(C - 30I)

acting on the carrier space

    V = V₂ ⊗ V₂ ⊗ V₂,    dim(V) = 125,

where V₂ is the spin-2 irrep of SU(2) with dim(V₂) = 5.

The canonical kernel subspace is

    E₄₇ = ker(K) = 5V₂ ⊕ 2V₅,    dim(E₄₇) = 47.

K² eigenvalue spectrum on V:

    spec(K²) = {0, 11664, 12544, 19600, 32400, 186624}.

Scope
-----
This module validates finite-dimensional algebraic properties.
It does not establish experimental or physical interpretations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import numpy as np
import qutip as qt


EXPECTED_KERNEL_DIMENSION: Final[int] = 47
CARRIER_DIMENSION: Final[int] = 125
BASE_SPIN: Final[float] = 2.0
BASE_DIMENSION: Final[int] = 5  # 2j+1 = 5

# K = (C - λ₁ I)(C - λ₂ I),  λ₁ = j(j+1) at j=2, λ₂ = j(j+1) at j=5
CASIMIR_ROOT_J2: Final[int] = 6    # 2 × 3
CASIMIR_ROOT_J5: Final[int] = 30   # 5 × 6

CANONICAL_K2_EIGENVALUES: Final[tuple[int, ...]] = (
    0,
    11_664,
    12_544,
    19_600,
    32_400,
    186_624,
)

CANONICAL_K2_SPECTRAL_GAP: Final[int] = 11_664
CANONICAL_K2_NORM: Final[int] = 186_624


@dataclass(frozen=True)
class E47Operators:
    """Canonical SU(2) operators on the carrier V₂ ⊗ V₂ ⊗ V₂."""

    casimir: qt.Qobj
    kernel: qt.Qobj
    kernel_squared: qt.Qobj
    identity_total: qt.Qobj
    carrier_dimension: int


@dataclass(frozen=True)
class KernelValidation:
    """Structured validation certificate for the E47 kernel operator."""

    inputs: dict[str, Any]
    results: dict[str, Any]
    tolerances: dict[str, float]
    checks: dict[str, dict[str, Any]]
    status: str


def build_e47_operators(
    *,
    eigenvalue_tolerance: float = 1e-8,
) -> E47Operators:
    """Construct the canonical SU(2) operators on V₂ ⊗ V₂ ⊗ V₂.

    Builds the total Casimir C = Jx² + Jy² + Jz² and the kernel operator
    K = (C - 6I)(C - 30I) for the three-fold tensor product of spin-2
    representations.

    Parameters
    ----------
    eigenvalue_tolerance
        Tolerance used during construction to symmetrize operators.

    Returns
    -------
    E47Operators
        Immutable container of the canonical operators.
    """

    j = BASE_SPIN
    d = int(2 * j + 1)  # = 5

    # Single-particle spin matrices
    jx = qt.jmat(j, "x")
    jy = qt.jmat(j, "y")
    jz = qt.jmat(j, "z")
    id1 = qt.qeye(d)

    # Total spin operators: J_tot = J ⊗ I ⊗ I + I ⊗ J ⊗ I + I ⊗ I ⊗ J
    jx_tot = (
        qt.tensor(jx, id1, id1)
        + qt.tensor(id1, jx, id1)
        + qt.tensor(id1, id1, jx)
    )
    jy_tot = (
        qt.tensor(jy, id1, id1)
        + qt.tensor(id1, jy, id1)
        + qt.tensor(id1, id1, jy)
    )
    jz_tot = (
        qt.tensor(jz, id1, id1)
        + qt.tensor(id1, jz, id1)
        + qt.tensor(id1, id1, jz)
    )

    # Total Casimir C = Jx² + Jy² + Jz² (Hermitian by construction)
    casimir = jx_tot * jx_tot + jy_tot * jy_tot + jz_tot * jz_tot
    casimir = 0.5 * (casimir + casimir.dag())

    # Total identity
    identity_total = qt.tensor(id1, id1, id1)

    # Kernel K = (C - 6I)(C - 30I)
    kernel = (
        (casimir - CASIMIR_ROOT_J2 * identity_total)
        * (casimir - CASIMIR_ROOT_J5 * identity_total)
    )
    kernel = 0.5 * (kernel + kernel.dag())

    # K²
    kernel_squared = kernel * kernel
    kernel_squared = 0.5 * (kernel_squared + kernel_squared.dag())

    return E47Operators(
        casimir=casimir,
        kernel=kernel,
        kernel_squared=kernel_squared,
        identity_total=identity_total,
        carrier_dimension=int(identity_total.shape[0]),
    )


def validate_e47_kernel(
    operators: E47Operators | None = None,
    *,
    eigenvalue_tolerance: float = 1e-8,
    hermiticity_tolerance: float = 1e-10,
) -> KernelValidation:
    """Validate the canonical E47 kernel operator.

    Checks include:

    - carrier dimension is 125;
    - Casimir eigenvalues cluster at j(j+1) for j = 0, …, 6;
    - kernel operator K is Hermitian;
    - K² is positive semidefinite;
    - kernel dimension dim(ker K) = 47;
    - coherence fraction 47/125;
    - K² spectral gap = 11664;
    - K² operator norm = 186624.

    Parameters
    ----------
    operators
        Pre-built canonical operators. Constructed automatically if omitted.
    eigenvalue_tolerance
        Threshold for classifying K² eigenvalues as zero.
    hermiticity_tolerance
        Threshold for Hermiticity residuals.

    Returns
    -------
    KernelValidation
        Immutable structured certificate.
    """

    if operators is None:
        operators = build_e47_operators()

    tolerance_values = {
        "eigenvalue_tolerance": eigenvalue_tolerance,
        "hermiticity_tolerance": hermiticity_tolerance,
    }

    for name, value in tolerance_values.items():
        if value <= 0:
            raise ValueError(f"{name} must be positive.")

    carrier_dimension = operators.carrier_dimension

    # Casimir eigenvalues
    casimir_eigenvalues = np.round(
        np.real_if_close(operators.casimir.eigenenergies()),
        decimals=5,
    ).astype(float)
    casimir_spectrum = sorted(set(casimir_eigenvalues.tolist()))

    # Expected Casimir eigenvalues j(j+1) for j = 0..6
    expected_casimir_spectrum = sorted(
        j * (j + 1) for j in range(7)
    )

    # K² eigenvalues
    k2_eigenvalues = np.real_if_close(
        operators.kernel_squared.eigenenergies()
    ).astype(float)

    k2_min = float(k2_eigenvalues[0])
    k2_max = float(k2_eigenvalues[-1])

    zero_mask = np.abs(k2_eigenvalues) <= eigenvalue_tolerance
    kernel_dimension = int(np.count_nonzero(zero_mask))

    positive_k2 = k2_eigenvalues[~zero_mask]
    k2_spectral_gap = (
        float(positive_k2[0])
        if positive_k2.size > 0
        else 0.0
    )

    coherence_fraction = (
        kernel_dimension / carrier_dimension
        if carrier_dimension > 0
        else float("nan")
    )

    # Hermiticity residuals
    kernel_hermiticity_error = float(
        (operators.kernel - operators.kernel.dag()).norm()
    )

    casimir_hermiticity_error = float(
        (operators.casimir - operators.casimir.dag()).norm()
    )

    # K² positive semidefinite check
    k2_min_eigenvalue = k2_min
    k2_psd_pass = k2_min_eigenvalue >= -hermiticity_tolerance

    # Casimir spectrum check
    casimir_spectrum_pass = all(
        abs(computed - expected) < eigenvalue_tolerance
        for computed, expected in zip(
            sorted(casimir_spectrum),
            expected_casimir_spectrum,
        )
    ) if len(casimir_spectrum) == len(expected_casimir_spectrum) else False

    checks: dict[str, dict[str, Any]] = {
        "carrier_dimension": {
            "description": "The carrier V₂ ⊗ V₂ ⊗ V₂ has dimension 125.",
            "expected": CARRIER_DIMENSION,
            "computed": carrier_dimension,
            "pass": carrier_dimension == CARRIER_DIMENSION,
        },
        "casimir_hermiticity": {
            "description": "The Casimir operator C is Hermitian.",
            "expected": 0.0,
            "computed": casimir_hermiticity_error,
            "pass": casimir_hermiticity_error < hermiticity_tolerance,
        },
        "kernel_hermiticity": {
            "description": "The kernel operator K is Hermitian.",
            "expected": 0.0,
            "computed": kernel_hermiticity_error,
            "pass": kernel_hermiticity_error < hermiticity_tolerance,
        },
        "casimir_spectrum": {
            "description": (
                "Casimir eigenvalues are j(j+1) for j = 0, 1, 2, 3, 4, 5, 6."
            ),
            "expected": expected_casimir_spectrum,
            "computed": sorted(casimir_spectrum),
            "pass": casimir_spectrum_pass,
        },
        "k2_positive_semidefinite": {
            "description": "K² is positive semidefinite.",
            "expected": 0.0,
            "computed": k2_min_eigenvalue,
            "pass": k2_psd_pass,
        },
        "kernel_dimension": {
            "description": "The kernel subspace E₄₇ has dimension 47.",
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": kernel_dimension,
            "pass": kernel_dimension == EXPECTED_KERNEL_DIMENSION,
        },
        "coherence_fraction": {
            "description": "The coherence fraction 47/125 = 0.376.",
            "expected": EXPECTED_KERNEL_DIMENSION / CARRIER_DIMENSION,
            "computed": coherence_fraction,
            "pass": abs(coherence_fraction - EXPECTED_KERNEL_DIMENSION / CARRIER_DIMENSION)
            < 1e-12,
        },
        "k2_spectral_gap": {
            "description": "The K² spectral gap is 11664.",
            "expected": CANONICAL_K2_SPECTRAL_GAP,
            "computed": k2_spectral_gap,
            "pass": abs(k2_spectral_gap - CANONICAL_K2_SPECTRAL_GAP)
            < eigenvalue_tolerance,
        },
        "k2_operator_norm": {
            "description": "The K² operator norm is 186624.",
            "expected": CANONICAL_K2_NORM,
            "computed": k2_max,
            "pass": abs(k2_max - CANONICAL_K2_NORM) < eigenvalue_tolerance,
        },
    }

    all_passed = all(bool(check["pass"]) for check in checks.values())

    results = {
        "carrier_dimension": carrier_dimension,
        "kernel_dimension": kernel_dimension,
        "coherence_fraction": coherence_fraction,
        "k2_spectral_gap": int(round(k2_spectral_gap)),
        "k2_operator_norm": k2_max,
        "k2_min_eigenvalue": k2_min,
        "casimir_hermiticity_error": casimir_hermiticity_error,
        "kernel_hermiticity_error": kernel_hermiticity_error,
        "casimir_spectrum": sorted(casimir_spectrum),
    }

    return KernelValidation(
        inputs={
            "base_spin": BASE_SPIN,
            "base_dimension": BASE_DIMENSION,
            "carrier_definition": "V₂ ⊗ V₂ ⊗ V₂",
            "kernel_definition": "K = (C - 6I)(C - 30I)",
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
    """Raise SystemExit if any kernel check failed.

    Parameters
    ----------
    validation
        Structured validation certificate from ``validate_e47_kernel``.

    Raises
    ------
    SystemExit
        If validation status is not ``"pass"``.
    """

    if validation.status != "pass":
        failed = [
            name
            for name, check in validation.checks.items()
            if not bool(check["pass"])
        ]
        raise SystemExit(
            "Canonical E47 kernel validation failed: "
            + ", ".join(failed)
        )


__all__ = [
    "BASE_DIMENSION",
    "BASE_SPIN",
    "CANONICAL_K2_EIGENVALUES",
    "CANONICAL_K2_NORM",
    "CANONICAL_K2_SPECTRAL_GAP",
    "CARRIER_DIMENSION",
    "CASIMIR_ROOT_J2",
    "CASIMIR_ROOT_J5",
    "E47Operators",
    "EXPECTED_KERNEL_DIMENSION",
    "KernelValidation",
    "build_e47_operators",
    "require_valid_e47_kernel",
    "validate_e47_kernel",
]


if __name__ == "__main__":
    operators = build_e47_operators()
    validation = validate_e47_kernel(operators)
    require_valid_e47_kernel(validation)
    print("Canonical E47 kernel validation PASSED.")
    print(f"  dim(E₄₇) = {validation.results['kernel_dimension']}")
    print(f"  Ωc = {validation.results['coherence_fraction']:.6f}")
    print(f"  K² spectral gap = {validation.results['k2_spectral_gap']}")
