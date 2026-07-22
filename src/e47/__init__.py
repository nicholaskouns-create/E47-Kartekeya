"""Canonical E47 SU(2) kernel algebra and validation.

This package provides finite-dimensional algebraic and numerical validation
of the E47 construction:

    V = V₂ ⊗ V₂ ⊗ V₂,    dim(V) = 125
    K = (C - 6I)(C - 30I)
    E₄₇ = ker(K),       dim(E₄₇) = 47

and of the SU(3) adjoint 512-dimensional singlet construction:

    V = V_adj ⊗ V_adj ⊗ V_adj,    dim(V) = 512
    K = C₂^tot
    Singlet = ker(C₂^tot),       dim = 2

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

from .su3_adjoint import (
    SU3AdjointOperators,
    SU3Certificate,
    SU3SingletProjector,
    adjoint_generators,
    build_su3_adjoint_operators,
    build_total_casimir,
    construct_singlet_projector,
    d_state,
    f_state,
    gell_mann_matrices,
    leakage,
    run_su3_adjoint_validation,
    structure_constants,
    symmetric_structure_constants,
    validate_su3_adjoint,
)

__all__ = [
    # SU(2) E47 kernel
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
    # SU(3) 512-dim adjoint
    "SU3AdjointOperators",
    "SU3Certificate",
    "SU3SingletProjector",
    "adjoint_generators",
    "build_su3_adjoint_operators",
    "build_total_casimir",
    "construct_singlet_projector",
    "d_state",
    "f_state",
    "gell_mann_matrices",
    "leakage",
    "run_su3_adjoint_validation",
    "structure_constants",
    "symmetric_structure_constants",
    "validate_su3_adjoint",
]
