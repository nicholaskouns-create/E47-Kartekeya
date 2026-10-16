#!/usr/bin/env python3
"""E47 neural-quantum benchmark: spectral checks behind the validated analysis.

Runs on the operators built by e47_neural_quantum_benchmark.py (same folder) and checks:
  1. SO(3) equivariance: C, P and Gamma commute with the total angular momentum J_a.
  2. Polynomial identity: the spectrally built Gamma equals I - K^2/99144.
  3. Exact per-sector eigenvalues of Gamma (rational arithmetic) and their match to the numerics.
  4. Optimal fixed step: eta = 2/(11664 + 186624) = 1/99144 gives spectral radius 15/17, the minimum
     over all layers I - eta K^2 (exact rational arithmetic).
  5. Measured ||Gamma^n - P||_2 against (15/17)^n.
  6. Postselection success probability ||Gamma^n psi||^2: non-increasing and never below ||P psi||^2.

Certificate: MC-E47-NEURAL-QUANTUM-RI-20261016-001 (written by e47_neural_quantum_validation_suite.py)
Usage: python3 e47_neural_quantum_spectral_checks.py
"""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EIG_K2 = (11664, 12544, 19600, 32400, 186624)


def load_bench(path: str | Path | None = None):
    path = Path(path) if path else HERE / "e47_neural_quantum_benchmark.py"
    spec = importlib.util.spec_from_file_location("e47_neural_quantum_benchmark", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def total_J(eb):
    I5 = np.eye(5, dtype=complex)
    return [np.kron(np.kron(a, I5), I5) + np.kron(np.kron(I5, a), I5) + np.kron(np.kron(I5, I5), a) for a in eb.spin2()]


def run(bench=None):
    eb = load_bench(bench)
    C, P, G, U, gam, spin = eb.build()
    J = total_J(eb)
    I = np.eye(125)
    out, checks = {}, {}

    # 1. equivariance (Frobenius norms of commutators)
    comm = {name: float(max(np.linalg.norm(X @ j - j @ X) for j in J)) for name, X in (("C", C), ("P", P), ("Gamma", G))}
    out["equivariance_commutator_frobenius"] = comm
    checks["equivariance_C_P_Gamma"] = max(comm.values()) < 1e-11

    # 2. polynomial identity
    K = (C - 6 * I) @ (C - 30 * I)
    poly = float(np.linalg.norm(G - (I - K @ K / 99144)))
    out["polynomial_identity_error"] = poly
    checks["gamma_equals_I_minus_K2_over_99144"] = poly < 1e-12

    # 3. exact per-sector eigenvalues
    sectors, worst = {}, 0.0
    for j in range(7):
        c = j * (j + 1)
        k2 = ((c - 6) * (c - 30)) ** 2
        g = 1 - Fraction(k2, 99144)
        num = gam[spin == j]
        worst = max(worst, float(np.max(np.abs(num - float(g)))))
        sectors[str(j)] = {"dimension": int((spin == j).sum()), "multiplicity": int((spin == j).sum()) // (2 * j + 1),
                           "K2": k2, "gamma": str(g), "gamma_float": float(g)}
    out["sectors"] = sectors
    out["sector_eigenvalue_numeric_mismatch"] = worst
    expected = ["103/153", "10825/12393", "1", "15/17", "9943/12393", "1", "-15/17"]
    checks["sector_eigenvalues_exact"] = [sectors[str(j)]["gamma"] for j in range(7)] == expected and worst < 1e-15
    checks["multiplicities_1_3_5_4_3_2_1"] = [sectors[str(j)]["multiplicity"] for j in range(7)] == [1, 3, 5, 4, 3, 2, 1]

    # 4. optimal fixed step (exact): rho(eta) = max(|1 - eta*l_min|, |1 - eta*l_max|) is minimised only at 2/(l_min + l_max)
    lmin, lmax = min(EIG_K2), max(EIG_K2)
    eta_star = Fraction(2, lmin + lmax)
    rho_star = max(abs(1 - eta_star * l) for l in EIG_K2)
    out["optimal_step"] = {"eta_star": str(eta_star), "rho_star": str(rho_star), "kappa": str(Fraction(lmax, lmin))}
    checks["optimal_step_is_1_over_99144"] = eta_star == Fraction(1, 99144)
    checks["optimal_rate_is_15_over_17"] = rho_star == Fraction(15, 17) and Fraction(lmax, lmin) == 16

    # 5. measured operator norm vs (15/17)^n
    r, norms = 15 / 17, {}
    for n in (1, 10, 50, 100, 220):
        norms[str(n)] = {"measured": float(np.linalg.norm(np.linalg.matrix_power(G, n) - P, 2)), "theory": r ** n}
    out["operator_norm"] = norms
    # Tolerance 1e-13, as in V1. The first run used 1e-14 and failed at n = 10, where double-precision
    # roundoff in the matrix power and the SVD gives a deviation of 1.13e-14 (relative 3.9e-14).
    out["operator_norm_max_abs_deviation"] = max(abs(v["measured"] - v["theory"]) for v in norms.values())
    checks["operator_norm_matches_15_17_power"] = out["operator_norm_max_abs_deviation"] < 1e-13

    # 6. success probability over every step of the benchmark's seed-47 state
    rng = np.random.default_rng(47)
    psi = rng.normal(size=125) + 1j * rng.normal(size=125)
    psi /= np.linalg.norm(psi)
    q = float(np.vdot(P @ psi, P @ psi).real)
    v, s = psi.copy(), []
    for _ in range(221):
        s.append(np.vdot(v, v).real)
        v = G @ v
    s = np.array(s)
    out["success_probability"] = {"projected_probability_q": q, "final": float(s[-1]),
                                  "min_excess_over_q": float((s - q).min()), "max_step_increase": float(np.diff(s).max())}
    checks["success_probability_never_increases"] = np.diff(s).max() <= 1e-15
    checks["success_probability_never_below_q"] = (s - q).min() > -1e-13
    return out, checks


def main():
    out, checks = run(sys.argv[1] if len(sys.argv) > 1 else None)
    print("Equivariance (max Frobenius commutator with J_a):", out["equivariance_commutator_frobenius"])
    print("||Gamma - (I - K^2/99144)||_F =", f'{out["polynomial_identity_error"]:.2e}')
    for j, d in out["sectors"].items():
        print(f"  j={j}: dim {d['dimension']:2d}  mult {d['multiplicity']}  K^2 {d['K2']:6d}  gamma {d['gamma']}")
    print("Optimal step:", out["optimal_step"])
    for n, d in out["operator_norm"].items():
        print(f"  n={n:>3}: ||Gamma^n - P||_2 = {d['measured']:.6e}   (15/17)^n = {d['theory']:.6e}")
    print("Success probability:", out["success_probability"])
    print("\n".join(f"[{'PASS' if ok else 'FAIL'}] {k}" for k, ok in checks.items()))
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
