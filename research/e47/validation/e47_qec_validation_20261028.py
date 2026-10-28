#!/usr/bin/env python3
"""E47 certificate — corrected validation.
Verifies the LEMMAS, not the arithmetic residues of the lemmas.
NumPy only; no SciPy, no tautological asserts.
Run:  python3 -I validate_e47.py      exits non-zero on any failure."""
import numpy as np, itertools, sys
from collections import Counter
from fractions import Fraction as F

FAIL = []
def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name:<52} {detail}")
    if not cond: FAIL.append(name)

# ---------------------------------------------------------------- generators
def spin(S):
    """Hermitian su(2) generators in the |S,m> basis, m = S .. -S."""
    dd = 2*S+1; ms = np.array([S-k for k in range(dd)], float)
    Jz = np.diag(ms).astype(complex)
    Jp = np.zeros((dd, dd), complex)
    for k, m in enumerate(ms):
        if m + 1 <= S: Jp[int(S-m-1), k] = np.sqrt(S*(S+1) - m*(m+1))
    Jm = Jp.conj().T
    return (Jp+Jm)/2, (Jp-Jm)/complex(0, 2), Jz      # explicit 2i, never the literal `2j`

S, d = 2, 5; N = d**3
Jx, Jy, Jz = spin(S); I = np.eye(d, dtype=complex)
# Delta^(2): the iterated coproduct, X -> X@1@1 + 1@X@1 + 1@1@X
D2 = lambda X: np.kron(np.kron(X,I),I) + np.kron(np.kron(I,X),I) + np.kron(np.kron(I,I),X)
Jxt, Jyt, Jzt = D2(Jx), D2(Jy), D2(Jz)
C  = Jxt@Jxt + Jyt@Jyt + Jzt@Jzt
Id = np.eye(N)

print("\nL0  carrier and generators")
check("su(2) brackets [Jx,Jy]=iJz on the image of Delta^(2)",
      np.allclose(Jxt@Jyt - Jyt@Jxt, 1j*Jzt))
check("C is Hermitian", np.allclose(C, C.conj().T))
check("C is central: [C, Delta^(2)(X)] = 0 for X = x,y,z",
      all(np.allclose(C@X - X@C, 0) for X in (Jxt,Jyt,Jzt)))

