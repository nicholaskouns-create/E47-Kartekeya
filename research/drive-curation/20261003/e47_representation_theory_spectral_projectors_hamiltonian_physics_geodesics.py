#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E47: Representation Theory, Spectral Projectors, Hamiltonian Physics and Geodesics

Locked deterministic first-principles construct.

Scope
-----
1. Spin-2 SU(2) representation -> 125-dimensional carrier.
2. Total Casimir -> exact E47 spectral kernel.
3. Polynomial spectral projector P47.
4. Parent Hamiltonian H = g K^2 with E47 as its exact ground manifold.
5. Optimal linear filter Gamma_f = I - eps_* K^2 -> P47.
6. Explicit E6 spatial copy W=(V2⊗V2)_{J=0}⊗V2.
7. Sym_0(3,R) realization, SO(3) orbit, Lorentzian 3+1 metric.
8. Levi-Civita connection, geodesic equations, curvature and Einstein tensor.
9. Derived stress-energy T = G/(8 pi G_N) in natural units.

No fitted spectral constants are used. g>0 sets the Hamiltonian energy scale.
The executable validator uses g=1 and G_N=1 as unit conventions.
"""

from __future__ import annotations

import json
import math
import hashlib
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np

TITLE = "E47: Representation Theory, Spectral Projectors, Hamiltonian Physics and Geodesics"
TOL = 1e-9

# ---------------------------------------------------------------------------
# LOCKED EXACT TARGETS
# ---------------------------------------------------------------------------
EXPECTED_C_SPEC = np.array([0, 2, 6, 12, 20, 30, 42], dtype=int)
EXPECTED_C_MULT = np.array([1, 9, 25, 28, 27, 22, 13], dtype=int)
EXPECTED_K2_POS = np.array([11664, 12544, 19600, 32400, 186624], dtype=int)
EXPECTED_DIM = 125
EXPECTED_E47_DIM = 47
EXPECTED_GAP = 11664
EXPECTED_K2_NORM = 186624
EXPECTED_EPS = Fraction(1, 99144)
EXPECTED_RHO = Fraction(15, 17)

# Unit conventions. g rescales all Hamiltonian energies but not eigenspaces.
g_energy = 1.0
G_N = 1.0


def fail_if(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)


def fro(A) -> float:
    return float(np.linalg.norm(A, ord="fro"))


def comm(A, B):
    return A @ B - B @ A


# ===========================================================================
# 01  SPIN-2 SU(2) GENERATORS
# ===========================================================================
spin = 2
m = np.arange(spin, -spin - 1, -1, dtype=float)
d = 2 * spin + 1

Jz = np.diag(m).astype(complex)
Jp = np.zeros((d, d), dtype=complex)
for i in range(d - 1):
    mm = m[i + 1]
    Jp[i, i + 1] = np.sqrt(spin * (spin + 1) - mm * (mm + 1))

Jm = Jp.conj().T
Jx = (Jp + Jm) / 2
Jy = (Jp - Jm) / (2j)
I5 = np.eye(5, dtype=complex)

single_C = Jx @ Jx + Jy @ Jy + Jz @ Jz


# ===========================================================================
# 02  125-DIMENSIONAL TENSOR CARRIER
# ===========================================================================
def kron3(A, B, C):
    return np.kron(np.kron(A, B), C)


I125 = np.eye(125, dtype=complex)

Jtot = []
for Ja in (Jx, Jy, Jz):
    Jtot.append(
        kron3(Ja, I5, I5)
        + kron3(I5, Ja, I5)
        + kron3(I5, I5, Ja)
    )


# ===========================================================================
# 03  TOTAL CASIMIR
# ===========================================================================
C = sum(Ja @ Ja for Ja in Jtot)

ce = np.linalg.eigvalsh(C)
c_round = np.rint(ce).astype(int)
c_spec, c_mult = np.unique(c_round, return_counts=True)


# ===========================================================================
# 04  CLEBSCH-GORDAN SPECTRUM
# ===========================================================================
# Exact representation-theory decomposition:
# V2^⊗3 ≅ V0 ⊕ 3V1 ⊕ 5V2 ⊕ 4V3 ⊕ 3V4 ⊕ 2V5 ⊕ V6.
irrep_copies = np.array([1, 3, 5, 4, 3, 2, 1], dtype=int)
irrep_dims = 2 * np.arange(7) + 1
dimension_from_decomposition = int(irrep_copies @ irrep_dims)


# ===========================================================================
# 05  E47 KERNEL SELECTOR
# ===========================================================================
K = (C - 6 * I125) @ (C - 30 * I125)
K2 = K @ K

ke = np.linalg.eigvalsh(K)
k2e = np.linalg.eigvalsh(K2)
kernel_dim = int(np.count_nonzero(np.abs(ke) < 1e-7))

positive_k2 = np.array(sorted({
    int(round(x)) for x in k2e if x > 1e-7
}), dtype=int)

Delta = int(positive_k2.min())
M = int(positive_k2.max())


# ===========================================================================
# 06  EXACT ORTHOGONAL PROJECTOR
# ===========================================================================
# Unique degree <= 6 interpolation polynomial on spec(C) with
# p(6)=p(30)=1 and p(0)=p(2)=p(12)=p(20)=p(42)=0.
#
# The root 31 is intentional: it enforces p(6)=p(30)=1 simultaneously.
P47 = (
    C
    @ (C - 2 * I125)
    @ (C - 12 * I125)
    @ (C - 20 * I125)
    @ (C - 31 * I125)
    @ (C - 42 * I125)
) / 1814400.0

Hcomp = I125 - P47

cw, CU = np.linalg.eigh(C)
mask47 = np.isclose(cw, 6, atol=TOL) | np.isclose(cw, 30, atol=TOL)
Pspec = CU[:, mask47] @ CU[:, mask47].conj().T


# ===========================================================================
# 07  PARENT HAMILTONIAN H = g K^2
# ===========================================================================
H = g_energy * K2
He = np.linalg.eigvalsh(H)

# Sector energy law:
# E_j = g [j(j+1)-6]^2 [j(j+1)-30]^2.
jvals = np.arange(7)
lambdas = jvals * (jvals + 1)
sector_energies = (
    g_energy
    * (lambdas - 6) ** 2
    * (lambdas - 30) ** 2
)

ground_dim_H = int(np.count_nonzero(np.abs(He) < 1e-7))
gap_H = g_energy * Delta

# Coercive / mass-isolation inequality as an operator:
# H >= g Delta (I-P47).
coercive_operator = H - gap_H * Hcomp
coercive_min_eig = float(np.min(np.linalg.eigvalsh(coercive_operator)))


# ===========================================================================
# 08  GROUND-MANIFOLD AND SPECTRAL-GAP PROOF
# ===========================================================================
# <psi|H|psi> = g ||K psi||^2 >= g Delta ||(I-P47)psi||^2.
# Therefore Ground(H)=ker(H)=ker(K)=im(P47)=E47.


# ===========================================================================
# 09  CONTRACTIVE PREPARATION Gamma_f^n -> P47
# ===========================================================================
eps_star = 2.0 / (Delta + M)
rho_star = (M - Delta) / (M + Delta)

Gamma_f = I125 - eps_star * K2

# Exact complement spectral radius.
gamma_eigs = np.linalg.eigvalsh(Gamma_f)
gamma_comp = gamma_eigs[np.abs(gamma_eigs - 1.0) > 1e-7]
rho_numeric = float(np.max(np.abs(gamma_comp)))

# Direct finite-n convergence witness.
n_filter = 220
Gamma_n = np.linalg.matrix_power(Gamma_f, n_filter)
gamma220_residual = fro(Gamma_n - P47)


# ===========================================================================
# 10  E47 SPATIAL SUBSPACE
# ===========================================================================
# Couple the first two spin-2 factors to their J=0 singlet:
# |S0> = 1/sqrt(5) sum_m (-1)^(2-m) |m,-m>.
singlet = np.zeros(25, dtype=complex)
for i, m1 in enumerate(m):
    j2 = int(np.flatnonzero(np.isclose(m, -m1))[0])
    singlet[i * 5 + j2] = (-1) ** int(spin - m1) / math.sqrt(5)

# W=(V2⊗V2)_{J=0}⊗V2, an explicit 5D subspace of the 125D carrier.
W = np.column_stack([
    np.kron(singlet, np.eye(5, dtype=complex)[:, k])
    for k in range(5)
])


# ===========================================================================
# 11  SO(3) ORBIT AND TANGENT BASIS
# ===========================================================================
# Sym_0(3,R) is an explicit real spin-2 model.
Q = np.diag([1.0, 0.0, -1.0])

A1 = np.array([[0, 0, 0], [0, 0, -1], [0, 1, 0]], dtype=float)
A2 = np.array([[0, 0, 1], [0, 0, 0], [-1, 0, 0]], dtype=float)
A3 = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 0]], dtype=float)
A = [A1, A2, A3]

D = [comm(Ai, Q) for Ai in A]
orbit_gram = np.array([
    [np.trace(Di.T @ Dj) for Dj in D]
    for Di in D
], dtype=float)

orbit_rank = int(np.linalg.matrix_rank(np.column_stack([
    Di.reshape(-1) for Di in D
])))

# Orthonormal basis of Sym_0(3,R).
Sbasis = [
    np.diag([1, -1, 0]) / math.sqrt(2),
    np.diag([1, 1, -2]) / math.sqrt(6),
    np.array([[0,1,0],[1,0,0],[0,0,0]], float) / math.sqrt(2),
    np.array([[0,0,1],[0,0,0],[1,0,0]], float) / math.sqrt(2),
    np.array([[0,0,0],[0,0,1],[0,1,0]], float) / math.sqrt(2),
]

L = []
for Ai in A:
    Li = np.zeros((5, 5), dtype=float)
    for col, S in enumerate(Sbasis):
        T = comm(Ai, S)
        for row, B in enumerate(Sbasis):
            Li[row, col] = np.trace(B.T @ T)
    L.append(Li)

# Hermitian spin generators for this real tensor model.
J_sym = [1j * Li for Li in L]
C_sym = sum(Ji @ Ji for Ji in J_sym)


# ===========================================================================
# 12  CLOCK DIRECTION
# ===========================================================================
# Add one independent negative-norm clock direction u.
# In basis {u,D1,D2,D3}:
g4_D = np.diag([-1.0, orbit_gram[0,0], orbit_gram[1,1], orbit_gram[2,2]])


# ===========================================================================
# 13  INDUCED 3+1 LORENTZIAN METRIC
# ===========================================================================
metric_eigs = np.linalg.eigvalsh(g4_D)
signature = (
    int(np.count_nonzero(metric_eigs < -TOL)),
    int(np.count_nonzero(metric_eigs > TOL)),
)

# Normalize the spatial orbit basis.
spatial_scales = np.sqrt(np.diag(orbit_gram))
# e_i = A_i / spatial_scales[i] on SO(3)/V4.


# ===========================================================================
# 14  LEVI-CIVITA CONNECTION
# ===========================================================================
# Structure constants [e_i,e_j] = c_ij^k e_k.
c = np.zeros((3, 3, 3), dtype=float)

for i in range(3):
    for j in range(3):
        bracket = comm(A[i], A[j])
        coeff_A = np.array([
            np.sum(bracket * Ak) / np.sum(Ak * Ak)
            for Ak in A
        ])
        c[i, j, :] = (
            coeff_A
            * spatial_scales
            / (spatial_scales[i] * spatial_scales[j])
        )

# Koszul formula in the orthonormal spatial frame:
# 2<∇_ei ej,ek> = <[ei,ej],ek> - <[ej,ek],ei> + <[ek,ei],ej>.
LC = np.zeros((3, 3, 3), dtype=float)
for i in range(3):
    for j in range(3):
        for k in range(3):
            LC[i, j, k] = 0.5 * (
                c[i, j, k]
                - c[j, k, i]
                + c[k, i, j]
            )

# Torsion residual: ∇_i e_j - ∇_j e_i - [e_i,e_j] = 0.
torsion_resid = float(np.max(np.abs(LC - np.swapaxes(LC, 0, 1) - c)))


# ===========================================================================
# 15  GEODESIC EQUATION
# ===========================================================================
# In the invariant orthonormal frame:
# dv^k/dtau + Gamma^k_ij v^i v^j = 0.
#
# Here the exact reduced spatial system is:
#   v1' = a v2 v3
#   v2' = 0
#   v3' = -a v1 v2
# with a = 3/(2 sqrt(2)).
a_geo = 3.0 / (2.0 * math.sqrt(2.0))

# Extract the quadratic coefficients directly from LC.
quad = np.zeros((3, 3, 3), dtype=float)
quad[:] = LC

# Deterministic analytic geodesic witness.
v10, v20, v30 = 0.4, 0.7, 0.2
v0_time = 1.5
omega = a_geo * v20

tau = np.linspace(0.0, 8.0, 801)
v1 = v10 * np.cos(omega * tau) + v30 * np.sin(omega * tau)
v2 = np.full_like(tau, v20)
v3 = v30 * np.cos(omega * tau) - v10 * np.sin(omega * tau)

dv1 = omega * (-v10 * np.sin(omega * tau) + v30 * np.cos(omega * tau))
dv2 = np.zeros_like(tau)
dv3 = omega * (-v30 * np.sin(omega * tau) - v10 * np.cos(omega * tau))

geo_residual = max(
    float(np.max(np.abs(dv1 - a_geo * v2 * v3))),
    float(np.max(np.abs(dv2))),
    float(np.max(np.abs(dv3 + a_geo * v1 * v2))),
)

spatial_speed2 = v1**2 + v2**2 + v3**2
spatial_speed_drift = float(np.max(np.abs(spatial_speed2 - spatial_speed2[0])))

lorentz_norm = -(v0_time**2) + spatial_speed2
lorentz_norm_drift = float(np.max(np.abs(lorentz_norm - lorentz_norm[0])))


# ===========================================================================
# 16  CURVATURE TENSOR
# ===========================================================================
# R(e_i,e_j)e_k = ∇_i∇_j e_k - ∇_j∇_i e_k - ∇_[ei,ej] e_k.
R = np.zeros((3, 3, 3, 3), dtype=float)
for i in range(3):
    for j in range(3):
        for k in range(3):
            term1 = np.einsum("m,ml->l", LC[j, k, :], LC[i, :, :])
            term2 = np.einsum("m,ml->l", LC[i, k, :], LC[j, :, :])
            term3 = np.einsum("m,ml->l", c[i, j, :], LC[:, k, :])
            R[i, j, k, :] = term1 - term2 - term3

K12 = float(R[0, 1, 1, 0])
K23 = float(R[1, 2, 2, 1])
K31 = float(R[2, 0, 0, 2])


# ===========================================================================
# 17  RICCI AND EINSTEIN TENSORS
# ===========================================================================
Ric3 = np.zeros((3, 3), dtype=float)
for j in range(3):
    for k in range(3):
        Ric3[j, k] = sum(R[i, j, k, i] for i in range(3))

R_scalar = float(np.trace(Ric3))

# Static product time x spatial orbit in orthonormal 3+1 frame.
Ric4 = np.zeros((4, 4), dtype=float)
Ric4[1:, 1:] = Ric3
eta4 = np.diag([-1.0, 1.0, 1.0, 1.0])
Einstein4 = Ric4 - 0.5 * R_scalar * eta4


# ===========================================================================
# 18  DERIVED STRESS-ENERGY
# ===========================================================================
T4 = Einstein4 / (8.0 * math.pi * G_N)

# 4D invariant-frame connection: time direction is flat/product.
LC4 = np.zeros((4, 4, 4), dtype=float)
LC4[1:, 1:, 1:] = LC

# Covariant divergence of constant invariant-frame T_ab:
# (∇_a T)_cb = -Gamma_ac^d T_db - Gamma_ab^d T_cd
# (div T)_b = g^{ac} (∇_a T)_cb.
divT = np.zeros(4, dtype=float)
for b in range(4):
    total = 0.0
    for aa in range(4):
        for cc in range(4):
            if eta4[aa, cc] == 0:
                continue
            covder = 0.0
            for dd in range(4):
                covder -= LC4[aa, cc, dd] * T4[dd, b]
                covder -= LC4[aa, b, dd] * T4[cc, dd]
            total += eta4[aa, cc] * covder
    divT[b] = total


# ===========================================================================
# 19  MACHINE CERTIFICATE
# ===========================================================================
checks = {}

def check(name, condition):
    checks[name] = bool(condition)

# Representation theory
check("SU2 [Jx,Jy]=iJz", fro(comm(Jx, Jy) - 1j * Jz) < TOL)
check("SU2 [Jy,Jz]=iJx", fro(comm(Jy, Jz) - 1j * Jx) < TOL)
check("SU2 [Jz,Jx]=iJy", fro(comm(Jz, Jx) - 1j * Jy) < TOL)
check("single-spin Casimir=6I5", fro(single_C - 6 * I5) < TOL)
check("carrier dim=125", C.shape == (125, 125))
check("CG dimension sum=125", dimension_from_decomposition == 125)
check("Casimir spectrum exact", np.array_equal(c_spec, EXPECTED_C_SPEC))
check("Casimir multiplicities exact", np.array_equal(c_mult, EXPECTED_C_MULT))

# Kernel/projector
check("ker K dim=47", kernel_dim == EXPECTED_E47_DIM)
check("positive spec(K^2) exact", np.array_equal(positive_k2, EXPECTED_K2_POS))
check("gap Delta=11664", Delta == EXPECTED_GAP)
check("||K^2||=186624", M == EXPECTED_K2_NORM)
check("P47 Hermitian", fro(P47.conj().T - P47) < TOL)
check("P47 idempotent", fro(P47 @ P47 - P47) < TOL)
check("rank(P47)=47", np.linalg.matrix_rank(P47, tol=1e-7) == 47)
check("tr(P47)=47", abs(np.trace(P47).real - 47) < 1e-7)
check("KP47=P47K=0", fro(K @ P47) < 1e-7 and fro(P47 @ K) < 1e-7)
check("P47=spectral projector", fro(P47 - Pspec) < 1e-7)

# Hamiltonian
check("H positive semidefinite", float(np.min(He)) > -1e-7)
check("ground(H) dim=47", ground_dim_H == 47)
check("ground(H)=E47 projector", fro(H @ P47) < 1e-7)
check("H sector energies", np.array_equal(
    np.rint(sector_energies).astype(int),
    np.array([32400,12544,0,11664,19600,0,186624])
))
check("Hamiltonian gap=11664*g", abs(gap_H - 11664.0) < TOL)
check("coercive inequality H>=gDelta(I-P)", coercive_min_eig > -1e-6)

# Filter
check("eps*=1/99144", abs(eps_star - float(EXPECTED_EPS)) < 1e-15)
check("rho*=15/17", abs(rho_star - float(EXPECTED_RHO)) < 1e-15)
check("Gamma_f P47=P47", fro(Gamma_f @ P47 - P47) < 1e-7)
check("complement spectral radius=15/17", abs(rho_numeric - float(EXPECTED_RHO)) < 1e-10)
check("Gamma_f^220 -> P47", gamma220_residual < 1e-7)

# Explicit W⊂E6
Jpair = [
    np.kron(Ja, I5) + np.kron(I5, Ja)
    for Ja in (Jx, Jy, Jz)
]
check("spin-2 pair singlet normalized", abs(np.vdot(singlet, singlet).real - 1) < TOL)
check("pair singlet J=0", max(np.linalg.norm(Ja @ singlet) for Ja in Jpair) < TOL)
check("W orthonormal dim5", fro(W.conj().T @ W - np.eye(5)) < TOL)
check("W subset E6", fro(C @ W - 6 * W) < 1e-8)
check("P47 fixes W", fro(P47 @ W - W) < 1e-7)

# Sym0 model / geometry
check("Sym0 generators spin-2 Casimir", fro(C_sym - 6 * np.eye(5)) < 1e-8)
check("orbit tangent rank=3", orbit_rank == 3)
check("orbit Gram=diag(2,8,2)", np.allclose(orbit_gram, np.diag([2,8,2]), atol=TOL))
check("Lorentzian metric diag(-1,2,8,2)", np.allclose(g4_D, np.diag([-1,2,8,2]), atol=TOL))
check("Lorentzian signature (1-,3+)", signature == (1,3))
check("Levi-Civita torsion-free", torsion_resid < TOL)

# Geodesics
# Recover exact reduced coefficients from LC.
coef_v1_v2v3 = -(LC[1,2,0] + LC[2,1,0])
coef_v2_v1v3 = -(LC[0,2,1] + LC[2,0,1])
coef_v3_v1v2 = -(LC[0,1,2] + LC[1,0,2])
check("geodesic coefficient v1", abs(coef_v1_v2v3 - a_geo) < TOL)
check("geodesic coefficient v2=0", abs(coef_v2_v1v3) < TOL)
check("geodesic coefficient v3", abs(coef_v3_v1v2 + a_geo) < TOL)
check("analytic geodesic residual", geo_residual < 1e-12)
check("spatial speed conserved", spatial_speed_drift < 1e-12)
check("Lorentz norm conserved", lorentz_norm_drift < 1e-12)

# Curvature / Einstein / stress energy
check("sectionals=(1/2,1/2,-1)", np.allclose([K12,K23,K31],[0.5,0.5,-1.0], atol=TOL))
check("Ricci spatial=diag(-1/2,1,-1/2)", np.allclose(Ric3, np.diag([-0.5,1,-0.5]), atol=TOL))
check("scalar curvature R=0", abs(R_scalar) < TOL)
check("Einstein4=diag(0,-1/2,1,-1/2)", np.allclose(
    Einstein4, np.diag([0,-0.5,1,-0.5]), atol=TOL
))
check("covariant divergence T=0", np.linalg.norm(divT) < TOL)

passed = sum(checks.values())
total = len(checks)

# Fail closed.
fail_if("LOCK FAILURE: one or more certificate checks failed", passed == total)

symbolic = r"""
SYMBOLIC CHAIN
==============
V2 ~= C^5
H_125 = V2^(x3)
C = J_tot^2

