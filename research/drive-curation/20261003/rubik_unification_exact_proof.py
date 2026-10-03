#!/usr/bin/env python3
"""
RUBIK UNIFICATION MAPPING INVESTIGATION
Exact Python Proof for the 5×5×5 Professor's-Cube Carrier,
Layer Permutations, Spectral Retention, and Phonon Continuity

Nicholas Kouns
AIMS Research Institute
Validation edition: July 2026

Carrier:
    Sigma = {0,1,2,3,4}^3, |Sigma| = 125

Laplacian:
    L = L1 ⊗ I ⊗ I + I ⊗ L1 ⊗ I + I ⊗ I ⊗ L1,
where L1 is the 5-cycle graph Laplacian.

This program constructs all 15 quarter-turn layer operators:
    R,L,U,D,F,B,
    L2,M,R2,
    B2,S,F2,
    D2,E,U2.

It validates:
1. Every layer operator is a 125×125 orthogonal permutation of order 4.
2. Every operator preserves the Euclidean norm and the uniform kernel mode.
3. The twist-energy identity
       DeltaE = rho^T(P^T L P - L)rho
   is exact.
4. Every layer turn has the same Laplacian defect norms:
       ||P^TLP-L||_2 = 2 sqrt(2),
       ||P^TLP-L||_F = 8 sqrt(3).
5. The first nonzero eigenspace retention is exactly 59/75.
6. The next eigenspace retention is exactly 11/15.
7. For continuous flow rho_dot=-L rho,
       d/dt (rho^T L rho) = -2 ||L rho||^2 <= 0.
8. For discrete flow rho_{n+1}=(I-epsilon L)rho_n,
   energy is nonincreasing for 0<epsilon<=2/lambda_max(L).
9. The flow converges to the preserved mean:
       rho_n -> mean(rho_0) * 1.
   Therefore, if mean(rho_0)=47/125, the limit is
       (47/125) * 1.

Canonical correction:
    ker(L) has dimension 1, not 47. The number 47/125 is a
    mean-value lock only when imposed by the initial mean or by a
    separate E47 projector. It is not the dimension ratio of ker(L).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import math

import numpy as np


TITLE = (
    "RUBIK UNIFICATION MAPPING INVESTIGATION: "
    "EXACT 5×5×5 PROFESSOR'S-CUBE OPERATOR PROOF, "
    "SPECTRAL RETENTION, AND PHONON CONTINUITY"
)

N = 5
DIM = N**3
ALPHA = (5.0 - math.sqrt(5.0)) / 2.0
BETA = (5.0 + math.sqrt(5.0)) / 2.0
OMEGA_C = 47.0 / 125.0


@dataclass(frozen=True)
class OperatorCertificate:
    name: str
    orthogonality_residual: float
    order_four_residual: float
    kernel_invariance_residual: float
    low_subspace_retention: float
    next_subspace_retention: float
    laplacian_defect_spectral_norm: float
    laplacian_defect_frobenius_norm: float


def idx(x: int, y: int, z: int) -> int:
    return x * 25 + y * 5 + z


def cycle_laplacian_5() -> np.ndarray:
    L1 = np.zeros((N, N), dtype=float)
    for i in range(N):
        L1[i, i] = 2.0
        L1[i, (i - 1) % N] = -1.0
        L1[i, (i + 1) % N] = -1.0
    return L1


def kronecker_sum_laplacian() -> np.ndarray:
    L1 = cycle_laplacian_5()
    I = np.eye(N)
    return (
        np.kron(np.kron(L1, I), I)
        + np.kron(np.kron(I, L1), I)
        + np.kron(np.kron(I, I), L1)
    )


def layer_map(axis: str, k: int, orientation: int):
    """
    orientation=+1:
      x: (k,y,z)->(k,4-z,y)
      y: (x,k,z)->(z,k,4-x)
      z: (x,y,k)->(y,4-x,k)
    orientation=-1 gives the inverse quarter-turn.
    """
    if orientation not in (-1, 1):
        raise ValueError("orientation must be ±1")

    def mapping(x: int, y: int, z: int) -> tuple[int, int, int]:
        if axis == "x" and x == k:
            return (x, 4 - z, y) if orientation == 1 else (x, z, 4 - y)
        if axis == "y" and y == k:
            return (z, y, 4 - x) if orientation == 1 else (4 - z, y, x)
        if axis == "z" and z == k:
            return (y, 4 - x, z) if orientation == 1 else (4 - y, x, z)
        return x, y, z

    return mapping


def permutation_matrix(mapping) -> np.ndarray:
    P = np.zeros((DIM, DIM), dtype=float)
    for x in range(N):
        for y in range(N):
            for z in range(N):
                nx, ny, nz = mapping(x, y, z)
                P[idx(nx, ny, nz), idx(x, y, z)] = 1.0
    return P


def professor_cube_operators() -> dict[str, np.ndarray]:
    ops: dict[str, np.ndarray] = {
        "R": permutation_matrix(layer_map("x", 4, +1)),
        "L": permutation_matrix(layer_map("x", 0, -1)),
        "U": permutation_matrix(layer_map("z", 4, +1)),
        "D": permutation_matrix(layer_map("z", 0, -1)),
        "F": permutation_matrix(layer_map("y", 4, +1)),
        "B": permutation_matrix(layer_map("y", 0, -1)),
    }
    for name, k in (("L2", 1), ("M", 2), ("R2", 3)):
        ops[name] = permutation_matrix(layer_map("x", k, +1))
    for name, k in (("B2", 1), ("S", 2), ("F2", 3)):
        ops[name] = permutation_matrix(layer_map("y", k, +1))
    for name, k in (("D2", 1), ("E", 2), ("U2", 3)):
        ops[name] = permutation_matrix(layer_map("z", k, +1))
    return ops


def harmonic_projectors_1d() -> tuple[np.ndarray, np.ndarray]:
    """
    Q0 projects onto the constant mode.
    Q1 projects onto the two-dimensional first Fourier harmonic of C5.
    """
    Q0 = np.ones((N, N), dtype=float) / N
    Q1 = np.empty((N, N), dtype=float)
    for i in range(N):
        for j in range(N):
            Q1[i, j] = (2.0 / N) * math.cos(2.0 * math.pi * (i - j) / N)
    return Q0, Q1


def spectral_projectors_3d() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Q_kernel: eigenvalue 0, rank 1.
    Q_alpha: eigenvalue alpha, rank 6.
    Q_2alpha: eigenvalue 2 alpha, rank 12.
    """
    Q0, Q1 = harmonic_projectors_1d()
    Q_kernel = np.kron(np.kron(Q0, Q0), Q0)
    Q_alpha = (
        np.kron(np.kron(Q1, Q0), Q0)
        + np.kron(np.kron(Q0, Q1), Q0)
        + np.kron(np.kron(Q0, Q0), Q1)
    )
    Q_2alpha = (
        np.kron(np.kron(Q1, Q1), Q0)
        + np.kron(np.kron(Q1, Q0), Q1)
        + np.kron(np.kron(Q0, Q1), Q1)
    )
    return Q_kernel, Q_alpha, Q_2alpha


