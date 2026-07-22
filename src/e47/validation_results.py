"""Aggregated validation results for the canonical E47 construction.

This module orchestrates all five validation layers and provides a single
immutable certificate structure that serves as the canonical validation
record for the E47 algebra.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from e47.contraction import (
    ContractionValidation,
    validate_contraction,
)
from e47.projector import (
    ProjectorValidation,
    construct_e47_projector,
    validate_e47_projector,
)
from e47.semigroup import (
    SemigroupValidation,
    validate_semigroup,
)
from e47.su2_kernel import (
    KernelValidation,
    build_e47_operators,
    validate_e47_kernel,
)


@dataclass(frozen=True)
class QuTiPValidation:
    """Validation result from QuTiP-based checks."""

    valid: bool
    carrier_dimension: int
    kernel_dimension: int
    coherence_fraction: float
    k2_spectral_gap: int
    errors: tuple[str, ...]


@dataclass(frozen=True)
class E47ValidationResults:
    """Complete immutable aggregation of all E47 validation certificates."""

    kernel_validation: KernelValidation
    projector_validation: ProjectorValidation
    contraction_validation: ContractionValidation
    semigroup_validation: SemigroupValidation
    qutip_validation: QuTiPValidation

    @property
    def valid(self) -> bool:
        """True if and only if all five layers pass validation."""
        return all(
            (
                self.kernel_validation.status == "pass",
                self.projector_validation.status == "pass",
                self.contraction_validation.valid,
                self.semigroup_validation.valid,
                self.qutip_validation.valid,
            )
        )

    def summarize(self) -> dict[str, Any]:
        """Return a summary dictionary suitable for logging or reporting."""
        return {
            "valid": self.valid,
            "kernel_valid": self.kernel_validation.status == "pass",
            "projector_valid": self.projector_validation.status == "pass",
            "contraction_valid": self.contraction_validation.valid,
            "semigroup_valid": self.semigroup_validation.valid,
            "qutip_valid": self.qutip_validation.valid,
            "kernel_dimension": self.kernel_validation.results["kernel_dimension"],
            "coherence_fraction": self.kernel_validation.results[
                "coherence_fraction"
            ],
            "k2_spectral_gap": round(
                self.kernel_validation.results["k2_spectral_gap"]
            ),
            "projector_rank": self.projector_validation.results["projector_rank"],
            "projector_trace": self.projector_validation.results["projector_trace"],
            "contraction_epsilon": self.contraction_validation.epsilon,
            "contraction_epsilon_max": (
                self.contraction_validation.epsilon_max
            ),
            "semigroup_decay_bound": (
                self.semigroup_validation.expected_decay_bound
            ),
        }


def run_all_validations() -> E47ValidationResults:
    """Execute all five validation layers and aggregate results.

    This is the canonical validation entry point for the E47 construction.
    It constructs operators, projectors, and validates all spectral,
    algebraic, and dynamical properties in sequence.

    Returns
    -------
    E47ValidationResults
        Immutable aggregation of all five validation certificates.

    Raises
    ------
    RuntimeError
        If any critical construction step fails before aggregation can begin.
    """

    # Layer 1: Kernel operator validation
    operators = build_e47_operators()
    kernel_validation = validate_e47_kernel(operators)

    # Layer 2: Projector validation
    projector_data = construct_e47_projector(operators)
    projector_validation = validate_e47_projector(projector_data, operators)

    # Layer 3: Contraction validation
    # qutip Qobj must be converted to numpy for the numpy-based validators.
    kernel_array = operators.kernel.full()
    projector_array = projector_data.projector.full()

    contraction_validation = validate_contraction(
        kernel_array,
        projector_array,
    )

    # Layer 4: Semigroup validation
    semigroup_validation = validate_semigroup(
        kernel_array,
        projector_array,
    )

    # Layer 5: QuTiP validation (simplified)
    qutip_errors: list[str] = []
    qutip_valid = True

    if operators.carrier_dimension != 125:
        qutip_errors.append(
            f"Carrier dimension {operators.carrier_dimension} != 125."
        )
        qutip_valid = False

    if kernel_validation.results["kernel_dimension"] != 47:
        qutip_errors.append(
            f"Kernel dimension {kernel_validation.results['kernel_dimension']} != 47."
        )
        qutip_valid = False

    expected_coherence = 47 / 125
    actual_coherence = kernel_validation.results["coherence_fraction"]
    if not abs(actual_coherence - expected_coherence) < 1e-12:
        qutip_errors.append(
            f"Coherence fraction {actual_coherence} != {expected_coherence}."
        )
        qutip_valid = False

    if not abs(kernel_validation.results["k2_spectral_gap"] - 11664) < 1e-3:
        qutip_errors.append(
            f"K² spectral gap {kernel_validation.results['k2_spectral_gap']} != 11664."
        )
        qutip_valid = False

    k2_spectral_gap_int: int = round(
        kernel_validation.results["k2_spectral_gap"]
    )

    qutip_validation = QuTiPValidation(
        valid=qutip_valid,
        carrier_dimension=operators.carrier_dimension,
        kernel_dimension=kernel_validation.results["kernel_dimension"],
        coherence_fraction=actual_coherence,
        k2_spectral_gap=k2_spectral_gap_int,
        errors=tuple(qutip_errors),
    )

    return E47ValidationResults(
        kernel_validation=kernel_validation,
        projector_validation=projector_validation,
        contraction_validation=contraction_validation,
        semigroup_validation=semigroup_validation,
        qutip_validation=qutip_validation,
    )


def require_all_validations(
    results: E47ValidationResults,
) -> E47ValidationResults:
    """Validate the aggregate and raise one aggregated error on failure.

    Parameters
    ----------
    results
        Aggregated validation results.

    Returns
    -------
    E47ValidationResults
        The input results, unchanged.

    Raises
    ------
    ValueError
        If any validation layer failed. The error message lists all failures
        across all five layers.
    """

    if results.valid:
        return results

    error_messages: list[str] = []

    if results.kernel_validation.status != "pass":
        failed_checks = [
            name
            for name, check in results.kernel_validation.checks.items()
            if not bool(check["pass"])
        ]
        error_messages.append(
            f"Kernel validation failed: {', '.join(failed_checks)}"
        )

    if results.projector_validation.status != "pass":
        failed_checks = [
            name
            for name, check in results.projector_validation.checks.items()
            if not bool(check["pass"])
        ]
        error_messages.append(
            f"Projector validation failed: {', '.join(failed_checks)}"
        )

    if not results.contraction_validation.valid:
        error_messages.append(
            "Contraction validation failed: "
            + ", ".join(results.contraction_validation.errors)
        )

    if not results.semigroup_validation.valid:
        error_messages.append(
            "Semigroup validation failed: "
            + ", ".join(results.semigroup_validation.errors)
        )

    if not results.qutip_validation.valid:
        error_messages.append(
            "QuTiP validation failed: "
            + ", ".join(results.qutip_validation.errors)
        )

    aggregated_error = "\n".join(
        f"  {index}. {message}"
        for index, message in enumerate(error_messages, start=1)
    )

    raise ValueError(
        "E47 canonical validation FAILED:\n" f"{aggregated_error}"
    )


__all__ = [
    "E47ValidationResults",
    "QuTiPValidation",
    "require_all_validations",
    "run_all_validations",
]
