#!/usr/bin/env python3
"""
RUB5-C17 DESCENT DERIVATION
Derives the dimensional descent asserted by plate RUB5-C17 from the
collective SU(2) structure of V_2 (x) V_2 (x) V_2, and checks every
constant the plate declares.

Nothing is asserted: multiplicities are read off the numerical Casimir
spectrum, and the commutant dimension is the nullity of the adjoint-action
Casimir superoperator.

Run: python3 -I rub5_c17_descent_derivation.py
"""
import numpy as np
from fractions import Fraction as F

PASS, FAIL = [], []

def check(name, got, want, tol=0.0):
    ok = (got == want) if tol == 0 else (abs(got - want) <= tol)
    (PASS if ok else FAIL).append(name)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:<54s} {got}"
          + ("" if ok else f"   (expected {want})"))
    return ok

def report(name, val):
    print(f"  [----] {name:<54s} {val}")

# ------------------------------------------------- spin-2 single site
def spin_ops(j):
    d = int(round(2*j + 1))
    m = np.array([j - k for k in range(d)])
    Jz = np.diag(m).astype(complex)
    # J+ |j,m> = sqrt(j(j+1) - m(m+1)) |j,m+1>
    Jp = np.zeros((d, d), complex)
    for k in range(1, d):
        mm = m[k]
        Jp[k-1, k] = np.sqrt(j*(j+1) - mm*(mm+1))
    Jm = Jp.conj().T
    Jx = 0.5*(Jp + Jm)
    Jy = -0.5j*(Jp - Jm)
    return Jx, Jy, Jz

jx, jy, jz = spin_ops(2)
I5 = np.eye(5, dtype=complex)
kron = lambda *a: np.kron(np.kron(a[0], a[1]), a[2])

Jx = kron(jx, I5, I5) + kron(I5, jx, I5) + kron(I5, I5, jx)
Jy = kron(jy, I5, I5) + kron(I5, jy, I5) + kron(I5, I5, jy)
Jz = kron(jz, I5, I5) + kron(I5, jz, I5) + kron(I5, I5, jz)

DIM = 125
I125 = np.eye(DIM, dtype=complex)

print("\n" + "="*80)
print("S1  CARRIER AND CASIMIR  --  multiplicities read off, not supplied")
print("="*80)
check("carrier dimension", Jz.shape[0], DIM)

C = Jx @ Jx + Jy @ Jy + Jz @ Jz
check("Casimir is Hermitian (residual < 1e-12)",
      float(np.linalg.norm(C - C.conj().T)) < 1e-12, True)
cev = np.linalg.eigvalsh(C)

# group eigenvalues into sectors
sectors = {}
for v in cev:
    key = int(round(v))
    sectors[key] = sectors.get(key, 0) + 1
print("  Casimir sector dimensions (numerically grouped):")
mult = {}
for cval in sorted(sectors):
    # C = j(j+1) -> j = (-1 + sqrt(1+4C))/2 ; dim of V_j = 2j+1
    j = (-1 + np.sqrt(1 + 4*cval))/2
    twojp1 = int(round(2*j + 1))
    m = sectors[cval] // twojp1
    mult[int(round(j))] = m
    print(f"     C = {cval:3d}   j = {j:.0f}   dim V_j = {twojp1:2d}"
          f"   sector dim = {sectors[cval]:3d}   multiplicity m_j = {m}")

check("multiplicities (m_0..m_6)",
      tuple(mult[j] for j in range(7)), (1, 3, 5, 4, 3, 2, 1))
check("sum m_j (2j+1) = 125",
      sum(mult[j]*(2*j+1) for j in range(7)), 125)
check("Casimir spectrum",
      tuple(sorted(sectors)), (0, 2, 6, 12, 20, 30, 42))

print("\n" + "="*80)
print("S2  CASIMIR FILTER AND THE 47-DIMENSIONAL KERNEL")
print("="*80)
K = (C - 6.0*I125) @ (C - 30.0*I125)
kev, kvec = np.linalg.eigh(K)
null = np.abs(kev) < 1e-8
P47 = kvec[:, null] @ kvec[:, null].conj().T
dim47 = int(round(np.trace(P47).real))

check("dim ker K", dim47, 47)
check("= m_2 (2*2+1) + m_5 (2*5+1)", mult[2]*5 + mult[5]*11, 47)
report("  j=2 branch: m_2 x dim V_2 = 5 x 5", mult[2]*5)
report("  j=5 branch: m_5 x dim V_5 = 2 x 11", mult[5]*11)

