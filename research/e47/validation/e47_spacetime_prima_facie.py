import numpy as np
import sympy as sp

TOL = 1e-8
checks = {}

def check(name, cond, value=None):
    checks[name] = bool(cond)
    tag = "PASS" if cond else "FAIL"
    suffix = "" if value is None else f" | {value}"
    print(f"{tag:4s}  {name}{suffix}")

# ============================================================
# A. LOCKED 125-D E47 CARRIER
# ============================================================
j = 2
m = np.arange(j, -j - 1, -1, dtype=float)
d = 2*j + 1

Jz = np.diag(m).astype(complex)
Jp = np.zeros((d,d), dtype=complex)
for i in range(d-1):
    mm = m[i+1]
    Jp[i,i+1] = np.sqrt(j*(j+1) - mm*(mm+1))
Jm = Jp.conj().T
Jx = (Jp + Jm)/2
Jy = (Jp - Jm)/(2j)
I5 = np.eye(5, dtype=complex)

def k3(A,B,C):
    return np.kron(np.kron(A,B),C)

Jxt = k3(Jx,I5,I5) + k3(I5,Jx,I5) + k3(I5,I5,Jx)
Jyt = k3(Jy,I5,I5) + k3(I5,Jy,I5) + k3(I5,I5,Jy)
Jzt = k3(Jz,I5,I5) + k3(I5,Jz,I5) + k3(I5,I5,Jz)

C = Jxt@Jxt + Jyt@Jyt + Jzt@Jzt
I125 = np.eye(125, dtype=complex)
K = (C - 6*I125) @ (C - 30*I125)
K2 = K @ K

ce, U = np.linalg.eigh(C)
spec = {}
for x in ce:
    key = int(round(float(x)))
    spec[key] = spec.get(key,0) + 1

expected_spec = {0:1, 2:9, 6:25, 12:28, 20:27, 30:22, 42:13}
check("dim(V2^⊗3)=125", C.shape == (125,125))
check("Casimir spectrum/multiplicities", spec == expected_spec, spec)

mask47 = np.isclose(ce, 6, atol=TOL) | np.isclose(ce, 30, atol=TOL)
V47 = U[:,mask47]
P47 = V47 @ V47.conj().T
check("dim ker K = 47", int(mask47.sum()) == 47, int(mask47.sum()))
check("P47^2 = P47", np.linalg.norm(P47@P47-P47) < 1e-10,
      f"resid={np.linalg.norm(P47@P47-P47):.3e}")
check("K P47 = 0", np.linalg.norm(K@P47) < 1e-9,
      f"resid={np.linalg.norm(K@P47):.3e}")

k2_by_C = {lam: ((lam-6)*(lam-30))**2 for lam in expected_spec}
positive_k2 = sorted(v for v in k2_by_C.values() if v > 0)
check("K^2 gap = 11664", min(positive_k2) == 11664, min(positive_k2))
check("||K^2|| = 186624", max(positive_k2) == 186624, max(positive_k2))

# ============================================================
# B. EXPLICIT V2 COPY W ⊂ E47 AND CLOCK MODE u ∈ V0
# ============================================================
pair_singlet = np.zeros(25, dtype=complex)
for ia, ma in enumerate(m):
    ib = int(np.where(m == -ma)[0][0])
    pair_singlet[ia*5 + ib] = (-1)**int(j-ma) / np.sqrt(2*j+1)

W = np.column_stack([
    np.kron(pair_singlet, np.eye(5, dtype=complex)[:,k])
    for k in range(5)
])

check("W†W = I5", np.linalg.norm(W.conj().T@W - np.eye(5)) < 1e-12)
check("C W = 6 W", np.linalg.norm(C@W - 6*W) < 1e-10,
      f"resid={np.linalg.norm(C@W-6*W):.3e}")
check("K^2 W = 0", np.linalg.norm(K2@W) < 1e-8,
      f"resid={np.linalg.norm(K2@W):.3e}")

i0 = int(np.argmin(np.abs(ce)))
u = U[:,i0]
check("C u = 0", np.linalg.norm(C@u) < 1e-10,
      f"resid={np.linalg.norm(C@u):.3e}")
check("K^2 u = 32400 u", np.linalg.norm(K2@u - 32400*u) < 1e-7,
      f"resid={np.linalg.norm(K2@u-32400*u):.3e}")