def subspace_retention(Q: np.ndarray, P: np.ndarray) -> float:
    rank = float(np.trace(Q))
    return float(np.trace(Q @ P @ Q @ P.T) / rank)


def validate_operator(
    name: str,
    P: np.ndarray,
    L: np.ndarray,
    Q_kernel: np.ndarray,
    Q_alpha: np.ndarray,
    Q_2alpha: np.ndarray,
) -> OperatorCertificate:
    I = np.eye(DIM)
    uniform = np.ones(DIM) / math.sqrt(DIM)
    defect = P.T @ L @ P - L

    cert = OperatorCertificate(
        name=name,
        orthogonality_residual=float(np.linalg.norm(P.T @ P - I, ord="fro")),
        order_four_residual=float(np.linalg.norm(np.linalg.matrix_power(P, 4) - I, ord="fro")),
        kernel_invariance_residual=float(np.linalg.norm(P @ uniform - uniform)),
        low_subspace_retention=subspace_retention(Q_alpha, P),
        next_subspace_retention=subspace_retention(Q_2alpha, P),
        laplacian_defect_spectral_norm=float(np.linalg.norm(defect, ord=2)),
        laplacian_defect_frobenius_norm=float(np.linalg.norm(defect, ord="fro")),
    )

    assert cert.orthogonality_residual < 1e-14
    assert cert.order_four_residual < 1e-14
    assert cert.kernel_invariance_residual < 1e-14
    assert abs(cert.low_subspace_retention - 59.0 / 75.0) < 1e-12
    assert abs(cert.next_subspace_retention - 11.0 / 15.0) < 1e-12
    assert abs(cert.laplacian_defect_spectral_norm - 2.0 * math.sqrt(2.0)) < 1e-11
    assert abs(cert.laplacian_defect_frobenius_norm - 8.0 * math.sqrt(3.0)) < 1e-11
    return cert