omega_c = F(dim47, DIM)
check("Omega_c = 47/125 exactly", omega_c, F(47, 125))
check("Omega_c decimal is exact", float(omega_c), 0.376, 1e-15)
check("idempotency ||P^2 - P|| < 1e-14",
      float(np.linalg.norm(P47 @ P47 - P47)) < 1e-14, True)
report("  ||P^2 - P||", f"{np.linalg.norm(P47 @ P47 - P47):.3e}")
# ||K|| ~ 432, so the achievable floor for ||K P|| is ~||K|| * eps, not 1e-15.
# The right test is relative.
nK = float(np.linalg.norm(K, 2))
rel_KP = float(np.linalg.norm(K @ P47)) / nK
check("kernel defect ||K P||/||K|| < 1e-13", rel_KP < 1e-13, True)
report("  ||K P||", f"{np.linalg.norm(K @ P47):.3e}")
report("  ||K||_2", f"{nK:.1f}")
report("  relative defect", f"{rel_KP:.3e}")
report("  float64 floor for this operator (||K||*eps)", f"{nK*2.22e-16:.3e}")
print("  >> Plate certificate [4] quotes ||K P|| = 4.31e-15 against a 1e-14")
print("     threshold. For an operator of norm 432 the float64 floor is")
print("     ~1e-13, so that figure is below what the arithmetic can resolve.")
print("     The honest test is relative, and it passes.")
check("P commutes with collective Jz (< 1e-12)",
      float(np.linalg.norm(P47 @ Jz - Jz @ P47)) < 1e-12, True)

print("\n" + "="*80)
print("S3  PLATE CONSTANTS  --  exact rational arithmetic")
print("="*80)
lam = [0, 2, 6, 12, 20, 30, 42]
k2 = {l: ((l-6)*(l-30))**2 for l in lam}
off = {l: v for l, v in k2.items() if v != 0}
report("spec(K^2) nonzero", sorted(off.values()))
check("gap = 11664 = 108^2", min(off.values()), 11664)
check("  108^2", 108**2, 11664)
check("norm ||K^2|| = 186624", max(off.values()), 186624)

NORM = 99144
check("normalizer = 2/(gap+norm) denominator",
      F(2, min(off.values()) + max(off.values())), F(1, NORM))
lo = F(min(off.values()), NORM); hi = F(max(off.values()), NORM)
check("spec(A)\\{0} / 99144 lies in (0,2)", (lo > 0 and hi < 2), True)
report("  interval", f"[{float(lo):.6f}, {float(hi):.6f}]")

gam = {l: F(1) - F(v, NORM) for l, v in off.items()}
radius = max(abs(g) for g in gam.values())
check("spectral radius on E47-perp = 15/17", radius, F(15, 17))
report("  Gamma eigenvalues off E47", {l: str(g) for l, g in gam.items()})
report("  equioscillation at j=3 (+15/17) and j=6 (-15/17)",
       f"{gam[12]} , {gam[42]}")

print("\n" + "="*80)
print("S4  THE DESCENT  --  derived commutant, not asserted M5(C)")
print("="*80)
# The algebra of observables on E47 that commute with collective SU(2) is
# the nullspace of the adjoint-action Casimir superoperator
#        L(X) = sum_a [J_a, [J_a, X]]
# restricted to E47. Its dimension is sum over retained j of m_j^2.
basis = kvec[:, null]                       # 125 x 47 isometry onto E47
Jx_e = basis.conj().T @ Jx @ basis
Jy_e = basis.conj().T @ Jy @ basis
Jz_e = basis.conj().T @ Jz @ basis
n = dim47
Ie = np.eye(n, dtype=complex)

def ad(J):
    return np.kron(J, Ie) - np.kron(Ie, J.T)

L = sum(a @ a for a in (ad(Jx_e), ad(Jy_e), ad(Jz_e)))
L = 0.5*(L + L.conj().T)
lev = np.linalg.eigvalsh(L)
comm_dim = int(np.count_nonzero(np.abs(lev) < 1e-6))

check("dim commutant on E47 (numerical nullity)", comm_dim, 29)
check("= m_2^2 + m_5^2 = 25 + 4", mult[2]**2 + mult[5]**2, 29)
report("block structure", "M_5(C) (+) M_2(C)")
report("  M_5(C) from the j=2 multiplicity space C^5", 5**2)
report("  M_2(C) from the j=5 multiplicity space C^2", 2**2)

