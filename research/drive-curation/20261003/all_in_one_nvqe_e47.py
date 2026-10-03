
import numpy as np
import pandas as pd
from fractions import Fraction
from scipy.linalg import expm, svd

np.set_printoptions(precision=12, suppress=True)

# ============================================================
# ALL-IN-ONE: FIRST-PRINCIPLES N-VQE / E47 HILBERT LIFT
# + su(2) ≅ so(3) Lie algebra audit
# ============================================================

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"

def int_to_base(n: int, base: int) -> str:
    if not (2 <= base <= 64):
        raise ValueError("base must be in [2,64]")
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    out = []
    while n:
        n, r = divmod(n, base)
        out.append(DIGITS[r])
    return sign + "".join(reversed(out))

def tagged(n: int, base: int) -> str:
    return f"{int_to_base(n, base)}_{base}"

# ------------------------------------------------------------
# 0. Golden-ratio / Heron correction
# ------------------------------------------------------------
phi = (1.0 + np.sqrt(5.0)) / 2.0
a = phi**-5
x_star = np.sqrt(a)
omega_e47 = Fraction(47, 125)

def T_a(x): return 0.5 * (x + a / x)
def Tprime(x): return 0.5 * (1.0 - a / (x*x))

x = 1.0
heron_rows = []
for n in range(7):
    err = x - x_star
    heron_rows.append(dict(n=n, x_n=x, error=err, residual=x*x-a))
    x = T_a(x)
heron_df = pd.DataFrame(heron_rows)

heron_error_identity_residuals = []
for row0, row1 in zip(heron_rows[:-1], heron_rows[1:]):
    e_n = row0["error"]
    predicted = e_n**2 / (2.0 * row0["x_n"])
    heron_error_identity_residuals.append(abs(row1["error"] - predicted))

# ------------------------------------------------------------
# 1. Spin-2 SU(2) generators from first principles
# ------------------------------------------------------------
j = 2
m = np.arange(j, -j-1, -1, dtype=float)  # [2,1,0,-1,-2]
d = 2*j + 1
Jz = np.diag(m).astype(complex)
Jp = np.zeros((d, d), dtype=complex)
for col in range(1, d):
    mm = m[col]
    Jp[col-1, col] = np.sqrt(j*(j+1) - mm*(mm+1))
Jm = Jp.conj().T
Jx = (Jp + Jm) / 2.0
Jy = (Jp - Jm) / (2.0j)
I5 = np.eye(d, dtype=complex)

# su(2) commutation audit (single particle)
comm_Jxy = np.linalg.norm(Jx@Jy - Jy@Jx - 1j*Jz)
comm_Jyz = np.linalg.norm(Jy@Jz - Jz@Jy - 1j*Jx)
comm_Jzx = np.linalg.norm(Jz@Jx - Jx@Jz - 1j*Jy)
casimir_single = np.linalg.norm(Jx@Jx + Jy@Jy + Jz@Jz - 6*np.eye(d))

# so(3) vector representation audit
A1 = np.array([[0,0,0],[0,0,-1],[0,1,0]],float)
A2 = np.array([[0,0,1],[0,0,0],[-1,0,0]],float)
A3 = np.array([[0,-1,0],[1,0,0],[0,0,0]],float)
comm_A12 = np.linalg.norm(A1@A2 - A2@A1 - A3)
comm_A23 = np.linalg.norm(A2@A3 - A3@A2 - A1)
comm_A31 = np.linalg.norm(A3@A1 - A1@A3 - A2)

# ------------------------------------------------------------
# 2. Three-body Hilbert space H125 = V2 ⊗ V2 ⊗ V2
# ------------------------------------------------------------
def kron3(A,B,C): return np.kron(np.kron(A,B),C)

Jx_tot = kron3(Jx,I5,I5) + kron3(I5,Jx,I5) + kron3(I5,I5,Jx)
Jy_tot = kron3(Jy,I5,I5) + kron3(I5,Jy,I5) + kron3(I5,I5,Jy)
Jz_tot = kron3(Jz,I5,I5) + kron3(I5,Jz,I5) + kron3(I5,I5,Jz)

# total J also must satisfy su(2)
comm_Jtot_xy = np.linalg.norm(Jx_tot@Jy_tot - Jy_tot@Jx_tot - 1j*Jz_tot)

C = Jx_tot@Jx_tot + Jy_tot@Jy_tot + Jz_tot@Jz_tot
I125 = np.eye(125, dtype=complex)
K = (C - 6*I125) @ (C - 30*I125)
H_NVE = K @ K

