#!/usr/bin/env python3
"""
CHIMERA / HAR-QEGT machine witness
==================================

1. Reconstruct canonical E47 FROM spin-2 SU(2) generators.
2. Verify Casimir spectrum, projector algebra, contraction, 47/125 invariant.
3. Implement the QEGT Gibbs/softmax strategy law.
4. Typed synthetic HAR->operator demonstration (NOT fitted biology).

Evidence classes kept separate:
- E47: exact finite-dimensional / machine reconstructed
- Gibbs strategy law: mathematical statistical operator
- HAR bridge: hypothesis interface awaiting fitted biological operators

Requires: numpy
"""

from __future__ import annotations

import json
import platform
import sys

import numpy as np

SEED = 470125
TOL = 1e-9


def spin2_generators():
    """Hermitian spin-2 Jx, Jy, Jz in the |m=2,1,0,-1,-2> basis."""
    j = 2
    m = np.arange(j, -j - 1, -1, dtype=float)
    d = 2 * j + 1
    Jp = np.zeros((d, d), dtype=complex)
    for col, mm in enumerate(m):
        mp = mm + 1
        if mp <= j:
            rows = np.where(np.isclose(m, mp))[0]
            if len(rows):
                row = int(rows[0])
                Jp[row, col] = np.sqrt(j * (j + 1) - mm * (mm + 1))
    Jm = Jp.conj().T
    Jx = (Jp + Jm) / 2
    Jy = (Jp - Jm) / (2j)
    Jz = np.diag(m)
    return Jx, Jy, Jz


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


def build_e47():
    Jx, Jy, Jz = spin2_generators()
    I5 = np.eye(5)
    Jtot = [
        kron3(J, I5, I5) + kron3(I5, J, I5) + kron3(I5, I5, J)
        for J in (Jx, Jy, Jz)
    ]
    C = sum(J @ J for J in Jtot)
    I = np.eye(125, dtype=complex)
    K = (C - 6 * I) @ (C - 30 * I)
    G = K.conj().T @ K

    evals_C, evecs_C = np.linalg.eigh(C)
    mask = np.isclose(evals_C, 6, atol=1e-8) | np.isclose(evals_C, 30, atol=1e-8)
    P = evecs_C[:, mask] @ evecs_C[:, mask].conj().T

    Ppoly = C.copy()
    for a in (2, 12, 20, 31, 42):
        Ppoly = Ppoly @ (C - a * I)
    Ppoly /= 1814400.0

    eps = 1.0 / 99144.0
    R = I - eps * G
    return C, K, G, P, Ppoly, R, evals_C


def cluster_spectrum(vals, decimals=8):
    u, n = np.unique(np.round(np.real(vals), decimals), return_counts=True)
    return {str(float(a)): int(b) for a, b in zip(u, n)}


def qegt_gibbs(costs, beta=1.0):
    costs = np.asarray(costs, dtype=float)
    z = -beta * costs
    z -= np.max(z)
    w = np.exp(z)
    return w / w.sum()


def synthetic_har_operator_demo():
    """Typed HAR-distribution DEMO. Mixed signs model compensatory substitution.
    Values are arbitrary synthetic coefficients — not biological effect sizes."""
    H0 = np.diag([0.9, 0.6, 0.8, 1.1, 0.7]).astype(float)
    B = [
        np.diag([-0.10, +0.04, 0.00, 0.00, +0.02]),
        np.diag([+0.06, -0.08, +0.03, 0.00, 0.00]),
        np.diag([0.00, +0.03, -0.07, +0.05, 0.00]),
        np.diag([+0.02, 0.00, +0.04, -0.06, +0.01]),
    ]
    h = np.array([1.0, 1.0, 1.0, 1.0])
    H = H0 + sum(x * b for x, b in zip(h, B))
    costs = np.diag(H)
    p = qegt_gibbs(costs, beta=2.0)
    return {
        "status": "SYNTHETIC_BRIDGE_DEMO_ONLY",
        "baseline_costs": np.diag(H0).tolist(),
        "perturbed_costs": costs.tolist(),
        "strategy_probabilities": p.tolist(),
        "normalization_residual": float(abs(p.sum() - 1.0)),
        "note": (
            "Replace B_i and h_i with estimates from HAR sequence swaps, "
            "MPRA, single-cell multiome, and 3D-contact data."
        ),
    }


def validate():
    C, K, G, P, Ppoly, R, evals_C = build_e47()
    evals_G = np.linalg.eigvalsh(G)
    nonzero_G = evals_G[evals_G > 1e-6]
    eps = 1.0 / 99144.0
    rho_perp = max(abs(1.0 - eps * nonzero_G))
    R250 = np.linalg.matrix_power(R, 250)

    out = {
        "run": "CHIMERA-QEGT-HAR-20260915",
        "status": "PASS",
        "seed": SEED,
        "evidence_classes": {
            "E47": "E0 exact identities + E1 deterministic NumPy reconstruction",
            "QEGT_Gibbs": "mathematical structural formalism",
            "HAR_bridge": "hypothesis / synthetic demonstrator only",
        },
        "e47": {
            "dimension": 125,
            "casimir_spectrum_multiplicity": cluster_spectrum(evals_C),
            "kernel_dimension": int(round(np.real(np.trace(P)))),
            "transient_dimension": 125 - int(round(np.real(np.trace(P)))),
            "omega_c": int(round(np.real(np.trace(P)))) / 125.0,
            "projector_rank": int(np.linalg.matrix_rank(P, tol=1e-8)),
            "projector_idempotence_fro": float(np.linalg.norm(P @ P - P, "fro")),
            "projector_hermiticity_fro": float(np.linalg.norm(P - P.conj().T, "fro")),
            "K_projector_fro": float(np.linalg.norm(K @ P, "fro")),
            "poly_vs_spectral_projector_fro": float(np.linalg.norm(Ppoly - P, "fro")),
            "nonzero_G_spectrum": sorted(set(np.round(nonzero_G, 6).tolist())),
            "epsilon_star": eps,
            "rho_perp_numeric": float(rho_perp),
            "rho_perp_exact_target": 15 / 17,
            "contraction_250_operator_norm": float(np.linalg.norm(R250 - P, 2)),
        },
        "qegt_softmax_check": {
            "costs": [0.2, 0.8, 1.3, -0.1],
            "beta": 1.7,
            "probabilities": qegt_gibbs([0.2, 0.8, 1.3, -0.1], beta=1.7).tolist(),
        },
        "har_demo": synthetic_har_operator_demo(),
        "boundary": (
            "No biological HAR effect size, cognition threshold, or physical "
            "quantum implementation is inferred by this script. The 47/125 "
            "quantity is the exact E47 invariant, not a fitted biological constant."
        ),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }

    checks = [
        out["e47"]["kernel_dimension"] == 47,
        abs(out["e47"]["omega_c"] - 47 / 125) < 1e-15,
        out["e47"]["projector_idempotence_fro"] < 1e-10,
        out["e47"]["K_projector_fro"] < 1e-9,
        abs(out["e47"]["rho_perp_numeric"] - 15 / 17) < 1e-12,
        out["e47"]["contraction_250_operator_norm"] < 1e-10,
        out["har_demo"]["normalization_residual"] < 1e-15,
    ]
    out["status"] = "PASS" if all(checks) else "FAIL"
    return out


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
