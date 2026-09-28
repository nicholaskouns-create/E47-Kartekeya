#!/usr/bin/env python3
"""E47 × KKP-RADAR bridge validator.

Certificate: MC-E47-RADAR-BRIDGE-20260927-001
Exact finite E47 algebra plus synthetic radar validation only.
"""

import json
import numpy as np

SEED = 470125
rng = np.random.default_rng(SEED)

def spin_two():
    m = np.arange(2, -3, -1, dtype=float)
    jz = np.diag(m).astype(complex)
    jp = np.zeros((5, 5), dtype=complex)
    for i in range(4):
        ml = m[i + 1]
        jp[i, i + 1] = np.sqrt(6 - ml * (ml + 1))
    jm = jp.conj().T
    return (jp + jm) / 2, (jp - jm) / (2j), jz

def total(a):
    I = np.eye(5, dtype=complex)
    return np.kron(np.kron(a, I), I) + np.kron(np.kron(I, a), I) + np.kron(np.kron(I, I), a)

jx, jy, jz = spin_two()
Jx, Jy, Jz = map(total, (jx, jy, jz))
I125 = np.eye(125, dtype=complex)
C = Jx @ Jx + Jy @ Jy + Jz @ Jz
evals, U = np.linalg.eigh(C)

shell_lambdas = np.array([0., 2., 6., 12., 20., 30., 42.])
shell_dims = np.array([1, 9, 25, 28, 27, 22, 13])
P_shell = []
for lam in shell_lambdas:
    ix = np.where(np.isclose(evals, lam, atol=1e-9))[0]
    P_shell.append(U[:, ix] @ U[:, ix].conj().T)

P_E = P_shell[2] + P_shell[5]
K = (C - 6 * I125) @ (C - 30 * I125)
K2 = K @ K
eps_star = 1 / 99144
T = I125 - eps_star * K2

def fro(A):
    return float(np.linalg.norm(A))

algebra = {
    "casimir_multiplicities": [int(np.sum(np.isclose(evals, x, atol=1e-9))) for x in shell_lambdas],
    "rank_P_E": int(np.linalg.matrix_rank(P_E, tol=1e-9)),
    "trace_P_E": float(np.trace(P_E).real),
    "P2_minus_P_fro": fro(P_E @ P_E - P_E),
    "Pdag_minus_P_fro": fro(P_E.conj().T - P_E),
    "K_P_fro": fro(K @ P_E),
}

k2_spec = np.linalg.eigvalsh(K2)
positive_k2 = sorted(set(np.round(k2_spec[k2_spec > 1e-6], 8)))
contraction = {
    "positive_K2_spectrum": [float(x) for x in positive_k2],
    "epsilon_star": eps_star,
    "rho_star": float(max(abs(1 - eps_star * np.array(positive_k2)))),
    "target_rho_star": 15 / 17,
}

x0 = rng.normal(size=125) + 1j * rng.normal(size=125)
xn = x0.copy()
for _ in range(220):
    xn = T @ xn
contraction["relative_error_after_220"] = float(np.linalg.norm(xn - P_E @ x0) / np.linalg.norm(x0))

def shell_profile(X):
    total_energy = np.sum(np.abs(X) ** 2, axis=1)
    cols = []
    for P in P_shell:
        Y = X @ P.T
        cols.append(np.sum(np.abs(Y) ** 2, axis=1) / total_energy)
    return np.stack(cols, axis=1)

NNULL = 10000
Xnull = (rng.normal(size=(NNULL, 125)) + 1j * rng.normal(size=(NNULL, 125))) / np.sqrt(2)
Qnull = shell_profile(Xnull)
eta = Qnull[:, 2] + Qnull[:, 5]
null_test = {
    "theoretical_mean": 47 / 125,
    "monte_carlo_mean": float(eta.mean()),
    "monte_carlo_sd": float(eta.std(ddof=1)),
    "absolute_mean_error": float(abs(eta.mean() - 47 / 125)),
}

