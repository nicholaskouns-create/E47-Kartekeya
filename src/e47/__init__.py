"""Canonical E47 SU(2) kernel algebra and validation.

This package provides finite-dimensional algebraic and numerical validation
of the E47 construction:

    V = V₂ ⊗ V₂ ⊗ V₂,    dim(V) = 125
    K = (C - 6I)(C - 30I)
    E₄₇ = ker(K),       dim(E₄₇) = 47

Public API includes operators, projectors, contractions, semigroups,
and aggregated validation infrastructure.

Scope
-----
This package validates algebraic and numerical properties only.
It does not establish experimental, physical, or hardware validation.
"""

from .su2_kernel import (
    E47Operators,
    KernelValidation,
    build_e47_operators,
    require_valid_e47_kernel,
    validate_e47_kernel,
)

from .projector import (
    E47Projector,
    ProjectorValidation,
    construct_e47_projector,
    require_valid_e47_projector,
    validate_e47_projector,
)

from .contraction import (
    ContractionValidation,
    build_contraction,
    require_valid_contraction,
    validate_contraction,
)

from .semigroup import (
    SemigroupValidation,
    construct_semigroup,
    require_valid_semigroup,
    validate_semigroup,
)

from .validation_results import (
    E47ValidationResults,
    require_all_validations,
    run_all_validations,
)

__all__ = [
    "E47Operators",
    "KernelValidation",
    "E47Projector",
    "ProjectorValidation",
    "ContractionValidation",
    "SemigroupValidation",
    "E47ValidationResults",
    "build_e47_operators",
    "validate_e47_kernel",
    "require_valid_e47_kernel",
    "construct_e47_projector",
    "validate_e47_projector",
    "require_valid_e47_projector",
    "build_contraction",
    "validate_contraction",
    "require_valid_contraction",
    "construct_semigroup",
    "validate_semigroup",
    "require_valid_semigroup",
    "run_all_validations",
    "require_all_validations",
]