# ---------------------------------------------------------------- L1
ev, U = np.linalg.eigh(C)
spec = sorted({int(round(v)) for v in ev.real})
states = Counter(int(round(v)) for v in ev.real)
mJ = {J: states[J*(J+1)]//(2*J+1) for J in range(7)}
print("\nL1  isotypic decomposition of V_2^{(x)3}")
check("spectrum = {0,2,6,12,20,30,42}", spec == [0,2,6,12,20,30,42], str(spec))
check("multiplicities m_J = (1,3,5,4,3,2,1)",
      [mJ[J] for J in range(7)] == [1,3,5,4,3,2,1], str([mJ[J] for J in range(7)]))
check("sum (2J+1) m_J = 125", sum((2*J+1)*mJ[J] for J in range(7)) == 125)

K  = (C - 6*Id) @ (C - 30*Id)
mask = np.isclose(ev, 6, atol=1e-8) | np.isclose(ev, 30, atol=1e-8)
V = U[:, mask]
check("dim ker K_e = 47  (COUNTED from the spectrum)", V.shape[1] == 47, f"= {V.shape[1]}")
check("rank K_e = 78", abs(np.linalg.matrix_rank(K, tol=1e-6) - 78) == 0)

# ---------------------------------------------------------------- L2
P = V @ V.conj().T
print("\nL2  the code projector")
check("P^2 = P", np.allclose(P@P, P))
check("P^dagger = P", np.allclose(P.conj().T, P))
check("Tr P = 47", abs(np.trace(P).real - 47) < 1e-9, f"= {np.trace(P).real:.12f}")
check("K_e P = P K_e = 0", np.allclose(K@P, 0) and np.allclose(P@K, 0))

# ---------------------------------------------------------------- L3  (derived)
print("\nL3  optimal contraction  (constants DERIVED, not asserted)")
K2 = K @ K
nz = sorted({int(round(v)) for v in np.linalg.eigvalsh(K2).real if v > 1e-6})
lam_lo, lam_hi = min(nz), max(nz)
eps  = F(2, lam_lo + lam_hi)
rho  = F(lam_hi - lam_lo, lam_hi + lam_lo)
kappa = F(lam_hi, lam_lo)
check("nonzero spec(K^2) = {11664,12544,19600,32400,186624}",
      nz == [11664,12544,19600,32400,186624], str(nz))
check("eps* = 2/(lam_min+lam_max) = 1/99144", eps == F(1,99144), f"= {eps}")
check("kappa = lam_max/lam_min = 16", kappa == 16, f"= {kappa}")
check("rho* = (kappa-1)/(kappa+1) = 15/17", rho == F(15,17) == (kappa-1)/(kappa+1), f"= {rho}")
G = Id - float(eps)*K2
for n in (10, 25, 50):
    err = np.linalg.norm(np.linalg.matrix_power(G, n) - P, 2)
    check(f"||Gamma^n - P||_2 = (15/17)^n at n={n}",
          abs(err/(15/17)**n - 1) < 1e-9, f"ratio {err/(15/17)**n:.12f}")

# ---------------------------------------------------------------- L4 (counted)
print("\nL4  Psi_e as an su(2)-module  (COUNTED, not asserted)")
n2, n5 = states[6], states[30]
check("J=2 sector: 25 states = m_2(5) x dim(5)", n2 == 25 and mJ[2] == 5, f"{mJ[2]} x 5 = {n2}")
check("J=5 sector: 22 states = m_5(2) x dim(11)", n5 == 22 and mJ[5] == 2, f"{mJ[5]} x 11 = {n5}")
check("Psi_e = 5 V_2 (+) 2 V_5, dim 25+22 = 47", n2 + n5 == 47)

# ---------------------------------------------------------------- L5 (computed)
print("\nL5  commutant on Psi_e  (COMPUTED by nullity, not asserted)")
A = [V.conj().T @ X @ V for X in (Jxt, Jyt, Jzt)]
n = 47
M = np.vstack([np.kron(X, np.eye(n)) - np.kron(np.eye(n), X.T) for X in A])
dim_comm = int((np.linalg.svd(M, compute_uv=False) < 1e-8).sum()) + (n*n - min(M.shape))
check("dim Comm(su(2)) on Psi_e = 29 = 5^2 + 2^2", dim_comm == 29, f"= {dim_comm}")

# ---------------------------------------------------------------- L6 / R3
def perm_op(p):
    Mx = np.zeros((N, N))
    for a,b,c in itertools.product(range(d), repeat=3):
        t = (a,b,c)
        Mx[t[p[0]]*d*d + t[p[1]]*d + t[p[2]], a*d*d + b*d + c] = 1
    return Mx
print("\nL6/R3  symmetry of the carrier")
check("all 6 factor permutations commute with C (S_3 <= Comm)",
      all(np.allclose(perm_op(p)@C, C@perm_op(p)) for p in itertools.permutations(range(3))))
w, Q = np.linalg.eigh(np.kron(np.kron(Jx,I),I))
Uf = Q @ np.diag(np.exp(1j*np.pi*w)) @ Q.conj().T      # expm(i.pi.J1x), no SciPy
check("exp(i.pi.J_{1x}) does NOT commute with C (S_4 is not a symmetry)",
      np.linalg.norm(Uf@C - C@Uf) > 1.0, f"||[.,.]||_F = {np.linalg.norm(Uf@C-C@Uf):.4f}")
# does S_3 exhaust the commutant?
B = [V.conj().T @ perm_op(p) @ V for p in itertools.permutations(range(3))]
span = np.vstack([b.reshape(1,-1) for b in B])
check("S_3 does NOT exhaust the 29-dim commutant (dim C[S_3] image < 29)",
      np.linalg.matrix_rank(span, tol=1e-8) < 29,
      f"rank {np.linalg.matrix_rank(span, tol=1e-8)} of 29")

# ---------------------------------------------------------------- R1 / R2
print("\nR1/R2  Knill-Laflamme  ||P E^dag E P - alpha P||_F  (alpha = Tr/47)")
def kl(E):
    Mx = V.conj().T @ E.conj().T @ E @ V
    return np.linalg.norm(Mx - (np.trace(Mx).real/47)*np.eye(47))
for name, E, want_ok in [("K_e  (selector, trivial)", K, True),
                         ("C    (Casimir, central)", C, False),
                         ("J_1z (single factor)", np.kron(np.kron(Jz,I),I), False),
                         ("J_1x (single factor)", np.kron(np.kron(Jx,I),I), False),
                         ("J_tot,z (collective)", Jzt, False),
                         ("J_tot,x (collective)", Jxt, False)]:
    v = kl(E)
    check(f"{name:<26} KL {'holds' if want_ok else 'FAILS'}",
          (v < 1e-8) == want_ok, f"{v:.4e}")

# ---------------------------------------------------------------- R6
print("\nR6  the 4-fold carrier")
w4 = Counter({0:1})
for _ in range(4):
    nw = Counter()
    for t,c in w4.items():
        for m in range(2*S, -2*S-1, -2): nw[t+m] += c
    w4 = nw
m4 = {tJ//2: w4[tJ] - w4.get(tJ+2, 0) for tJ in range(8*S, -1, -2)}
check("V_2^{(x)4}: m_2 = 16, m_5 = 10", m4[2] == 16 and m4[5] == 10, f"{m4[2]}, {m4[5]}")
check("dim ker K_4 = 16*5 + 10*11 = 190, NOT 187",
      m4[2]*5 + m4[5]*11 == 190, f"= {m4[2]*5 + m4[5]*11}")

print("\n" + ("ALL CHECKS PASS" if not FAIL else f"{len(FAIL)} FAILURES: {FAIL}"))
sys.exit(1 if FAIL else 0)
