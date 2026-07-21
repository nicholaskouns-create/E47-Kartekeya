"""Spectral projector onto the canonical E47 kernel.

This module constructs the orthogonal projector P₄₇ onto

    E₄₇ = ker(K),

where

    K = (C - 6I)(C - 30I)

acts on the carrier

    V = V₂ ⊗ V₂ ⊗ V₂.

The projector is built from the eigenspaces of the Hermitian operator K².
It is distinct from K itself:

- K is a polynomial kernel operator.
- P₄₇ is an orthogonal projector.
- P₄₇ satisfies P₄₇² = P₄₇.
- K satisfies K P₄₇ = 0.

Scope
-----
This module validates finite-dimensional spectral and projector properties.
It does not establish any experimental or physical interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import qutip as qt

from e47.su2_kernel import (
    EXPECTED_KERNEL_DIMENSION,
    E47Operators,
    build_e47_operators,
)


@dataclass(frozen=True)
class E47Projector:
    """Canonical orthogonal projector onto the E47 kernel."""

    projector: qt.Qobj
    kernel_basis: tuple[qt.Qobj, ...]
    kernel_dimension: int
    construction_tolerance: float


@dataclass(frozen=True)
class ProjectorValidation:
    """Structured validation output for the E47 projector."""

    inputs: dict[str, Any]
    results: dict[str, Any]
    tolerances: dict[str, float]
    checks: dict[str, dict[str, Any]]
    status: str


def construct_e47_projector(
    operators: E47Operators | None = None,
    *,
    kernel_tolerance: float = 1e-8,
) -> E47Projector:
    """
    Construct the orthogonal projector onto ker(K).

    The eigensystem of K² is used because K² is Hermitian and
    positive semidefinite. Eigenvectors with eigenvalue below
    ``kernel_tolerance`` span the canonical E47 kernel.

    Parameters
    ----------
    operators:
        Canonical operators returned by ``build_e47_operators``.
        If omitted, they are constructed automatically.
    kernel_tolerance:
        Numerical threshold used to classify eigenvectors as belonging
        to the zero eigenspace of K².

    Returns
    -------
    E47Projector
        The orthogonal projector, its orthonormal kernel basis,
        and construction metadata.
    """

    if kernel_tolerance <= 0:
        raise ValueError("kernel_tolerance must be positive.")

    if operators is None:
        operators = build_e47_operators()

    eigenvalues, eigenstates = (
        operators.kernel_squared.eigenstates()
    )

    kernel_basis = tuple(
        state
        for eigenvalue, state in zip(
            eigenvalues,
            eigenstates,
            strict=True,
        )
        if abs(float(np.real_if_close(eigenvalue)))
        < kernel_tolerance
    )

    if not kernel_basis:
        raise RuntimeError(
            "No zero-eigenvalue states were identified for K²."
        )

    projector = sum(
        (
            state * state.dag()
            for state in kernel_basis
        ),
        qt.Qobj(
            np.zeros(
                (
                    operators.carrier_dimension,
                    operators.carrier_dimension,
                ),
                dtype=complex,
            ),
            dims=operators.identity_total.dims,
        ),
    )

    projector = 0.5 * (
        projector + projector.dag()
    )

    return E47Projector(
        projector=projector,
        kernel_basis=kernel_basis,
        kernel_dimension=len(kernel_basis),
        construction_tolerance=kernel_tolerance,
    )


def validate_e47_projector(
    projector_data: E47Projector | None = None,
    operators: E47Operators | None = None,
    *,
    idempotence_tolerance: float = 1e-10,
    hermiticity_tolerance: float = 1e-10,
    annihilation_tolerance: float = 1e-8,
    trace_tolerance: float = 1e-8,
    basis_tolerance: float = 1e-10,
) -> ProjectorValidation:
    """
    Validate the canonical E47 spectral projector.

    Checks include:

    - projector rank and trace;
    - idempotence;
    - Hermiticity;
    - kernel annihilation K P₄₇ = 0;
    - invariance K² P₄₇ = 0;
    - orthonormality of the extracted kernel basis;
    - action as the identity on its own basis;
    - commutation with K and C.
    """

    tolerance_values = {
        "idempotence_tolerance": idempotence_tolerance,
        "hermiticity_tolerance": hermiticity_tolerance,
        "annihilation_tolerance": annihilation_tolerance,
        "trace_tolerance": trace_tolerance,
        "basis_tolerance": basis_tolerance,
    }

    for name, value in tolerance_values.items():
        if value <= 0:
            raise ValueError(
                f"{name} must be positive."
            )

    if operators is None:
        operators = build_e47_operators()

    if projector_data is None:
        projector_data = construct_e47_projector(
            operators
        )

    projector = projector_data.projector

    if projector.shape != (
        operators.carrier_dimension,
        operators.carrier_dimension,
    ):
        raise ValueError(
            "Projector dimension does not match "
            "the E47 carrier dimension."
        )

    idempotence_error = float(
        (projector * projector - projector).norm()
    )

    hermiticity_error = float(
        (projector - projector.dag()).norm()
    )

    kernel_annihilation_error = float(
        (operators.kernel * projector).norm()
    )

    kernel_squared_annihilation_error = float(
        (
            operators.kernel_squared
            * projector
        ).norm()
    )

    projector_kernel_commutator_error = float(
        (
            projector * operators.kernel
            - operators.kernel * projector
        ).norm()
    )

    projector_casimir_commutator_error = float(
        (
            projector * operators.casimir
            - operators.casimir * projector
        ).norm()
    )

    trace_value = complex(projector.tr())
    trace_imaginary_error = abs(trace_value.imag)
    trace_real = float(trace_value.real)
    trace_error = abs(
        trace_real - EXPECTED_KERNEL_DIMENSION
    )

    projector_eigenvalues = np.real_if_close(
        projector.eigenenergies()
    ).astype(float)

    numerical_rank = int(
        np.sum(projector_eigenvalues > 0.5)
    )

    basis_size = len(
        projector_data.kernel_basis
    )

    gram_matrix = np.array(
        [
            [
                complex(
                    left.dag() * right
                )
                for right in (
                    projector_data.kernel_basis
                )
            ]
            for left in (
                projector_data.kernel_basis
            )
        ],
        dtype=complex,
    )

    gram_error = float(
        np.linalg.norm(
            gram_matrix
            - np.eye(basis_size),
            ord="fro",
        )
    )

    basis_action_errors = [
        float(
            (
                projector * state - state
            ).norm()
        )
        for state in projector_data.kernel_basis
    ]

    maximum_basis_action_error = (
        max(basis_action_errors)
        if basis_action_errors
        else float("inf")
    )

    complement = (
        operators.identity_total - projector
    )

    complement_idempotence_error = float(
        (
            complement * complement
            - complement
        ).norm()
    )

    orthogonal_decomposition_error = float(
        (
            projector * complement
        ).norm()
    )

    checks: dict[str, dict[str, Any]] = {
        "kernel_basis_dimension": {
            "description": (
                "The extracted zero eigenspace of K² "
                "contains exactly 47 orthonormal vectors."
            ),
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": basis_size,
            "pass": (
                basis_size
                == EXPECTED_KERNEL_DIMENSION
            ),
        },
        "projector_trace": {
            "description": (
                "The trace of an orthogonal projector "
                "equals its rank."
            ),
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": trace_real,
            "absolute_error": trace_error,
            "imaginary_component_error": (
                trace_imaginary_error
            ),
            "pass": (
                trace_error < trace_tolerance
                and trace_imaginary_error
                < trace_tolerance
            ),
        },
        "projector_rank": {
            "description": (
                "The numerical rank of P₄₇ is 47."
            ),
            "expected": EXPECTED_KERNEL_DIMENSION,
            "computed": numerical_rank,
            "pass": (
                numerical_rank
                == EXPECTED_KERNEL_DIMENSION
            ),
        },
        "projector_idempotence": {
            "description": (
                "P₄₇ is idempotent: P₄₇² = P₄₇."
            ),
            "expected": 0.0,
            "computed": idempotence_error,
            "pass": (
                idempotence_error
                < idempotence_tolerance
            ),
        },
        "projector_hermiticity": {
            "description": (
                "P₄₇ is Hermitian: P₄₇† = P₄₇."
            ),
            "expected": 0.0,
            "computed": hermiticity_error,
            "pass": (
                hermiticity_error
                < hermiticity_tolerance
            ),
        },
        "kernel_annihilation": {
            "description": (
                "K annihilates the range of P₄₇: "
                "K P₄₇ = 0."
            ),
            "expected": 0.0,
            "computed": (
                kernel_annihilation_error
            ),
            "pass": (
                kernel_annihilation_error
                < annihilation_tolerance
            ),
        },
        "kernel_squared_annihilation": {
            "description": (
                "K² annihilates the range of P₄₇."
            ),
            "expected": 0.0,
            "computed": (
                kernel_squared_annihilation_error
            ),
            "pass": (
                kernel_squared_annihilation_error
                < annihilation_tolerance
            ),
        },
        "kernel_basis_orthonormality": {
            "description": (
                "The extracted kernel eigenvectors "
                "form an orthonormal basis."
            ),
            "expected": 0.0,
            "computed": gram_error,
            "pass": (
                gram_error
                < basis_tolerance
            ),
        },
        "projector_identity_on_basis": {
            "description": (
                "P₄₇ acts as the identity on every "
                "kernel-basis vector."
            ),
            "expected": 0.0,
            "computed": (
                maximum_basis_action_error
            ),
            "pass": (
                maximum_basis_action_error
                < basis_tolerance
            ),
        },
        "projector_commutes_with_kernel": {
            "description": (
                "P₄₇ and K commute."
            ),
            "expected": 0.0,
            "computed": (
                projector_kernel_commutator_error
            ),
            "pass": (
                projector_kernel_commutator_error
                < annihilation_tolerance
            ),
        },
        "projector_commutes_with_casimir": {
            "description": (
                "P₄₇ is a spectral projector of C "
                "and therefore commutes with C."
            ),
            "expected": 0.0,
            "computed": (
                projector_casimir_commutator_error
            ),
            "pass": (
                projector_casimir_commutator_error
                < annihilation_tolerance
            ),
        },
        "complement_idempotence": {
            "description": (
                "I - P₄₇ is also an orthogonal "
                "projector."
            ),
            "expected": 0.0,
            "computed": (
                complement_idempotence_error
            ),
            "pass": (
                complement_idempotence_error
                < idempotence_tolerance
            ),
        },
        "orthogonal_decomposition": {
            "description": (
                "The projector and its complement "
                "have orthogonal ranges."
            ),
            "expected": 0.0,
            "computed": (
                orthogonal_decomposition_error
            ),
            "pass": (
                orthogonal_decomposition_error
                < basis_tolerance
            ),
        },
    }

    all_passed = all(
        bool(check["pass"])
        for check in checks.values()
    )

    results = {
        "carrier_dimension": (
            operators.carrier_dimension
        ),
        "projector_rank": numerical_rank,
        "projector_trace": trace_real,
        "kernel_basis_dimension": basis_size,
        "construction_tolerance": (
            projector_data.construction_tolerance
        ),
        "projector_idempotence_error": (
            idempotence_error
        ),
        "projector_hermiticity_error": (
            hermiticity_error
        ),
        "kernel_annihilation_error": (
            kernel_annihilation_error
        ),
        "kernel_squared_annihilation_error": (
            kernel_squared_annihilation_error
        ),
        "basis_orthonormality_error": (
            gram_error
        ),
        "maximum_basis_action_error": (
            maximum_basis_action_error
        ),
        "projector_kernel_commutator_error": (
            projector_kernel_commutator_error
        ),
        "projector_casimir_commutator_error": (
            projector_casimir_commutator_error
        ),
        "complement_idempotence_error": (
            complement_idempotence_error
        ),
        "orthogonal_decomposition_error": (
            orthogonal_decomposition_error
        ),
    }

    return ProjectorValidation(
        inputs={
            "projector_definition": (
                "P47 = sum_i |e_i><e_i| "
                "over the zero eigenspace of K^2"
            ),
            "kernel_operator": (
                "K = (C - 6I)(C - 30I)"
            ),
            "carrier_dimension": (
                operators.carrier_dimension
            ),
            "expected_rank": (
                EXPECTED_KERNEL_DIMENSION
            ),
        },
        results=results,
        tolerances=tolerance_values,
        checks=checks,
        status=(
            "pass"
            if all_passed
            else "fail"
        ),
    )


def require_valid_e47_projector(
    validation: ProjectorValidation,
) -> None:
    """
    Raise SystemExit if any projector check failed.
    """

    if validation.status != "pass":
        failed = [
            name
            for name, check
            in validation.checks.items()
            if not bool(check["pass"])
        ]

        raise SystemExit(
            "Canonical E47 projector validation failed: "
            + ", ".join(failed)
        )


if __name__ == "__main__":
    operators = build_e47_operators()

    projector_data = construct_e47_projector(
        operators
    )

    validation = validate_e47_projector(
        projector_data,
        operators,
    )

    require_valid_e47_projector(
        validation
    )

    print(
        "Canonical E47 projector validation PASSED."
    )
