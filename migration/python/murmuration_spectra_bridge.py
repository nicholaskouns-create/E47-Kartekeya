#!/usr/bin/env python3
"""
MURMURATION <-> SPECTRA BRIDGE CERTIFICATE

Formal bridge
-------------
SPECTRA:
    A -> K=q(A) -> E=ker(K) -> P_E
    Gamma = I - eps K^2
    Gamma^n -> P_E

Murmuration:
    q=0: A_t = L_0(t),       E_t = ker L_0(t)       ~= H_0
    q=1: A_t = Delta_1(t),   E_t = ker Delta_1(t)   ~= H_1

Therefore:
    dim ker Delta_q(t) = beta_q(t)

At every frozen time t, topology extraction is literally a spectral
projection. Across time, the swarm is a non-autonomous product of
spectral contractions:
    Phi_T = Gamma_{T-1} ... Gamma_1 Gamma_0
"""

import numpy as np
import json
from pathlib import Path

np.set_printoptions(precision=12, suppress=True)
TOL = 1e-9
SEED = 470125
rng = np.random.default_rng(SEED)

OUT = Path("./murmuration_spectra_artifacts")
OUT.mkdir(exist_ok=True)

def fro(A):
    return float(np.linalg.norm(A, "fro"))

def projector_from_kernel(A, tol=1e-9):
    A = 0.5*(A+A.T)
    vals, vecs = np.linalg.eigh(A)
    mask = np.abs(vals) < tol
    V = vecs[:, mask]
    P = V @ V.T if V.size else np.zeros_like(A)
    return vals, V, P

# ============================================================
# I. TIME-DEPENDENT GRAPH LAPLACIAN: q = 0
# ============================================================

N = 16
theta = 2*np.pi*np.arange(N)/N

# Local graph: first-, second-, third-neighbor ring coupling.
edge_set = set()
for off in (1, 2, 3):
    for i in range(N):
        a, b = sorted((i, (i+off) % N))
        if a != b:
            edge_set.add((a, b))
edges = sorted(edge_set)

B = np.zeros((N, len(edges)))
for e, (i, j) in enumerate(edges):
    B[i, e] = -1.0
    B[j, e] = +1.0

one = np.ones(N)
P_cons = np.outer(one, one) / N
P_perp = np.eye(N) - P_cons

x0 = rng.normal(size=N)
x = x0.copy()

gaps = []
rhos = []
operator_product = np.eye(N)

for t in range(240):
    # Moving annular geometry changes weights and therefore L(t),
    # while preserving connectivity and the common kernel span{1}.
    phase = 0.045 * t
    r = 1.0 + 0.20*np.sin(3*theta + phase) + 0.08*np.cos(5*theta - 0.6*phase)
    ang = theta + 0.10*np.sin(phase)
    X = np.c_[r*np.cos(ang), r*np.sin(ang)]

    lengths = np.array([np.linalg.norm(X[j]-X[i]) for i,j in edges])
    w = np.exp(-(lengths/0.75)**2) + 0.35
    L = B @ np.diag(w) @ B.T
    L = 0.5*(L+L.T)

    vals = np.linalg.eigvalsh(L)
    gap = float(vals[1])
    lmax = float(vals[-1])

    assert gap > 0
    assert np.linalg.norm(L @ one) < 1e-10

    # Exact SPECTRA form using K_t = L_t:
    # Gamma_t = I - eps_t K_t^2.
    eps = 2.0 / (gap**2 + lmax**2)
    Gamma = np.eye(N) - eps*(L @ L)

    assert fro(Gamma @ P_cons - P_cons) < 1e-9

    rho = float(np.linalg.norm(P_perp @ Gamma @ P_perp, 2))
    assert rho < 1.0

    x = Gamma @ x
    operator_product = Gamma @ operator_product

    gaps.append(gap)
    rhos.append(rho)

initial_disagreement = float(np.linalg.norm(P_perp @ x0))
final_disagreement = float(np.linalg.norm(P_perp @ x))
product_to_projector = fro(operator_product - P_cons)

assert final_disagreement < 1e-6 * initial_disagreement
assert product_to_projector < 1e-5

# ============================================================
# II. HODGE TOPOLOGY: q = 1
# ============================================================

# Three oriented edges forming a triangular 1-cycle:
# e0: 0->1, e1: 1->2, e2: 2->0
B1 = np.array([
    [-1.,  0., +1.],
    [+1., -1.,  0.],
    [ 0., +1., -1.],
])

# ----- Unfilled cycle: beta_1 = 1 -----

Delta1_hole = B1.T @ B1
vals_hole, Vh, P_harm = projector_from_kernel(Delta1_hole)

beta1_hole = Vh.shape[1]
assert beta1_hole == 1
assert fro(P_harm @ P_harm - P_harm) < 1e-10
assert fro(Delta1_hole @ P_harm) < 1e-10

# Contract arbitrary edge flow onto the harmonic representative.
u0 = rng.normal(size=3)
u = u0.copy()

positive = vals_hole[vals_hole > 1e-9]
gap_h = float(positive.min())
max_h = float(positive.max())
eps_h = 2.0/(gap_h**2 + max_h**2)
Gamma_h = np.eye(3) - eps_h*(Delta1_hole @ Delta1_hole)

for _ in range(20):
    u = Gamma_h @ u

u_target = P_harm @ u0
harmonic_projection_error = float(np.linalg.norm(u-u_target))
assert harmonic_projection_error < 1e-10

