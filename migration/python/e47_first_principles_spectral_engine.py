#!/usr/bin/env python3
"""
E47 FIRST-PRINCIPLES EXECUTABLE THEOREM PACKAGE

Derives the full spectral chain from spin-2 generators:

    V2^{⊗3}
      -> J_tot,x,y,z
      -> C = J_tot^2
      -> spectrum / multiplicities
      -> K = (C-6I)(C-30I)
      -> E47 = ker(K)
      -> P47
      -> Gamma = I - eps*K^2
      -> Gamma^n -> P47

No Clebsch-Gordan multiplicities are hard-coded.

Requires:
    numpy

Optional:
    matplotlib   (only if you enable MAKE_PLOT below)
"""

import json
from pathlib import Path
import numpy as np

np.set_printoptions(precision=12, suppress=True, linewidth=160)

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

TOL = 1e-9
SEED = 470125
rng = np.random.default_rng(SEED)

OUT_DIR = Path("./e47_artifacts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MAKE_PLOT = False


# =====================================================================
# 1. SINGLE-SPIN j=2 REPRESENTATION
# =====================================================================

j = 2
d = 2 * j + 1
assert d == 5

# Basis ordering: |m>, m = +2,+1,0,-1,-2
mvals = np.arange(j, -j - 1, -1, dtype=float)

Jz = np.diag(mvals).astype(complex)
Jp = np.zeros((d, d), dtype=complex)

# J_+ |m> = sqrt(j(j+1)-m(m+1)) |m+1>
for col, m in enumerate(mvals):
    mp = m + 1
    if mp <= j:
        rows = np.where(np.isclose(mvals, mp))[0]
        if len(rows):
            row = int(rows[0])
            Jp[row, col] = np.sqrt(j * (j + 1) - m * (m + 1))

Jm = Jp.conj().T
Jx = 0.5 * (Jp + Jm)
Jy = (Jp - Jm) / (2j)

I5 = np.eye(d, dtype=complex)

# su(2) checks
def fro(A):
    return float(np.linalg.norm(A, "fro"))

assert fro(Jx @ Jy - Jy @ Jx - 1j * Jz) < TOL
assert fro(Jy @ Jz - Jz @ Jy - 1j * Jx) < TOL
assert fro(Jz @ Jx - Jx @ Jz - 1j * Jy) < TOL

single_C = Jx @ Jx + Jy @ Jy + Jz @ Jz
assert fro(single_C - j * (j + 1) * I5) < TOL


# =====================================================================
# 2. THREE-SPIN CARRIER H = V2 ⊗ V2 ⊗ V2
# =====================================================================

def kron3(A, B, C):
    return np.kron(np.kron(A, B), C)

I = I5

Jx_tot = kron3(Jx, I, I) + kron3(I, Jx, I) + kron3(I, I, Jx)
Jy_tot = kron3(Jy, I, I) + kron3(I, Jy, I) + kron3(I, I, Jy)
Jz_tot = kron3(Jz, I, I) + kron3(I, Jz, I) + kron3(I, I, Jz)

dim_H = Jx_tot.shape[0]
assert dim_H == 125

# Total quadratic Casimir
C = Jx_tot @ Jx_tot + Jy_tot @ Jy_tot + Jz_tot @ Jz_tot
C = 0.5 * (C + C.conj().T)  # numerical Hermitian symmetrization

assert fro(C - C.conj().T) < TOL

# Casimir must commute with total angular momentum
assert fro(C @ Jx_tot - Jx_tot @ C) < 1e-8
assert fro(C @ Jy_tot - Jy_tot @ C) < 1e-8
assert fro(C @ Jz_tot - Jz_tot @ C) < 1e-8


# =====================================================================
# 3. DERIVE SPECTRUM AND MULTIPLICITIES — NOTHING HARD-CODED
# =====================================================================

evals, evecs = np.linalg.eigh(C)

# Round eigenvalues to nearest integer, then validate
evals_round = np.rint(evals).astype(int)
assert np.max(np.abs(evals - evals_round)) < 1e-8

unique_lam, sector_dims = np.unique(evals_round, return_counts=True)

expected_lam = np.array([0, 2, 6, 12, 20, 30, 42])
assert np.array_equal(unique_lam, expected_lam)
assert int(np.sum(sector_dims)) == dim_H

# Recover J from lambda = J(J+1)
spins = []
for lam in unique_lam:
    J = int(round((-1 + np.sqrt(1 + 4 * lam)) / 2))
    assert J * (J + 1) == lam
    spins.append(J)
spins = np.array(spins, dtype=int)

irrep_dims = 2 * spins + 1

# Multiplicity m_J = dimension of eigenspace / (2J+1)
multiplicities = sector_dims // irrep_dims
assert np.array_equal(multiplicities * irrep_dims, sector_dims)

# This is the derived Clebsch-Gordan decomposition:
# V2^⊗3 ≅ V0 ⊕ 3V1 ⊕ 5V2 ⊕ 4V3 ⊕ 3V4 ⊕ 2V5 ⊕ V6
expected_sector_dims = np.array([1, 9, 25, 28, 27, 22, 13])
expected_mults = np.array([1, 3, 5, 4, 3, 2, 1])
assert np.array_equal(sector_dims, expected_sector_dims)
assert np.array_equal(multiplicities, expected_mults)


# =====================================================================
# 4. CONSTRAINT OPERATOR K AND E47
# =====================================================================

I125 = np.eye(dim_H, dtype=complex)

K = (C - 6 * I125) @ (C - 30 * I125)
K = 0.5 * (K + K.conj().T)

assert fro(K - K.conj().T) < 1e-8

mu = (unique_lam - 6) * (unique_lam - 30)
mu2 = mu ** 2

kernel_mask = (mu == 0)
dim_E47 = int(np.sum(sector_dims[kernel_mask]))
dim_perp = dim_H - dim_E47

assert dim_E47 == 47
assert dim_perp == 78

# Direct numerical rank / nullity check
k_evals = np.linalg.eigvalsh(K)
nullity_K = int(np.sum(np.abs(k_evals) < 1e-8))
rank_K = dim_H - nullity_K

assert nullity_K == 47
assert rank_K == 78

omega_c = dim_E47 / dim_H
assert omega_c == 47 / 125


# =====================================================================
# 5. EXACT SPECTRAL PROJECTOR P47
# =====================================================================

# The following degree-6 polynomial is 1 at lambda=6,30
# and 0 at lambda=0,2,12,20,42.
#
# p(lambda) =
#   lambda(lambda-2)(lambda-12)(lambda-20)(lambda-31)(lambda-42)
#   / 1,814,400
#
# The root 31 is an interpolation root chosen so p(6)=p(30)=1.

def poly_P47_matrix(A):
    return (
        A
        @ (A - 2 * I125)
        @ (A - 12 * I125)
        @ (A - 20 * I125)
        @ (A - 31 * I125)
        @ (A - 42 * I125)
    ) / 1814400.0

P47_poly = poly_P47_matrix(C)
P47_poly = 0.5 * (P47_poly + P47_poly.conj().T)

# Independent spectral construction from eigenvectors
mask_evecs = np.isin(evals_round, [6, 30])
V47 = evecs[:, mask_evecs]
P47_spec = V47 @ V47.conj().T

# Projector checks
assert V47.shape == (125, 47)
assert fro(P47_poly - P47_spec) < 1e-8
assert fro(P47_spec @ P47_spec - P47_spec) < 1e-8
assert fro(P47_spec - P47_spec.conj().T) < 1e-8
assert fro(K @ P47_spec) < 1e-8
assert abs(np.trace(P47_spec).real - 47.0) < 1e-8

# Completeness
P_perp = I125 - P47_spec
assert fro(P_perp @ P47_spec) < 1e-8
assert fro(P_perp @ P_perp - P_perp) < 1e-8


# =====================================================================
# 6. POSITIVE DISSIPATIVE GENERATOR G = K^2
# =====================================================================

G = K @ K
G = 0.5 * (G + G.conj().T)

G_evals = np.linalg.eigvalsh(G)
positive_G = G_evals[G_evals > 1e-8]

spectral_gap = float(np.min(positive_G))
lambda_max = float(np.max(G_evals))
kappa = lambda_max / spectral_gap

assert np.isclose(spectral_gap, 11664.0)
assert np.isclose(lambda_max, 186624.0)
assert np.isclose(kappa, 16.0)


# =====================================================================
# 7. OPTIMAL DISCRETE CONTRACTION
# =====================================================================

# Richardson-optimal step for eigenvalues in [Delta, Lambda_max]
eps_star = 2.0 / (lambda_max + spectral_gap)
rho_star = (kappa - 1.0) / (kappa + 1.0)

assert np.isclose(eps_star, 1 / 99144)
assert np.isclose(rho_star, 15 / 17)

Gamma = I125 - eps_star * G

# Kernel is fixed point set
assert fro(Gamma @ P47_spec - P47_spec) < 1e-8

# Spectral radius / operator norm on the invariant complement.
# Do NOT pair separately sorted eigvalsh(G) and eigvalsh(Gamma):
# gamma(lambda)=1-eps*lambda reverses the spectral ordering.
Gamma_perp = P_perp @ Gamma @ P_perp
rho_numeric = float(np.linalg.norm(Gamma_perp, 2))
assert np.isclose(rho_numeric, rho_star, atol=1e-10)


# =====================================================================
# 8. NUMERICAL DEMONSTRATION Gamma^n -> P47
# =====================================================================

# Random normalized state
x0 = rng.normal(size=dim_H) + 1j * rng.normal(size=dim_H)
x0 /= np.linalg.norm(x0)

x_kernel = P47_spec @ x0
x = x0.copy()

history = []

for n in range(0, 221):
    err_vec = x - x_kernel
    err = float(np.linalg.norm(err_vec))
    bound = float((rho_star ** n) * np.linalg.norm(P_perp @ x0))
    history.append((n, err, bound))
    if n < 220:
        x = Gamma @ x

assert np.linalg.norm(x - x_kernel) < 1e-10

# Operator convergence demonstration
Gamma_n = np.linalg.matrix_power(Gamma, 220)
operator_error_220 = fro(Gamma_n - P47_spec)
assert operator_error_220 < 1e-10


# =====================================================================
# 9. CONTINUOUS-TIME CONTRACTION CHECK
# =====================================================================

# Because G is diagonal in the C eigenbasis:
# exp(-tG) = V diag(exp(-t lambda_i(G))) V†
#
# As t -> infinity, this converges to P47.

def expm_G(t):
    decay = np.exp(-t * (k_evals ** 2))
    # K and C share eigenvectors because K is polynomial in C.
    # Construct using the C eigenbasis and eigenvalues q(lambda)^2:
    g_diag = ((evals - 6.0) * (evals - 30.0)) ** 2
    return (evecs * np.exp(-t * g_diag)) @ evecs.conj().T

E_t = expm_G(0.01)
continuous_error = fro(E_t - P47_spec)

# Bound is dominated by exp(-Delta t) on complement
continuous_bound = np.exp(-spectral_gap * 0.01) * np.sqrt(dim_perp)
assert continuous_error <= continuous_bound * (1 + 1e-8)


# =====================================================================
# 10. MACHINE-READABLE CERTIFICATE
# =====================================================================

certificate = {
    "name": "E47 First-Principles Spectral Contraction Certificate",
    "seed": SEED,
    "primitive_spin": j,
    "primitive_dimension": d,
    "carrier_dimension": dim_H,
    "casimir_spectrum": unique_lam.tolist(),
    "sector_dimensions": sector_dims.tolist(),
    "irrep_multiplicities": multiplicities.tolist(),
    "constraint_mu": mu.tolist(),
    "constraint_mu_squared": mu2.tolist(),
    "kernel_dimension": dim_E47,
    "complement_dimension": dim_perp,
    "rank_K": rank_K,
    "omega_c": omega_c,
    "spectral_gap_K2": spectral_gap,
    "lambda_max_K2": lambda_max,
    "condition_number": kappa,
    "epsilon_star": eps_star,
    "rho_star": rho_star,
    "trace_P47": float(np.trace(P47_spec).real),
    "projector_idempotence_fro": fro(P47_spec @ P47_spec - P47_spec),
    "projector_polynomial_vs_spectral_fro": fro(P47_poly - P47_spec),
    "KP47_fro": fro(K @ P47_spec),
    "Gamma220_minus_P47_fro": operator_error_220,
    "continuous_t_0p01_minus_P47_fro": continuous_error,
    "status": "PASS"
}

cert_path = OUT_DIR / "e47_first_principles_certificate.json"
cert_path.write_text(json.dumps(certificate, indent=2))


# =====================================================================
# 11. HUMAN-READABLE REPORT
# =====================================================================

print("\n[✓] FIRST-PRINCIPLES E47 SPECTRAL PACKAGE: PASS\n")

print("Derived carrier:")
print(f"  H = V_2^⊗3, dim(H) = {dim_H}\n")

print("Derived Casimir decomposition:")
print("  J   lambda=J(J+1)   eigenspace_dim   multiplicity   irrep_dim")
for J, lam, dim_s, mult, ir_dim in zip(
    spins, unique_lam, sector_dims, multiplicities, irrep_dims
):
    print(f"  {J:1d}        {lam:2d}              {dim_s:3d}             {mult:2d}          {ir_dim:2d}")

print("\nDerived decomposition:")
parts = []
for J, mult in zip(spins, multiplicities):
    parts.append(f"{'' if mult == 1 else str(mult)}V_{J}")
print("  V_2^⊗3 ≅ " + " ⊕ ".join(parts))

print("\nConstraint:")
print("  K = (C - 6I)(C - 30I)")
print(f"  dim ker(K) = {dim_E47}")
print(f"  rank(K)    = {rank_K}")
print("  E47 = E_6 ⊕ E_30 ≅ 5V_2 ⊕ 2V_5")
print(f"  Ω_c = {omega_c:.12f} = 47/125")

print("\nProjector:")
print("  P47(C) = C(C-2I)(C-12I)(C-20I)(C-31I)(C-42I) / 1,814,400")
print(f"  Tr(P47) = {np.trace(P47_spec).real:.12f}")
print(f"  ||P47²-P47||_F = {fro(P47_spec @ P47_spec - P47_spec):.3e}")
print(f"  ||K P47||_F    = {fro(K @ P47_spec):.3e}")

print("\nContraction:")
print("  G = K²")
print(f"  Δ       = {spectral_gap:.0f}")
print(f"  Λ_max   = {lambda_max:.0f}")
print(f"  κ       = {kappa:.0f}")
print(f"  ε*      = {eps_star:.15f} = 1/99144")
print(f"  ρ*      = {rho_star:.15f} = 15/17")
print("  Γ       = I - ε* K²")
print(f"  ||Γ^220 - P47||_F = {operator_error_220:.3e}")

print("\nTheorem realized computationally:")
print("  lim_{n→∞} (I - ε*K²)^n = P47")
print("  lim_{t→∞} exp(-t K²)    = P47")

print(f"\n[✓] Certificate written to: {cert_path.resolve()}")

# =====================================================================
# 12. OPTIONAL PLOT
# =====================================================================

if MAKE_PLOT:
    import matplotlib.pyplot as plt

    hist = np.array(history, dtype=float)

    plt.figure(figsize=(8, 5))
    plt.semilogy(hist[:, 0], hist[:, 1], label="actual ||Γ^n x - P47 x||")
    plt.semilogy(hist[:, 0], hist[:, 2], "--", label="bound ρ^n ||x_perp||")
    plt.xlabel("n")
    plt.ylabel("error")
    plt.title("E47 contraction: Γ^n → P47")
    plt.legend()
    plt.tight_layout()

    plot_path = OUT_DIR / "e47_contraction.png"
    plt.savefig(plot_path, dpi=180)
    plt.close()
    print(f"[✓] Plot written to: {plot_path.resolve()}")
