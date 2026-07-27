"""Canonical SU(2) kernel algebra for the E47 construction.

This module builds the canonical operators acting on

    V = V₂ ⊗ V₂ ⊗ V₂,    dim(V) = 125

and provides the core validation harness for the spectral kernel

    K = (C - 6I)(C - 30I),    E₄₇ = ker(K),    dim(E₄₇) = 47

where C = J²_total is the total SU(2) Casimir operator.

Scope
-----
This module validates finite-dimensional algebraic and spectral properties
only.  It does not establish experimental, physical, or hardware validation.

Canonical constants
-------------------
- dim(V) = 125
- dim(E₄₇) = 47
- coherence fraction = 47 / 125
- K = (C - 6I)(C - 30I)
- spec(K²) = {0, 11664, 12544, 19600, 32400, 186624}
- gap(K²) = 11664
- max eigenvalue(K²) = 186624
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any, Final

import numpy as np
import qutip as qt

# ── Canonical constants ──────────────────────────────────────────────────────

CARRIER_DIMENSION: Final[int] = 125
EXPECTED_KERNEL_DIMENSION: Final[int] = 47
E47_DIMENSION: Final[int] = 47
BASE_SPIN: Final[float] = 2.0
BASE_DIMENSION: Final[int] = 5  # 2 * BASE_SPIN + 1

# Casimir eigenvalues that K annihilates: λ = j(j+1) for j = 2 and j = 5.
KERNEL_CASIMIR_ROOTS: Final[tuple[int, int]] = (6, 30)

# Full K² spectrum derived from first principles (verified in validate_e47_kernel).
CANONICAL_K2_SPECTRUM: Final[tuple[int, ...]] = (
    0,
    11_664,
    12_544,
    19_600,
    32_400,
    186_624,
)
CANONICAL_SPECTRAL_GAP: Final[int] = 11_664
CANONICAL_K2_MAX_EIGENVALUE: Final[int] = 186_624

# ── Data structures ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class E47Operators:
    """Canonical operator set for the E47 algebraic construction.

    All operators act on V = V₂ ⊗ V₂ ⊗ V₂.

    Attributes
    ----------
    carrier_dimension:
        dim(V) = 125.
    casimir:
        Total SU(2) Casimir operator C = J²_x + J²_y + J²_z.
    kernel:
        Polynomial kernel operator K = (C - 6I)(C - 30I).
    kernel_squared:
        K² = K @ K.  Positive semidefinite.
    identity_total:
        Identity operator on V.
    """

    carrier_dimension: int
    casimir: qt.Qobj
    kernel: qt.Qobj
    kernel_squared: qt.Qobj
    identity_total: qt.Qobj


@dataclass(frozen=True)
class KernelValidation:
    """Structured validation certificate for the E47 kernel operator.

    Attributes
    ----------
    status:
        ``"pass"`` if all checks succeeded, ``"fail"`` otherwise.
    results:
        Scalar summary values keyed by name.  Required keys:
        ``"kernel_dimension"``, ``"coherence_fraction"``,
        ``"k2_spectral_gap"``.
    checks:
        Per-check results.  Each value is a dict containing at least
        a ``"pass"`` key (bool).
    """

    status: str
    results: dict[str, Any]
    checks: dict[str, dict[str, Any]]


# ── Construction ─────────────────────────────────────────────────────────────


def build_e47_operators(
    j: float = BASE_SPIN,
) -> E47Operators:
    """Construct the canonical E47 operator set using QuTiP.

    Parameters
    ----------
    j:
        Spin quantum number for each factor.  The canonical value is 2.

    Returns
    -------
    E47Operators
        Immutable dataclass holding the Casimir, kernel, kernel-squared,
        and identity operators.

    Raises
    ------
    ValueError
        If ``j`` is not a non-negative half-integer.
    RuntimeError
        If the constructed carrier dimension is not 125 (when ``j=2``).
    """
    dim_single = int(round(2 * j + 1))
    if abs(dim_single - (2 * j + 1)) > 1e-12:
        raise ValueError(f"j must be a non-negative half-integer; got {j!r}.")

    dim_total = dim_single ** 3

    # Single-spin operators and identity.
    Jx, Jy, Jz = qt.jmat(j)
    I = qt.qeye(dim_single)

    # Lift each component to V₂ ⊗ V₂ ⊗ V₂.
    Jx_tot = (
        qt.tensor(Jx, I, I)
        + qt.tensor(I, Jx, I)
        + qt.tensor(I, I, Jx)
    )
    Jy_tot = (
        qt.tensor(Jy, I, I)
        + qt.tensor(I, Jy, I)
        + qt.tensor(I, I, Jy)
    )
    Jz_tot = (
        qt.tensor(Jz, I, I)
        + qt.tensor(I, Jz, I)
        + qt.tensor(I, I, Jz)
    )

    # Total Casimir C = Jx² + Jy² + Jz².
    casimir = Jx_tot ** 2 + Jy_tot ** 2 + Jz_tot ** 2

    identity_total = qt.qeye([dim_single] * 3)

    # K = (C − λ₁ I)(C − λ₂ I) where λ₁ = 6, λ₂ = 30.
    lambda1, lambda2 = KERNEL_CASIMIR_ROOTS
    kernel = (casimir - lambda1 * identity_total) * (
        casimir - lambda2 * identity_total
    )

    kernel_squared = kernel * kernel

    if j == BASE_SPIN and dim_total != CARRIER_DIMENSION:
        raise RuntimeError(
            f"Carrier dimension mismatch: expected {CARRIER_DIMENSION}, "
            f"got {dim_total}."
        )

    return E47Operators(
        carrier_dimension=dim_total,
        casimir=casimir,
        kernel=kernel,
        kernel_squared=kernel_squared,
        identity_total=identity_total,
    )


# ── Validation ───────────────────────────────────────────────────────────────


def validate_e47_kernel(
    operators: E47Operators | None = None,
    *,
    dimension_tolerance: float = 0.0,
    spectral_tolerance: float = 1e-8,
    hermitian_tolerance: float = 1e-10,
    coherence_tolerance: float = 1e-12,
) -> KernelValidation:
    """Validate the canonical E47 kernel operator from first principles.

    Parameters
    ----------
    operators:
        Canonical operators.  Constructed automatically when omitted.
    dimension_tolerance:
        Allowed deviation from the expected carrier dimension 125.
        The exact check uses integer equality, so 0.0 is the strict default.
    spectral_tolerance:
        Threshold for classifying K² eigenvalues as numerically zero.
    hermitian_tolerance:
        Tolerance for Hermiticity residuals of C, K, and K².
    coherence_tolerance:
        Absolute tolerance for the coherence-fraction check.

    Returns
    -------
    KernelValidation
        Immutable certificate.
    """
    if operators is None:
        operators = build_e47_operators()

    # ── Carrier dimension ────────────────────────────────────────────────────
    carrier_dimension = operators.carrier_dimension
    carrier_dimension_pass = carrier_dimension == CARRIER_DIMENSION

    # ── Hermiticity of C, K, K² ──────────────────────────────────────────────
    casimir_hermitian_residual = float(
        (operators.casimir - operators.casimir.dag()).norm()
    )
    kernel_hermitian_residual = float(
        (operators.kernel - operators.kernel.dag()).norm()
    )
    k2_hermitian_residual = float(
        (operators.kernel_squared - operators.kernel_squared.dag()).norm()
    )
    hermitian_pass = (
        casimir_hermitian_residual < hermitian_tolerance
        and kernel_hermitian_residual < hermitian_tolerance
        and k2_hermitian_residual < hermitian_tolerance
    )

    # ── Casimir eigenvalue spectrum ──────────────────────────────────────────
    # Compute from first principles; do not hard-code the result.
    casimir_eigenvalues_raw = np.real(operators.casimir.eigenenergies())
    casimir_eigenvalues = np.round(casimir_eigenvalues_raw, decimals=10)

    expected_casimir_eigenvalues: dict[int, int] = {
        0: 1,   # j=0: dim=1
        2: 9,   # j=1: dim=3, mult=3  → 9
        6: 25,  # j=2: dim=5, mult=5  → 25
        12: 28, # j=3: dim=7, mult=4  → 28
        20: 27, # j=4: dim=9, mult=3  → 27
        30: 22, # j=5: dim=11, mult=2 → 22
        42: 13, # j=6: dim=13, mult=1 → 13
    }
    computed_casimir_spectrum: dict[int, int] = {}
    for ev in casimir_eigenvalues:
        key = int(round(float(ev)))
        computed_casimir_spectrum[key] = (
            computed_casimir_spectrum.get(key, 0) + 1
        )

    casimir_spectrum_pass = (
        computed_casimir_spectrum == expected_casimir_eigenvalues
    )

    # ── K² eigenvalue spectrum and kernel dimension ──────────────────────────
    # Derived entirely from diagonalization; canonical constants are only
    # used for the comparison, not to define the eigenvalues.
    k2_eigenvalues_raw = np.real(operators.kernel_squared.eigenenergies())
    k2_eigenvalues = np.sort(k2_eigenvalues_raw)

    kernel_dimension = int(np.sum(k2_eigenvalues < spectral_tolerance))
    kernel_dimension_pass = kernel_dimension == EXPECTED_KERNEL_DIMENSION

    # Spectral gap: smallest strictly positive eigenvalue.
    positive_k2 = k2_eigenvalues[k2_eigenvalues >= spectral_tolerance]
    k2_spectral_gap_float = float(positive_k2[0]) if positive_k2.size else 0.0
    k2_spectral_gap = int(round(k2_spectral_gap_float))
    k2_spectral_gap_pass = k2_spectral_gap == CANONICAL_SPECTRAL_GAP

    k2_max_eigenvalue_float = float(k2_eigenvalues[-1])
    k2_max_eigenvalue = int(round(k2_max_eigenvalue_float))
    k2_max_pass = k2_max_eigenvalue == CANONICAL_K2_MAX_EIGENVALUE

    # Verify the full K² spectrum matches canonical values.
    k2_unique_rounded = tuple(
        sorted({int(round(float(v))) for v in k2_eigenvalues})
    )
    k2_spectrum_pass = k2_unique_rounded == tuple(sorted(CANONICAL_K2_SPECTRUM))

    # ── Positive semidefiniteness of K² ─────────────────────────────────────
    k2_min_eigenvalue = float(k2_eigenvalues[0])
    k2_psd_pass = k2_min_eigenvalue >= -spectral_tolerance

    # ── Coherence fraction ───────────────────────────────────────────────────
    coherence_fraction = kernel_dimension / carrier_dimension
    expected_coherence = EXPECTED_KERNEL_DIMENSION / CARRIER_DIMENSION
    coherence_pass = abs(coherence_fraction - expected_coherence) < coherence_tolerance

    # ── K annihilates its kernel ─────────────────────────────────────────────
    # Build the projector lazily from the zero eigenspace.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        k2_ev, k2_states = operators.kernel_squared.eigenstates()

    kernel_basis = [
        state
        for ev, state in zip(k2_ev, k2_states)
        if abs(float(np.real(ev))) < spectral_tolerance
    ]
    if kernel_basis:
        annihilation_errors = [
            float((operators.kernel * v).norm())
            for v in kernel_basis
        ]
        max_annihilation_error = max(annihilation_errors)
    else:
        max_annihilation_error = float("inf")
    kernel_annihilation_pass = max_annihilation_error < spectral_tolerance

    # ── Aggregate ────────────────────────────────────────────────────────────
    checks: dict[str, dict[str, Any]] = {
        "carrier_dimension": {
            "description": "dim(V) = dim(V₂ ⊗ V₂ ⊗ V₂) = 5³ = 125.",
            "expected": CARRIER_DIMENSION,
            "computed": carrier_dimension,
            "pass": carrier_dimension_pass,
        },
        "casimir_hermiticity": {
            "description": "C is Hermitian.",
            "expected": 0.0,
            "computed": casimir_hermitian_residual,
            "pass": casimir_hermitian_residual < hermitian_tolerance,
        },
        "kernel_hermiticity": {
            "description": "K = (C − 6I)(C − 30I) is Hermitian.",
            "expected": 0.0,
            "computed": kernel_hermitian_residual,
            "pass": kernel_hermitian_residual < hermitian_tolerance,
        },
        "kernel_squared_hermiticity": {
            "description": "K² is Hermitian.",
            "expected": 0.0,
            "computed": k2_hermitian_residual,
            "pass": k2_hermitian_residual < hermitian_tolerance,
        },
        "casimir_eigenvalue_spectrum": {
            "description": (
                "C has eigenvalue multiplicities consistent with "
                "V₂ ⊗ V₂ ⊗ V₂ decomposed into SU(2) irreps."
            ),
            "expected": expected_casimir_eigenvalues,
            "computed": computed_casimir_spectrum,
            "pass": casimir_spectrum_pass,
        },
        "kernel_dimension": {
            "description": "dim(ker K) = 47.",
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": kernel_dimension,
            "pass": kernel_dimension_pass,
        },
        "k2_spectral_gap": {
            "description": "Smallest positive eigenvalue of K² is 11664.",
            "expected": CANONICAL_SPECTRAL_GAP,
            "computed": k2_spectral_gap,
            "pass": k2_spectral_gap_pass,
        },
        "k2_max_eigenvalue": {
            "description": "Largest eigenvalue of K² is 186624.",
            "expected": CANONICAL_K2_MAX_EIGENVALUE,
            "computed": k2_max_eigenvalue,
            "pass": k2_max_pass,
        },
        "k2_spectrum": {
            "description": (
                "K² spectrum equals {0, 11664, 12544, 19600, 32400, 186624}."
            ),
            "expected": tuple(sorted(CANONICAL_K2_SPECTRUM)),
            "computed": k2_unique_rounded,
            "pass": k2_spectrum_pass,
        },
        "k2_positive_semidefinite": {
            "description": "K² is positive semidefinite.",
            "expected": 0.0,
            "computed": k2_min_eigenvalue,
            "pass": k2_psd_pass,
        },
        "coherence_fraction": {
            "description": "dim(E₄₇) / dim(V) = 47/125.",
            "expected": expected_coherence,
            "computed": coherence_fraction,
            "pass": coherence_pass,
        },
        "kernel_annihilation": {
            "description": "K annihilates every vector in ker(K²).",
            "expected": 0.0,
            "computed": max_annihilation_error,
            "pass": kernel_annihilation_pass,
        },
    }

    all_passed = all(bool(c["pass"]) for c in checks.values())

    results: dict[str, Any] = {
        "carrier_dimension": carrier_dimension,
        "kernel_dimension": kernel_dimension,
        "coherence_fraction": coherence_fraction,
        "k2_spectral_gap": k2_spectral_gap,
        "k2_max_eigenvalue": k2_max_eigenvalue,
        "k2_unique_eigenvalues": k2_unique_rounded,
        "casimir_hermitian_residual": casimir_hermitian_residual,
        "kernel_hermitian_residual": kernel_hermitian_residual,
        "k2_hermitian_residual": k2_hermitian_residual,
        "max_kernel_annihilation_error": max_annihilation_error,
    }

    return KernelValidation(
        status="pass" if all_passed else "fail",
        results=results,
        checks=checks,
    )


def require_valid_e47_kernel(validation: KernelValidation) -> None:
    """Raise ``ValueError`` if any kernel validation check failed.

    Parameters
    ----------
    validation:
        Certificate returned by ``validate_e47_kernel``.

    Raises
    ------
    ValueError
        Aggregated message listing every failed check.
    """
    if validation.status == "pass":
        return

    failed = [
        name
        for name, check in validation.checks.items()
        if not bool(check["pass"])
    ]
    raise ValueError(
        "E47 kernel validation FAILED: " + ", ".join(failed)
    )


# ── Module self-test ─────────────────────────────────────────────────────────

__all__ = [
    "BASE_DIMENSION",
    "BASE_SPIN",
    "CANONICAL_K2_MAX_EIGENVALUE",
    "CANONICAL_K2_SPECTRUM",
    "CANONICAL_SPECTRAL_GAP",
    "CARRIER_DIMENSION",
    "E47Operators",
    "E47_DIMENSION",
    "EXPECTED_KERNEL_DIMENSION",
    "KERNEL_CASIMIR_ROOTS",
    "KernelValidation",
    "build_e47_operators",
    "require_valid_e47_kernel",
    "validate_e47_kernel",
]


if __name__ == "__main__":
    operators = build_e47_operators()
    validation = validate_e47_kernel(operators)
    require_valid_e47_kernel(validation)
    print("E47 kernel validation PASSED.")
    print(f"  dim(V)   = {validation.results['carrier_dimension']}")
    print(f"  dim(E47) = {validation.results['kernel_dimension']}")
    print(f"  Ω_c      = {validation.results['coherence_fraction']:.6f}")
    print(f"  gap(K²)  = {validation.results['k2_spectral_gap']}")
    print(f"  max λ(K²)= {validation.results['k2_max_eigenvalue']}")
