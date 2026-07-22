"""Canonical SU(2) kernel construction for the E47 validation stack."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import qutip as qt


BASE_SPIN = 2
BASE_DIMENSION = 5
TENSOR_PRODUCT_RANK = 3
EXPECTED_CARRIER_DIMENSION = 125
EXPECTED_KERNEL_DIMENSION = 47
EXPECTED_COHERENCE_FRACTION = 47 / 125
EXPECTED_K2_SPECTRAL_GAP = 11_664


@dataclass(frozen=True)
class E47Operators:
    """Canonical operators for the E47 carrier."""

    base_spin: int
    base_dimension: int
    tensor_product_rank: int
    carrier_dimension: int
    identity_total: qt.Qobj
    casimir: qt.Qobj
    kernel: qt.Qobj
    kernel_squared: qt.Qobj


@dataclass(frozen=True)
class KernelValidation:
    """Structured validation output for the canonical SU(2) kernel."""

    inputs: dict[str, Any]
    results: dict[str, Any]
    tolerances: dict[str, float]
    checks: dict[str, dict[str, Any]]
    status: str


def build_e47_operators() -> E47Operators:
    """Construct the canonical SU(2) Casimir and kernel operators."""

    jx, jy, jz = qt.jmat(BASE_SPIN)
    identity_single = qt.qeye(BASE_DIMENSION)

    j1x = qt.tensor(jx, identity_single, identity_single)
    j1y = qt.tensor(jy, identity_single, identity_single)
    j1z = qt.tensor(jz, identity_single, identity_single)

    j2x = qt.tensor(identity_single, jx, identity_single)
    j2y = qt.tensor(identity_single, jy, identity_single)
    j2z = qt.tensor(identity_single, jz, identity_single)

    j3x = qt.tensor(identity_single, identity_single, jx)
    j3y = qt.tensor(identity_single, identity_single, jy)
    j3z = qt.tensor(identity_single, identity_single, jz)

    jx_total = j1x + j2x + j3x
    jy_total = j1y + j2y + j3y
    jz_total = j1z + j2z + j3z

    carrier_dimension = BASE_DIMENSION**TENSOR_PRODUCT_RANK
    identity_total = qt.qeye(carrier_dimension)
    casimir = jx_total * jx_total + jy_total * jy_total + jz_total * jz_total
    casimir = 0.5 * (casimir + casimir.dag())

    kernel = (casimir - 6 * identity_total) * (casimir - 30 * identity_total)
    kernel = 0.5 * (kernel + kernel.dag())
    kernel_squared = kernel * kernel
    kernel_squared = 0.5 * (kernel_squared + kernel_squared.dag())

    return E47Operators(
        base_spin=BASE_SPIN,
        base_dimension=BASE_DIMENSION,
        tensor_product_rank=TENSOR_PRODUCT_RANK,
        carrier_dimension=carrier_dimension,
        identity_total=identity_total,
        casimir=casimir,
        kernel=kernel,
        kernel_squared=kernel_squared,
    )


def _cluster_values(values: np.ndarray, *, tol: float) -> list[float]:
    """Cluster sorted eigenvalues by tolerance and return representatives."""

    clusters: list[float] = []
    for value in np.sort(np.real_if_close(values).astype(float)):
        if not clusters or abs(value - clusters[-1]) >= tol:
            clusters.append(float(value))
    return clusters


def validate_e47_kernel(
    operators: E47Operators | None = None,
    *,
    zero_tolerance: float = 1e-8,
    spectrum_tolerance: float = 1e-8,
) -> KernelValidation:
    """Validate the canonical E47 kernel operator."""

    if zero_tolerance <= 0:
        raise ValueError("zero_tolerance must be positive.")
    if spectrum_tolerance <= 0:
        raise ValueError("spectrum_tolerance must be positive.")

    if operators is None:
        operators = build_e47_operators()

    kernel_eigenvalues = np.array(
        operators.kernel.eigenenergies(),
        dtype=float,
    )
    kernel_squared_eigenvalues = np.array(
        operators.kernel_squared.eigenenergies(),
        dtype=float,
    )
    casimir_eigenvalues = np.array(
        operators.casimir.eigenenergies(),
        dtype=float,
    )

    kernel_dimension = int(np.count_nonzero(np.abs(kernel_eigenvalues) < zero_tolerance))
    coherence_fraction = kernel_dimension / operators.carrier_dimension
    positive_k2 = kernel_squared_eigenvalues[kernel_squared_eigenvalues > zero_tolerance]
    k2_spectral_gap = int(round(float(np.min(positive_k2))))

    casimir_spectrum = _cluster_values(casimir_eigenvalues, tol=spectrum_tolerance)
    kernel_zero_cluster = _cluster_values(
        kernel_eigenvalues[np.abs(kernel_eigenvalues) < zero_tolerance],
        tol=spectrum_tolerance,
    )

    checks = {
        "carrier_dimension": {
            "expected": EXPECTED_CARRIER_DIMENSION,
            "computed": operators.carrier_dimension,
            "pass": operators.carrier_dimension == EXPECTED_CARRIER_DIMENSION,
        },
        "kernel_dimension": {
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": kernel_dimension,
            "pass": kernel_dimension == EXPECTED_KERNEL_DIMENSION,
        },
        "coherence_fraction": {
            "expected": EXPECTED_COHERENCE_FRACTION,
            "computed": coherence_fraction,
            "pass": abs(coherence_fraction - EXPECTED_COHERENCE_FRACTION) < zero_tolerance,
        },
        "k2_spectral_gap": {
            "expected": EXPECTED_K2_SPECTRAL_GAP,
            "computed": k2_spectral_gap,
            "pass": k2_spectral_gap == EXPECTED_K2_SPECTRAL_GAP,
        },
    }

    return KernelValidation(
        inputs={
            "base_spin": operators.base_spin,
            "base_dimension": operators.base_dimension,
            "tensor_product_rank": operators.tensor_product_rank,
        },
        results={
            "carrier_dimension": operators.carrier_dimension,
            "kernel_dimension": kernel_dimension,
            "coherence_fraction": coherence_fraction,
            "k2_spectral_gap": k2_spectral_gap,
            "casimir_spectrum": casimir_spectrum,
            "kernel_eigenvalues": kernel_zero_cluster,
        },
        tolerances={
            "zero_tolerance": float(zero_tolerance),
            "spectrum_tolerance": float(spectrum_tolerance),
        },
        checks=checks,
        status="pass" if all(check["pass"] for check in checks.values()) else "fail",
    )


def require_valid_e47_kernel(
    operators: E47Operators | None = None,
    *,
    zero_tolerance: float = 1e-8,
    spectrum_tolerance: float = 1e-8,
) -> KernelValidation:
    """Validate the canonical kernel and raise on failure."""

    validation = validate_e47_kernel(
        operators,
        zero_tolerance=zero_tolerance,
        spectrum_tolerance=spectrum_tolerance,
    )
    if validation.status == "pass":
        return validation

    failures = [
        name
        for name, check in validation.checks.items()
        if not bool(check["pass"])
    ]
    raise ValueError(f"E47 kernel validation failed: {', '.join(failures)}")


__all__ = [
    "E47Operators",
    "EXPECTED_KERNEL_DIMENSION",
    "KernelValidation",
    "build_e47_operators",
    "require_valid_e47_kernel",
    "validate_e47_kernel",
]
