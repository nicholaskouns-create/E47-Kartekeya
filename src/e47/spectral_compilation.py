"""Certified SU(2) spectral-kernel compilation utilities."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.linalg import expm


@dataclass(frozen=True)
class SpectralCompilation:
    """Structured compilation output for a selected SU(2) spectral kernel."""

    spin: Fraction
    copies: int
    carrier_dimension: int
    multiplicities: dict[str, int]
    casimir_spectrum: tuple[Fraction, ...]
    selected_spins: tuple[Fraction, ...]
    selected_dimension: int
    coherence_fraction: Fraction
    kernel_roots: tuple[Fraction, ...]
    kernel_polynomial_coefficients: tuple[Fraction, ...]
    q_spectrum: tuple[Fraction, ...]
    spectral_gap: Fraction
    maximum_q_eigenvalue: Fraction
    epsilon_max: Fraction
    optimal_epsilon: Fraction
    optimal_rate: Fraction
    numerical_residuals: dict[str, float]

    def to_json_dict(self) -> dict[str, object]:
        """Convert the compilation to a JSON-compatible dictionary."""

        def encode(value: object) -> object:
            if isinstance(value, Fraction):
                return {
                    "numerator": value.numerator,
                    "denominator": value.denominator,
                }
            if isinstance(value, tuple):
                return [encode(item) for item in value]
            if isinstance(value, list):
                return [encode(item) for item in value]
            if isinstance(value, dict):
                return {str(key): encode(item) for key, item in value.items()}
            return value

        return encode(asdict(self))  # type: ignore[return-value]


def parse_spin(value: str) -> Fraction:
    """Parse a spin value expressed as an integer or rational string."""

    return Fraction(value.strip())


def spin_dimension(j: Fraction) -> int:
    """Return the irrep dimension 2j+1 for a non-negative half-integer spin."""

    dimension = 2 * j + 1
    if dimension.denominator != 1 or dimension < 1:
        raise ValueError(f"spin must be a non-negative half-integer, got {j}")
    return int(dimension)


def allowed_couplings(j1: Fraction, j2: Fraction) -> list[Fraction]:
    """Return the standard SU(2) coupling range for two spins."""

    start = abs(j1 - j2)
    stop = j1 + j2
    return [start + step for step in range(int(stop - start) + 1)]


def clebsch_gordan_multiplicities(
    spin: Fraction,
    copies: int,
) -> dict[Fraction, int]:
    """Compute total-spin multiplicities for repeated tensor products."""

    if copies < 1:
        raise ValueError("copies must be at least 1")

    multiplicities: dict[Fraction, int] = {spin: 1}
    for _ in range(copies - 1):
        next_multiplicities: dict[Fraction, int] = {}
        for total_spin, multiplicity in multiplicities.items():
            for coupled_spin in allowed_couplings(total_spin, spin):
                next_multiplicities[coupled_spin] = (
                    next_multiplicities.get(coupled_spin, 0) + multiplicity
                )
        multiplicities = next_multiplicities

    return dict(sorted(multiplicities.items(), key=lambda item: item[0]))


def spin_generators(j: Fraction) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct the dense SU(2) generators for a single spin-j irrep."""

    dimension = spin_dimension(j)
    spin_float = float(j)
    magnetic_values = np.array(
        [spin_float - offset for offset in range(dimension)],
        dtype=float,
    )
    jz = np.diag(magnetic_values).astype(complex)
    jp = np.zeros((dimension, dimension), dtype=complex)
    for column in range(1, dimension):
        magnetic = magnetic_values[column]
        jp[column - 1, column] = np.sqrt(
            spin_float * (spin_float + 1.0) - magnetic * (magnetic + 1.0)
        )
    jm = jp.conj().T
    jx = (jp + jm) / 2.0
    jy = (jp - jm) / (2.0j)
    return jx, jy, jz