print("\n  >> The plate's certificate [6] reads '125 -> 47 -> M5(C)'.")
print("     M5(C) alone has dimension 25. The derived commutant has")
print("     dimension 29. The missing M2(C) is the j=5 branch -- the")
print("     protected logical qubit. The descent is 125 -> 47 -> 5 (+) 2.")

# full-carrier commutant, by the same multiplicity law
full_comm = sum(mult[j]**2 for j in range(7))
check("dim commutant on full carrier = sum m_j^2", full_comm, 65)

print("\n" + "="*80)
print("S5  STATE GEOMETRY  --  is D_can 24-dimensional?")
print("="*80)
# Unit-trace Hermitian elements of (+)_i M_{n_i} form a convex body of
# real dimension (sum n_i^2) - 1.
d_M5      = 5**2 - 1
d_M5_M2   = (5**2 + 2**2) - 1
check("dim D(M5(C))        = 24", d_M5, 24)
check("dim D(M5 (+) M2)    = 28", d_M5_M2, 28)
report("plate asserts D_can", 24)
print("  >> 24 is the state body of the j=2 branch only. Carrying both")
print("     protected branches the canonical state geometry is 28-")
print("     dimensional: 24 (M5) + 3 (M2) + 1 (branch population).")

print("\n" + "="*80)
print("S6  THE CONVERGENCE TABLE IN SECTION III")
print("="*80)
# Plate table, as printed
plate = {0: 0.291403, 1: 0.336356, 2: 0.364245, 5: 0.422568, 10: 0.512355,
         20: 0.677735, 50: 0.935264, 100: 0.996494}
# Real dynamics: Gamma = I - K^2/99144, rho -> Gamma rho Gamma (then renormalize)
Gam = I125 - (K @ K)/NORM
rng = np.random.default_rng(17)
A0 = rng.standard_normal((DIM, DIM)) + 1j*rng.standard_normal((DIM, DIM))
rho = A0 @ A0.conj().T
rho /= np.trace(rho).real

print(f"  {'k':>4s} {'plate C_k':>12s} {'plate R_k':>12s} {'(15/17)^k':>12s}"
      f" {'plate R_k <= bound?':>21s} {'true R_k':>12s}")
true_R = {}
r = rho.copy()
for k in range(101):
    if k in plate:
        Ck = float(np.trace(P47 @ r).real)
        true_R[k] = 1.0 - Ck
        bound = (15/17)**k
        pR = 1 - plate[k]
        ok = "yes" if pR <= bound + 1e-12 else "NO -- violates bound"
        print(f"  {k:4d} {plate[k]:12.6f} {pR:12.6f} {bound:12.3e}"
              f" {ok:>21s} {true_R[k]:12.3e}")
    r = Gam @ r @ Gam
    tr = np.trace(r).real
    if tr > 0:
        r /= tr

viol = sum(1 for k in plate if (1-plate[k]) > (15/17)**k + 1e-12)
check("plate rows that violate their own (15/17)^k bound", viol, 5)
report("  rows checked", len(plate))
report("  first violating step", min(k for k in plate
                                    if (1-plate[k]) > (15/17)**k + 1e-12))
check("true residual at k=50 is far below the bound",
      true_R[50] < (15/17)**50, True)
report("  true R_50", f"{true_R[50]:.3e}")
report("  bound (15/17)^50", f"{(15/17)**50:.3e}")
report("  plate R_50", f"{1-plate[50]:.3e}")
print("  >> Under rho -> Gamma rho Gamma the residual decays like")
print("     (15/17)^(2k), because Gamma acts on both sides. The real")
print("     trajectory beats the plate's bound; the printed one breaks it.")
print("     The Section III table is not output of this iteration.")

print("\n" + "="*80)
print(f"VERDICT   {len(PASS)} passed, {len(FAIL)} failed")
for f in FAIL:
    print("   FAILED:", f)
print("="*80)
print(f"""
  CONFIRMED EXACTLY
    dim V = 125, dim E47 = 47, Omega_c = 47/125 = 0.376
    gap 11664 = 108^2, ||K^2|| = 186624, normalizer 99144
    spectral radius on E47-perp = 15/17, equioscillating at j=3 and j=6
    P idempotent, K P = 0, [P, J] = 0

  CORRECTED BY DERIVATION
    descent      125 -> 47 -> M5(C) (+) M2(C)      not  -> M5(C)
    commutant    dim 29 = 5^2 + 2^2                 not  25
    geometry     dim D_can = 28                     not  24
    Section III  5 of 8 rows exceed (15/17)^k; true residual ~ (15/17)^(2k)
""")