NCAL = 6000
Xcal = (rng.normal(size=(NCAL, 125)) + 1j * rng.normal(size=(NCAL, 125))) / np.sqrt(2)
Qcal = shell_profile(Xcal)
mu = Qcal.mean(axis=0)
cov_inv = np.linalg.pinv(np.cov(Qcal, rowvar=False), rcond=1e-10)

def shell_score(Q):
    D = Q - mu
    return np.einsum("bi,ij,bj->b", D, cov_inv, D)

def auc(y, score):
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    n1 = int(np.sum(y))
    n0 = len(y) - n1
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

g = np.arange(-2, 3, dtype=float)
A, R, TT = np.meshgrid(g, g, g, indexing="ij")

def make_targets(n):
    out = np.empty((n, 125), dtype=complex)
    for i in range(n):
        k = rng.uniform(-2.2, 2.2, size=3)
        sig = rng.uniform(0.6, 1.5, size=3)
        ctr = rng.uniform(-0.5, 0.5, size=3)
        amp = np.exp(-0.5 * (((A-ctr[0])/sig[0])**2 + ((R-ctr[1])/sig[1])**2 + ((TT-ctr[2])/sig[2])**2))
        phase = np.exp(1j * (k[0]*A + k[1]*R + k[2]*TT))
        v = (amp * phase).reshape(-1)
        out[i] = v / np.linalg.norm(v)
    return out

NTEST = 2000
noise0 = (rng.normal(size=(NTEST, 125)) + 1j * rng.normal(size=(NTEST, 125))) / np.sqrt(2)
Q0 = shell_profile(noise0)
S0 = shell_score(Q0)
eta0 = Q0[:, 2] + Q0[:, 5]
target = make_targets(NTEST)

bench = []
for snr_db in (-10, -5, 0, 5):
    noise1 = (rng.normal(size=(NTEST, 125)) + 1j * rng.normal(size=(NTEST, 125))) / np.sqrt(2)
    X1 = noise1 + np.sqrt(125 * 10 ** (snr_db / 10)) * target
    Q1 = shell_profile(X1)
    S1 = shell_score(Q1)
    eta1 = Q1[:, 2] + Q1[:, 5]
    y = np.r_[np.zeros(NTEST, dtype=int), np.ones(NTEST, dtype=int)]
    bench.append({
        "snr_db": snr_db,
        "auc_full_7_shell_profile": auc(y, np.r_[S0, S1]),
        "auc_abs_E47_occupancy_deviation": auc(y, np.r_[np.abs(eta0-47/125), np.abs(eta1-47/125)]),
        "mean_eta_E_target_plus_noise": float(eta1.mean()),
    })

passed = (
    algebra["casimir_multiplicities"] == shell_dims.tolist()
    and algebra["rank_P_E"] == 47
    and algebra["P2_minus_P_fro"] < 1e-10
    and algebra["K_P_fro"] < 1e-9
    and abs(contraction["rho_star"] - 15/17) < 1e-12
    and contraction["relative_error_after_220"] < 1e-10
    and null_test["absolute_mean_error"] < 0.002
)

certificate = {
    "certificate": "MC-E47-RADAR-BRIDGE-20260927-001",
    "status": "PASS" if passed else "FAIL",
    "evidence": {
        "algebra": "exact identities checked numerically",
        "radar_bridge": "synthetic numerical validation only",
        "measured_radar": "not tested"
    },
    "bridge": {
        "input": "calibrated/whitened 5x5x5 complex I/Q patch",
        "carrier": "V_2^{⊗3} ≅ C^125",
        "kernel": "K=(C-6I)(C-30I)",
        "projector": "P_E=P_6+P_30, rank 47",
        "E47_occupancy": "eta_E=||P_E x||^2/||x||^2",
        "shell_profile": "q_j=||P_j x||^2/||x||^2, j=0,...,6"
    },
    "algebra": algebra,
    "contraction": contraction,
    "isotropic_null": null_test,
    "synthetic_benchmark": bench,
}
print(json.dumps(certificate, indent=2))