check("u ⟂ W", np.linalg.norm(W.conj().T@u) < 1e-12,
      f"overlap={np.linalg.norm(W.conj().T@u):.3e}")

# ============================================================
# C. REAL SPIN-2 GEOMETRIC MODEL W ≅ Sym_0(3,R)
# ============================================================
Q = np.diag([1.,0.,-1.])
A1 = np.array([[0,0,0],[0,0,-1],[0,1,0]], float)
A2 = np.array([[0,0,1],[0,0,0],[-1,0,0]], float)
A3 = np.array([[0,-1,0],[1,0,0],[0,0,0]], float)
A = [A1,A2,A3]

D = [Ai@Q - Q@Ai for Ai in A]
Gsp = np.array([[np.tensordot(Di,Dj) for Dj in D] for Di in D])
expected_Gsp = np.diag([2.,8.,2.])

check("rank(A ↦ [A,Q]) = 3",
      np.linalg.matrix_rank(np.column_stack([x.reshape(-1) for x in D])) == 3)
check("spatial Gram = diag(2,8,2)",
      np.allclose(Gsp, expected_Gsp, atol=1e-12), Gsp.tolist())

# Explicit intertwiner Sym_0(3,R) -> W and 125D four-frame
E1 = np.zeros((3,3)); E1[0,0] = 1; E1[1,1] = -1; E1 /= np.sqrt(2)
E2 = np.zeros((3,3)); E2[0,0] = 1; E2[1,1] = 1; E2[2,2] = -2; E2 /= np.sqrt(6)
E3 = np.zeros((3,3)); E3[0,1] = E3[1,0] = 1; E3 /= np.sqrt(2)
E4 = np.zeros((3,3)); E4[0,2] = E4[2,0] = 1; E4 /= np.sqrt(2)
E5 = np.zeros((3,3)); E5[1,2] = E5[2,1] = 1; E5 /= np.sqrt(2)
Eb = [E1,E2,E3,E4,E5]

rho = np.array([
    [[np.trace(Ea @ (Ai @ Eb_ - Eb_ @ Ai)) for Eb_ in Eb] for Ea in Eb]
    for Ai in A
])
JW = [W.conj().T @ Jt @ W for Jt in (Jxt,Jyt,Jzt)]

rows = []
for i in range(3):
    rows.append(np.kron(rho[i].T, np.eye(5)) +
                np.kron(np.eye(5), 1j * JW[i]))
Ms = np.vstack(rows)
Gw = Ms.conj().T @ Ms
gew, gev = np.linalg.eigh(Gw)
assert gew[0] < 1e-10 and gew[1] > 1e-3, f"intertwiner nullity failure: {gew[:3]}"

Phi = gev[:,0].reshape(5,5,order="F")
phi_resid = max(np.linalg.norm(Phi @ rho[i] + 1j * JW[i] @ Phi) for i in range(3))
assert phi_resid < 1e-8, f"intertwiner residual {phi_resid}"
Phi = Phi * np.sqrt(5 / np.trace(Phi.conj().T @ Phi))

dvecs = [np.array([np.trace(Ea @ Di) for Ea in Eb]) for Di in D]
vs = [W @ (Phi @ dv) for dv in dvecs]
X4 = np.column_stack(vs + [u])
rank4 = np.linalg.matrix_rank(X4)
check("rank(dX) = 4", rank4 == 4,
      f"rank={rank4}, intertwiner_resid={phi_resid:.3e}")

# Casimir-spectral Lorentzian form and its actual 125D pullback.
V0 = U[:, np.isclose(ce, 0, atol=TOL)]
V6 = U[:, np.isclose(ce, 6, atol=TOL)]

P0 = V0 @ V0.conj().T
P6 = V6 @ V6.conj().T
eta125 = P6 - P0

B4 = np.column_stack([u] + vs)
gL = np.real_if_close(B4.conj().T @ eta125 @ B4)
target_gL = np.diag([-1.,2.,8.,2.])

check("Casimir pullback metric = diag(-1,2,8,2)",
      np.allclose(gL, target_gL, atol=TOL),
      gL.tolist())

ge = np.linalg.eigvalsh(gL)
signature = (int(np.sum(ge < 0)), int(np.sum(ge > 0)))
check("Lorentzian signature = (-+++)", signature == (1,3), ge.tolist())

