#!/usr/bin/env python3
"""
It from Qubit -- E47 numeric validation.

Nicholas S. Kouns, The Kouns-Killion Paradigm | Recursive Intelligence Framework.

Builds the total-spin Casimir C on the carrier V = V_2 (x) V_2 (x) V_2 (dim 125)
and asserts every number stated in the "Results" section of
research/e47/papers/IT_FROM_QUBIT_E47.md:

  * Casimir census  n(J) = 1,3,5,4,3,2,1 ; sector dims 1,9,25,28,27,22,13
  * spectral moments  mu = 18, sigma = 12  (and mu = 3j(j+1), sigma = 2j(j+1))
  * moment selector   K = (C - 6I)(C - 30I),  6 = mu - sigma, 30 = mu + sigma
  * E47 = ker K = 5 V_2 (+) 2 V_5,  dim 47,  Omega_c = 47/125 = 0.376
  * K spectrum per sector 180,112,0,-108,-140,0,432
  * K^2 gap 11664, max 186624, eps* = 1/99144, contraction 15/17 (by iteration)
  * Fibonacci-Lucas lemma  n(j) = F_k, n(J) = F_{k-2}, J(J+1) = 5 j(j+1)

Requires only numpy. Exits 0 when every assertion passes.
"""
from fractions import Fraction as Fr
import sys

import numpy as np

TOL = 1e-9
checks = []


def check(name, ok, detail=""):
    checks.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    assert ok, name


# ---------------------------------------------------------------- spin matrices
def spin_matrices(j):
    d = int(round(2 * j + 1))
    m = np.array([j - k for k in range(d)], dtype=float)          # j, j-1, ..., -j
    Jp = np.zeros((d, d))
    for i in range(d - 1):                                         # J+ |m> ~ |m+1>
        Jp[i, i + 1] = np.sqrt(j * (j + 1) - m[i + 1] * (m[i + 1] + 1))
    Jm = Jp.T
    Jx = 0.5 * (Jp + Jm)
    Jy = -0.5j * (Jp - Jm)
    Jz = np.diag(m)
    return Jx, Jy, Jz


def total_casimir(j, n=3):
    ops = spin_matrices(j)
    d = ops[0].shape[0]
    I = np.eye(d)
    C = 0
    for A in ops:
        tot = 0
        for site in range(n):
            f = np.array([[1.0]])
            for s in range(n):
                f = np.kron(f, A if s == site else I)
            tot = tot + f
        C = C + tot @ tot
    C = 0.5 * (C + C.conj().T)
    return C


# ---------------------------------------------- exact census by weight counting
def census_exact(j, n=3):
    """Multiplicity of each total spin J in V_j^{(x)n}, exact integers."""
    two_j = int(round(2 * j))
    # weights in units of 1/2: each factor contributes 2m in {-2j, ..., 2j} step 2
    w = {0: 1}
    for _ in range(n):
        nw = {}
        for a, c in w.items():
            for t in range(-two_j, two_j + 1, 2):
                nw[a + t] = nw.get(a + t, 0) + c
        w = nw
    top = n * two_j
    mult = {}
    for twoJ in range(top, -1, -2):
        mult[Fr(twoJ, 2)] = w.get(twoJ, 0) - w.get(twoJ + 2, 0)
    return {J: c for J, c in mult.items() if c}


print("=" * 72)
print("It from Qubit -- E47 validation  (carrier V_2^{(x)3})")
print("=" * 72)

# ------------------------------------------------------------------ 1. carrier
j = 2
C = total_casimir(j)
D = C.shape[0]
check("carrier dimension 125", D == 125, f"dim V = {D}")
check("C is Hermitian", np.allclose(C, C.conj().T, atol=TOL))

evals, evecs = np.linalg.eigh(C)
rounded = np.round(evals).astype(int)
check("spectrum of C is integral", np.max(np.abs(evals - rounded)) < 1e-8,
      f"max dev {np.max(np.abs(evals - rounded)):.1e}")

