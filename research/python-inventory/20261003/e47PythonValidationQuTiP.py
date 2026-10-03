import numpy as np

# 1. Spin-2 SU(2) Representation
s = 2
d = int(2 * s + 1)
m_vals = np.arange(s, -s - 1, -1)

# Ladder operators
Jz = np.diag(m_vals).astype(complex)
Jp = np.zeros((d, d), dtype=complex)
Jm = np.zeros((d, d), dtype=complex)
for i in range(d - 1):
    Jp[i, i + 1] = np.sqrt(s * (s + 1) - m_vals[i + 1] * (m_vals[i + 1] + 1))
for i in range(1, d):
    Jm[i, i - 1] = np.sqrt(s * (s + 1) - m_vals[i - 1] * (m_vals[i - 1] - 1))

Jx = 0.5 * (Jp + Jm)
Jy = -0.5j * (Jp - Jm)
I5 = np.eye(d, dtype=complex)

def kron3(A, B, C):
    return np.kron(np.kron(A, B), C)

# 2. Total Angular Momentum in V = V2 x V2 x V2
Jx_tot = kron3(Jx, I5, I5) + kron3(I5, Jx, I5) + kron3(I5, I5, Jx)
Jy_tot = kron3(Jy, I5, I5) + kron3(I5, Jy, I5) + kron3(I5, I5, Jy)
Jz_tot = kron3(Jz, I5, I5) + kron3(I5, Jz, I5) + kron3(I5, I5, Jz)

# 3. Casimir Operator C
C = Jx_tot @ Jx_tot + Jy_tot @ Jy_tot + Jz_tot @ Jz_tot
C = 0.5 * (C + C.conj().T)  # Enforce strict Hermiticity

eigenvalues = np.round(np.linalg.eigvalsh(C)).astype(int)
unique_evals, counts = np.unique(eigenvalues, return_counts=True)
spectrum_dict = dict(zip(unique_evals, counts))

# 4. Spectral Kernel K
I125 = np.eye(125)
K = (C - 6 * I125) @ (C - 30 * I125)

# 5. Extract Invariant Kernel E47
K_evals = np.linalg.eigvalsh(K)
kernel_dim = np.sum(np.abs(K_evals) < 1e-10)
omega_c = kernel_dim / 125

print(f"State Space Dimension: {len(C)}")
print(f"Casimir Spectrum (Eval: Mult): {spectrum_dict}")
print(f"Invariant Kernel Dimension: {kernel_dim}")
print(f"Coherence Threshold (Omega_c): {omega_c:.3f}")
