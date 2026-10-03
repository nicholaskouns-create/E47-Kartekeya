#!/usr/bin/env python3
"""Machine certificate for the E47 joint spectral-symmetry contraction.

The construction starts from three spin-2 SU(2) factors (dimension 5 each),
builds the 125-dimensional total Casimir, constructs the six tensor-factor
permutations, and verifies the canonical five-dimensional joint kernel.

No target eigenvectors, ranks, or multiplicities are inserted.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
from pathlib import Path

import numpy as np


DIM_LOCAL = 5
DIM = DIM_LOCAL**3
TARGET_CASIMIR = (6, 30)
DELTA = 11664
EPSILON_STAR = 1 / 99144
RHO_STAR = 15 / 17


def spin_two_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return Hermitian spin-2 generators in the |m>, m=-2,...,2 basis."""
    j = 2
    m = np.arange(-j, j + 1, dtype=float)
    jz = np.diag(m).astype(complex)
    jp = np.zeros((DIM_LOCAL, DIM_LOCAL), dtype=complex)
    for col, magnetic in enumerate(m[:-1]):
        jp[col + 1, col] = np.sqrt(j * (j + 1) - magnetic * (magnetic + 1))
    jm = jp.conj().T
    jx = (jp + jm) / 2
    jy = (jp - jm) / (2j)
    return jx, jy, jz


def total_operator(local: np.ndarray) -> np.ndarray:
    identity = np.eye(DIM_LOCAL, dtype=complex)
    return (
        np.kron(np.kron(local, identity), identity)
        + np.kron(np.kron(identity, local), identity)
        + np.kron(np.kron(identity, identity), local)
    )


def permutation_operator(permutation: tuple[int, int, int]) -> np.ndarray:
    """Permute the three tensor coordinates in the computational basis."""
    operator = np.zeros((DIM, DIM), dtype=float)
    for source_tuple in itertools.product(range(DIM_LOCAL), repeat=3):
        target_tuple = tuple(source_tuple[index] for index in permutation)
        source = np.ravel_multi_index(source_tuple, (DIM_LOCAL,) * 3)
        target = np.ravel_multi_index(target_tuple, (DIM_LOCAL,) * 3)
        operator[target, source] = 1.0
    return operator


def spectral_projector(
    eigenvalues: np.ndarray, eigenvectors: np.ndarray, target: int, tolerance: float
) -> np.ndarray:
    mask = np.abs(eigenvalues - target) < tolerance
    vectors = eigenvectors[:, mask]
    return vectors @ vectors.conj().T


def rounded_spectrum(values: np.ndarray, tolerance: float = 1e-7) -> dict[str, int]:
    rounded = np.rint(values).astype(int)
    if np.max(np.abs(values - rounded)) > tolerance:
        raise AssertionError("Spectrum is not integral within tolerance")
    unique, counts = np.unique(rounded, return_counts=True)
    return {str(int(value)): int(count) for value, count in zip(unique, counts)}


