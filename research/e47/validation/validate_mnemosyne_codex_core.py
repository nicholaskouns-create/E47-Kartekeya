"""Reconstructed E47 canonical validator. Python >=3.10; NumPy, SciPy.

Independently verifies core spectral algebra referenced by Mnemosyne Python Codex.
Does not validate experimental physical or artificial-consciousness claims.
Run: python research/e47/validation/validate_mnemosyne_codex_core.py
"""
import numpy as np
from scipy.linalg import eigh

j = 2
m = np.arange(j, -j - 1, -1)
raising = np.zeros((5, 5), complex)
for i in range(1, 5):
    raising[i - 1, i] = np.sqrt(j * (j + 1) - m[i] * (m[i] + 1))
jx = (raising + raising.conj().T) / 2
jy = (raising - raising.conj().T) / (2j)
jz = np.diag(m)
i5 = np.eye(5)
def total(a):
    return (np.kron(np.kron(a, i5), i5)
            + np.kron(np.kron(i5, a), i5)
            + np.kron(np.kron(i5, i5), a))

c = sum(total(a) @ total(a) for a in (jx, jy, jz))
eigenvalues, eigenvectors = eigh(c)
spectrum = [0, 2, 6, 12, 20, 30, 42]
multiplicities = [int(np.sum(abs(eigenvalues - v) < 1e-7)) for v in spectrum]
selected = (abs(eigenvalues - 6) < 1e-7) | (abs(eigenvalues - 30) < 1e-7)
projector = eigenvectors[:, selected] @ eigenvectors[:, selected].conj().T
k = (c - 6 * np.eye(125)) @ (c - 30 * np.eye(125))
k_values = np.array([(v - 6) * (v - 30) for v in spectrum])
gap = int(min(v * v for v in k_values if v))
gamma = np.eye(125) - k @ k / 99144
rho = max(abs(1 - v*v / 99144) for v in k_values if v)
checks = {
    "dimension": len(eigenvalues) == 125,
    "multiplicities": multiplicities == [1, 9, 25, 28, 27, 22, 13],
    "kernel_rank": int(round(np.trace(projector).real)) == 47,
    "projector_idempotence": np.linalg.norm(projector @ projector - projector) < 1e-10,
    "spectral_gap": gap == 11664,
    "contraction_rate": abs(rho - 15/17) < 1e-12,
    "gamma_kernel_fixed": np.linalg.norm(gamma @ projector - projector) < 1e-9,
}
for name, passed in checks.items():
    print(f"{'PASS' if passed else 'FAIL'} {name}")
print(f"PASS {sum(checks.values())}/{len(checks)}")
print(f"max projector residual {np.linalg.norm(projector @ projector - projector):.5g}")
print(f"rho {rho:.16g}")
assert all(checks.values())
