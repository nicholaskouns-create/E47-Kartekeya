import numpy as np
from math import sqrt
from scipy.linalg import eigh

j = 2
m = np.arange(2, -3, -1, dtype=float)
Sp = np.zeros((5, 5), complex)
for i in range(1, 5):
    q = m[i]
    Sp[i - 1, i] = sqrt((2 - q) * (3 + q))
Sm = Sp.conj().T
Sx = (Sp + Sm) / 2
Sy = (Sp - Sm) / (2 * 1j)
Sz = np.diag(m)
I5 = np.eye(5)
I = np.eye(125)
J = [
    np.kron(np.kron(s, I5), I5)
    + np.kron(np.kron(I5, s), I5)
    + np.kron(np.kron(I5, I5), s)
    for s in (Sx, Sy, Sz)
]
C = sum((a @ a for a in J))
C = (C + C.conj().T) / 2
w, U = eigh(C)
lambdas = np.array([0, 2, 6, 12, 20, 30, 42])
counts = [int(np.sum(abs(w - z) < 1e-7)) for z in lambdas]
k = (w - 6) * (w - 30)
a = k * k / 99144
r = 1 - a
mask = abs(k) < 1e-7
rng = np.random.default_rng(47)
x = rng.normal(size=125) + 1j * rng.normal(size=125)
y = U.conj().T @ x
rho = max(abs(r[~mask]))
amin = min(a[~mask])
print('Casimir multiplicities:', dict(zip(lambdas, counts)))
print('Kernel rank:', sum(mask), 'discrete spectral radius:', rho, 'continuous spectral gap:', amin)
print('Discrete eigenvalues by C:', dict(zip(lambdas, np.round(1 - ((lambdas - 6) * (lambdas - 30)) ** 2 / 99144, 12))))
for n in [0, 1, 5, 20, 100, 220]:
    v = np.sum(abs(y[~mask]) ** 2 * abs(r[~mask]) ** (2 * n))
    bound = rho ** (2 * n) * np.sum(abs(y[~mask]) ** 2)
    print(f'n={n:3d} Lyapunov={v:.12g} upper={bound:.12g} valid={v <= bound + 1e-12}')
for t in [0, 1, 10, 50, 100]:
    err = max(np.exp(-t * a[~mask]))
    print(f't={t:3d} continuous operator error={err:.12g} exact={np.exp(-2 * t / 17):.12g}')
z = np.copy(y)
delta = 0.001
for n in range(1000):
    u = np.zeros(125, complex)
    u[~mask] = delta * y[~mask] / np.linalg.norm(y[~mask])
    z = r * z + u
trans = np.linalg.norm(z[~mask])
print('Perturbed transverse norm:', trans, 'ISS asymptotic bound:', 8.5 * delta, 'PASS:', trans <= 8.5 * delta + 1e-12)
i = int(np.where(~mask)[0][np.argmin(a[~mask])])
t = 10
outside = np.exp(-2 * a[i] * t)
print('CPTP quantum relaxation (outside-kernel probability, t=10):', outside, 'expected:', np.exp(-4 * t / 17))
assert counts == [1, 9, 25, 28, 27, 22, 13] and sum(mask) == 47
assert abs(rho - 15 / 17) < 1e-12 and abs(amin - 2 / 17) < 1e-12
assert trans <= 8.5 * delta + 1e-12
print('ALL ASSERTIONS PASS')