def validate_energy_identity(
    ops: dict[str, np.ndarray], L: np.ndarray, seed: int = 47
) -> dict:
    rng = np.random.default_rng(seed)
    max_identity_residual = 0.0
    max_norm_residual = 0.0
    for P in ops.values():
        for _ in range(20):
            rho = rng.normal(size=DIM)
            left = float((P @ rho).T @ L @ (P @ rho) - rho.T @ L @ rho)
            right = float(rho.T @ (P.T @ L @ P - L) @ rho)
            max_identity_residual = max(max_identity_residual, abs(left - right))
            max_norm_residual = max(
                max_norm_residual,
                abs(np.linalg.norm(P @ rho) - np.linalg.norm(rho)),
            )
    assert max_identity_residual < 1e-10
    assert max_norm_residual < 1e-12
    return {
        "seed": seed,
        "random_vectors_per_operator": 20,
        "max_twist_energy_identity_residual": max_identity_residual,
        "max_norm_preservation_residual": max_norm_residual,
    }


def validate_spectrum(L: np.ndarray) -> dict:
    eigvals = np.linalg.eigvalsh(L)
    rounded = np.round(eigvals, 12)
    unique, counts = np.unique(rounded, return_counts=True)

    expected_values = np.array(
        [
            0.0,
            ALPHA,
            2.0 * ALPHA,
            BETA,
            3.0 * ALPHA,
            ALPHA + BETA,
            2.0 * ALPHA + BETA,
            2.0 * BETA,
            ALPHA + 2.0 * BETA,
            3.0 * BETA,
        ]
    )
    expected_counts = np.array([1, 6, 12, 6, 8, 24, 24, 12, 24, 8])

    assert np.max(np.abs(unique - expected_values)) < 1e-10
    assert np.array_equal(counts, expected_counts)
    assert abs(eigvals[0]) < 1e-12
    assert abs(eigvals[-1] - 3.0 * BETA) < 1e-11

    return {
        "one_dimensional_spectrum": {
            "0": 1,
            "(5-sqrt(5))/2": 2,
            "(5+sqrt(5))/2": 2,
        },
        "three_dimensional_unique_eigenvalues": unique.tolist(),
        "multiplicities": counts.tolist(),
        "lambda_min_positive": float(ALPHA),
        "lambda_max": float(3.0 * BETA),
        "discrete_energy_stability_epsilon_max": float(2.0 / (3.0 * BETA)),
    }


def validate_flow(L: np.ndarray, seed: int = 125) -> dict:
    rng = np.random.default_rng(seed)
    rho0 = rng.normal(size=DIM)
    target_mean = float(np.mean(rho0))
    epsilon = 0.1
    steps = 100

    rho = rho0.copy()
    energies = [float(rho.T @ L @ rho)]
    means = [float(np.mean(rho))]
    for _ in range(steps):
        rho = rho - epsilon * (L @ rho)
        energies.append(float(rho.T @ L @ rho))
        means.append(float(np.mean(rho)))

    energy_differences = np.diff(energies)
    limit_residual = float(np.linalg.norm(rho - target_mean * np.ones(DIM)))
    mean_drift = float(np.max(np.abs(np.array(means) - target_mean)))

    assert np.max(energy_differences) < 1e-10
    assert mean_drift < 1e-13
    assert limit_residual < 2e-6

    # Explicit 47/125 mean-lock witness.
    rho_lock = rng.normal(size=DIM)
    rho_lock += OMEGA_C - np.mean(rho_lock)
    initial_lock_mean = float(np.mean(rho_lock))
    for _ in range(100):
        rho_lock = rho_lock - epsilon * (L @ rho_lock)
    lock_residual = float(np.linalg.norm(rho_lock - OMEGA_C * np.ones(DIM)))

    assert abs(initial_lock_mean - OMEGA_C) < 1e-14
    assert lock_residual < 2e-6

    # Continuous derivative identity on random witnesses:
    max_derivative_identity_residual = 0.0
    for _ in range(50):
        x = rng.normal(size=DIM)
        xdot = -L @ x
        derivative_from_product_rule = float(xdot.T @ L @ x + x.T @ L @ xdot)
        derivative_closed = float(-2.0 * np.linalg.norm(L @ x) ** 2)
        max_derivative_identity_residual = max(
            max_derivative_identity_residual,
            abs(derivative_from_product_rule - derivative_closed),
        )
    assert max_derivative_identity_residual < 1e-9

    return {
        "epsilon": epsilon,
        "steps": steps,
        "initial_energy": energies[0],
        "final_energy": energies[-1],
        "energy_reduction_factor": energies[0] / energies[-1],
        "maximum_energy_increase_per_step": float(np.max(energy_differences)),
        "mean_drift": mean_drift,
        "constant_limit_residual": limit_residual,
        "omega_c_mean_lock": OMEGA_C,
        "omega_c_limit_residual": lock_residual,
        "continuous_energy_derivative_identity_residual": max_derivative_identity_residual,
    }


