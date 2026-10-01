#!/usr/bin/env python3
"""
Newton–E47 Product-Kernel Validator
===================================
Validates the coupled scalar Newton / E47 spectral contraction construction.

Checks:
  - E47 projector rank 47 and complement rank 78
  - K P = 0, P^2 = P
  - Gamma*=I-K^2/99144 fixes E47
  - spectral radius on E47^perp is 15/17
  - ||Gamma^n-P||_2=(15/17)^n numerically
  - Newton quadratic error identity
  - product fixed manifold witness
  - joint Lyapunov zero-set witness
  - CPTP dephasing completion D_P(rho)=P rho P+Q rho Q
"""

import math
import json
import numpy as np
from numpy.linalg import norm, eigvalsh

TOL = 1e-10

def spin2_generators():
    j = 2
    mvals = np.array([2, 1, 0, -1, -2], dtype=float)
    Jz = np.diag(mvals).astype(complex)
    Jp = np.zeros((5, 5), dtype=complex)
    for col, m in enumerate(mvals):
        mp = m + 1
        if mp <= j:
            rows = np.where(mvals == mp)[0]
            if len(rows):
                Jp[rows[0], col] = math.sqrt(j * (j + 1) - m * (m + 1))
    Jm = Jp.conj().T
    Jx = (Jp + Jm) / 2
    Jy = (Jp - Jm) / (2j)
    return Jx, Jy, Jz

def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)

def build_e47():
    Jx, Jy, Jz = spin2_generators()
    I5 = np.eye(5, dtype=complex)
    Jxt = kron3(Jx, I5, I5) + kron3(I5, Jx, I5) + kron3(I5, I5, Jx)
    Jyt = kron3(Jy, I5, I5) + kron3(I5, Jy, I5) + kron3(I5, I5, Jy)
    Jzt = kron3(Jz, I5, I5) + kron3(I5, Jz, I5) + kron3(I5, I5, Jz)
    C = Jxt @ Jxt + Jyt @ Jyt + Jzt @ Jzt
    I125 = np.eye(125, dtype=complex)
    K = (C - 6 * I125) @ (C - 30 * I125)
    K2 = K @ K
    w, U = np.linalg.eigh(C)
    mask = np.isclose(w, 6, atol=1e-8) | np.isclose(w, 30, atol=1e-8)
    P = U[:, mask] @ U[:, mask].conj().T
    Q = I125 - P
    Gamma = I125 - K2 / 99144
    return C, K, K2, P, Q, Gamma

def main():
    C, K, K2, P, Q, Gamma = build_e47()
    target_rho = 15 / 17

    gamma_eigs = eigvalsh((Gamma + Gamma.conj().T) / 2)
    unit_mask = np.isclose(gamma_eigs, 1.0, atol=1e-10)
    comp = gamma_eigs[~unit_mask]
    rho_comp = float(np.max(np.abs(comp)))

    a = 4.0
    root = math.sqrt(a)
    B = lambda x: 0.5 * (x + a / x)

    rng = np.random.default_rng(47)
    psi0 = rng.normal(size=125) + 1j * rng.normal(size=125)
    psi0 /= norm(psi0)
    psiE = P @ psi0

    joint_fixed_residual = float(math.sqrt(abs(root * root - a) ** 2 + norm(K @ psiE) ** 2))
    fixed_map_residual = float(math.sqrt(abs(B(root) - root) ** 2 + norm(Gamma @ psiE - psiE) ** 2))

    x = 3.1
    e = x - root
    quad_resid = float(abs((B(x) - root) - e * e / (2 * x)))

    norm_law = {}
    for n in (1, 2, 5, 10, 25):
        lhs = float(norm(np.linalg.matrix_power(Gamma, n) - P, 2))
        rhs = float(target_rho ** n)
        norm_law[str(n)] = {"lhs": lhs, "rhs": rhs, "abs_err": abs(lhs - rhs)}

    rho = np.outer(psi0, psi0.conj())
    rhoD = P @ rho @ P + Q @ rho @ Q
    trace_resid = float(abs(np.trace(rhoD) - 1))
    herm_resid = float(norm(rhoD - rhoD.conj().T))
    min_eval = float(np.min(eigvalsh((rhoD + rhoD.conj().T) / 2)))
    cross_resid = float(norm(P @ rhoD @ Q) + norm(Q @ rhoD @ P))
    psiE_n = psiE / norm(psiE)
    rhoE = np.outer(psiE_n, psiE_n.conj())
    inv_resid = float(norm((P @ rhoE @ P + Q @ rhoE @ Q) - rhoE))

    checks = {
        "dim_P_47": bool(abs(np.trace(P).real - 47) < 1e-8),
        "dim_Q_78": bool(abs(np.trace(Q).real - 78) < 1e-8),
        "P_idempotent": bool(norm(P @ P - P) < 1e-10),
        "KP_zero": bool(norm(K @ P) < 1e-8),
        "Gamma_P_fixed": bool(norm(Gamma @ P - P) < 1e-8),
        "Gamma_47_unit_eigs": bool(np.sum(unit_mask) == 47),
        "Gamma_complement_rho_15_17": bool(abs(rho_comp - target_rho) < 1e-10),
        "fixed_joint_residual": bool(joint_fixed_residual < 1e-8),
        "fixed_map_residual": bool(fixed_map_residual < 1e-8),
        "quadratic_error_identity": bool(quad_resid < 1e-14),
        "norm_law_exact_numeric": bool(max(v["abs_err"] for v in norm_law.values()) < 1e-10),
        "quantum_trace_preserving": bool(trace_resid < 1e-12),
        "quantum_hermitian": bool(herm_resid < 1e-12),
        "quantum_positive": bool(min_eval > -1e-12),
        "quantum_block_dephased": bool(cross_resid < 1e-12),
        "quantum_kernel_invariance": bool(inv_resid < 1e-12),
    }

    result = {
        "certificate": "MC-E47-NEWTON-PRODUCT-20260930-001",
        "rank_P": float(np.trace(P).real),
        "rank_Q": float(np.trace(Q).real),
        "rho_complement": rho_comp,
        "target_rho": target_rho,
        "joint_fixed_residual": joint_fixed_residual,
        "fixed_map_residual": fixed_map_residual,
        "quadratic_identity_residual": quad_resid,
        "norm_law": norm_law,
        "quantum": {
            "trace_residual": trace_resid,
            "hermiticity_residual": herm_resid,
            "min_eigenvalue": min_eval,
            "cross_block_residual": cross_resid,
            "kernel_invariance_residual": inv_resid,
        },
        "checks": checks,
        "pass_count": sum(checks.values()),
        "total_checks": len(checks),
    }

    print(json.dumps(result, indent=2))
    assert all(checks.values())

if __name__ == "__main__":
    main()