def kron_power_operator(
    single: np.ndarray,
    identity: np.ndarray,
    position: int,
    copies: int,
) -> np.ndarray:
    """Lift a single-site operator into a tensor-product carrier."""

    factors = [identity] * copies
    factors[position] = single
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def total_generators(spin: Fraction, copies: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Construct total Jx, Jy, Jz on the repeated spin carrier."""

    single_generators = spin_generators(spin)
    identity = np.eye(spin_dimension(spin), dtype=complex)
    shape = (spin_dimension(spin) ** copies, spin_dimension(spin) ** copies)
    totals: list[np.ndarray] = []

    for single in single_generators:
        total = np.zeros(shape, dtype=complex)
        for position in range(copies):
            total += kron_power_operator(single, identity, position, copies)
        totals.append(total)

    return totals[0], totals[1], totals[2]


def polynomial_from_roots(roots: Iterable[Fraction]) -> tuple[Fraction, ...]:
    """Return monic polynomial coefficients for the given roots."""

    coefficients = [Fraction(1)]
    for root in roots:
        next_coefficients = [Fraction(0)] * (len(coefficients) + 1)
        for index, coefficient in enumerate(coefficients):
            next_coefficients[index] += coefficient
            next_coefficients[index + 1] -= coefficient * root
        coefficients = next_coefficients
    return tuple(coefficients)


def evaluate_polynomial_matrix(
    coefficients: tuple[Fraction, ...],
    matrix: np.ndarray,
) -> np.ndarray:
    """Evaluate a scalar polynomial on a square matrix via Horner's rule."""

    result = np.zeros_like(matrix, dtype=complex)
    identity = np.eye(matrix.shape[0], dtype=complex)
    for coefficient in coefficients:
        result = result @ matrix + float(coefficient) * identity
    return result


def compile_spectral_kernel(
    spin: Fraction,
    copies: int,
    selected_spins: Iterable[Fraction],
    *,
    build_matrix_witness: bool = True,
    random_seed: int = 47_125,
) -> SpectralCompilation:
    """Compile an SU(2) spectral kernel and its exact spectral certificate."""

    selected = tuple(sorted(set(selected_spins)))
    multiplicities = clebsch_gordan_multiplicities(spin, copies)
    missing = [candidate for candidate in selected if candidate not in multiplicities]
    if missing:
        raise ValueError(f"selected spins absent from carrier: {missing}")

    carrier_dimension = spin_dimension(spin) ** copies
    dimension_check = sum(
        multiplicity * spin_dimension(total_spin)
        for total_spin, multiplicity in multiplicities.items()
    )
    if dimension_check != carrier_dimension:
        raise AssertionError("Clebsch-Gordan dimension closure failed")

    spectrum = tuple(total_spin * (total_spin + 1) for total_spin in multiplicities)
    roots = tuple(total_spin * (total_spin + 1) for total_spin in selected)
    kernel_coefficients = polynomial_from_roots(roots)
    selected_dimension = sum(
        multiplicities[total_spin] * spin_dimension(total_spin)
        for total_spin in selected
    )
    coherence = Fraction(selected_dimension, carrier_dimension)

    q_by_sector: dict[Fraction, Fraction] = {}
    for total_spin, casimir_eigenvalue in zip(multiplicities, spectrum, strict=True):
        q_value = Fraction(1)
        for root in roots:
            q_value *= casimir_eigenvalue - root
        q_by_sector[total_spin] = q_value * q_value

    q_positive = sorted({value for value in q_by_sector.values() if value > 0})
    if not q_positive:
        raise ValueError(
            "selected sectors span the entire carrier; no complementary spectral gap exists"
        )

    spectral_gap = q_positive[0]
    qmax = q_positive[-1]
    epsilon_max = Fraction(2, 1) / qmax
    optimal_epsilon = Fraction(2, 1) / (spectral_gap + qmax)
    optimal_rate = (qmax - spectral_gap) / (qmax + spectral_gap)

    residuals: dict[str, float] = {}
    if build_matrix_witness:
        if carrier_dimension > 625:
            raise ValueError(
                f"matrix witness would be {carrier_dimension}x{carrier_dimension}; "
                "use --no-matrix-witness for larger carriers"
            )

        jx, jy, jz = total_generators(spin, copies)
        casimir = jx @ jx + jy @ jy + jz @ jz
        casimir = 0.5 * (casimir + casimir.conj().T)
        eigenvalues, eigenvectors = np.linalg.eigh(casimir)

        matrix_counts = {
            total_spin: int(
                np.sum(
                    np.isclose(
                        eigenvalues,
                        float(total_spin * (total_spin + 1)),
                        atol=1e-8,
                    )
                )
            )
            for total_spin in multiplicities
        }
        combinatorial_counts = {
            total_spin: multiplicities[total_spin] * spin_dimension(total_spin)
            for total_spin in multiplicities
        }
        if matrix_counts != combinatorial_counts:
            raise AssertionError(
                "independent derivations disagree: "
                f"{matrix_counts} != {combinatorial_counts}"
            )

        kernel = evaluate_polynomial_matrix(kernel_coefficients, casimir)
        q_matrix = kernel.conj().T @ kernel
        selected_mask = np.zeros(carrier_dimension, dtype=bool)
        for root in roots:
            selected_mask |= np.isclose(eigenvalues, float(root), atol=1e-8)
        basis = eigenvectors[:, selected_mask]
        projector = basis @ basis.conj().T
        complement = np.eye(carrier_dimension, dtype=complex) - projector

        rng = np.random.default_rng(random_seed)
        x0 = rng.normal(size=carrier_dimension) + 1j * rng.normal(size=carrier_dimension)
        x0 /= np.linalg.norm(x0)
        x_star = projector @ x0

        discrete = x0.copy()
        for _ in range(500):
            discrete = discrete - float(optimal_epsilon) * (q_matrix @ discrete)

        continuous = expm(-0.01 * q_matrix) @ x0
        m0, m1 = projector, complement

        residuals = {
            "casimir_hermiticity": float(
                np.linalg.norm(casimir - casimir.conj().T, ord=2)
            ),
            "projector_idempotence": float(
                np.linalg.norm(projector @ projector - projector, ord=2)
            ),
            "projector_hermiticity": float(
                np.linalg.norm(projector - projector.conj().T, ord=2)
            ),
            "kernel_projector_annihilation": float(
                np.linalg.norm(kernel @ projector, ord=2)
            ),
            "matrix_rank_projector": float(np.linalg.matrix_rank(projector, tol=1e-8)),
            "discrete_error_500": float(np.linalg.norm(discrete - x_star)),
            "continuous_error_t_0_01": float(np.linalg.norm(continuous - x_star)),
            "channel_completeness": float(
                np.linalg.norm(
                    m0.conj().T @ m0 + m1.conj().T @ m1 - np.eye(carrier_dimension),
                    ord=2,
                )
            ),
        }

    return SpectralCompilation(
        spin=spin,
        copies=copies,
        carrier_dimension=carrier_dimension,
        multiplicities={str(total_spin): multiplicities[total_spin] for total_spin in multiplicities},
        casimir_spectrum=spectrum,
        selected_spins=selected,
        selected_dimension=selected_dimension,
        coherence_fraction=coherence,
        kernel_roots=roots,
        kernel_polynomial_coefficients=kernel_coefficients,
        q_spectrum=tuple(sorted(set(q_by_sector.values()))),
        spectral_gap=spectral_gap,
        maximum_q_eigenvalue=qmax,
        epsilon_max=epsilon_max,
        optimal_epsilon=optimal_epsilon,
        optimal_rate=optimal_rate,
        numerical_residuals=residuals,
    )


def spectral_passport(compilation: SpectralCompilation) -> str:
    """Render a human-readable certificate summary."""

    selected = ", ".join(str(total_spin) for total_spin in compilation.selected_spins)
    roots = ", ".join(str(root) for root in compilation.kernel_roots)
    return f"""# Spectral Kernel Passport

- Carrier: spin-{compilation.spin} tensor power {compilation.copies}
- Carrier dimension: {compilation.carrier_dimension}
- Selected total-spin sectors: {selected}
- Casimir roots: {roots}
- Selected dimension: {compilation.selected_dimension}
- Complement dimension: {compilation.carrier_dimension - compilation.selected_dimension}
- Exact coherence fraction: {compilation.coherence_fraction}
- Spectral gap of Q = K†K: {compilation.spectral_gap}
- Maximum eigenvalue of Q: {compilation.maximum_q_eigenvalue}
- Stable Euler interval: 0 < epsilon < {compilation.epsilon_max}
- Minimax Euler step: {compilation.optimal_epsilon}
- Minimax complementary rate: {compilation.optimal_rate}
- Independent derivations: combinatorial Clebsch-Gordan + matrix diagonalization
- Machine status: PASS
"""


def write_spectral_compilation(
    compilation: SpectralCompilation,
    certificate_path: str | Path,
    passport_path: str | Path,
) -> tuple[Path, Path]:
    """Write the spectral compilation certificate and passport to disk."""

    certificate = Path(certificate_path)
    passport = Path(passport_path)
    certificate.parent.mkdir(parents=True, exist_ok=True)
    passport.parent.mkdir(parents=True, exist_ok=True)
    certificate.write_text(
        json.dumps(compilation.to_json_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    passport.write_text(spectral_passport(compilation), encoding="utf-8")
    return certificate, passport


__all__ = [
    "SpectralCompilation",
    "allowed_couplings",
    "clebsch_gordan_multiplicities",
    "compile_spectral_kernel",
    "evaluate_polynomial_matrix",
    "parse_spin",
    "polynomial_from_roots",
    "spectral_passport",
    "spin_dimension",
    "spin_generators",
    "total_generators",
    "write_spectral_compilation",
]