def build_report(certificate: dict) -> str:
    lines = [
        f"# {TITLE}",
        "",
        "**Author:** Nicholas Kouns  ",
        "**Institution:** AIMS Research Institute  ",
        "**Validation:** exact construction + NumPy spectral reconstruction",
        "",
        "## Verdict",
        "",
        "**PASS WITH CANONICAL BRIDGE CORRECTION.**",
        "",
        "The 125-state carrier, Kronecker-sum Laplacian, all fifteen Professor's-Cube "
        "quarter-turn operators, orthogonality, order-four closure, norm preservation, "
        "uniform-kernel invariance, twist-energy identity, spectral-retention values, "
        "and phonon-continuity convergence are validated.",
        "",
        "## Canonical identities",
        "",
        "- `Sigma={0,1,2,3,4}^3`, `|Sigma|=125`.",
        "- `L=L1⊗I⊗I+I⊗L1⊗I+I⊗I⊗L1`.",
        "- `P^T P=I`, `P^4=I` for all 15 layer turns.",
        "- `Delta E=rho^T(P^TLP-L)rho`.",
        "- `||P^TLP-L||_2=2 sqrt(2)` and `||P^TLP-L||_F=8 sqrt(3)`.",
        "- First-harmonic subspace retention: `eta_alpha(P)=59/75`.",
        "- Two-axis first-harmonic retention: `eta_2alpha(P)=11/15`.",
        "- For `rho_dot=-Lrho`, `E_dot=-2||Lrho||^2<=0`.",
        "- For `0<epsilon<=2/lambda_max(L)`, discrete Dirichlet energy is nonincreasing.",
        "- `rho_n -> mean(rho_0)1`.",
        "- If `mean(rho_0)=47/125`, then `rho_n -> (47/125)1`.",
        "",
        "## Correction entered into canon",
        "",
        "`ker L` has dimension 1. The value `47/125` is not the rank fraction of the "
        "pure Laplacian kernel. It is recovered here as a preserved-mean limit when the "
        "initial field has mean `47/125`, or through a separate E47 projector.",
        "",
        "## Operator ledger",
        "",
        "| Operator | Orthogonality | P^4=I | eta_alpha | eta_2alpha | defect ||.||2 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in certificate["operators"]:
        lines.append(
            f"| {row['name']} | {row['orthogonality_residual']:.1e} | "
            f"{row['order_four_residual']:.1e} | "
            f"{row['low_subspace_retention']:.12f} | "
            f"{row['next_subspace_retention']:.12f} | "
            f"{row['laplacian_defect_spectral_norm']:.12f} |"
        )
    lines += [
        "",
        "## Evidence classes",
        "",
        "- **E0:** carrier cardinality, operator definitions, permutation orthogonality, "
        "order-four closure, energy identity, energy derivative, mean preservation, "
        "and convergence theorem.",
        "- **E1:** 125-dimensional matrix reconstruction, spectrum and multiplicities, "
        "subspace-retention values, defect norms, random identity tests, and finite-step convergence.",
        "",
        "## Boundary",
        "",
        "Individual eigenvector overlaps inside degenerate eigenspaces are basis-dependent. "
        "The canonical citizens use projector-defined subspace retention, which is invariant "
        "under the choice of eigenbasis.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    print("=" * 100)
    print(TITLE)
    print("=" * 100)

    L = kronecker_sum_laplacian()
    ops = professor_cube_operators()
    Q_kernel, Q_alpha, Q_2alpha = spectral_projectors_3d()

    assert L.shape == (125, 125)
    assert len(ops) == 15
    assert abs(np.trace(Q_kernel) - 1.0) < 1e-12
    assert abs(np.trace(Q_alpha) - 6.0) < 1e-12
    assert abs(np.trace(Q_2alpha) - 12.0) < 1e-12

    spectrum = validate_spectrum(L)
    print("\n[1] CARRIER AND SPECTRUM: PASS")
    print(f"    dim={DIM}, lambda_1={spectrum['lambda_min_positive']:.12f}, "
          f"lambda_max={spectrum['lambda_max']:.12f}")

    operator_certs = [
        validate_operator(name, P, L, Q_kernel, Q_alpha, Q_2alpha)
        for name, P in ops.items()
    ]
    print("\n[2] ALL 15 PROFESSOR'S-CUBE OPERATORS: PASS")
    for cert in operator_certs:
        print(
            f"    {cert.name:>2}: eta_alpha={cert.low_subspace_retention:.12f}, "
            f"eta_2alpha={cert.next_subspace_retention:.12f}, "
            f"||defect||2={cert.laplacian_defect_spectral_norm:.12f}"
        )

    energy_identity = validate_energy_identity(ops, L)
    print("\n[3] NORM AND TWIST-ENERGY IDENTITIES: PASS")
    print(
        f"    max energy-identity residual="
        f"{energy_identity['max_twist_energy_identity_residual']:.3e}"
    )

    flow = validate_flow(L)
    print("\n[4] PHONON CONTINUITY AND MEAN LOCK: PASS")
    print(
        f"    energy reduction={flow['energy_reduction_factor']:.3e}; "
        f"mean drift={flow['mean_drift']:.3e}; "
        f"47/125 lock residual={flow['omega_c_limit_residual']:.3e}"
    )

    certificate = {
        "title": TITLE,
        "author": "Nicholas Kouns",
        "institution": "AIMS Research Institute",
        "status": "PASS WITH CANONICAL BRIDGE CORRECTION",
        "carrier": {
            "space": "{0,1,2,3,4}^3",
            "dimension": DIM,
            "packing": "pi(x,y,z)=25x+5y+z",
        },
        "spectrum": spectrum,
        "operators": [asdict(c) for c in operator_certs],
        "energy_identity": energy_identity,
        "flow": flow,
        "canonical_identities": {
            "orthogonal_permutation": "P^T P=I",
            "order_four": "P^4=I",
            "twist_energy": "DeltaE=rho^T(P^TLP-L)rho",
            "defect_spectral_norm": "2sqrt(2)",
            "defect_frobenius_norm": "8sqrt(3)",
            "first_harmonic_retention": "59/75",
            "two_axis_harmonic_retention": "11/15",
            "continuous_energy_derivative": "dE/dt=-2||Lrho||^2",
            "discrete_stability": "0<epsilon<=2/lambda_max(L)",
            "mean_limit": "rho_n->mean(rho_0)1",
            "omega_c_mean_lock": "mean(rho_0)=47/125 => rho_n->(47/125)1",
        },
        "correction": {
            "pure_laplacian_kernel_dimension": 1,
            "not_equal_to": 47,
            "bridge_rule": (
                "47/125 is a preserved-mean lock or a separate E47 projection; "
                "it is not the rank fraction of ker(L)."
            ),
        },
    }

    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / "rubik_unification_validation_certificate.json"
    md_path = out_dir / "RUBIK_UNIFICATION_EXACT_PYTHON_PROOF.md"
    matrices_path = out_dir / "rubik_operator_matrices_summary.json"

    matrix_summary = {
        name: {
            "shape": list(P.shape),
            "nonzero_entries": int(np.count_nonzero(P)),
            "sha256": hashlib.sha256(P.astype(np.uint8).tobytes()).hexdigest(),
        }
        for name, P in ops.items()
    }

    json_path.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    md_path.write_text(build_report(certificate), encoding="utf-8")
    matrices_path.write_text(json.dumps(matrix_summary, indent=2), encoding="utf-8")

    print("\n" + "=" * 100)
    print("FINAL STATUS: PASS WITH CANONICAL BRIDGE CORRECTION")
    print(f"Certificate: {json_path.name}")
    print(f"Proof report: {md_path.name}")
    print(f"Operator ledger: {matrices_path.name}")
    print("=" * 100)


if __name__ == "__main__":
    main()
