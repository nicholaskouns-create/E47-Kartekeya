#!/usr/bin/env python3
"""
Validate the SU(3) adjoint triple-singlet sector on 8 ⊗ 8 ⊗ 8.

This script constructs the adjoint representation from the SU(3)
structure constants, builds the total quadratic Casimir on the
512-dimensional carrier, extracts the two-dimensional singlet sector,
and verifies that the normalized f_abc and d_abc tensors span it.

It also validates the singlet projector, leakage functional, and
discrete contraction toward the singlet sector.

Scope:
    Finite-dimensional SU(3) representation theory and numerical
    projector validation only.

Boundary:
    The standard Yang-Mills three-gluon color factor is f_abc.
    The symmetric d_abc tensor is an independent SU(3)-invariant tensor,
    not a second ordinary three-gluon vertex.

Python:
    3.10+

Dependencies:
    numpy
    scipy
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.linalg import eigh

ComplexArray = NDArray[np.complex128]
RealArray = NDArray[np.float64]

EXPECTED_SINGLET_DIMENSION = 2
EXPECTED_BOUNDARY = (
    "The standard Yang-Mills three-gluon color factor is f_abc. "
    "The symmetric d_abc tensor is an independent SU(3)-invariant tensor, "
    "not a second ordinary three-gluon vertex."
)


@dataclass(frozen=True)
class ValidationConfig:
    tolerance: float = 1e-10
    kernel_tolerance: float = 1e-8
    epsilon: float = 1.0 / 225.0
    contraction_iterations: int = 400
    random_seed: int = 47


@dataclass(frozen=True)
class ValidationResults:
    valid: bool
    carrier_dimension: int
    singlet_dimension: int
    expected_singlet_dimension: int

    casimir_hermitian_error: float
    projector_hermitian_error: float
    projector_idempotence_error: float
    projector_rank: int
    projector_trace: float
    casimir_projector_annihilation_error: float

    f_norm_squared: float
    d_norm_squared: float
    f_d_overlap: float
    f_total_generator_error: float
    d_total_generator_error: float
    invariant_span_projector_error: float

    positive_casimir_gap: float
    max_casimir_eigenvalue: float
    positive_k2_gap: float
    max_k2_eigenvalue: float

    epsilon: float
    contraction_iterations: int
    contraction_error: float
    theoretical_contraction_factor: float
    theoretical_contraction_bound: float

    leakage_f: float
    leakage_d: float
    leakage_equal_mixture: float
    leakage_random_state: float
    expected_random_leakage: float

    spectrum: dict[str, int]
    corrections: list[str]
    boundary: str


def gell_mann_matrices() -> list[ComplexArray]:
    """Return the standard eight Gell-Mann matrices."""
    zero = 0.0
    one = 1.0
    i = 1j
    sqrt3 = np.sqrt(3.0)

    return [
        np.array(
            [[zero, one, zero], [one, zero, zero], [zero, zero, zero]],
            dtype=np.complex128,
        ),
        np.array(
            [[zero, -i, zero], [i, zero, zero], [zero, zero, zero]],
            dtype=np.complex128,
        ),
        np.array(
            [[one, zero, zero], [zero, -one, zero], [zero, zero, zero]],
            dtype=np.complex128,
        ),
        np.array(
            [[zero, zero, one], [zero, zero, zero], [one, zero, zero]],
            dtype=np.complex128,
        ),
        np.array(
            [[zero, zero, -i], [zero, zero, zero], [i, zero, zero]],
            dtype=np.complex128,
        ),
        np.array(
            [[zero, zero, zero], [zero, zero, one], [zero, one, zero]],
            dtype=np.complex128,
        ),
        np.array(
            [[zero, zero, zero], [zero, zero, -i], [zero, i, zero]],
            dtype=np.complex128,
        ),
        np.array(
            [
                [one / sqrt3, zero, zero],
                [zero, one / sqrt3, zero],
                [zero, zero, -2.0 / sqrt3],
            ],
            dtype=np.complex128,
        ),
    ]


def structure_constants(
    lambdas: list[ComplexArray],
) -> tuple[RealArray, RealArray]:
    """
    Compute the antisymmetric f_abc and symmetric d_abc tensors.

    Conventions:
        [λ_a, λ_b] = 2 i f_abc λ_c
        {λ_a, λ_b} = 4/3 δ_ab I + 2 d_abc λ_c
    """
    f = np.zeros((8, 8, 8), dtype=np.float64)
    d = np.zeros((8, 8, 8), dtype=np.float64)
    identity = np.eye(3, dtype=np.complex128)

    for a in range(8):
        for b in range(8):
            commutator = lambdas[a] @ lambdas[b] - lambdas[b] @ lambdas[a]
            anticommutator = lambdas[a] @ lambdas[b] + lambdas[b] @ lambdas[a]
            trace_ab = np.trace(lambdas[a] @ lambdas[b]).real
            anticommutator_traceless = anticommutator - (trace_ab / 3.0) * identity

            for c in range(8):
                f_value = np.trace(commutator @ lambdas[c]) / (4.0j)
                d_value = np.trace(anticommutator_traceless @ lambdas[c]) / 4.0

                f[a, b, c] = float(np.real_if_close(f_value))
                d[a, b, c] = float(np.real_if_close(d_value))

    return f, d


def adjoint_generators(f: RealArray) -> list[ComplexArray]:
    """
    Construct the adjoint generators.

    (T_a)_{bc} = -i f_abc
    """
    return [(-1j * f[a]).astype(np.complex128, copy=False) for a in range(8)]


def total_generators(
    single_generators: list[ComplexArray],
) -> list[ComplexArray]:
    """Construct generators on 8 ⊗ 8 ⊗ 8."""
    identity = np.eye(8, dtype=np.complex128)

    return [
        np.kron(np.kron(generator, identity), identity)
        + np.kron(np.kron(identity, generator), identity)
        + np.kron(np.kron(identity, identity), generator)
        for generator in single_generators
    ]


def quadratic_casimir(
    generators: list[ComplexArray],
) -> ComplexArray:
    """Compute C2 = Σ_a T_a²."""
    dimension = generators[0].shape[0]
    casimir = np.zeros((dimension, dimension), dtype=np.complex128)

    for generator in generators:
        casimir += generator @ generator

    return 0.5 * (casimir + casimir.conj().T)


def normalized_invariant_tensor(tensor: RealArray) -> ComplexArray:
    """Flatten and normalize an invariant rank-three tensor."""
    vector = tensor.astype(np.complex128).reshape(-1)
    norm = np.linalg.norm(vector)

    if norm == 0.0:
        raise ValueError("Invariant tensor has zero norm.")

    return vector / norm


def spectral_projector_from_kernel(
    operator: ComplexArray,
    tolerance: float,
) -> tuple[ComplexArray, ComplexArray, RealArray]:
    """
    Construct the orthogonal projector onto ker(operator).

    Returns:
        projector
        kernel basis matrix
        eigenvalues
    """
    eigenvalues, eigenvectors = eigh(operator)
    mask = np.abs(eigenvalues) <= tolerance

    kernel_basis = eigenvectors[:, mask]
    projector = kernel_basis @ kernel_basis.conj().T

    return projector, kernel_basis, eigenvalues.astype(np.float64, copy=False)


def group_spectrum(
    eigenvalues: RealArray,
    decimals: int = 8,
) -> dict[str, int]:
    """Group numerical eigenvalues into an exact-looking spectrum map."""
    rounded = np.round(eigenvalues, decimals=decimals)
    values, counts = np.unique(rounded, return_counts=True)

    spectrum: dict[str, int] = {}
    for value, count in zip(values, counts, strict=True):
        if abs(value - round(value)) < 10 ** (-decimals + 2):
            label = str(int(round(value)))
        else:
            label = f"{value:.{decimals}g}"

        spectrum[label] = int(count)

    return spectrum


def matrix_rank_hermitian(
    matrix: ComplexArray,
    tolerance: float,
) -> int:
    """Compute numerical rank for a Hermitian matrix."""
    eigenvalues = np.linalg.eigvalsh(matrix)
    return int(np.count_nonzero(np.abs(eigenvalues) > tolerance))


def density_matrix(vector: ComplexArray) -> ComplexArray:
    """Return |ψ><ψ| for a normalized state vector."""
    return np.outer(vector, vector.conj())


def operator_norm(matrix: ComplexArray) -> float:
    """Return the spectral norm of a matrix."""
    return float(np.linalg.norm(matrix, ord=2))


def leakage(projector: ComplexArray, rho: ComplexArray) -> float:
    """Return 1 - Tr(P rho), clipped to [0, 1] up to roundoff."""
    value = 1.0 - float(np.real_if_close(np.trace(projector @ rho)))
    return float(np.clip(value, 0.0, 1.0))


def random_unit_vector(
    dimension: int,
    *,
    seed: int,
) -> ComplexArray:
    """Sample a normalized complex Gaussian state."""
    rng = np.random.default_rng(seed)
    vector = rng.normal(size=dimension) + 1j * rng.normal(size=dimension)
    vector = vector.astype(np.complex128, copy=False)
    return vector / np.linalg.norm(vector)


def invariant_span_projector(vectors: list[ComplexArray]) -> ComplexArray:
    """Construct the orthogonal projector onto the span of the input vectors."""
    matrix = np.column_stack(vectors)
    orthonormal_basis, _ = np.linalg.qr(matrix, mode="reduced")
    return orthonormal_basis @ orthonormal_basis.conj().T


def validate_su3_adjoint_singlets(
    config: ValidationConfig | None = None,
) -> ValidationResults:
    """Run the full SU(3) adjoint triple-singlet validation."""
    if config is None:
        config = ValidationConfig()

    lambdas = gell_mann_matrices()
    f_tensor, d_tensor = structure_constants(lambdas)
    generators = adjoint_generators(f_tensor)
    total = total_generators(generators)
    casimir = quadratic_casimir(total)
    projector, kernel_basis, eigenvalues = spectral_projector_from_kernel(
        casimir,
        config.kernel_tolerance,
    )

    carrier_dimension = casimir.shape[0]
    singlet_dimension = kernel_basis.shape[1]

    f_vector = normalized_invariant_tensor(f_tensor)
    d_vector = normalized_invariant_tensor(d_tensor)
    span_projector = invariant_span_projector([f_vector, d_vector])

    k2 = casimir @ casimir
    k2 = 0.5 * (k2 + k2.conj().T)
    k2_eigenvalues = np.linalg.eigvalsh(k2)

    positive_casimir = eigenvalues[eigenvalues > config.kernel_tolerance]
    positive_k2 = k2_eigenvalues[k2_eigenvalues > config.kernel_tolerance]

    gamma = np.eye(carrier_dimension, dtype=np.complex128) - config.epsilon * k2
    gamma_power = np.linalg.matrix_power(gamma, config.contraction_iterations)

    f_density = density_matrix(f_vector)
    d_density = density_matrix(d_vector)
    equal_mixture = 0.5 * (f_density + d_density)
    random_state = random_unit_vector(carrier_dimension, seed=config.random_seed)
    random_density = density_matrix(random_state)

    contraction_factors = np.abs(1.0 - config.epsilon * positive_k2)
    theoretical_factor = float(np.max(contraction_factors))

    corrections = [
        "The singlet sector of 8 ⊗ 8 ⊗ 8 is two-dimensional.",
        "The normalized f_abc and d_abc tensors span the full singlet sector.",
        "Only f_abc is the ordinary Yang-Mills three-gluon color factor.",
    ]

    results = ValidationResults(
        valid=False,
        carrier_dimension=carrier_dimension,
        singlet_dimension=singlet_dimension,
        expected_singlet_dimension=EXPECTED_SINGLET_DIMENSION,
        casimir_hermitian_error=operator_norm(casimir - casimir.conj().T),
        projector_hermitian_error=operator_norm(projector - projector.conj().T),
        projector_idempotence_error=operator_norm(projector @ projector - projector),
        projector_rank=matrix_rank_hermitian(projector, config.kernel_tolerance),
        projector_trace=float(np.trace(projector).real),
        casimir_projector_annihilation_error=operator_norm(casimir @ projector),
        f_norm_squared=float(np.vdot(f_tensor.reshape(-1), f_tensor.reshape(-1)).real),
        d_norm_squared=float(np.vdot(d_tensor.reshape(-1), d_tensor.reshape(-1)).real),
        f_d_overlap=float(np.vdot(f_vector, d_vector).real),
        f_total_generator_error=max(operator_norm(generator @ f_vector) for generator in total),
        d_total_generator_error=max(operator_norm(generator @ d_vector) for generator in total),
        invariant_span_projector_error=operator_norm(projector - span_projector),
        positive_casimir_gap=float(np.min(positive_casimir)),
        max_casimir_eigenvalue=float(np.max(eigenvalues)),
        positive_k2_gap=float(np.min(positive_k2)),
        max_k2_eigenvalue=float(np.max(k2_eigenvalues)),
        epsilon=config.epsilon,
        contraction_iterations=config.contraction_iterations,
        contraction_error=operator_norm(gamma_power - projector),
        theoretical_contraction_factor=theoretical_factor,
        theoretical_contraction_bound=float(theoretical_factor**config.contraction_iterations),
        leakage_f=leakage(projector, f_density),
        leakage_d=leakage(projector, d_density),
        leakage_equal_mixture=leakage(projector, equal_mixture),
        leakage_random_state=leakage(projector, random_density),
        expected_random_leakage=1.0 - singlet_dimension / carrier_dimension,
        spectrum=group_spectrum(eigenvalues),
        corrections=corrections,
        boundary=EXPECTED_BOUNDARY,
    )

    valid = all(
        (
            results.singlet_dimension == results.expected_singlet_dimension,
            results.projector_rank == results.expected_singlet_dimension,
            results.casimir_hermitian_error <= config.tolerance,
            results.projector_hermitian_error <= config.tolerance,
            results.projector_idempotence_error <= config.tolerance,
            abs(results.projector_trace - results.expected_singlet_dimension)
            <= config.tolerance,
            results.casimir_projector_annihilation_error <= config.tolerance,
            abs(results.f_d_overlap) <= config.tolerance,
            results.f_total_generator_error <= config.tolerance,
            results.d_total_generator_error <= config.tolerance,
            results.invariant_span_projector_error <= config.kernel_tolerance,
            results.positive_casimir_gap > 0.0,
            results.positive_k2_gap > 0.0,
            results.theoretical_contraction_factor < 1.0,
            results.contraction_error <= results.theoretical_contraction_bound + 1e-12,
            results.leakage_f <= config.tolerance,
            results.leakage_d <= config.tolerance,
            results.leakage_equal_mixture <= config.tolerance,
        )
    )

    return ValidationResults(**{**asdict(results), "valid": valid})


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="Write the validation JSON payload to this path.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level for stdout and optional output.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the validator and emit JSON results."""
    args = parse_args()
    results = validate_su3_adjoint_singlets()
    payload = asdict(results)
    text = json.dumps(payload, indent=args.indent)
    print(text)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")

    return 0 if results.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
