#!/usr/bin/env python3
"""Recursive Identity and E47: machine checks of the formalization's mathematical claims.

Uses the operators built by e47_neural_quantum_benchmark.py (same folder):
H = V_2^{x3} = C^125, J_a total angular momentum, C = sum_a J_a^2, K = (C - 6)(C - 30),
P = projector onto E47 = ker K, Gamma = I - K^2/99144.

Stated claims checked
  Thm 1  su(2) relations; J_a commutes with C, K, P, Gamma; H = V0+3V1+5V2+4V3+3V4+2V5+V6; E47 = 5V2+2V5, dim 47
         ((Poly) is completed for P by P = p(C), p the Lagrange polynomial on the seven Casimir values)
  Thm 2  Fix(Gamma) = E47; Gamma P = P Gamma = P; ||Gamma(I - P)||_2 = 15/17
  IV     Gamma psi = psi - eta grad E(psi), E = |K psi|^2/2, eta = 1/99144; descent premise 0 <= eta*lambda(K^2) <= 2
  V      U = [[Gamma, B], [B, -Gamma]], B = (I - Gamma^2)^{1/2}: U^+ U = I and |Gamma psi|^2 + |B psi|^2 = |psi|^2

Consequences of the same definitions, also checked
  1. sharp geometric descent  E(Gamma psi) <= (15/17)^2 E(psi), equality on the j = 3 and j = 6 sectors
  2. coherence C(psi) = |P psi|^2/|psi|^2 is non-decreasing along the recursion, with
     1 - C(Gamma^n psi) <= (15/17)^{2n} (1 - C(psi))/C(psi)
  3. with loop rate l(c) = 1/(1 - c) the time functional T advances by 2 ln(17/15) per step asymptotically
  4. grad C(psi) = 2(P psi - C(psi) psi)/|psi|^2 vanishes exactly on E47 and on its orthogonal complement
  5. U is Hermitian, hence U^2 = I

Certificate: MC-E47-NEURAL-QUANTUM-RI-20261016-001 (written by e47_neural_quantum_validation_suite.py)
Usage: python3 e47_recursive_identity_checks.py
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ETA, R = 1 / 99144, 15 / 17


def load_bench(path=None):
    path = Path(path) if path else HERE / "e47_neural_quantum_benchmark.py"
    spec = importlib.util.spec_from_file_location("e47_neural_quantum_benchmark", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def n2(A):
    return float(np.linalg.norm(A, 2))


def run(bench=None):
    eb = load_bench(bench)
    C, P, G, U, gam, spin = eb.build()
    I5, I = np.eye(5, dtype=complex), np.eye(125)
    J = [np.kron(np.kron(a, I5), I5) + np.kron(np.kron(I5, a), I5) + np.kron(np.kron(I5, I5), a) for a in eb.spin2()]
    K = (C - 6 * I) @ (C - 30 * I)
    K2 = K @ K
    out, checks = {}, {}

    # Theorem 1
    eps = np.zeros((3, 3, 3))
    eps[0, 1, 2] = eps[1, 2, 0] = eps[2, 0, 1] = 1
    eps[0, 2, 1] = eps[2, 1, 0] = eps[1, 0, 2] = -1
    su2 = max(n2(J[a] @ J[b] - J[b] @ J[a] - 1j * sum(eps[a, b, c] * J[c] for c in range(3))) for a in range(3) for b in range(3))
    rel = {nm: max(n2(j @ X - X @ j) for j in J) / n2(X) for nm, X in (("C", C), ("K", K), ("P", P), ("Gamma", G))}
    mult = [int((spin == j).sum()) // (2 * j + 1) for j in range(7)]
    dimker = 125 - int(np.linalg.matrix_rank(K, tol=1e-6 * n2(K)))
    cas = [j * (j + 1) for j in range(7)]
    pC = np.zeros((125, 125), complex)
    for ci in (6, 30):
        term = I.astype(complex)
        for cj in cas:
            if cj != ci:
                term = term @ (C - cj * I) / (ci - cj)
        pC += term
    out["theorem_1"] = {"su2_relation_error": su2, "relative_commutators": rel, "multiplicities": mult,
                        "dim_ker_K": dimker, "P_minus_lagrange_polynomial_of_C": n2(P - pC)}
    checks["T1_su2_relations"] = su2 < 1e-13
    checks["T1_invariance_C_K_P_Gamma"] = max(rel.values()) < 1e-12
    checks["T1_decomposition_and_dim_47"] = mult == [1, 3, 5, 4, 3, 2, 1] and dimker == 47
    checks["T1_P_is_polynomial_in_C"] = out["theorem_1"]["P_minus_lagrange_polynomial_of_C"] < 1e-12

    # Theorem 2
    ev = np.linalg.eigvalsh((G + G.conj().T) / 2)
    out["theorem_2"] = {"unit_eigenvalues": int((abs(ev - 1) < 1e-9).sum()), "Gamma_minus_I_on_E47": n2((G - I) @ P),
                        "GammaP_minus_P": n2(G @ P - P), "PGamma_minus_P": n2(P @ G - P), "norm_Gamma_I_minus_P": n2(G @ (I - P))}
    t2 = out["theorem_2"]
    checks["T2_fixed_space_is_E47"] = t2["unit_eigenvalues"] == 47 and t2["Gamma_minus_I_on_E47"] < 1e-13
    checks["T2_GammaP_eq_PGamma_eq_P"] = max(t2["GammaP_minus_P"], t2["PGamma_minus_P"]) < 1e-13
    checks["T2_rate_15_over_17"] = abs(t2["norm_Gamma_I_minus_P"] - R) < 1e-12

    # Section IV: gradient step and descent
    rng = np.random.default_rng(1)
    psi = rng.normal(size=125) + 1j * rng.normal(size=125)
    E = lambda v: 0.5 * np.linalg.norm(K @ v) ** 2
    d = rng.normal(size=125) + 1j * rng.normal(size=125)
    h = 1e-6
    fd = (E(psi + h * d) - E(psi - h * d)) / (2 * h)
    an = float(np.real(np.vdot(K2 @ psi, d)))
    lam = np.unique(np.round(np.linalg.eigvalsh((K2 + K2.conj().T) / 2)))
    lam = lam[lam > 0.5]
    factor = float(max((1 - ETA * lam) ** 2))
    X = rng.normal(size=(125, 20000)) + 1j * rng.normal(size=(125, 20000))
    ratio = float((np.linalg.norm(K @ (G @ X), axis=0) ** 2 / np.linalg.norm(K @ X, axis=0) ** 2).max())
    v3 = U[:, spin == 3][:, 0]
    attained = float(np.linalg.norm(K @ G @ v3) ** 2 / np.linalg.norm(K @ v3) ** 2)
    out["section_IV"] = {"gradient_finite_difference_rel_error": abs(fd - an) / abs(an),
                         "update_identity_error": float(np.linalg.norm(G @ psi - (psi - ETA * K2 @ psi))),
                         "nonzero_eigenvalues_K2": [int(x) for x in lam], "max_eta_lambda": float(ETA * lam.max()),
                         "sharp_descent_factor": factor, "max_ratio_20000_states": ratio, "ratio_on_j3_state": attained}
    s4 = out["section_IV"]
    checks["IV_gradient_step"] = s4["gradient_finite_difference_rel_error"] < 1e-6 and s4["update_identity_error"] < 1e-12
    checks["IV_descent_premise"] = s4["nonzero_eigenvalues_K2"] == [11664, 12544, 19600, 32400, 186624] and s4["max_eta_lambda"] <= 2
    checks["X1_sharp_descent_factor_15_17_squared"] = (abs(factor - R ** 2) < 1e-14 and ratio <= factor + 1e-14
                                                     and abs(attained - R ** 2) < 1e-12)

    # Coherence along the recursion (seed-47 state of the benchmark)
    rng = np.random.default_rng(47)
    psi = rng.normal(size=125) + 1j * rng.normal(size=125)
    psi /= np.linalg.norm(psi)
    coh = lambda v: np.linalg.norm(P @ v) ** 2 / np.linalg.norm(v) ** 2
    v, cs = psi.copy(), []
    for _ in range(221):
        cs.append(coh(v))
        v = G @ v
    cs = np.array(cs)
    c0 = cs[0]
    bound_ratio = max((1 - cs[k]) / ((R ** (2 * k)) * (1 - c0) / c0) for k in range(101))
    out["coherence"] = {"values_n_0_1_5_10_25_50": [float(cs[k]) for k in (0, 1, 5, 10, 25, 50)],
                        "min_step_change": float(np.diff(cs).min()), "max_ratio_to_geometric_bound_n_le_100": float(bound_ratio)}
    checks["X2_coherence_monotone"] = np.diff(cs).min() > -1e-14
    checks["X2_coherence_geometric_bound"] = bound_ratio <= 1

    # Time functional with l(c) = 1/(1 - c), from the exact eigenbasis amplitudes (no roundoff floor)
    a = np.abs(U.conj().T @ psi) ** 2
    ker = np.isin(spin, [2, 5])
    def T(n):
        om = (a[~ker] * gam[~ker] ** (2 * n)).sum() / (a[ker].sum() + (a[~ker] * gam[~ker] ** (2 * n)).sum())
        return float(np.log(a[~ker].sum() / om))
    slope = (T(300) - T(200)) / 100
    out["time_functional"] = {"loop_rate": "1/(1-c)", "T_200": T(200), "T_300": T(300), "mean_step_200_300": slope,
                              "two_ln_17_15": float(2 * np.log(17 / 15))}
    checks["X3_time_step_tends_to_2ln17_15"] = abs(slope - 2 * np.log(17 / 15)) < 1e-3

    # Critical points of the coherence functional
    gradC = lambda v: 2 * (P @ v - coh(v) * v) / np.linalg.norm(v) ** 2
    k = P @ psi
    k /= np.linalg.norm(k)
    w = (I - P) @ psi
    w /= np.linalg.norm(w)
    out["coherence_gradient"] = {"on_E47": float(np.linalg.norm(gradC(k))), "on_E47_perp": float(np.linalg.norm(gradC(w))),
                                 "at_psi0": float(np.linalg.norm(gradC(psi)))}
    cg = out["coherence_gradient"]
    checks["X4_coherence_critical_set"] = cg["on_E47"] < 1e-12 and cg["on_E47_perp"] < 1e-12 and cg["at_psi0"] > 1e-3

    # Section V: unitary dilation
    B = (U * np.sqrt(np.maximum(0, 1 - gam ** 2))) @ U.conj().T
    UU = np.block([[G, B], [B, -G]])
    out["section_V"] = {"unitarity": n2(UU.conj().T @ UU - np.eye(250)), "hermiticity": n2(UU - UU.conj().T),
                        "involution": n2(UU @ UU - np.eye(250)),
                        "norm_conservation": float(abs(np.linalg.norm(G @ psi) ** 2 + np.linalg.norm(B @ psi) ** 2 - 1))}
    s5 = out["section_V"]
    checks["V_dilation_unitary_and_norm_conserving"] = s5["unitarity"] < 1e-12 and s5["norm_conservation"] < 1e-12
    checks["X5_dilation_is_a_reflection"] = s5["hermiticity"] < 1e-12 and s5["involution"] < 1e-12
    return out, checks


def main():
    out, checks = run(sys.argv[1] if len(sys.argv) > 1 else None)
    for section in ("theorem_1", "theorem_2", "section_IV", "coherence", "time_functional", "coherence_gradient", "section_V"):
        print(f"{section}: {out[section]}")
    print("\n".join(f"[{'PASS' if ok else 'FAIL'}] {k}" for k, ok in checks.items()))
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
