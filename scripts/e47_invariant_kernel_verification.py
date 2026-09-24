"""
E47 invariant-kernel verification
Full end-to-end validation:
1. Build spin-2 su(2) generators
2. Build total Casimir on V2⊗V2⊗V2
3. Verify spectrum and moments
4. Build K=(C-6I)(C-30I)
5. Construct E47 projector P
6. Build contraction operator
       Γ = I - K²/99144
7. Apply Γ exactly 252 times by matrix multiplication
8. Compare Γ^252 against projector P
9. Measure random-state residual collapse

Requires: numpy only
"""

import numpy as np

# ============================================================
# 1. Spin-2 su(2) generators
# ============================================================

j = 2
m = np.arange(j, -j - 1, -1)
d = 2 * j + 1

Jz = np.diag(m).astype(complex)

Jp = np.zeros((d, d), dtype=complex)
for i in range(d - 1):
    mm = m[i + 1]
    Jp[i, i + 1] = np.sqrt(j * (j + 1) - mm * (mm + 1))

Jm = Jp.conj().T

Jx = (Jp + Jm) / 2
Jy = (Jp - Jm) / (2j)

C_single = Jx @ Jx + Jy @ Jy + Jz @ Jz

print("single-site Casimir check:")
print(np.allclose(C_single, 6 * np.eye(d)))

I5 = np.eye(5)


def kron3(A, B, C):
    return np.kron(np.kron(A, B), C)


# ============================================================
# 2. Total generators on V2⊗V2⊗V2
# ============================================================

Jx_tot = (
    kron3(Jx, I5, I5)
    + kron3(I5, Jx, I5)
    + kron3(I5, I5, Jx)
)

Jy_tot = (
    kron3(Jy, I5, I5)
    + kron3(I5, Jy, I5)
    + kron3(I5, I5, Jy)
)

Jz_tot = (
    kron3(Jz, I5, I5)
    + kron3(I5, Jz, I5)
    + kron3(I5, I5, Jz)
)

C = (
    Jx_tot @ Jx_tot
    + Jy_tot @ Jy_tot
    + Jz_tot @ Jz_tot
)

N = C.shape[0]

print("\nambient dimension")
print(N)

# ============================================================
# 3. Spectrum and moments
# ============================================================

evals = np.linalg.eigvalsh(C).real
ev_round = np.round(evals).astype(int)

uniq, counts = np.unique(ev_round, return_counts=True)

print("\nCasimir spectrum")
for lam, mult in zip(uniq, counts):
    print(f"lambda={lam:2d} multiplicity={mult}")

trC = np.trace(C).real
trC2 = np.trace(C @ C).real

mu = trC / N
tau = trC2 / N
var = tau - mu ** 2
sigma = np.sqrt(var)

print("\nMoments")
print("mu       =", mu)
print("tau      =", tau)
print("var      =", var)
print("sigma    =", sigma)
print("mu-sigma =", mu - sigma)
print("mu+sigma =", mu + sigma)

# ============================================================
# 4. Kernel operator
# ============================================================

K = (
    (C - 6 * np.eye(N))
    @
    (C - 30 * np.eye(N))
)

rankK = np.linalg.matrix_rank(K, tol=1e-6)
nullK = N - rankK

print("\nKernel")
print("rank(K)    =", rankK)
print("nullity(K) =", nullK)

# ============================================================
# 5. Projector onto E47
# ============================================================

w, V = np.linalg.eigh(C)

mask = (
    (np.round(w) == 6)
    |
    (np.round(w) == 30)
)

Q = V[:, mask]
P = Q @ Q.conj().T

print("\nProjector checks")
print("tr(P) =", np.trace(P).real)
print("||P²-P|| =", np.linalg.norm(P @ P - P))
print("||PK|| =", np.linalg.norm(P @ K))

# ============================================================
# 6. K² spectrum
# ============================================================

H = K @ K

H_eigs = np.linalg.eigvalsh(H).real
H_round = np.round(H_eigs).astype(int)

H_unique = sorted(set(H_round))

print("\nK² spectrum")
print(H_unique)

# ============================================================
# 7. Contraction operator
# ============================================================

Gamma = np.eye(N) - H / 99144.0

Gamma_eigs = np.linalg.eigvalsh(Gamma).real

print("\nGamma eigenvalue range")
print("min =", Gamma_eigs.min())
print("max =", Gamma_eigs.max())

rho_off_kernel = max(
    abs(x)
    for x in Gamma_eigs
    if abs(x - 1.0) > 1e-12
)

print("rho =", rho_off_kernel)
print("15/17 =", 15 / 17)

# ============================================================
# 8. EXACT 252-step multiplication
# ============================================================

G = np.eye(N)

for _ in range(252):
    G = Gamma @ G

print("\n252-step multiplication complete")

# ============================================================
# 9. Compare with direct power
# ============================================================

Gpow = np.linalg.matrix_power(Gamma, 252)

print("\nPower cross-check")
print(
    "||iter - power||_F =",
    np.linalg.norm(G - Gpow)
)

# ============================================================
# 10. Compare against projector
# ============================================================

print("\nConvergence to projector")

print(
    "||G252 - P||_2 =",
    np.linalg.norm(G - P, 2)
)

print(
    "||G252 - P||_F =",
    np.linalg.norm(G - P)
)

print(
    "max entry error =",
    np.max(np.abs(G - P))
)

# ============================================================
# 11. Random-state residual test
# ============================================================

rng = np.random.default_rng(0)

x = rng.standard_normal(N)
x /= np.linalg.norm(x)

r0 = np.linalg.norm((np.eye(N) - P) @ x)

x252 = G @ x

r252 = np.linalg.norm(
    (np.eye(N) - P) @ x252
)

print("\nResidual collapse")
print("r0    =", r0)
print("r252  =", r252)
print("ratio =", r252 / r0)

# ============================================================
# 12. Theoretical worst-case bound
# ============================================================

bound = (15 / 17) ** 252

print("\nTheory")
print("bound =", bound)
print("observed ratio =", r252 / r0)