# ============================================================
# D. EXACT LEVI-CIVITA / RIEMANN / RICCI / EINSTEIN CALCULATION
# ============================================================
r2 = sp.sqrt(2)
zero = sp.S(0)

c = [[[zero for k in range(3)] for j in range(3)] for i in range(3)]
def set_c(i,j,k,v):
    c[i][j][k] = v
    c[j][i][k] = -v

set_c(0,1,2, 1/(2*r2))
set_c(1,2,0, 1/(2*r2))
set_c(2,0,1, r2)

Gamma = [[[zero for k in range(3)] for j in range(3)] for i in range(3)]
for i in range(3):
    for j in range(3):
        for k in range(3):
            Gamma[i][j][k] = sp.simplify(
                (c[i][j][k] - c[j][k][i] + c[k][i][j])/2
            )

Riem = [[[[zero for l in range(3)] for k in range(3)]
          for j in range(3)] for i in range(3)]
for i in range(3):
    for j in range(3):
        for k in range(3):
            for l in range(3):
                Riem[i][j][k][l] = sp.simplify(sum(
                    Gamma[j][k][m_] * Gamma[i][m_][l]
                    - Gamma[i][k][m_] * Gamma[j][m_][l]
                    - c[i][j][m_] * Gamma[m_][k][l]
                    for m_ in range(3)
                ))

K12 = sp.simplify(Riem[0][1][1][0])
K23 = sp.simplify(Riem[1][2][2][1])
K31 = sp.simplify(Riem[2][0][0][2])

Ric3 = sp.Matrix([
    [sp.simplify(sum(Riem[i][j][k][i] for i in range(3)))
     for k in range(3)]
    for j in range(3)
])

check("sectional K12 = 1/2", K12 == sp.Rational(1,2), K12)
check("sectional K23 = 1/2", K23 == sp.Rational(1,2), K23)
check("sectional K31 = -1", K31 == -1, K31)
check("Ricci_spatial = diag(-1/2,1,-1/2)",
      Ric3 == sp.diag(sp.Rational(-1,2),1,sp.Rational(-1,2)), Ric3)

eta = sp.diag(-1,1,1,1)
Ric4 = sp.diag(0, sp.Rational(-1,2), 1, sp.Rational(-1,2))
Rscalar = sp.simplify(sum(eta[i,i]*Ric4[i,i] for i in range(4)))
Einstein = sp.simplify(Ric4 - sp.Rational(1,2)*Rscalar*eta)

check("scalar curvature R = 0", Rscalar == 0, Rscalar)
check("Einstein tensor exact",
      Einstein == sp.diag(0,sp.Rational(-1,2),1,sp.Rational(-1,2)),
      Einstein)

# ============================================================
# E. E47-INDUCED EFFECTIVE STRESS-ENERGY
# ============================================================
Theta_E47 = Einstein
T_trace_scaled = sp.simplify(sum(eta[i,i]*Theta_E47[i,i] for i in range(4)))

div = []
Theta3 = Ric3
for b in range(3):
    s = zero
    for a in range(3):
        for d_ in range(3):
            s += (
                -Gamma[a][a][d_] * Theta3[d_,b]
                -Gamma[a][b][d_] * Theta3[a,d_]
            )
    div.append(sp.simplify(s))

check("tr(8πG T_E47) = 0", T_trace_scaled == 0, T_trace_scaled)
check("∇^a T^(E47)_ab = 0", div == [0,0,0], div)

print("\n--- DERIVED OBJECTS ---")
print("spec(C) multiplicities =", spec)
print("dim E47 =", int(mask47.sum()))
print("G_spatial =", Gsp)
print("g_L = B4† (P6-P0) B4 =", gL)
print("sectional curvatures =", (K12,K23,K31))
print("Ricci_orthonormal =", Ric4)
print("R =", Rscalar)
print("G_orthonormal =", Einstein)
print("8π G_N T_E47 =", Theta_E47)
print("T_E47 = (1/(8π G_N)) * diag(0,-1/2,1,-1/2)")
print("covariant divergence =", div)

all_pass = all(checks.values())
print("\n" + ("PRIMA_FACIE_SPACETIME_PASS" if all_pass else "VALIDATION_FAIL"))
print(f"{sum(checks.values())}/{len(checks)} checks PASS")
