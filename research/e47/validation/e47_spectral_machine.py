"""E47 spectral matrix machine: 125x125 spin-2 tensor representation.

Three spin-2 carriers V_2^{(x)3} (dim 125). The Casimir C splits them into
total-spin sectors J = 0..6; the selector K = (C-6I)(C-30I) vanishes exactly on
J = 2 and J = 5, so ker K has dimension 25 + 22 = 47 (the K_{47/125} kernel).
Q = K^2 is positive semidefinite with ker Q = ker K, and two dynamics converge
to the projector P onto those 47 states:
  discrete   R^n = (I - eps Q)^n -> P,  ||R^n - P|| = (15/17)^n
  continuous exp(-tQ)          -> P,  ||exp(-tQ) - P|| = exp(-11664 t)

Run: python e47_spectral_machine.py
Requires numpy, scipy.
"""
import json
import numpy as np
from scipy.linalg import expm

j = 2
m = np.arange(j, -j - 1, -1, dtype=float)
Jz = np.diag(m).astype(complex)
Jplus = np.zeros((5, 5), dtype=complex)
for i in range(1, 5):
    Jplus[i - 1, i] = np.sqrt(j * (j + 1) - m[i] * (m[i] + 1))
Jx = (Jplus + Jplus.conj().T) / 2
Jy = (Jplus - Jplus.conj().T) / (2j)
I5 = np.eye(5)
I125 = np.eye(125)


def total(a):
    return (np.kron(np.kron(a, I5), I5)
            + np.kron(np.kron(I5, a), I5)
            + np.kron(np.kron(I5, I5), a))


J = [total(a) for a in (Jx, Jy, Jz)]
C = sum(a @ a for a in J)
K = (C - 6 * I125) @ (C - 30 * I125)
Q = K @ K
w, V = np.linalg.eigh(C)
selected = (np.abs(w - 6) < 1e-8) | (np.abs(w - 30) < 1e-8)
U = V[:, selected]
P = U @ U.conj().T
rho_min, rho_max = 11664, 186624
epsilon = 2 / (rho_min + rho_max)
R = I125 - epsilon * Q
rho = (rho_max - rho_min) / (rho_max + rho_min)

# Spectral data of Q, used for a numerically stable evaluation of ||R^n - P||.
q = np.linalg.eigvalsh(Q)
q_off = q[q > 1e-6]  # eigenvalues off the 47-dim kernel


def discrete_residual(n):
    # R^n - P = sum over off-kernel eigenspaces of (1 - eps*q)^n; its 2-norm is the max.
    return float(np.max(np.abs(1 - epsilon * q_off) ** n))


checks = {
    'carrier dimension 125': C.shape == (125, 125),
    'Casimir eigenvalues': np.array_equal(np.unique(np.rint(w).astype(int)), [0, 2, 6, 12, 20, 30, 42]),
    'Casimir multiplicities': np.array_equal(np.unique(np.rint(w).astype(int), return_counts=True)[1], [1, 9, 25, 28, 27, 22, 13]),
    'Casimir Hermitian': np.linalg.norm(C - C.conj().T) < 1e-10,
    'selector Hermitian': np.linalg.norm(K - K.conj().T) < 1e-9,
    'Q equals K squared': np.linalg.norm(Q - K @ K) < 1e-7,
    'kernel rank 47': int(selected.sum()) == 47,
    'P rank 47': np.linalg.matrix_rank(P, tol=1e-8) == 47,
    'P idempotent': np.linalg.norm(P @ P - P) < 1e-10,
    'P Hermitian': np.linalg.norm(P - P.conj().T) < 1e-10,
    'KP zero': np.linalg.norm(K @ P) < 1e-8,
    'QP zero': np.linalg.norm(Q @ P) < 1e-6,
    'Q positive semidefinite': q.min() > -1e-7,
    'rho min': min(int(round(x * x)) for x in [180, 112, -108, -140, 432]) == rho_min,
    'rho max': max(int(round(x * x)) for x in [180, 112, -108, -140, 432]) == rho_max,
    'Q spectrum matches K^2 values': np.array_equal(sorted(set(np.rint(q_off).astype(int))), sorted({x * x for x in [180, 112, -108, -140, 432]})),
    'epsilon optimal': abs(epsilon - 1 / 99144) < 1e-15,
    'rho optimal': abs(rho - 15 / 17) < 1e-15,
}
print('E47 SPECTRAL MATRIX MACHINE')
print('Casimir sectors:', list(zip(*[a.tolist() for a in np.unique(np.rint(w).astype(int), return_counts=True)])))
print('rank(P):', selected.sum(), 'epsilon:', epsilon, 'rho:', rho)
for n in (0, 10, 50, 100, 220, 300):
    residual = discrete_residual(n)
    bound = rho ** n
    print(f'discrete n={n:3d}: observed={residual:.8e}, exact={bound:.8e}')
for t in (0.0, 0.0001, 0.001, 0.01):
    residual = float(np.max(np.exp(-t * q_off)))  # stable spectral evaluation
    exact = np.exp(-t * rho_min)
    print(f'continuous t={t:.4g}: observed={residual:.8e}, exact={exact:.8e}')
# Direct (matrix-power) cross-check at moderate n, where rounding is negligible.
direct100 = np.linalg.norm(np.linalg.matrix_power(R, 100) - P, 2)
checks['discrete n100 convergence'] = direct100 < 1e-4
checks['discrete n100 matches (15/17)^100'] = abs(direct100 - rho ** 100) / rho ** 100 < 1e-6
checks['spectral residual equals rho^n'] = all(abs(discrete_residual(n) - rho ** n) <= 1e-12 * rho ** n for n in (10, 100, 300))
direct_t = np.linalg.norm(expm(-.001 * Q) - P, 2)  # direct expm cross-check
checks['continuous t0.001 convergence'] = direct_t < 1e-4
checks['continuous t0.001 matches exp(-11.664)'] = abs(direct_t - np.exp(-11.664)) / np.exp(-11.664) < 1e-6
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL'), name)
assert all(checks.values()), 'Some validations failed'
print('OVERALL:', len(checks), '/', len(checks), 'PASS')
with open('e47_spectral_results.json', 'w') as f:
    json.dump({'checks': {k: bool(v) for k, v in checks.items()}, 'rank': 47,
               'epsilon': epsilon, 'rho': rho}, f, indent=2)