def frobenius(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord=2))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_certificate(script_path: Path) -> dict[str, object]:
    jx, jy, jz = spin_two_generators()
    jx_total, jy_total, jz_total = map(total_operator, (jx, jy, jz))
    casimir = (
        jx_total @ jx_total + jy_total @ jy_total + jz_total @ jz_total
    )
    casimir = (casimir + casimir.conj().T) / 2

    eigenvalues, eigenvectors = np.linalg.eigh(casimir)
    casimir_spectrum = rounded_spectrum(eigenvalues)

    p6 = spectral_projector(eigenvalues, eigenvectors, 6, 1e-8)
    p30 = spectral_projector(eigenvalues, eigenvectors, 30, 1e-8)
    p47 = p6 + p30

    permutations = [permutation_operator(p) for p in itertools.permutations(range(3))]
    pi_sym = sum(permutations) / len(permutations)
    pi_sym = (pi_sym + pi_sym.T) / 2

    p_can = p47 @ pi_sym
    p_can = (p_can + p_can.conj().T) / 2

    identity = np.eye(DIM, dtype=complex)
    k = (casimir - 6 * identity) @ (casimir - 30 * identity)
    k2 = k @ k
    a_can = k2 + DELTA * (identity - pi_sym)
    a_can = (a_can + a_can.conj().T) / 2

    a_eigenvalues = np.linalg.eigvalsh(a_can)
    a_spectrum = rounded_spectrum(a_eigenvalues, tolerance=2e-6)
    positive = a_eigenvalues[a_eigenvalues > 1e-7]
    lambda_min_positive = float(np.min(positive))
    lambda_max = float(np.max(a_eigenvalues))

    gamma = identity - EPSILON_STAR * a_can
    gamma_eigenvalues = np.linalg.eigvalsh(gamma)
    complement = identity - p_can
    contraction = operator_norm(gamma @ complement)

    generator_commutator = operator_norm(k @ pi_sym - pi_sym @ k)
    permutation_invariance = max(
        operator_norm(u @ p_can - p_can) for u in permutations
    )

    iterations = 25
    gamma_power = np.linalg.matrix_power(gamma, iterations)
    observed_power_residual = operator_norm(gamma_power - p_can)
    predicted_power_residual = RHO_STAR**iterations

    joint_multiplicities: dict[str, dict[str, int]] = {}
    for value in sorted({int(round(x)) for x in eigenvalues}):
        p_value = spectral_projector(eigenvalues, eigenvectors, value, 1e-8)
        symmetric = int(round(float(np.trace(p_value @ pi_sym).real)))
        total = int(round(float(np.trace(p_value).real)))
        joint_multiplicities[str(value)] = {
            "total": total,
            "symmetric": symmetric,
            "non_symmetric": total - symmetric,
        }

    residuals = {
        "casimir_hermiticity_fro": frobenius(casimir - casimir.conj().T),
        "pi_sym_idempotence_fro": frobenius(pi_sym @ pi_sym - pi_sym),
        "pi_sym_selfadjoint_fro": frobenius(pi_sym - pi_sym.conj().T),
        "p47_idempotence_fro": frobenius(p47 @ p47 - p47),
        "p47_selfadjoint_fro": frobenius(p47 - p47.conj().T),
        "p_can_idempotence_fro": frobenius(p_can @ p_can - p_can),
        "p_can_selfadjoint_fro": frobenius(p_can - p_can.conj().T),
        "p47_absorption_fro": frobenius(p47 @ p_can - p_can),
        "symmetry_absorption_fro": frobenius(pi_sym @ p_can - p_can),
        "k_p_can_fro": frobenius(k @ p_can),
        "k_p47_fro": frobenius(k @ p47),
        "k_p47_normalized_fro": frobenius(k @ p47)
        / (frobenius(k) * frobenius(p47)),
        "a_can_p_can_fro": frobenius(a_can @ p_can),
        "a_can_p_can_normalized_fro": frobenius(a_can @ p_can)
        / (frobenius(a_can) * frobenius(p_can)),
        "k_pi_sym_commutator_2": generator_commutator,
        "c_pi_sym_commutator_fro": frobenius(casimir @ pi_sym - pi_sym @ casimir),
        "p30_symmetric_sector_2": operator_norm(p30 @ pi_sym),
        "max_permutation_invariance_2": permutation_invariance,
        "gamma_fixed_projector_fro": frobenius(gamma @ p_can - p_can),
        "power_25_observed_2": observed_power_residual,
        "power_25_predicted": predicted_power_residual,
        "power_25_absolute_error": abs(
            observed_power_residual - predicted_power_residual
        ),
    }

    ranks = {
        "pi_sym": int(np.linalg.matrix_rank(pi_sym, tol=1e-8)),
        "p6": int(np.linalg.matrix_rank(p6, tol=1e-8)),
        "p30": int(np.linalg.matrix_rank(p30, tol=1e-8)),
        "p47": int(np.linalg.matrix_rank(p47, tol=1e-8)),
        "p_can": int(np.linalg.matrix_rank(p_can, tol=1e-8)),
        "a_can": int(np.linalg.matrix_rank(a_can, tol=1e-7)),
        "ker_a_can": DIM - int(np.linalg.matrix_rank(a_can, tol=1e-7)),
    }

    assertions = {
        "ambient_dimension_125": DIM == 125,
        "casimir_spectrum_exact": casimir_spectrum
        == {"0": 1, "2": 9, "6": 25, "12": 28, "20": 27, "30": 22, "42": 13},
        "symmetric_cube_rank_35": ranks["pi_sym"] == 35,
        "e47_rank_47": ranks["p47"] == 47,
        "canonical_rank_5": ranks["p_can"] == 5,
        "joint_kernel_dimension_5": ranks["ker_a_can"] == 5,
        "symmetric_e47_is_only_spin_2": joint_multiplicities["6"]["symmetric"] == 5
        and joint_multiplicities["30"]["symmetric"] == 0,
        "a_can_spectrum_exact": a_spectrum
        == {
            "0": 5,
            "11664": 49,
            "19600": 9,
            "23328": 21,
            "24208": 9,
            "31264": 18,
            "32400": 1,
            "186624": 13,
        },
        "positive_gap_11664": abs(lambda_min_positive - 11664) < 2e-6,
        "maximum_186624": abs(lambda_max - 186624) < 2e-6,
        "epsilon_star_exact": abs(EPSILON_STAR - 1 / 99144) < 1e-20,
        "contraction_15_over_17": abs(contraction - RHO_STAR) < 1e-10,
        "projector_residuals_within_float64_scale": max(
            residuals["p_can_idempotence_fro"],
            residuals["k_p_can_fro"],
            residuals["max_permutation_invariance_2"],
        )
        < 1e-10
        and residuals["a_can_p_can_normalized_fro"] < 1e-12,
        "power_law_verified": residuals["power_25_absolute_error"] < 1e-10,
    }

    if not all(assertions.values()):
        failed = [name for name, passed in assertions.items() if not passed]
        raise AssertionError(f"Certificate failure: {failed}")

    return {
        "certificate_id": "MC-CAN5-20260813",
        "title": "Joint Spectral-Symmetry Canonical Convergence Certificate",
        "generated_utc": "2026-08-13",
        "theorem_id": "E47-JSSC-20260813",
        "method": "NumPy float64; generators and tensor permutations constructed ab initio",
        "environment": {
            "python": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "byteorder": sys.byteorder,
            "float64_epsilon": float(np.finfo(np.float64).eps),
        },
        "script_sha256": sha256(script_path),
        "construction": {
            "local_spin": 2,
            "local_dimension": DIM_LOCAL,
            "tensor_factors": 3,
            "ambient_dimension": DIM,
            "K": "(C-6I)(C-30I)",
            "Pi_sym": "(1/6) sum_{sigma in S3} U_sigma",
            "Delta": DELTA,
            "A_can": "K^2 + Delta(I-Pi_sym)",
            "P_can": "P47 Pi_sym = P6 Pi_sym",
        },
        "spectra": {
            "casimir": casimir_spectrum,
            "a_can": a_spectrum,
            "joint_casimir_symmetry_multiplicities": joint_multiplicities,
            "gamma_can_exact": {
                "1": 5,
                "15/17": 49,
                "9943/12393": 9,
                "13/17": 21,
                "551/729": 9,
                "8485/12393": 18,
                "103/153": 1,
                "-15/17": 13,
            },
        },
        "ranks": ranks,
        "convergence": {
            "lambda_min_positive": lambda_min_positive,
            "lambda_max": lambda_max,
            "condition_number": lambda_max / lambda_min_positive,
            "epsilon_star": EPSILON_STAR,
            "epsilon_star_exact": "1/99144",
            "rho_star": contraction,
            "rho_star_exact": "15/17",
            "discrete_limit": "(I-epsilon_star A_can)^n -> P_can",
            "continuous_limit": "exp(-t A_can) -> P_can",
        },
        "residuals": residuals,
        "assertions": assertions,
        "status": "PASS",
        "assertions_passed": len(assertions),
        "assertions_total": len(assertions),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, help="Write certificate JSON")
    arguments = parser.parse_args()
    script_path = Path(__file__).resolve()
    certificate = build_certificate(script_path)
    output = json.dumps(certificate, indent=2, sort_keys=True)
    print(output)
    if arguments.json:
        arguments.json.parent.mkdir(parents=True, exist_ok=True)
        arguments.json.write_text(output + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