# --------------------------------------------------------------- 2. census
exp_mult = {0: 1, 1: 3, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
exp_dim = {0: 1, 1: 9, 2: 25, 3: 28, 4: 27, 5: 22, 6: 13}
print("\n  J   J(J+1)   mult   dim")
for J in range(7):
    dimJ = int(np.sum(rounded == J * (J + 1)))
    multJ = dimJ // (2 * J + 1)
    print(f"  {J}   {J*(J+1):5d}   {multJ:4d}   {dimJ:3d}")
    check(f"census J={J}: mult {exp_mult[J]}, dim {exp_dim[J]}",
          dimJ == exp_dim[J] and multJ == exp_mult[J] and dimJ % (2 * J + 1) == 0)
check("census sums to 125", sum(exp_dim.values()) == 125 == len(rounded))
check("exact weight-count census agrees",
      {int(k): v for k, v in census_exact(2).items()} == exp_mult)

# --------------------------------------------------------------- 3. moments
mu = np.trace(C).real / D
var = np.trace(C @ C).real / D - mu ** 2
sigma = np.sqrt(var)
check("mu = 18", abs(mu - 18) < TOL, f"mu = {mu:.12f}")
check("sigma = 12", abs(sigma - 12) < TOL, f"sigma = {sigma:.12f}")

print("\n  general triple product V_j^{(x)3} (exact rational, from census):")
for two_j in range(1, 13):
    jj = Fr(two_j, 2)
    cen = census_exact(jj)
    dim = (two_j + 1) ** 3
    m1 = sum(c * (2 * J + 1) * J * (J + 1) for J, c in cen.items()) / dim
    m2 = sum(c * (2 * J + 1) * (J * (J + 1)) ** 2 for J, c in cen.items()) / dim
    ok = (m1 == 3 * jj * (jj + 1)) and (m2 - m1 ** 2 == (2 * jj * (jj + 1)) ** 2)
    print(f"    j={str(jj):>4}: mu={str(m1):>7}  sigma^2={str(m2 - m1**2):>9}")
    check(f"mu=3j(j+1), sigma=2j(j+1) at j={jj}", ok)

# --------------------------------------------------------------- 4. selector
lo, hi = mu - sigma, mu + sigma
check("mu - sigma = 6, mu + sigma = 30", abs(lo - 6) < TOL and abs(hi - 30) < TOL)
# unique monic quadratic with roots lo, hi:  x^2 - (lo+hi) x + lo*hi
coeffs = np.poly([lo, hi])
check("unique monic quadratic vanishing at mu+-sigma is x^2 - 36x + 180",
      np.allclose(coeffs, [1, -36, 180]))
I = np.eye(D)
K = (C - 6 * I) @ (C - 30 * I)

kspec = {J: (J * (J + 1) - 6) * (J * (J + 1) - 30) for J in range(7)}
check("K sector spectrum 180,112,0,-108,-140,0,432",
      [kspec[J] for J in range(7)] == [180, 112, 0, -108, -140, 0, 432])
Kev = np.linalg.eigvalsh(K)
check("numeric K eigenvalues match sector values",
      np.allclose(np.sort(Kev), np.sort([kspec[J] for J in rounded.tolist()
                                          for J in [int(round((-1 + np.sqrt(1 + 4 * J)) / 2))]]),
                  atol=1e-7))

ker_dim = int(np.sum(np.abs(Kev) < 1e-7))
check("dim ker K = 47", ker_dim == 47, f"dim ker K = {ker_dim}")
check("ker K = 5 V_2 (+) 2 V_5", 5 * 5 + 2 * 11 == ker_dim)
P47 = evecs[:, (rounded == 6) | (rounded == 30)]
P = P47 @ P47.conj().T
check("K P47 = 0", np.linalg.norm(K @ P) < 1e-8)
omega = np.trace(P).real / D
check("Omega_c = 47/125 = 0.376", abs(omega - 0.376) < TOL and Fr(47, 125) == Fr(376, 1000),
      f"Omega_c = {omega:.12f}")

# --------------------------------------------------------------- 5. K^2 flow
K2 = K @ K
nz = sorted({v * v for v in kspec.values() if v != 0})
lam_min, lam_max = nz[0], nz[-1]
check("K^2 spectral gap 11664 (=108^2)", lam_min == 11664)
check("K^2 max eigenvalue 186624 (=432^2)", lam_max == 186624)
K2ev = np.linalg.eigvalsh(K2)
check("numeric K^2 gap / max agree",
      abs(np.min(K2ev[K2ev > 1]) - 11664) < 1e-5 and abs(np.max(K2ev) - 186624) < 1e-5)
eps = Fr(2, lam_min + lam_max)
check("eps* = 2/(gap+max) = 1/99144", eps == Fr(1, 99144))
rho = max(abs(1 - eps * v) for v in nz)
check("worst-case contraction max|1 - eps* lambda| = 15/17", rho == Fr(15, 17))

R = I - float(eps) * K2
rng = np.random.default_rng(47)
x = rng.standard_normal(D) + 1j * rng.standard_normal(D)
x_ker0 = P @ x
e = x - x_ker0
e0 = np.linalg.norm(e)
steps = 60
ratios = []
for n in range(1, steps + 1):
    x = R @ x
    e_new = x - P @ x
    ratios.append(np.linalg.norm(e_new) / np.linalg.norm(e))
    e = e_new
    assert np.linalg.norm(e) <= (15 / 17) ** n * e0 * (1 + 1e-9), f"bound violated at n={n}"
check("iteration: ||e_n|| <= (15/17)^n ||e_0|| for n=1..60", True,
      f"||e_60||/||e_0|| = {np.linalg.norm(e)/e0:.3e}, bound {(15/17)**steps:.3e}")
# asymptotic rate: iterate the (renormalized) error e_{n+1} = R e_n on the complement
v = (I - P) @ (rng.standard_normal(D) + 1j * rng.standard_normal(D))
v /= np.linalg.norm(v)
for _ in range(3000):
    w = R @ v
    rate = np.linalg.norm(w)
    v = (I - P) @ w / rate          # (I-P) only scrubs round-off leakage into ker K
check("iteration: observed asymptotic per-step ratio = 15/17",
      abs(rate - 15 / 17) < 1e-9, f"ratio_3000 = {rate:.12f}, 15/17 = {15/17:.12f}")
check("iteration: kernel component preserved", np.linalg.norm(P @ x - x_ker0) < 1e-9)

# --------------------------------------------------------- 6. Fibonacci-Lucas
F = [0, 1]
for _ in range(20):
    F.append(F[-1] + F[-2])
L = [2, 1]
for _ in range(20):
    L.append(L[-1] + L[-2])
print("\n  k   (j, J)          n(j)  n(J)  dim ker K_mom / dim V")
for k in (3, 5, 7, 9, 11):
    jj, JJ = Fr(F[k] - 1, 2), Fr(L[k] - 1, 2)
    cen = census_exact(jj)
    nj, nJ = cen.get(jj, 0), cen.get(JJ, 0)
    sel = nj * (2 * jj + 1) + nJ * (2 * JJ + 1)
    print(f"  {k:<3} ({str(jj)}, {str(JJ)}){'':<{12-len(str(jj))-len(str(JJ))}}"
          f"{nj:5d} {nJ:5d}   {sel} / {(2*jj+1)**3}")
    check(f"F-L k={k}: J(J+1)=5j(j+1), n(j)=F_{k}, n(J)=F_{k-2}",
          JJ * (JJ + 1) == 5 * jj * (jj + 1) and nj == F[k] and nJ == F[k - 2])

# ----------------------------------------------------------------- summary
n_pass = sum(ok for _, ok in checks)
print("\n" + "=" * 72)
print(f"{n_pass}/{len(checks)} checks PASS")
print("E47 = 5V_2 (+) 2V_5, dim 47, Omega_c = 0.376, contraction 15/17: VERIFIED")
print("=" * 72)
sys.exit(0 if n_pass == len(checks) else 1)
