#!/usr/bin/env python3
r"""Standalone E47 finite spectral constant/invariant validator.

Reconstructs the spin-2 SU(2) tensor cube V_2^{\otimes 3}, its total Casimir,
K=(C-6I)(C-30I), the rank-47 projector P, and the minimax contraction
Gamma = I - epsilon_* K^2.

Requires: numpy, pandas
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd


def kron3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.kron(np.kron(a, b), c)


def build_spin2_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    j = 2
    m = np.arange(j, -j - 1, -1)
    d = 2 * j + 1

    jz = np.diag(m).astype(complex)
    jp = np.zeros((d, d), dtype=complex)
    for i in range(d - 1):
        mm = m[i + 1]
        jp[i, i + 1] = np.sqrt(j * (j + 1) - mm * (mm + 1))

    jm = jp.conj().T
    jx = (jp + jm) / 2
    jy = (jp - jm) / (2j)
    return jx, jy, jz


def validate() -> tuple[pd.DataFrame, dict[str, object]]:
    jx, jy, jz = build_spin2_generators()
    i5 = np.eye(5)

    jx_tot = kron3(jx, i5, i5) + kron3(i5, jx, i5) + kron3(i5, i5, jx)
    jy_tot = kron3(jy, i5, i5) + kron3(i5, jy, i5) + kron3(i5, i5, jy)
    jz_tot = kron3(jz, i5, i5) + kron3(i5, jz, i5) + kron3(i5, i5, jz)

    c = jx_tot @ jx_tot + jy_tot @ jy_tot + jz_tot @ jz_tot
    n = c.shape[0]
    identity = np.eye(n)

    evals = np.linalg.eigvalsh(c).real
    rounded = np.rint(evals).astype(int)
    spectrum, multiplicities = np.unique(rounded, return_counts=True)

    mu = np.trace(c).real / n
    tau = np.trace(c @ c).real / n
    variance = tau - mu**2
    sigma = np.sqrt(variance)

    k = (c - 6 * identity) @ (c - 30 * identity)
    rank_k = np.linalg.matrix_rank(k, tol=1e-6)
    nullity_k = n - rank_k
    k_sector_values = [(int(lam), int((lam - 6) * (lam - 30))) for lam in spectrum]

    w, vecs = np.linalg.eigh(c)
    mask = np.isclose(w, 6, atol=1e-10) | np.isclose(w, 30, atol=1e-10)
    q = vecs[:, mask]
    p = q @ q.conj().T

    rank_p = np.linalg.matrix_rank(p, tol=1e-8)
    trace_p = np.trace(p).real
    p_idempotence = np.linalg.norm(p @ p - p)
    p_hermiticity = np.linalg.norm(p.conj().T - p)
    kp_residual = np.linalg.norm(k @ p)

    h = k @ k
    h_eigs = np.linalg.eigvalsh(h).real
    h_spectrum = np.unique(np.rint(h_eigs).astype(int))
    positive_h = h_spectrum[h_spectrum > 0]

    delta = int(positive_h.min())
    h_norm = int(positive_h.max())
    k_norm = int(round(np.max(np.abs(np.linalg.eigvalsh(k).real))))

    epsilon = 2 / (delta + h_norm)
    epsilon_exact = Fraction(2, delta + h_norm)
    rho = (h_norm - delta) / (h_norm + delta)
    rho_exact = Fraction(h_norm - delta, h_norm + delta)

    gamma = identity - epsilon * h
    gamma_eigs = np.linalg.eigvalsh(gamma).real
    rho_numeric = max(abs(x) for x in gamma_eigs if abs(x - 1) > 1e-10)

    iterations = 252
    gamma_252 = np.linalg.matrix_power(gamma, iterations)
    gamma_252_error = np.linalg.norm(gamma_252 - p, 2)
    theoretical_bound = rho**iterations

    checks = [
        ("Ambient dimension N", n, 125, n == 125),
        ("Kernel dimension", nullity_k, 47, nullity_k == 47),
        ("Complement dimension", rank_k, 78, rank_k == 78),
        ("Omega_c", nullity_k / n, 47 / 125, np.isclose(nullity_k / n, 47 / 125)),
        ("mu", mu, 18, np.isclose(mu, 18)),
        ("sigma", sigma, 12, np.isclose(sigma, 12)),
        ("lambda_-", mu - sigma, 6, np.isclose(mu - sigma, 6)),
        ("lambda_+", mu + sigma, 30, np.isclose(mu + sigma, 30)),
        ("||K||_2", k_norm, 432, k_norm == 432),
        ("Delta = min nonzero eig(K^2)", delta, 11664, delta == 11664),
        ("||K^2||_2", h_norm, 186624, h_norm == 186624),
        ("epsilon_*", epsilon, 1 / 99144, np.isclose(epsilon, 1 / 99144)),
        ("rho_*", rho, 15 / 17, np.isclose(rho, 15 / 17)),
        ("rank(P)", rank_p, 47, rank_p == 47),
        ("tr(P)", trace_p, 47, np.isclose(trace_p, 47)),
        ("P^2=P residual", p_idempotence, 0.0, p_idempotence < 1e-12),
        ("P^†=P residual", p_hermiticity, 0.0, p_hermiticity < 1e-12),
        ("KP=0 residual", kp_residual, 0.0, kp_residual < 1e-10),
        ("rho from Gamma spectrum", rho_numeric, 15 / 17, np.isclose(rho_numeric, 15 / 17)),
    ]

    df = pd.DataFrame(checks, columns=["Quantity", "Computed", "Expected", "PASS"])
    summary: dict[str, object] = {
        "casimir_spectrum": spectrum.tolist(),
        "multiplicities": multiplicities.tolist(),
        "k_sector_values": k_sector_values,
        "k2_spectrum": h_spectrum.tolist(),
        "epsilon_star_exact": str(epsilon_exact),
        "rho_star_exact": str(rho_exact),
        "gamma252_minus_p_op": float(gamma_252_error),
        "theoretical_bound_252": float(theoretical_bound),
        "pass_count": int(df["PASS"].sum()),
        "fail_count": int((~df["PASS"]).sum()),
        "all_pass": bool(df["PASS"].all()),
    }
    return df, summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, help="Optional path for the validation table CSV")
    args = parser.parse_args()

    df, summary = validate()
    print(df.to_string(index=False))
    print()
    for key, value in summary.items():
        print(f"{key}: {value}")

    if args.csv:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(args.csv, index=False)
        print(f"csv: {args.csv}")

    return 0 if summary["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
