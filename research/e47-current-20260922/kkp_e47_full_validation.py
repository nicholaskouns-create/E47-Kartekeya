
import numpy as np
import sympy as sp
import math, json
from pathlib import Path

TOL = 1e-9
results = []

def add(name, status, value=None, expected=None, note=""):
    results.append({
        "claim": name,
        "status": status,
        "value": value,
        "expected": expected,
        "note": note
    })

# ============================================================
# I. E47 / SU(2) BEDROCK
# ============================================================

j = 2
m = np.arange(j, -j-1, -1, dtype=float)   # 2,1,0,-1,-2
d = 2*j + 1
Jz = np.diag(m)
Jp = np.zeros((d,d), dtype=complex)
for col, mm in enumerate(m):
    mp = mm + 1
    if mp <= j and col > 0:
        row = col - 1
        Jp[row, col] = np.sqrt(j*(j+1) - mm*(mm+1))
Jm = Jp.conj().T
Jx = (Jp + Jm)/2
Jy = (Jp - Jm)/(2j)

I5 = np.eye(d)
def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

Jxt = kron3(Jx,I5,I5)+kron3(I5,Jx,I5)+kron3(I5,I5,Jx)
Jyt = kron3(Jy,I5,I5)+kron3(I5,Jy,I5)+kron3(I5,I5,Jy)
Jzt = kron3(Jz,I5,I5)+kron3(I5,Jz,I5)+kron3(I5,I5,Jz)
C = Jxt@Jxt + Jyt@Jyt + Jzt@Jzt
C = (C + C.conj().T)/2
I = np.eye(C.shape[0])
K = (C - 6*I) @ (C - 30*I)
K = (K + K.conj().T)/2
K2 = K @ K

evals_C = np.linalg.eigvalsh(C)
rounded_C = np.rint(evals_C).astype(int)
vals, counts = np.unique(rounded_C, return_counts=True)

expected_vals = np.array([0,2,6,12,20,30,42])
expected_counts = np.array([1,9,25,28,27,22,13])

add("dim V = 5^3 = 125",
    "PASS" if C.shape == (125,125) else "FAIL",
    C.shape[0], 125)

add("spec(C) = {0,2,6,12,20,30,42}",
    "PASS" if np.array_equal(vals, expected_vals) else "FAIL",
    vals.tolist(), expected_vals.tolist())

add("Casimir eigenspace dimensions = [1,9,25,28,27,22,13]",
    "PASS" if np.array_equal(counts, expected_counts) else "FAIL",
    counts.tolist(), expected_counts.tolist())