K = (C-6I)(C-30I)
E47 = ker(K) = E6 (+) E30
dim(E47) = 25+22 = 47

P47 = C(C-2I)(C-12I)(C-20I)(C-31I)(C-42I)/1814400
im(P47) = E47

H = g K^2 >= 0
Ground(H) = ker(H) = ker(K) = E47
<psi|H|psi> >= g Delta ||(I-P47)psi||^2
Delta = 11664

Gamma_f = I - eps_* K^2
eps_* = 1/99144
rho(Gamma_f|E47^perp) = 15/17
Gamma_f^n -> P47

W = (V2 x V2)_{J=0} x V2  subset E6 subset E47
W ~= Sym_0(3,R)
O = SO(3).Q,  Q=diag(1,0,-1)
g_{u,D} = diag(-1,2,8,2)

In orthonormal invariant spatial frame:
v1' = (3/(2 sqrt(2))) v2 v3
v2' = 0
v3' = -(3/(2 sqrt(2))) v1 v2
v0' = 0

K12=1/2, K23=1/2, K31=-1
Ric_spatial=diag(-1/2,1,-1/2)
R=0
G_4=diag(0,-1/2,1,-1/2)
T=G_4/(8 pi G_N)
"""

print("=" * 92)
print(TITLE)
print("=" * 92)
print(symbolic.strip())
print("\nMACHINE CERTIFICATE")
print("-" * 92)

for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL':4s}  {name}")

print("-" * 92)
print(f"{passed}/{total} CHECKS PASS")
print(f"spec(C) = {c_spec.tolist()}")
print(f"mult(C) = {c_mult.tolist()}")
print(f"dim ker K = {kernel_dim}")
print(f"rank(P47) = {np.linalg.matrix_rank(P47, tol=1e-7)}")
print(f"tr(P47) = {np.trace(P47).real:.15f}")
print(f"Delta(K^2) = {Delta}")
print(f"||K^2|| = {M}")
print(f"eps* = 1/99144 = {eps_star:.16g}")
print(f"rho* = 15/17 = {rho_star:.16g}")
print(f"||Gamma_f^220-P47||_F = {gamma220_residual:.3e}")
print(f"metric(u,D1,D2,D3) = {np.diag(g4_D).tolist()}")
print(f"sectionals = {(K12,K23,K31)}")
print(f"Ricci spatial =\n{Ric3}")
print(f"Einstein 4D =\n{Einstein4}")
print(f"||div T|| = {np.linalg.norm(divT):.3e}")
print(f"analytic geodesic residual = {geo_residual:.3e}")
print(f"Lorentz norm drift = {lorentz_norm_drift:.3e}")
print("=" * 92)
print("LOCKED: ALL DECLARED FIRST-PRINCIPLES IDENTITIES RECONSTRUCTED.")
print("=" * 92)

certificate = {
    "title": TITLE,
    "status": "PASS",
    "checks_passed": passed,
    "checks_total": total,
    "carrier_dimension": 125,
    "casimir_spectrum": c_spec.tolist(),
    "casimir_multiplicities": c_mult.tolist(),
    "kernel_dimension": kernel_dim,
    "projector_rank": int(np.linalg.matrix_rank(P47, tol=1e-7)),
    "projector_trace": float(np.trace(P47).real),
    "hamiltonian": "H=gK^2",
    "g_unit_convention": g_energy,
    "ground_manifold": "E47=ker(K)=E6+E30",
    "spectral_gap_K2": Delta,
    "lambda_max_K2": M,
    "epsilon_star": "1/99144",
    "rho_star": "15/17",
    "metric_u_D": np.diag(g4_D).tolist(),
    "signature": "(-,+,+,+)",
    "sectional_curvatures": [K12, K23, K31],
    "ricci_spatial": Ric3.tolist(),
    "scalar_curvature": R_scalar,
    "einstein_4d": Einstein4.tolist(),
    "div_T_norm": float(np.linalg.norm(divT)),
    "geodesic_reduced_system": {
        "a": "3/(2sqrt(2))",
        "dv1": "a*v2*v3",
        "dv2": "0",
        "dv3": "-a*v1*v2",
        "dv0": "0",
    },
    "geodesic_residual": geo_residual,
    "lorentz_norm_drift": lorentz_norm_drift,
}
