import numpy as np
from fractions import Fraction
import pandas as pd
from caas_jupyter_tools import display_dataframe_to_user

# -----------------------------
# 1. Spin-2 su(2) generators
# -----------------------------
j = 2
m = np.arange(j, -j - 1, -1)
d = 2*j + 1

Jz = np.diag(m).astype(complex)
Jp = np.zeros((d, d), dtype=complex)

for i in range(d - 1):
    mm = m[i + 1]
    Jp[i, i + 1] = np.sqrt(j*(j+1) - mm*(mm+1))

Jm = Jp.conj().T
Jx = (Jp + Jm)/2
Jy = (Jp - Jm)/(2j)
I5 = np.eye(5)

def kron3(A, B, C):
    return np.kron(np.kron(A, B), C)

# -----------------------------
# 2. Total Casimir on V2^⊗3
# -----------------------------
Jx_tot = kron3(Jx,I5,I5) + kron3(I5,Jx,I5) + kron3(I5,I5,Jx)
Jy_tot = kron3(Jy,I5,I5) + kron3(I5,Jy,I5) + kron3(I5,I5,Jy)
Jz_tot = kron3(Jz,I5,I5) + kron3(I5,Jz,I5) + kron3(I5,I5,Jz)

C = Jx_tot @ Jx_tot + Jy_tot @ Jy_tot + Jz_tot @ Jz_tot
N = C.shape[0]

evals = np.linalg.eigvalsh(C).real
rounded = np.rint(evals).astype(int)
spec, mult = np.unique(rounded, return_counts=True)

# -----------------------------
# 3. Spectral moments
# -----------------------------
mu = np.trace(C).real / N
tau = np.trace(C @ C).real / N
var = tau - mu**2
sigma = np.sqrt(var)

# -----------------------------
# 4. Kernel operator
# -----------------------------
I = np.eye(N)
K = (C - 6*I) @ (C - 30*I)
rankK = np.linalg.matrix_rank(K, tol=1e-6)
nullK = N - rankK

# K sector values from polynomial
K_sector = [(int(lam), int((lam-6)*(lam-30))) for lam in spec]

# -----------------------------
# 5. Projector
# -----------------------------
w, V = np.linalg.eigh(C)
mask = np.isclose(w, 6, atol=1e-10) | np.isclose(w, 30, atol=1e-10)
Q = V[:, mask]
P = Q @ Q.conj().T

rankP = np.linalg.matrix_rank(P, tol=1e-8)
trP = np.trace(P).real
proj_idem = np.linalg.norm(P@P - P)
proj_herm = np.linalg.norm(P.conj().T - P)
KP = np.linalg.norm(K @ P)

# -----------------------------
# 6. K^2, gap, norms
# -----------------------------
H = K @ K
H_eigs = np.linalg.eigvalsh(H).real
H_unique = np.unique(np.rint(H_eigs).astype(int))
positive_H = H_unique[H_unique > 0]

Delta = int(positive_H.min())
Hnorm = int(positive_H.max())
Knorm = int(round(np.max(np.abs(np.linalg.eigvalsh(K).real))))

# -----------------------------
# 7. Optimal contraction
# -----------------------------
epsilon = 2 / (Delta + Hnorm)
epsilon_frac = Fraction(2, Delta + Hnorm)
rho = (Hnorm - Delta) / (Hnorm + Delta)
rho_frac = Fraction(Hnorm - Delta, Hnorm + Delta)

Gamma = I - epsilon * H
gamma_eigs = np.linalg.eigvalsh(Gamma).real
rho_num = max(abs(x) for x in gamma_eigs if abs(x-1) > 1e-10)

# -----------------------------
# 8. Convergence law
# -----------------------------
n = 252
G252 = np.linalg.matrix_power(Gamma, n)
err_op = np.linalg.norm(G252 - P, 2)
theory = rho**n

# -----------------------------
# 9. Claimed constants / checks
# -----------------------------
checks = [
    ("Ambient dimension N", N, 125, N == 125),
    ("Kernel dimension", nullK, 47, nullK == 47),
    ("Complement dimension", rankK, 78, rankK == 78),
    ("Omega_c", nullK/N, 47/125, np.isclose(nullK/N, 47/125)),
    ("mu", mu, 18, np.isclose(mu, 18)),
    ("sigma", sigma, 12, np.isclose(sigma, 12)),
    ("lambda_-", mu-sigma, 6, np.isclose(mu-sigma, 6)),
    ("lambda_+", mu+sigma, 30, np.isclose(mu+sigma, 30)),
    ("||K||_2", Knorm, 432, Knorm == 432),
    ("Delta = min nonzero eig(K^2)", Delta, 11664, Delta == 11664),
    ("||K^2||_2", Hnorm, 186624, Hnorm == 186624),
    ("epsilon_*", epsilon, 1/99144, np.isclose(epsilon, 1/99144)),
    ("rho_*", rho, 15/17, np.isclose(rho, 15/17)),
    ("rank(P)", rankP, 47, rankP == 47),
    ("tr(P)", trP, 47, np.isclose(trP, 47)),
    ("P^2=P residual", proj_idem, 0.0, proj_idem < 1e-12),
    ("P†=P residual", proj_herm, 0.0, proj_herm < 1e-12),
    ("KP=0 residual", KP, 0.0, KP < 1e-10),
    ("rho from Gamma spectrum", rho_num, 15/17, np.isclose(rho_num, 15/17)),
]

df = pd.DataFrame(checks, columns=["Quantity", "Computed", "Expected", "PASS"])
display_dataframe_to_user("E47 constant validation", df)

print("Casimir spectrum:", spec.tolist())
print("Multiplicities:", mult.tolist())
print("K sector values:", K_sector)
print("K^2 spectrum:", H_unique.tolist())
print("epsilon_* exact:", epsilon_frac)
print("rho_* exact:", rho_frac)
print("||Gamma^252 - P||_2 =", err_op)
print("(15/17)^252 =", theory)
print("All checks pass:", bool(df["PASS"].all()))