# SU(2) irrep multiplicities: eigenspace dimension / (2J+1)
irrep_mult = [int(counts[k] // (2*k+1)) for k in range(7)]
add("SU(2) irrep multiplicities J=0..6 = [1,3,5,4,3,2,1]",
    "PASS" if irrep_mult == [1,3,5,4,3,2,1] else "FAIL",
    irrep_mult, [1,3,5,4,3,2,1])

evals_K = np.linalg.eigvalsh(K)
rankK = np.linalg.matrix_rank(K, tol=1e-8)
nullK = 125-rankK
add("K=(C-6I)(C-30I) is self-adjoint",
    "PASS" if np.linalg.norm(K-K.conj().T,2) < 1e-10 else "FAIL",
    float(np.linalg.norm(K-K.conj().T,2)), 0.0)

add("dim ker K = 47",
    "PASS" if nullK == 47 else "FAIL",
    nullK, 47)

add("rank K = dim im K = 78",
    "PASS" if rankK == 78 else "FAIL",
    rankK, 78)

omega = sp.Rational(47,125)
add("Omega_c = 47/125 = 0.376",
    "PASS" if float(omega) == 0.376 else "FAIL",
    str(omega) + f" = {float(omega):.15f}", "47/125 = 0.376")

# Kernel SU(2) decomposition: J=2 has multiplicity 5; J=5 multiplicity 2
add("ker K ≅ 5 V_2 ⊕ 2 V_5",
    "PASS" if irrep_mult[2] == 5 and irrep_mult[5] == 2 else "FAIL",
    f"{irrep_mult[2]} V_2 + {irrep_mult[5]} V_5", "5 V_2 + 2 V_5")

# Polynomial spectral projector onto C=6 and C=30
spec = [0,2,6,12,20,30,42]
def lagrange_projector(target):
    P = np.eye(125, dtype=complex)
    denom = 1.0
    for lam in spec:
        if lam == target: 
            continue
        P = P @ (C - lam*I)
        denom *= (target - lam)
    return P/denom

P6 = lagrange_projector(6)
P30 = lagrange_projector(30)
P = (P6 + P30)
P = (P + P.conj().T)/2

proj_err = np.linalg.norm(P@P-P, 2)
kp_err = np.linalg.norm(K@P, 2)
trP = np.trace(P).real

add("P_47 is an orthogonal projector",
    "PASS" if proj_err < 1e-10 else "FAIL",
    proj_err, "<1e-10")

add("K P_47 = 0",
    "PASS" if kp_err < 1e-9 else "FAIL",
    kp_err, "<1e-9")

add("tr(P_47)=rank(P_47)=47",
    "PASS" if abs(trP-47)<1e-9 and np.linalg.matrix_rank(P,tol=1e-8)==47 else "FAIL",
    {"trace":trP,"rank":int(np.linalg.matrix_rank(P,tol=1e-8))}, 47)

# K^2 spectrum, gap, norm
k2vals = []
for lam in spec:
    kval = (lam-6)*(lam-30)
    k2vals.append(kval*kval)
positive = sorted({x for x in k2vals if x>0})
gap = min(positive)
normk2 = max(positive)

add("positive spectrum(K^2) = {11664,12544,19600,32400,186624}",
    "PASS" if positive == [11664,12544,19600,32400,186624] else "FAIL",
    positive, [11664,12544,19600,32400,186624])

add("spectral gap Δ = 11664",
    "PASS" if gap == 11664 else "FAIL", gap, 11664)

add("||K^2|| = 186624",
    "PASS" if normk2 == 186624 else "FAIL", normk2, 186624)

eps_max = sp.Rational(2,normk2)
eps_star = sp.Rational(2,gap+normk2)
rho_star = sp.Rational(normk2-gap,normk2+gap)

add("stability interval 0<ε<2/||K^2|| = 1/93312",
    "PASS" if eps_max == sp.Rational(1,93312) else "FAIL",
    str(eps_max), "1/93312")

add("optimal ε* = 1/99144",
    "PASS" if eps_star == sp.Rational(1,99144) else "FAIL",
    str(eps_star), "1/99144")

add("optimal transverse contraction ρ*=15/17",
    "PASS" if rho_star == sp.Rational(15,17) else "FAIL",
    str(rho_star), "15/17")

Gamma = I - float(eps_star)*K2
G220 = np.linalg.matrix_power(Gamma,220)
g220err = np.linalg.norm(G220-P,2)
add("Γ^220 ≈ P_47 for Γ=I-ε*K^2, ε*=1/99144",
    "PASS" if g220err < 1e-10 else "FAIL",
    g220err, "<1e-10")

# ============================================================
# II. A5 / ICOSAHEDRAL RESTRICTION
# ============================================================

# SO(3) spin-l character for a rotation angle θ.
def chi_l(l, theta):
    if abs(theta) < 1e-14:
        return 2*l+1
    return math.sin((l+0.5)*theta)/math.sin(theta/2)

# Class order chosen to match the plate: [e, 5A, 5B, 3A, 2A]
angles = [0.0, 2*math.pi/5, 4*math.pi/5, 2*math.pi/3, math.pi]
chi_kernel = [round(5*chi_l(2,t)+2*chi_l(5,t)) for t in angles]
add("A5 character of ker K on [e,5A,5B,3A,2A] = [47,2,2,-7,3]",
    "PASS" if chi_kernel == [47,2,2,-7,3] else "FAIL",
    chi_kernel, [47,2,2,-7,3])

# Irreducible A5 characters in same class order
sqrt5 = sp.sqrt(5)
phi = (1+sqrt5)/2
phibar = (1-sqrt5)/2
A5_chars = {
    "1":  [1,1,1,1,1],
    "T1": [3,phi,phibar,0,-1],
    "T2": [3,phibar,phi,0,-1],
    "G":  [4,-1,-1,1,0],
    "H":  [5,0,0,-1,1],
}
class_sizes = [1,12,12,20,15]
chiKsym = [sp.Integer(x) for x in chi_kernel]
mults = {}
for name,ch in A5_chars.items():
    inner = sum(sp.Integer(sz)*sp.conjugate(sp.sympify(c))*q for sz,c,q in zip(class_sizes,ch,chiKsym))/60
    mults[name] = sp.simplify(inner)

add("A5 decomposition ker K = 2T1 ⊕ 2T2 ⊕ 7H",
    "PASS" if mults == {"1":0,"T1":2,"T2":2,"G":0,"H":7} else "FAIL",
    {k:str(v) for k,v in mults.items()},
    {"1":"0","T1":"2","T2":"2","G":"0","H":"7"})

phi_trace = sp.simplify(1 + 2*sp.cos(2*sp.pi/5))
add("1 + 2 cos(2π/5) = φ",
    "PASS" if sp.simplify(phi_trace-phi)==0 else "FAIL",
    str(phi_trace), str(phi))

# ============================================================
# III. RECURSION DYNAMICS
# ============================================================

q = sp.Rational(78,125)
GammaP = float(q)*I + float(omega)*P
gp_evals = np.linalg.eigvalsh((GammaP+GammaP.conj().T)/2)
u_gp = sorted(set(np.round(gp_evals,12)))
add("Γ_P=(1-Ωc)I+ΩcP has eigenvalues {78/125,1}",
    "PASS" if np.allclose(u_gp, [78/125,1.0]) else "FAIL",
    u_gp, [78/125,1.0])

p0 = float(omega)
n = 10
p10 = 1-(1-p0)*(1-float(omega))**n
add("scalar overlap recursion p_n=1-(1-p0)(1-Ωc)^n exceeds 99% by n=10 for p0=Ωc",
    "PASS" if p10 > 0.99 else "FAIL",
    p10, ">0.99")

# ============================================================
# IV. BABYLONIAN / GOLDEN-RATIO IDENTITIES
# ============================================================

x, tau = sp.symbols('x tau', positive=True)
R = sp.Rational(1,2)*(x + tau/x)
Rprime = sp.diff(R,x)
R2 = sp.diff(R,x,2)
fixed = sp.sqrt(tau)
R_at_fixed = sp.simplify(R.subs(x,fixed))
Rp_at_fixed = sp.simplify(Rprime.subs(x,fixed))
R2_at_fixed = sp.simplify(R2.subs(x,fixed))

add("Babylonian map R(x)=1/2(x+τ/x) fixes x*=sqrt(τ)",
    "PASS" if sp.simplify(R_at_fixed-fixed)==0 else "FAIL",
    str(R_at_fixed), str(fixed))

add("Babylonian map has quadratic local convergence: R'(sqrt τ)=0",
    "PASS" if Rp_at_fixed==0 else "FAIL",
    str(Rp_at_fixed), "0")

add("R''(sqrt τ)=1/sqrt(τ)",
    "PASS" if sp.simplify(R2_at_fixed-1/sp.sqrt(tau))==0 else "FAIL",
    str(R2_at_fixed), "1/sqrt(tau)")

phi_num = (1+math.sqrt(5))/2
phi_minus5 = phi_num**-5
add("Claim Ωc = φ^-5",
    "PASS" if abs(phi_minus5-float(omega))<1e-12 else "FAIL",
    {"47/125":float(omega),"phi^-5":phi_minus5},
    "equality")

# Find the actual exponent n such that phi^-n = 47/125
n_eff = -math.log(float(omega))/math.log(phi_num)
add("Exponent n solving φ^-n = 47/125",
    "INFO",
    n_eff, "not an integer; ≈2.0323")

# Fibonacci transfer matrix dominant eigenvalue
F = sp.Matrix([[1,1],[1,0]])
F_eigs = F.eigenvals()
add("Fibonacci recurrence has dominant eigenvalue φ",
    "PASS" if phi in F_eigs else "FAIL",
    [str(v) for v in F_eigs.keys()], str(phi))

poly = sp.Symbol('z')**2-sp.Symbol('z')-1
roots = sp.solve(poly)
add("x^2-x-1 roots are {φ,-1/φ}",
    "PASS" if set(map(sp.simplify,roots)) == set(map(sp.simplify,[phi,-1/phi])) else "FAIL",
    [str(sp.simplify(r)) for r in roots], [str(phi),str(-1/phi)])

# ============================================================
# V. PLATE 9 LAGRANGIAN: WHAT FOLLOWS SYMBOLICALLY
# ============================================================

Om, Omc, Lam = sp.symbols('Omega Omega_c Lambda', real=True)
V = Lam/4*(Om**2-Omc**2)**2
dV = sp.factor(sp.diff(V,Om))
add("V(Ω)=Λ/4(Ω^2-Ωc^2)^2 gives dV/dΩ=ΛΩ(Ω^2-Ωc^2)",
    "PASS" if sp.simplify(dV-Lam*Om*(Om**2-Omc**2))==0 else "FAIL",
    str(dV), "Lambda*Omega*(Omega^2-Omega_c^2)")

# Mass term exactly as shown in the plate: no explicit Omega dependence
N, chi, mpl = sp.symbols('N chi m_Pl', real=True)
ph = sp.Symbol('phi', positive=True)
M = mpl*ph**(-(N+chi/3))*(1-ph**(-5*N+2*chi))**sp.Rational(3,2)
dMdOm = sp.diff(M,Om)
add("Displayed recursive mass term has ∂M/∂Ω = 0 if N,χ are Ω-independent",
    "PASS" if dMdOm==0 else "FAIL",
    str(dMdOm), "0")

add("Displayed Ω field equation from the shown Lagrangian has no mass-source RHS unless N(Ω) or χ(Ω) is supplied",
    "FAIL" if dMdOm==0 else "PASS",
    "RHS = ∂M/∂Ω = 0 with the displayed definitions",
    "nonzero mass-source requires additional Ω dependence",
    "This is a structural test of the formula as printed, not of a modified model with N(Ω) or χ(Ω).")

# m_eff relation is an independent constitutive definition, not derived from displayed L
add("m_eff = m_static(1-Ω)",
    "CONDITIONAL",
    "internally consistent as a constitutive definition",
    "derivation from displayed Lagrangian",
    "The displayed Lagrangian does not contain this coupling explicitly.")

# ============================================================
# VI. BINDING-THEORY KERNEL THEOREM FOR PSD OPERATORS
# ============================================================

# Concrete numerical theorem check: construct three PSD matrices with common kernel span(e0,e1)
rng = np.random.default_rng(470125)
n_dim = 12
common = 2
As = []
for _ in range(3):
    B = rng.normal(size=(n_dim-common,n_dim-common))
    Q = B.T@B + np.eye(n_dim-common)*0.2
    A = np.zeros((n_dim,n_dim))
    A[common:,common:] = Q
    As.append(A)
S = sum(As)
null_sum = n_dim - np.linalg.matrix_rank(S,tol=1e-10)
null_each = [n_dim-np.linalg.matrix_rank(A,tol=1e-10) for A in As]
add("For PSD K_A,K_B,K_C: ker(K_A+K_B+K_C)=ker K_A ∩ ker K_B ∩ ker K_C",
    "PASS" if null_sum==common and all(x==common for x in null_each) else "FAIL",
    {"common_nullity":null_sum,"individual_nullities":null_each}, common,
    "General proof: x*(ΣK_i)x=Σ x*K_i x=0; PSD makes each term ≥0, hence each K_i^{1/2}x=0.")

# ============================================================
# VII. CULTURAL/ARITHMETIC MAPPINGS
# ============================================================

add("1+3+12+20+42 = 78",
    "PASS" if 1+3+12+20+42==78 else "FAIL",
    1+3+12+20+42, 78,
    "Arithmetic match only; it is not by itself a representation-theoretic derivation.")

add("1/φ ≈ 0.618",
    "PASS" if abs(1/phi_num-0.6180339887498948)<1e-12 else "FAIL",
    1/phi_num, 0.6180339887498948)

# ============================================================
# VIII. CLAIMS THAT PYTHON CANNOT TURN INTO EMPIRICAL PROOF
# ============================================================

for claim, note in [
    ("Collider resonance signatures / exact TeV targets",
     "Requires a fully specified interaction Hamiltonian/cross section and collider data."),
    ("Vacuum interferometer phase shift",
     "The formula can be simulated, but physical truth requires measured phase data and calibrated apparatus parameters."),
    ("PCO resonator inertial-mass variation",
     "Requires measured mass/inertia response; no computation alone establishes the effect."),
    ("Metric-propulsion thrust",
     "Requires a covariant stress-energy/metric solution and thrust data; the displayed proportionality is a prediction, not a proof."),
    ("Exact particle mass spectrum",
     "Requires the complete (N,chi) assignments and comparison dataset; the plate alone is insufficient."),
    ("Pyramid tangency K_p=phi",
     "Exact tangency equations/coordinates are not included in the supplied plate."),
    ("Lindblad fidelity 0.9997 for four initial states",
     "Needs the explicit Hamiltonian, collapse operators, rates, time grid, and four initial states."),
    ("13-pillar post-quantum security",
     "Functional code can be tested, but cryptographic security needs a precise adversary model and a reduction/proof or empirical cryptanalysis."),
    ("E47 implies Einstein geometry / propulsion",
     "Needs an explicit map from E47 states to a spacetime metric/stress tensor, then curvature and Einstein-residual computation.")
]:
    add(claim, "NEEDS_INPUT_OR_EXPERIMENT", None, None, note)

# ============================================================
# OUTPUT
# ============================================================

summary = {}
for r in results:
    summary[r["status"]] = summary.get(r["status"],0)+1

cert = {
    "schema":"KKP-E47-PYTHON-VALIDATION-1.0",
    "numpy_version":np.__version__,
    "sympy_version":sp.__version__,
    "summary":summary,
    "results":results
}

out = Path("/mnt/data")
(out/"kkp_e47_validation_certificate.json").write_text(json.dumps(cert,indent=2,default=str))

lines = []
lines.append("# KKP / E47 Python Validation Report")
lines.append("")
lines.append("## Summary")
for k,v in summary.items():
    lines.append(f"- **{k}**: {v}")
lines.append("")
lines.append("## Results")
for i,r in enumerate(results,1):
    lines.append(f"{i}. **{r['status']}** — {r['claim']}")
    if r["value"] is not None:
        lines.append(f"   - computed: `{r['value']}`")
    if r["expected"] is not None:
        lines.append(f"   - target: `{r['expected']}`")
    if r["note"]:
        lines.append(f"   - note: {r['note']}")
(out/"kkp_e47_validation_report.md").write_text("\n".join(lines))

print(json.dumps(summary, indent=2))
print("\nSelected numerical invariants:")
print("dim ker K =", nullK)
print("rank K    =", rankK)
print("Omega_c   =", float(omega))
print("gap       =", gap)
print("||K^2||   =", normk2)
print("eps*      =", eps_star)
print("rho*      =", rho_star)
print("||Gamma^220-P||_2 =", g220err)
print("A5 character =", chi_kernel)
print("A5 multiplicities =", {k:str(v) for k,v in mults.items()})
print("phi trace =", sp.simplify(phi_trace))
print("phi^-5    =", phi_minus5)
print("47/125    =", float(omega))
print("dM/dOmega =", dMdOm)