# ------------------------------------------------------------
# 3. Spectral reconstruction
# ------------------------------------------------------------
c_eval, _ = np.linalg.eigh(C)
c_rounded = np.rint(np.real(c_eval)).astype(int)
unique_C, mult_C = np.unique(c_rounded, return_counts=True)

expected_C = np.array([0,2,6,12,20,30,42])
expected_mult = np.array([1,9,25,28,27,22,13])

k2_eval, k2_evec = np.linalg.eigh(H_NVE)
k2_eval = np.real_if_close(k2_eval).real
zero_mask = np.isclose(k2_eval, 0.0, atol=1e-8)
positive_k2 = np.sort(np.unique(np.rint(k2_eval[~zero_mask]).astype(int)))

V0 = k2_evec[:, zero_mask]
P47 = V0 @ V0.conj().T

gap = int(np.rint(np.min(k2_eval[~zero_mask])))
norm_k2 = int(np.rint(np.max(k2_eval)))
epsilon_star = Fraction(1, 99144)
rho_star = Fraction(15, 17)

Gamma = I125 - float(epsilon_star) * H_NVE
gamma_eval = np.linalg.eigvalsh(Gamma)
transient = np.abs(gamma_eval[np.abs(gamma_eval - 1.0) > 1e-8])
rho_numeric = float(np.max(transient))

projector_idempotence = np.linalg.norm(P47 @ P47 - P47, ord="fro")
projector_hermiticity = np.linalg.norm(P47.conj().T - P47, ord="fro")
KP_residual = np.linalg.norm(K @ P47, ord="fro")
HPSD_min = float(np.min(k2_eval))

# ------------------------------------------------------------
# 4. 7-qubit lift 125 -> 128
# ------------------------------------------------------------
H128 = np.zeros((128,128), dtype=complex)
H128[:125,:125] = H_NVE
H128[125:,125:] = norm_k2 * np.eye(3)

h128_eval, h128_evec = np.linalg.eigh(H128)
ground128 = np.isclose(h128_eval, 0.0, atol=1e-8)
ground_dim_128 = int(np.sum(ground128))
gap_128 = int(np.rint(np.min(h128_eval[~ground128])))

rng = np.random.default_rng(47)
psi0 = rng.normal(size=128) + 1j*rng.normal(size=128)
psi0 /= np.linalg.norm(psi0)
Vg = h128_evec[:, ground128]
Pg128 = Vg @ Vg.conj().T

def energy(state,H): return float(np.real(np.vdot(state, H @ state)))
def ground_weight(state,P): return float(np.real(np.vdot(state, P @ state)))
def imaginary_time(state,t):
    coeff = h128_evec.conj().T @ state
    evolved = h128_evec @ (np.exp(-t*h128_eval) * coeff)
    return evolved / np.linalg.norm(evolved)

psi_t = imaginary_time(psi0, 1e-3)
E0 = energy(psi0, H128)
Et = energy(psi_t, H128)
W0 = ground_weight(psi0, Pg128)
Wt = ground_weight(psi_t, Pg128)

# ------------------------------------------------------------
# 5. Multiradix proof
# ------------------------------------------------------------
radix_rows = []
for base in (5,10,12,64):
    radix_rows.append({
        "base": base,
        "47": tagged(47, base),
        "78": tagged(78, base),
        "125": tagged(125, base),
        "identity": f"{tagged(47,base)} + {tagged(78,base)} = {tagged(125,base)}",
        "Ωc": "0.142_5" if base==5 else "0.376_10" if base==10 else f"{tagged(47,base)}/{tagged(125,base)}"
    })
radix_df = pd.DataFrame(radix_rows)

key_values = {
    "dim(V)":125, "dim(E47)":47, "complement":78,
    "C root 1":6, "C root 2":30,
    "gap(K²)":gap, "||K²||":norm_k2,
    "epsilon denom":99144, "7-qubit dim":128,
}
base_table = []
for name,val in key_values.items():
    base_table.append({
        "invariant":name,
        "base5":int_to_base(val,5),
        "base10":int_to_base(val,10),
        "base12":int_to_base(val,12),
        "base64":int_to_base(val,64),
    })
base_df = pd.DataFrame(base_table)

