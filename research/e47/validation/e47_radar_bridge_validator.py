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

CONTROL_SEED = 470126
N_RANDOM_SPLITS = 5
control_rng = np.random.default_rng(CONTROL_SEED)
random_controls = []
for _ in range(N_RANDOM_SPLITS):
    Z = (
        control_rng.normal(size=(125, 125))
        + 1j * control_rng.normal(size=(125, 125))
    ) / np.sqrt(2)
    basis, R = np.linalg.qr(Z)
    phases = np.diag(R)
    phases = np.where(np.abs(phases) > 0, phases / np.abs(phases), 1.0)
    basis = basis * phases.conj()[None, :]
    Qc = random_split_profile(Xcal, basis)
    muc = Qc.mean(axis=0)
    cinv = np.linalg.pinv(np.cov(Qc, rowvar=False), rcond=1e-10)
    random_controls.append((basis, muc, cinv))

def random_shell_score(Q, muc, cinv):
    D = Q - muc
    return np.einsum("bi,ij,bj->b", D, cinv, D)

def auc(y, score):
    order = np.argsort(score)
    ranks = np.empty_like(order, dtype=float)
    ranks[order] = np.arange(1, len(score) + 1)
    n1 = int(np.sum(y))
    n0 = len(y) - n1
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def fft_peak_score(X):
    """Maximum 3-D FFT-bin power divided by total FFT power."""
    F = np.fft.fftn(X.reshape(-1, 5, 5, 5), axes=(1, 2, 3))
    power = np.abs(F) ** 2
    power = power.reshape(len(X), -1)
    return power.max(axis=1) / power.sum(axis=1)

def random_split_profile(X, basis, dims=shell_dims):
    """Energy fractions in a random orthonormal basis with the Casimir shell sizes."""
    Z = X @ basis.conj()
    energy = np.abs(Z) ** 2
    total_energy = energy.sum(axis=1)
    starts = np.cumsum(np.r_[0, dims[:-1]])
    return np.stack(
        [energy[:, start:start + dim].sum(axis=1) / total_energy
         for start, dim in zip(starts, dims)],
        axis=1,
    )

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
fft0 = fft_peak_score(noise0)
random0 = []
for basis, muc, cinv in random_controls:
    Qr0 = random_split_profile(noise0, basis)
    random0.append(random_shell_score(Qr0, muc, cinv))
target = make_targets(NTEST)

bench = []
for snr_db in (-10, -5, 0, 5):
    noise1 = (rng.normal(size=(NTEST, 125)) + 1j * rng.normal(size=(NTEST, 125))) / np.sqrt(2)
    X1 = noise1 + np.sqrt(125 * 10 ** (snr_db / 10)) * target
    Q1 = shell_profile(X1)
    S1 = shell_score(Q1)
    eta1 = Q1[:, 2] + Q1[:, 5]
    fft1 = fft_peak_score(X1)
    y = np.r_[np.zeros(NTEST, dtype=int), np.ones(NTEST, dtype=int)]
    random_aucs = []
    for (basis, muc, cinv), sr0 in zip(random_controls, random0):
        Qr1 = random_split_profile(X1, basis)
        sr1 = random_shell_score(Qr1, muc, cinv)
        random_aucs.append(auc(y, np.r_[sr0, sr1]))
    bench.append({
        "snr_db": snr_db,
        "auc_full_7_shell_profile": auc(y, np.r_[S0, S1]),
        "auc_abs_E47_occupancy_deviation": auc(y, np.r_[np.abs(eta0-47/125), np.abs(eta1-47/125)]),
        "auc_fft_peak_over_total_energy": auc(y, np.r_[fft0, fft1]),
        "auc_random_same_size_splits": random_aucs,
        "random_same_size_auc_min": float(min(random_aucs)),
        "random_same_size_auc_max": float(max(random_aucs)),
        "mean_eta_E_target_plus_noise": float(eta1.mean()),
    })

random_control_max_deviation = max(
    abs(v - 0.5)
    for row in bench
    for v in row["auc_random_same_size_splits"]
)
fft_beats_casimir_all_snr = all(
    row["auc_fft_peak_over_total_energy"] > row["auc_full_7_shell_profile"]
    for row in bench
)
casimir_beats_random_max_all_snr = all(
    row["auc_full_7_shell_profile"] > row["random_same_size_auc_max"]
    for row in bench
)

passed = (
    algebra["casimir_multiplicities"] == shell_dims.tolist()
    and algebra["rank_P_E"] == 47
    and algebra["P2_minus_P_fro"] < 1e-10
    and algebra["K_P_fro"] < 1e-9
    and abs(contraction["rho_star"] - 15/17) < 1e-12
    and contraction["relative_error_after_220"] < 1e-10
    and null_test["absolute_mean_error"] < 0.002
    and random_control_max_deviation < 0.04
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
    "controls": {
        "random_same_size_splits": {
            "draws": N_RANDOM_SPLITS,
            "seed": CONTROL_SEED,
            "dimensions": shell_dims.tolist(),
            "construction": "Haar-random complex orthonormal basis, contiguous groups with Casimir shell sizes",
            "max_auc_deviation_from_chance": float(random_control_max_deviation),
        },
        "fft_peak_over_total_energy": {
            "definition": "max(|FFT3(X)|^2) / sum(|FFT3(X)|^2)",
            "kind": "standard spectral peak-to-total-energy baseline; CFAR-style statistic, not a full operational CFAR detector",
        },
        "comparative_result": {
            "casimir_beats_random_same_size_max_at_every_snr": bool(casimir_beats_random_max_all_snr),
            "fft_beats_casimir_at_every_snr": bool(fft_beats_casimir_all_snr),
        },
    },
    "synthetic_benchmark": bench,
}
print(json.dumps(certificate, indent=2))
if not passed:
    raise SystemExit(1)
