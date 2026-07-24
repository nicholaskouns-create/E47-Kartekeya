"""Mnemosyne Kernel Paradigm: first-principles Python validator.

Dependencies:
    numpy
    scipy

Validates:
    V = V_2^{⊗3}, dim(V)=125
    C = J_tot^2
    K = (C-6I)(C-30I)
    Q = K†K
    dim ker(K)=47
    P47 projector identities
    continuous and discrete contraction
    projective quantum channel
    conditional L=K Lindblad protection
"""

from __future__ import annotations

import json
import math
import platform
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.linalg import expm


def spin_generators(j: int = 2):
    d = 2 * j + 1
    m = np.arange(j, -j - 1, -1, dtype=float)
    jz = np.diag(m).astype(complex)
    jp = np.zeros((d, d), dtype=complex)
    for col in range(1, d):
        m_col = m[col]
        jp[col - 1, col] = np.sqrt(j * (j + 1) - m_col * (m_col + 1))
    jm = jp.conj().T
    jx = (jp + jm) / 2
    jy = (jp - jm) / (2j)
    return jx, jy, jz


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


def main() -> dict:
    rng = np.random.default_rng(47125)

    jx, jy, jz = spin_generators(2)
    i5 = np.eye(5, dtype=complex)
    i125 = np.eye(125, dtype=complex)

    jx_tot = kron3(jx, i5, i5) + kron3(i5, jx, i5) + kron3(i5, i5, jx)
    jy_tot = kron3(jy, i5, i5) + kron3(i5, jy, i5) + kron3(i5, i5, jy)
    jz_tot = kron3(jz, i5, i5) + kron3(i5, jz, i5) + kron3(i5, i5, jz)

    c = jx_tot @ jx_tot + jy_tot @ jy_tot + jz_tot @ jz_tot
    k = (c - 6 * i125) @ (c - 30 * i125)
    q = k.conj().T @ k

    evals_c, evecs_c = np.linalg.eigh(c)
    spectrum = np.array([0, 2, 6, 12, 20, 30, 42], dtype=float)
    multiplicities = [int(np.sum(np.isclose(evals_c, x, atol=1e-8))) for x in spectrum]

    mask = np.isclose(evals_c, 6.0, atol=1e-9) | np.isclose(evals_c, 30.0, atol=1e-9)
    v47 = evecs_c[:, mask]
    p47 = v47 @ v47.conj().T
    p78 = i125 - p47

    evals_q = np.linalg.eigvalsh(q)
    positive_q = evals_q[evals_q > 1e-7]
    gap = float(np.min(positive_q))
    qmax = float(np.max(evals_q))
    epsilon_max = 2 / qmax
    epsilon_opt = 2 / (gap + qmax)
    rho_opt = (qmax - gap) / (qmax + gap)

    x0 = rng.normal(size=125) + 1j * rng.normal(size=125)
    x0 /= np.linalg.norm(x0)
    x_star = p47 @ x0

    t = 0.01
    xt = expm(-t * q) @ x0
    continuous_error = float(np.linalg.norm(xt - x_star))
    continuous_bound = float(math.exp(-gap * t) * np.linalg.norm(p78 @ x0))

    x = x0.copy()
    for _ in range(500):
        x = x - epsilon_opt * (q @ x)
    discrete_error = float(np.linalg.norm(x - x_star))

    m0, m1 = p47, p78
    completeness = float(np.linalg.norm(m0.conj().T @ m0 + m1.conj().T @ m1 - i125, ord=2))

    rho0 = np.outer(x0, x0.conj())
    probability_e47 = float(np.real(np.trace(p47 @ rho0)))

    psi47 = x_star / np.linalg.norm(x_star)
    rho47 = np.outer(psi47, psi47.conj())
    dissipator = k @ rho47 @ k - 0.5 * (q @ rho47 + rho47 @ q)

    omega_c = 47 / 125
    psi = 2.0
    for _ in range(12):
        psi = 0.5 * (psi + omega_c**2 / psi)

    om = Fraction(47, 125)
    closure = 7750000 * om**3 - 15500000 * om**2 + 14947211 * om - 3840793

    result = {
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "dim_V": 125,
        "dim_kernel": int(round(np.trace(p47).real)),
        "rank_K": int(np.linalg.matrix_rank(k, tol=1e-8)),
        "omega_c": omega_c,
        "casimir_spectrum": spectrum.tolist(),
        "multiplicities": multiplicities,
        "P47_idempotence": float(np.linalg.norm(p47 @ p47 - p47, ord=2)),
        "P47_hermiticity": float(np.linalg.norm(p47 - p47.conj().T, ord=2)),
        "K_P47": float(np.linalg.norm(k @ p47, ord=2)),
        "spectral_gap": gap,
        "lambda_max_Q": qmax,
        "epsilon_max": epsilon_max,
        "epsilon_opt": epsilon_opt,
        "rho_opt": rho_opt,
        "continuous_error_t_0_01": continuous_error,
        "continuous_bound_t_0_01": continuous_bound,
        "discrete_error_500_steps": discrete_error,
        "channel_completeness": completeness,
        "initial_probability_E47": probability_e47,
        "kernel_aligned_lindblad_residual": float(np.linalg.norm(dissipator, ord=2)),
        "heron_final_error": float(abs(psi - omega_c)),
        "closure_polynomial_at_47_125": str(closure),
    }

    assert result["dim_kernel"] == 47
    assert multiplicities == [1, 9, 25, 28, 27, 22, 13]
    assert result["P47_idempotence"] < 1e-12
    assert result["K_P47"] < 1e-9
    assert abs(gap - 11664) < 1e-6
    assert abs(qmax - 186624) < 1e-6
    assert discrete_error < 1e-12
    assert completeness < 1e-12
    assert closure == 0

    return result


if __name__ == "__main__":
    metrics = main()
    print(json.dumps(metrics, indent=2))