# ------------------------------------------------------------
# 6. Formal checks (including Lie algebra)
# ------------------------------------------------------------
checks = {
    "[Jx,Jy]=iJz single": comm_Jxy < 1e-12,
    "[Jy,Jz]=iJx single": comm_Jyz < 1e-12,
    "[Jz,Jx]=iJy single": comm_Jzx < 1e-12,
    "C_single = 6I": casimir_single < 1e-12,
    "[A1,A2]=A3": comm_A12 < 1e-12,
    "[A2,A3]=A1": comm_A23 < 1e-12,
    "[A3,A1]=A2": comm_A31 < 1e-12,
    "[Jx_tot,Jy_tot]=iJz_tot": comm_Jtot_xy < 1e-10,
    "Heron fixed point solves x²=a": abs(x_star*x_star-a) < 1e-14,
    "Heron T'(x*)=0": abs(Tprime(x_star)) < 1e-14,
    "Heron quadratic error identity": max(heron_error_identity_residuals) < 1e-14,
    "dim(V2^⊗3)=125": C.shape==(125,125),
    "Casimir spectrum exact": np.array_equal(unique_C, expected_C),
    "Casimir multiplicities exact": np.array_equal(mult_C, expected_mult),
    "K² PSD": HPSD_min > -1e-8,
    "ground energy =0": abs(np.min(k2_eval)) < 1e-8,
    "ground mult =47": int(np.sum(zero_mask))==47,
    "positive K² spectrum": np.array_equal(positive_k2, np.array([11664,12544,19600,32400,186624])),
    "gap=11664": gap==11664,
    "norm=186624": norm_k2==186624,
    "P47²=P47": projector_idempotence < 1e-10,
    "P47†=P47": projector_hermiticity < 1e-10,
    "K P47=0": KP_residual < 1e-8,
    "rho*=15/17": abs(rho_numeric-float(rho_star)) < 1e-10,
    "128 keeps mult 47": ground_dim_128==47,
    "128 keeps gap 11664": gap_128==11664,
    "imag energy dec": Et < E0,
    "imag weight inc": Wt > W0,
}
check_df = pd.DataFrame([{"check":k,"status":"PASS" if v else "FAIL"} for k,v in checks.items()])

# ------------------------------------------------------------
# 7. Print certificate
# ------------------------------------------------------------
print("FIRST-PRINCIPLES PROOF — ALL-IN-ONE")
print("N-VQE / E47 + su(2) ≅ so(3) Lie audit + Hilbert lift")
print("="*78)
print("\nI. LIE ALGEBRA AUDIT")
print(f"||[Jx,Jy]-iJz|| = {comm_Jxy:.3e}  ||[Jy,Jz]-iJx|| = {comm_Jyz:.3e}  ||[Jz,Jx]-iJy|| = {comm_Jzx:.3e}")
print(f"||C_single-6I|| = {casimir_single:.3e}")
print(f"||[A1,A2]-A3|| = {comm_A12:.3e}  ||[A2,A3]-A1|| = {comm_A23:.3e}  ||[A3,A1]-A2|| = {comm_A31:.3e}")
print(f"||[Jx_tot,Jy_tot]-iJz_tot|| = {comm_Jtot_xy:.3e}")

print("\nII. SCALAR / HERON")
print(f"phi={phi:.15f}  a=phi^-5={a:.15f}  sqrt(a)=phi^-5/2={x_star:.15f}  T'(x*)={Tprime(x_star):.3e}")
print(f"Ωc=47/125={float(omega_e47):.15f}")

print("\nIII. HILBERT SPACE")
print(f"spec(C)={unique_C.tolist()}  mult={mult_C.tolist()}")
print(f"positive spec(K²)={positive_k2.tolist()}  gap={gap}  ||K²||={norm_k2}")
print(f"||P²-P||_F={projector_idempotence:.3e}  ||P†-P||_F={projector_hermiticity:.3e}  ||KP||_F={KP_residual:.3e}")
print(f"epsilon*=1/99144  rho*=15/17={float(rho_star)}  rho_numeric={rho_numeric:.15f}")

print("\nIV. 7-QUBIT LIFT H128 = K² ⊕ 186624 I3")
print(f"ground mult={ground_dim_128}  gap={gap_128}  W0={W0:.12f} -> Wt={Wt:.12f}  E0={E0:.6f} -> Et={Et:.3e}")

print("\nV. MULTIRADIX IDENTITY 47+78=125")
print(radix_df.to_string(index=False))
print("\nInvariants in bases 5,10,12,64:")
print(base_df.to_string(index=False))

print("\nVI. HERON ITERATION")
print(heron_df.to_string(index=False))

print("\nVII. MACHINE CHECKS")
print(check_df.to_string(index=False))
passed=sum(checks.values())
print(f"\nCERTIFICATE: {passed}/{len(checks)} PASS")
print("Evidence: algebra, fixed-point, spectrum, projector, contraction, 128-state sim.")
print("Not claimed: consciousness, phenomenology, phi-derived Ωc.")
