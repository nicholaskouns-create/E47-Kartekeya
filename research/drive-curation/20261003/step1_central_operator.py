"""
STEP 1 — VALIDATE THE CENTRAL OPERATOR

Claim from the dashboards:
  - State space V = R^(5x5x5), dim V = 125
  - C is the 5x5x5 discrete Laplacian with periodic BC
  - "Eigenvalues of C: lambda_i(C) in [0, 12]"
  - Kartekeya operator: K = (C - 6I)(C - 30I)
  - dim ker(K) = 47
  - "Universal coherence constant" Omega_c = 47/125 = 0.376
  - Rank(K) = 78

We construct C exactly and report what scipy/numpy actually compute.
"""

import numpy as np

# ---- Build 5x5x5 periodic discrete Laplacian via Kronecker sum ----
N = 5

def lap1d_periodic(N):
    """1D periodic Laplacian on Z_N: L = 2I - S - S^T where S is the cyclic shift."""
    L = 2.0 * np.eye(N) - np.eye(N, k=1) - np.eye(N, k=-1)
    L[0, -1] = -1.0  # periodic wrap
    L[-1, 0] = -1.0
    return L

L1 = lap1d_periodic(N)
I1 = np.eye(N)

# 3D Laplacian = L1 (x) I (x) I  +  I (x) L1 (x) I  +  I (x) I (x) L1
C = (
    np.kron(np.kron(L1, I1), I1)
    + np.kron(np.kron(I1, L1), I1)
    + np.kron(np.kron(I1, I1), L1)
)

print(f"dim V = {C.shape[0]}  (claim: 125)  -> match: {C.shape[0] == 125}")

# ---- Spectrum of C ----
eigs_C = np.linalg.eigvalsh(C)
print(f"\nC eigenvalue range: [{eigs_C.min():.6f}, {eigs_C.max():.6f}]")
print(f"  dashboard claim: [0, 12]")
print(f"  match on lower bound 0?  {np.isclose(eigs_C.min(), 0.0)}")
print(f"  match on upper bound 12? {np.isclose(eigs_C.max(), 12.0)}")

# Distinct eigenvalues of C (rounded) with multiplicities
vals, counts = np.unique(np.round(eigs_C, 6), return_counts=True)
print("\nDistinct eigenvalues of C (rounded to 6 dp):")
for v, c in zip(vals, counts):
    print(f"   lambda = {v:>10.6f}   multiplicity = {c}")
print(f"  total multiplicity = {counts.sum()}")

# ---- Build K = (C - 6I)(C - 30I) and compute spectrum ----
I125 = np.eye(125)
K = (C - 6.0 * I125) @ (C - 30.0 * I125)
K = 0.5 * (K + K.T)  # symmetrize for clean eigvalsh

eigs_K = np.linalg.eigvalsh(K)
tol = 1e-8
nullity_K = int(np.sum(np.abs(eigs_K) < tol))
print(f"\nK = (C - 6I)(C - 30I)")
print(f"K eigenvalue range: [{eigs_K.min():.6e}, {eigs_K.max():.6e}]")
print(f"Numerical nullity of K (|lambda| < {tol}): {nullity_K}")
print(f"  dashboard claim: dim ker K = 47")
print(f"  match? {nullity_K == 47}")

# Why? Check whether 6 or 30 are eigenvalues of C
hits_6  = int(np.sum(np.isclose(eigs_C,  6.0, atol=1e-8)))
hits_30 = int(np.sum(np.isclose(eigs_C, 30.0, atol=1e-8)))
print(f"\nMultiplicity of eigenvalue 6  in spec(C): {hits_6}")
print(f"Multiplicity of eigenvalue 30 in spec(C): {hits_30}")
print(f"=> dim ker(K) = mult(6) + mult(30) = {hits_6 + hits_30}")

# Save spectra for later plots
np.save("/home/claude/kartekeya/eigs_C.npy", eigs_C)
np.save("/home/claude/kartekeya/eigs_K.npy", eigs_K)
print("\nSaved eigs_C.npy and eigs_K.npy")
