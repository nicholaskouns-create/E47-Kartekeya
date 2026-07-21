"""Discrete contraction onto the canonical E47 spectral kernel.

The contraction operator is

    Gamma(epsilon) = I - epsilon K^2,

where

    K = (C - 6 I)(C - 30 I).

Because K is Hermitian and positive semidefinite after squaring, repeated
application of Gamma converges to the orthogonal projector onto ker(K)
whenever

    0 < epsilon < 2 / lambda_max(K^2).

For the canonical V_2^{tensor 3} carrier,

    spec(K^2) = {0, 11664, 12544, 19600, 32400, 186624},

so the sharp upper stability bound is

    epsilon_max = 1 / 93312.

The more restrictive interval

    0 < epsilon <= 1 / 186624

keeps every eigenvalue of Gamma in [0, 1), producing monotone,
non-oscillatory contraction on the complement of E47.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import numpy as np
from numpy.typing import ArrayLike, NDArray


FloatArray = NDArray[np.float64]
ComplexArray = NDArray[np.complex128]
Matrix = NDArray[np.complexfloating]


CARRIER_DIMENSION: Final[int] = 125
E47_DIMENSION: Final[int] = 47
COMPLEMENT_DIMENSION: Final[int] = 78

CANONICAL_K2_EIGENVALUES: Final[tuple[int, ...]] = (
    0,
    11_664,
    12_544,
    19_600,
    32_400,
    186_624,
)

CANONICAL_SPECTRAL_GAP: Final[int] = 11_664
CANONICAL_K2_NORM: Final[int] = 186_624

# Sharp interval for convergence:
#       0 < epsilon < 2 / ||K^2||
SHARP_EPSILON_MAX: Final[float] = 2.0 / CANONICAL_K2_NORM

# Conservative interval with no negative Gamma eigenvalues:
#       0 < epsilon <= 1 / ||K^2||
MONOTONE_EPSILON_MAX: Final[float] = 1.0 / CANONICAL_K2_NORM

DEFAULT_EPSILON: Final[float] = 0.9 / CANONICAL_K2_NORM


@dataclass(frozen=True)
class ContractionValidation:
    """Structured certificate for an E47 contraction operator."""

    valid: bool
    epsilon: float
    epsilon_max: float
    monotone_epsilon_max: float

    carrier_dimension: int
    kernel_dimension: int
    complement_dimension: int

    k2_min_eigenvalue: float
    k2_max_eigenvalue: float
    spectral_gap: float

    gamma_min_eigenvalue: float
    gamma_max_eigenvalue: float
    complement_spectral_radius: float

    hermitian_residual: float
    kernel_fixed_residual: float
    projector_commutator_residual: float
    asymptotic_projector_residual: float

    iterations: int
    tolerance: float
    errors: tuple[str, ...]


def _as_square_matrix(
    matrix: ArrayLike,
    *,
    name: str,
) -> ComplexArray:
    """Convert an input to a finite square complex matrix."""

    array = np.asarray(matrix, dtype=np.complex128)

    if array.ndim != 2:
        raise ValueError(f"{name} must be two-dimensional; got ndim={array.ndim}.")

    rows, columns = array.shape
    if rows != columns:
        raise ValueError(
            f"{name} must be square; got shape {array.shape}."
        )

    if rows == 0:
        raise ValueError(f"{name} must be non-empty.")

    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite entries.")

    return array


def build_contraction(
    kernel: ArrayLike,
    epsilon: float = DEFAULT_EPSILON,
) -> ComplexArray:
    """Construct Gamma = I - epsilon K^2.

    Parameters
    ----------
    kernel
        Hermitian spectral-kernel matrix K.
    epsilon
        Positive discrete contraction step.

    Returns
    -------
    numpy.ndarray
        The contraction matrix Gamma.

    Raises
    ------
    ValueError
        If K is malformed or epsilon is not finite and positive.
    """

    K = _as_square_matrix(kernel, name="kernel")

    if not np.isfinite(epsilon):
        raise ValueError("epsilon must be finite.")

    if epsilon <= 0.0:
        raise ValueError(f"epsilon must be positive; got {epsilon!r}.")

    identity = np.eye(K.shape[0], dtype=np.complex128)
    K2 = K @ K

    return identity - epsilon * K2


def apply_contraction(
    gamma: ArrayLike,
    state: ArrayLike,
) -> ComplexArray:
    """Apply one contraction step to a vector or matrix of states."""

    Gamma = _as_square_matrix(gamma, name="gamma")
    state_array = np.asarray(state, dtype=np.complex128)

    if state_array.ndim not in (1, 2):
        raise ValueError(
            "state must be a vector or a matrix whose columns are states."
        )

    if state_array.shape[0] != Gamma.shape[0]:
        raise ValueError(
            "state dimension does not match gamma: "
            f"{state_array.shape[0]} != {Gamma.shape[0]}."
        )

    if not np.all(np.isfinite(state_array)):
        raise ValueError("state contains non-finite entries.")

    return Gamma @ state_array


def iterate_contraction(
    gamma: ArrayLike,
    state: ArrayLike,
    iterations: int,
) -> ComplexArray:
    """Apply Gamma repeatedly without renormalizing intermediate states.

    The unnormalized iteration preserves the linear convergence theorem:

        Gamma^n x -> P_E47 x.

    Renormalization should only be performed afterward when a normalized
    state vector is required.
    """

    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise TypeError("iterations must be an integer.")

    if iterations < 0:
        raise ValueError("iterations must be non-negative.")

    Gamma = _as_square_matrix(gamma, name="gamma")
    result = np.asarray(state, dtype=np.complex128).copy()

    if result.ndim not in (1, 2):
        raise ValueError(
            "state must be a vector or a matrix whose columns are states."
        )

    if result.shape[0] != Gamma.shape[0]:
        raise ValueError(
            "state dimension does not match gamma: "
            f"{result.shape[0]} != {Gamma.shape[0]}."
        )

    if not np.all(np.isfinite(result)):
        raise ValueError("state contains non-finite entries.")

    for _ in range(iterations):
        result = Gamma @ result

    return result


def contraction_power(
    gamma: ArrayLike,
    iterations: int,
) -> ComplexArray:
    """Return Gamma raised to a non-negative integer power."""

    if isinstance(iterations, bool) or not isinstance(iterations, int):
        raise TypeError("iterations must be an integer.")

    if iterations < 0:
        raise ValueError("iterations must be non-negative.")

    Gamma = _as_square_matrix(gamma, name="gamma")
    return np.linalg.matrix_power(Gamma, iterations)


def required_iterations(
    complement_spectral_radius: float,
    tolerance: float = 1e-12,
) -> int:
    """Estimate iterations needed for complement suppression.

    Returns the least integer n satisfying

        radius**n <= tolerance.

    A radius of zero requires one step. A radius greater than or equal to
    one has no finite convergence certificate.
    """

    if not np.isfinite(complement_spectral_radius):
        raise ValueError("complement_spectral_radius must be finite.")

    if not np.isfinite(tolerance):
        raise ValueError("tolerance must be finite.")

    if tolerance <= 0.0 or tolerance >= 1.0:
        raise ValueError("tolerance must lie strictly between 0 and 1.")

    if complement_spectral_radius < 0.0:
        raise ValueError("complement_spectral_radius cannot be negative.")

    if complement_spectral_radius == 0.0:
        return 1

    if complement_spectral_radius >= 1.0:
        raise ValueError(
            "No finite contraction bound exists when spectral radius >= 1."
        )

    return int(
        np.ceil(
            np.log(tolerance) / np.log(complement_spectral_radius)
        )
    )


def validate_contraction(
    kernel: ArrayLike,
    projector: ArrayLike | None = None,
    *,
    epsilon: float = DEFAULT_EPSILON,
    iterations: int | None = None,
    tolerance: float = 1e-10,
    zero_tolerance: float = 1e-8,
) -> ContractionValidation:
    """Validate Gamma = I - epsilon K^2.

    Parameters
    ----------
    kernel
        Canonical Hermitian E47 kernel K.
    projector
        Optional orthogonal projector P47 onto ker(K). Supplying it enables
        exact fixed-space and asymptotic-projector checks.
    epsilon
        Positive contraction step.
    iterations
        Power used to compare Gamma^n with P47. When omitted, an iteration
        count is estimated from the complement spectral radius and tolerance.
    tolerance
        Numerical tolerance for Hermiticity, commutators, and convergence.
    zero_tolerance
        Threshold used to identify numerical zero eigenvalues of K^2.

    Returns
    -------
    ContractionValidation
        Immutable validation certificate.
    """

    errors: list[str] = []

    if not np.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("epsilon must be finite and positive.")

    if not np.isfinite(tolerance) or tolerance <= 0.0:
        raise ValueError("tolerance must be finite and positive.")

    if not np.isfinite(zero_tolerance) or zero_tolerance <= 0.0:
        raise ValueError("zero_tolerance must be finite and positive.")

    K = _as_square_matrix(kernel, name="kernel")
    dimension = K.shape[0]

    identity = np.eye(dimension, dtype=np.complex128)
    K2 = K @ K
    Gamma = identity - epsilon * K2

    kernel_hermitian_residual = float(
        np.linalg.norm(K - K.conj().T, ord=2)
    )
    gamma_hermitian_residual = float(
        np.linalg.norm(Gamma - Gamma.conj().T, ord=2)
    )
    hermitian_residual = max(
        kernel_hermitian_residual,
        gamma_hermitian_residual,
    )

    if hermitian_residual > tolerance:
        errors.append(
            "K or Gamma is not Hermitian within tolerance: "
            f"{hermitian_residual:.3e} > {tolerance:.3e}."
        )

    # Hermitian eigensolver is justified after recording the residual.
    K2_hermitian = 0.5 * (K2 + K2.conj().T)
    k2_eigenvalues = np.linalg.eigvalsh(K2_hermitian)

    k2_min = float(k2_eigenvalues[0])
    k2_max = float(k2_eigenvalues[-1])

    if k2_min < -zero_tolerance:
        errors.append(
            f"K^2 is not positive semidefinite: min eigenvalue={k2_min:.3e}."
        )

    zero_mask = np.abs(k2_eigenvalues) <= zero_tolerance
    kernel_dimension = int(np.count_nonzero(zero_mask))
    complement_dimension = dimension - kernel_dimension

    positive_eigenvalues = k2_eigenvalues[~zero_mask]
    spectral_gap = (
        float(positive_eigenvalues[0])
        if positive_eigenvalues.size
        else 0.0
    )

    epsilon_max = np.inf if k2_max <= zero_tolerance else 2.0 / k2_max
    monotone_epsilon_max = (
        np.inf if k2_max <= zero_tolerance else 1.0 / k2_max
    )

    if epsilon >= epsilon_max:
        errors.append(
            "epsilon is outside the strict convergence interval: "
            f"{epsilon:.17g} >= {epsilon_max:.17g}."
        )

    gamma_eigenvalues = 1.0 - epsilon * k2_eigenvalues
    gamma_min = float(np.min(gamma_eigenvalues))
    gamma_max = float(np.max(gamma_eigenvalues))

    complement_gamma_eigenvalues = gamma_eigenvalues[~zero_mask]
    complement_spectral_radius = (
        float(np.max(np.abs(complement_gamma_eigenvalues)))
        if complement_gamma_eigenvalues.size
        else 0.0
    )

    if complement_spectral_radius >= 1.0:
        errors.append(
            "Gamma is not strictly contractive on ker(K)^perp: "
            f"spectral radius={complement_spectral_radius:.17g}."
        )

    kernel_fixed_residual = float("nan")
    projector_commutator_residual = float("nan")
    asymptotic_projector_residual = float("nan")

    if iterations is None:
        if complement_spectral_radius == 0.0:
            iterations_used = 1
        elif complement_spectral_radius < 1.0:
            iterations_used = required_iterations(
                complement_spectral_radius,
                tolerance=tolerance,
            )
        else:
            iterations_used = 0
    else:
        if isinstance(iterations, bool) or not isinstance(iterations, int):
            raise TypeError("iterations must be an integer or None.")

        if iterations < 0:
            raise ValueError("iterations must be non-negative.")

        iterations_used = iterations

    if projector is not None:
        P = _as_square_matrix(projector, name="projector")

        if P.shape != K.shape:
            raise ValueError(
                "projector and kernel must have the same shape; "
                f"got {P.shape} and {K.shape}."
            )

        projector_hermitian_residual = float(
            np.linalg.norm(P - P.conj().T, ord=2)
        )
        projector_idempotence_residual = float(
            np.linalg.norm(P @ P - P, ord=2)
        )

        if projector_hermitian_residual > tolerance:
            errors.append(
                "Projector is not Hermitian within tolerance: "
                f"{projector_hermitian_residual:.3e}."
            )

        if projector_idempotence_residual > tolerance:
            errors.append(
                "Projector is not idempotent within tolerance: "
                f"{projector_idempotence_residual:.3e}."
            )

        numerical_rank = int(
            np.count_nonzero(
                np.linalg.eigvalsh(0.5 * (P + P.conj().T))
                > 0.5
            )
        )

        if numerical_rank != kernel_dimension:
            errors.append(
                "Projector rank does not equal dim ker(K): "
                f"{numerical_rank} != {kernel_dimension}."
            )

        kernel_fixed_residual = float(
            np.linalg.norm(Gamma @ P - P, ord=2)
        )
        projector_commutator_residual = float(
            np.linalg.norm(Gamma @ P - P @ Gamma, ord=2)
        )

        if kernel_fixed_residual > tolerance:
            errors.append(
                "Gamma does not fix the supplied kernel projector: "
                f"{kernel_fixed_residual:.3e}."
            )

        if projector_commutator_residual > tolerance:
            errors.append(
                "Gamma does not commute with the supplied projector: "
                f"{projector_commutator_residual:.3e}."
            )

        if iterations_used > 0 and complement_spectral_radius < 1.0:
            Gamma_n = np.linalg.matrix_power(Gamma, iterations_used)
            asymptotic_projector_residual = float(
                np.linalg.norm(Gamma_n - P, ord=2)
            )

            # Allow a small numerical margin above the requested tolerance.
            convergence_limit = max(
                10.0 * tolerance,
                complement_spectral_radius**iterations_used
                + 10.0 * np.finfo(float).eps,
            )

            if asymptotic_projector_residual > convergence_limit:
                errors.append(
                    "Gamma^n does not approximate P47 within the certified "
                    "convergence bound: "
                    f"{asymptotic_projector_residual:.3e} > "
                    f"{convergence_limit:.3e}."
                )

    if dimension == CARRIER_DIMENSION:
        if kernel_dimension != E47_DIMENSION:
            errors.append(
                "Canonical carrier has incorrect kernel dimension: "
                f"{kernel_dimension} != {E47_DIMENSION}."
            )

        if not np.isclose(
            k2_max,
            CANONICAL_K2_NORM,
            rtol=0.0,
            atol=zero_tolerance,
        ):
            errors.append(
                "Canonical maximum K^2 eigenvalue is incorrect: "
                f"{k2_max:.12g} != {CANONICAL_K2_NORM}."
            )

        if not np.isclose(
            spectral_gap,
            CANONICAL_SPECTRAL_GAP,
            rtol=0.0,
            atol=zero_tolerance,
        ):
            errors.append(
                "Canonical K^2 spectral gap is incorrect: "
                f"{spectral_gap:.12g} != {CANONICAL_SPECTRAL_GAP}."
            )

    return ContractionValidation(
        valid=not errors,
        epsilon=float(epsilon),
        epsilon_max=float(epsilon_max),
        monotone_epsilon_max=float(monotone_epsilon_max),
        carrier_dimension=dimension,
        kernel_dimension=kernel_dimension,
        complement_dimension=complement_dimension,
        k2_min_eigenvalue=k2_min,
        k2_max_eigenvalue=k2_max,
        spectral_gap=spectral_gap,
        gamma_min_eigenvalue=gamma_min,
        gamma_max_eigenvalue=gamma_max,
        complement_spectral_radius=complement_spectral_radius,
        hermitian_residual=hermitian_residual,
        kernel_fixed_residual=kernel_fixed_residual,
        projector_commutator_residual=projector_commutator_residual,
        asymptotic_projector_residual=asymptotic_projector_residual,
        iterations=iterations_used,
        tolerance=float(tolerance),
        errors=tuple(errors),
    )


def require_valid_contraction(
    kernel: ArrayLike,
    projector: ArrayLike | None = None,
    *,
    epsilon: float = DEFAULT_EPSILON,
    iterations: int | None = None,
    tolerance: float = 1e-10,
    zero_tolerance: float = 1e-8,
) -> ContractionValidation:
    """Validate the contraction and raise one aggregated error on failure."""

    validation = validate_contraction(
        kernel,
        projector,
        epsilon=epsilon,
        iterations=iterations,
        tolerance=tolerance,
        zero_tolerance=zero_tolerance,
    )

    if not validation.valid:
        details = "\n".join(
            f"  {index}. {message}"
            for index, message in enumerate(
                validation.errors,
                start=1,
            )
        )
        raise ValueError(
            "E47 contraction validation failed:\n"
            f"{details}"
        )

    return validation


__all__ = [
    "CANONICAL_K2_EIGENVALUES",
    "CANONICAL_K2_NORM",
    "CANONICAL_SPECTRAL_GAP",
    "CARRIER_DIMENSION",
    "COMPLEMENT_DIMENSION",
    "ContractionValidation",
    "DEFAULT_EPSILON",
    "E47_DIMENSION",
    "MONOTONE_EPSILON_MAX",
    "SHARP_EPSILON_MAX",
    "apply_contraction",
    "build_contraction",
    "contraction_power",
    "iterate_contraction",
    "required_iterations",
    "require_valid_contraction",
    "validate_contraction",
]


if __name__ == "__main__":
    from e47.su2_kernel import (
        build_e47_operators,
        require_valid_e47_kernel,
        validate_e47_kernel,
    )
    from e47.projector import construct_e47_projector

    operators = build_e47_operators()
    kernel_validation = validate_e47_kernel(operators)
    require_valid_e47_kernel(kernel_validation)

    projector_data = construct_e47_projector(operators)

    certificate = require_valid_contraction(
        operators.kernel,
        projector_data.projector,
    )

    print(certificate)