# ----- Fill the 2-simplex: beta_1 = 0 -----

# Boundary of oriented face [0,1,2] is e0+e1+e2.
B2 = np.array([[1.], [1.], [1.]])
assert np.linalg.norm(B1 @ B2) < 1e-12  # d∘d = 0

Delta1_filled = B1.T @ B1 + B2 @ B2.T
vals_filled, Vf, P_filled = projector_from_kernel(Delta1_filled)

beta1_filled = Vf.shape[1]
assert beta1_filled == 0
assert fro(P_filled) < 1e-12
assert vals_filled.min() > 1e-9

# ============================================================
# III. FROZEN-TIME SPECTRA THEOREM CHECK
# ============================================================

def frozen_check(Delta, n=120):
    vals, V, P = projector_from_kernel(Delta)
    positive = vals[vals > 1e-9]
    if len(positive) == 0:
        return 0.0, 0.0
    eps = 2.0/(positive.min()**2 + positive.max()**2)
    Gamma = np.eye(Delta.shape[0]) - eps*(Delta @ Delta)
    Gn = np.linalg.matrix_power(Gamma, n)
    Q = np.eye(Delta.shape[0]) - P
    rho = float(np.linalg.norm(Q @ Gamma @ Q, 2))
    return fro(Gn-P), rho

hole_operator_error, hole_rho = frozen_check(Delta1_hole)
filled_operator_error, filled_rho = frozen_check(Delta1_filled)

assert hole_operator_error < 1e-10
assert filled_operator_error < 1e-10

# ============================================================
# IV. CERTIFICATE
# ============================================================

certificate = {
    "name": "Murmuration-SPECTRA Time-Dependent Laplacian Bridge Certificate",
    "seed": SEED,
    "formal_bridge": {
        "SPECTRA": "A -> K=q(A) -> ker(K) -> P; Gamma=I-eps*K^2",
        "Murmuration_q0": "A_t=L_0(t), K_t=L_0(t), ker(L_0)=H_0, nullity=beta_0",
        "Murmuration_q1": "A_t=Delta_1(t), K_t=Delta_1(t), ker(Delta_1)=H_1, nullity=beta_1",
        "time_dependent": "Phi_T=Gamma_{T-1}...Gamma_1 Gamma_0"
    },
    "dynamic_q0": {
        "agents": N,
        "edges": len(edges),
        "steps": 240,
        "min_lambda2": min(gaps),
        "max_complement_operator_norm": max(rhos),
        "initial_disagreement": initial_disagreement,
        "final_disagreement": final_disagreement,
        "product_minus_consensus_projector_fro": product_to_projector,
        "status": "PASS"
    },
    "hodge_q1_unfilled_cycle": {
        "beta1": beta1_hole,
        "spectrum_Delta1": vals_hole.tolist(),
        "harmonic_projection_error": harmonic_projection_error,
        "Gamma120_minus_Pharm_fro": hole_operator_error,
        "status": "PASS"
    },
    "hodge_q1_filled_cycle": {
        "beta1": beta1_filled,
        "spectrum_Delta1": vals_filled.tolist(),
        "Gamma120_minus_Pharm_fro": filled_operator_error,
        "status": "PASS"
    },
    "conclusion": {
        "topological_extraction_is_literal_spectral_contraction": True,
        "full_time_varying_swarm_equals_one_fixed_projector": False,
        "precise_result": (
            "For every frozen complex, H_q(t)=ker Delta_q(t) exactly and "
            "Gamma_q,t^n -> P_ker(Delta_q(t)). The moving swarm is the "
            "non-autonomous product Phi_T=Gamma_{T-1}...Gamma_0. "
            "When the kernels share a common invariant sector, the product "
            "contracts to that sector; when topology changes, the kernel and "
            "projector change with it."
        )
    },
    "status": "PASS"
}

cert_path = OUT / "murmuration_spectra_bridge_certificate.json"
cert_path.write_text(json.dumps(certificate, indent=2))

print("[✓] MURMURATION ↔ SPECTRA BRIDGE: PASS\n")

print("TIME-DEPENDENT q=0 GRAPH")
print(f"  agents                           : {N}")
print(f"  local edges                      : {len(edges)}")
print(f"  min λ2(L_t)                      : {min(gaps):.6e}")
print(f"  max ||Γ_t|⊥||₂                   : {max(rhos):.12f}")
print(f"  initial disagreement             : {initial_disagreement:.6e}")
print(f"  final disagreement               : {final_disagreement:.6e}")
print(f"  ||Γ_239...Γ_0 - P_cons||_F       : {product_to_projector:.6e}\n")

print("HODGE q=1 TOPOLOGY")
print(f"  unfilled cycle β1                : {beta1_hole}")
print(f"  Spec(Δ1 unfilled)                : {vals_hole}")
print(f"  flow -> harmonic projector error : {harmonic_projection_error:.6e}")
print(f"  filled cycle β1                  : {beta1_filled}")
print(f"  Spec(Δ1 filled)                  : {vals_filled}\n")

print("RESULT")
print("  Frozen topology extraction: LITERAL spectral contraction.")
print("  Moving flock: non-autonomous PRODUCT of spectral contractions.")
print("  One fixed projector exists only when the relevant invariant kernel is common/stable.\n")

print(f"[✓] certificate: {cert_path.resolve()}")
