"""
E47 / Invariant-Grammar validation — built from scratch.
Nothing is hard-coded: C is assembled from su(2) generators, and every
claimed number (125, 78, 47, 25+22, projector norms, Omega_c, the gap)
is DERIVED and checked. Run with: python e47_validation.py
Requires only numpy.
"""
import numpy as np

# ---------- 1. Spin-2 su(2) generators (j = 2, dim 5) ----------
j = 2
m = np.arange(j, -j - 1, -1)            # [2,1,0,-1,-2]
d = 2 * j + 1                           # 5
Jz = np.diag(m).astype(complex)
# J+ raising: <m+1|J+|m> = sqrt(j(j+1) - m(m+1))
Jp = np.zeros((d, d), complex)
for i in range(d - 1):
    mm = m[i + 1]                       # lower m that gets raised
    Jp[i, i + 1] = np.sqrt(j * (j + 1) - mm * (mm + 1))
Jm = Jp.conj().T
Jx = (Jp + Jm) / 2
Jy = (Jp - Jm) / (2j)

# sanity: single-site Casimir = j(j+1) I = 6 I
C1 = Jx @ Jx + Jy @ Jy + Jz @ Jz
assert np.allclose(C1, 6 * np.eye(d)), "single-site Casimir wrong"

I5 = np.eye(d)
def kron3(A, B, Cc): return np.kron(np.kron(A, B), Cc)

# ---------- 2. Total generators on V2 tensor V2 tensor V2 (dim 125) ----------
Jx_t = kron3(Jx, I5, I5) + kron3(I5, Jx, I5) + kron3(I5, I5, Jx)
Jy_t = kron3(Jy, I5, I5) + kron3(I5, Jy, I5) + kron3(I5, I5, Jy)
Jz_t = kron3(Jz, I5, I5) + kron3(I5, Jz, I5) + kron3(I5, I5, Jz)
C = Jx_t @ Jx_t + Jy_t @ Jy_t + Jz_t @ Jz_t
N = C.shape[0]
print(f"dim Sigma (V2^tensor3)        : {N}   (expect 125)")

# C must be Hermitian and commute with total generators
print(f"C Hermitian                   : {np.allclose(C, C.conj().T)}")
print(f"[C, Jz_tot] = 0               : {np.allclose(C@Jz_t - Jz_t@C, 0, atol=1e-9)}")

# ---------- 3. Spectrum, traces, moments ----------
evals = np.linalg.eigvalsh(C).real
# round to nearest integer eigenvalue for counting (J(J+1) are integers)
ev_round = np.round(evals).astype(int)
uniq, counts = np.unique(ev_round, return_counts=True)
print("\nCasimir eigenvalues  J(J+1)   count")
for v, c in zip(uniq, counts):
    print(f"   lambda = {v:3d}                {c:3d}")

trC  = np.trace(C).real
trC2 = np.trace(C @ C).real
mu   = trC / N
tau  = trC2 / N
var  = tau - mu**2
sig  = np.sqrt(var)
print(f"\nTr(C)={trC:.1f}  Tr(C^2)={trC2:.1f}")
print(f"mu = tau(C)                   : {mu:.4f}   (expect 18)")
print(f"tau(C^2)                      : {tau:.4f}   (expect 468)")
print(f"sigma^2                       : {var:.4f}   (expect 144)")
print(f"sigma                         : {sig:.4f}   (expect 12)")
print(f"mu^2 + sigma^2 == tau(C^2)    : {np.isclose(mu**2+var, tau)}")
print(f"roots mu +/- sigma            : {mu-sig:.1f}, {mu+sig:.1f}   (expect 6, 30)")

# ---------- 4. Kernel filter K = (C - 6I)(C - 30I) ----------
K = (C - 6*np.eye(N)) @ (C - 30*np.eye(N))
rankK = np.linalg.matrix_rank(K, tol=1e-6)
nullK = N - rankK
print(f"\nrank K                        : {rankK}   (expect 78)")
print(f"nullity K (dim Psi)           : {nullK}   (expect 47)")

# kernel split: count states at lambda=6 (J=2) and lambda=30 (J=5)
n6  = counts[list(uniq).index(6)]  if 6  in uniq else 0
n30 = counts[list(uniq).index(30)] if 30 in uniq else 0
print(f"kernel split 25 + 22          : {n6} + {n30} = {n6+n30}")

# ---------- 5. Spectral projector onto ker K ----------
w, Vv = np.linalg.eigh(C)
mask = (np.abs(np.round(w) - 6) < 1e-6) | (np.abs(np.round(w) - 30) < 1e-6)
Q = Vv[:, mask]
P = (Q @ Q.conj().T).real
print(f"\n||P^2 - P||                   : {np.linalg.norm(P@P - P):.2e}")
print(f"||P - P^H||                   : {np.linalg.norm(P - P.conj().T):.2e}")
print(f"||P K||  (Plate V closure)    : {np.linalg.norm(P @ K):.2e}")
print(f"||K P||                       : {np.linalg.norm(K @ P):.2e}")
print(f"tr(P)                         : {np.trace(P):.4f}   (expect 47)")

# ---------- 6. Omega_c ----------
omega_theory = np.trace(P).real / N
print(f"\nOmega_c = tr(P)/125           : {omega_theory:.6f}   (expect 0.376 = 47/125)")
print(f"47/125 exactly                : {47/125:.6f}")

# empirical mean coherence over random vectors
rng = np.random.default_rng(0)
vals = []
for _ in range(50000):
    x = rng.standard_normal(N)
    vals.append((np.linalg.norm(P @ x)**2) / (np.linalg.norm(x)**2))
print(f"empirical E[Omega], 50k draws : {np.mean(vals):.6f}   (Monte-Carlo ~ 47/125)")

# ---------- 7. Contraction Gamma = I - eps K^dag K  ->  P ----------
KK = K.conj().T @ K
eps = 1.0 / np.linalg.norm(KK, 2)      # safely inside (0, 2/lambda_max)
G = np.eye(N) - eps * KK
Gn = np.linalg.matrix_power(G, 400)
print(f"\n||Gamma^400 - P||             : {np.linalg.norm(Gn - P):.2e}   (-> 0 confirms lock)")

# ---------- 8. Gap: first positive eigenvalue of H = K^2 ----------
Hdiag = np.round(np.unique(ev_round))
Kvals = (Hdiag - 6) * (Hdiag - 30)
Hvals = Kvals**2
posH = sorted(v for v in Hvals if v > 1e-6)
print(f"\nfirst positive H=K^2 level    : {posH[0]:.0f}   (expect 11664 = 108^2)")
print(f"108^2                         : {108**2}")

