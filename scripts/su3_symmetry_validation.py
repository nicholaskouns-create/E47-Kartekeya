import json
import numpy as np

SQRT3 = np.sqrt(3.0)
LAM = [
    np.array([[0,1,0],[1,0,0],[0,0,0]], complex),
    np.array([[0,-1j,0],[1j,0,0],[0,0,0]], complex),
    np.array([[1,0,0],[0,-1,0],[0,0,0]], complex),
    np.array([[0,0,1],[0,0,0],[1,0,0]], complex),
    np.array([[0,0,-1j],[0,0,0],[1j,0,0]], complex),
    np.array([[0,0,0],[0,0,1],[0,1,0]], complex),
    np.array([[0,0,0],[0,0,-1j],[0,1j,0]], complex),
    np.array([[1,0,0],[0,1,0],[0,0,-2]], complex) / SQRT3,
]
T = [x / 2 for x in LAM]
I3 = np.eye(3, dtype=complex)

def kron_all(*ops):
    out = ops[0]
    for op in ops[1:]:
        out = np.kron(out, op)
    return out

def total_generators(reps):
    dims = [rep[0].shape[0] for rep in reps]
    total = []
    for a in range(8):
        G = np.zeros((int(np.prod(dims)), int(np.prod(dims))), complex)
        for site, rep in enumerate(reps):
            ops = [rep[a] if j == site else np.eye(d, dtype=complex)
                   for j, d in enumerate(dims)]
            G += kron_all(*ops)
        total.append(G)
    return total

def casimir2(gens):
    return sum(G @ G for G in gens)

def opnorm(A):
    return float(np.linalg.norm(A, ord=2))

def clusters(H, tol=1e-9):
    vals = np.linalg.eigvalsh(H)
    out = []
    for x in vals:
        for row in out:
            if abs(x - row["value"]) < tol:
                row["multiplicity"] += 1
                break
        else:
            out.append({"value": float(x.real), "multiplicity": 1})
    return out

# 3 x 3bar
Tbar = [-g.conj() for g in T]
C_mes = casimir2(total_generators([T, Tbar]))
I9 = np.eye(9, dtype=complex)
P1_mes = I9 - C_mes / 3
P8_mes = C_mes / 3

# 3 x 3 x 3
G_bar = total_generators([T, T, T])
C_bar = casimir2(G_bar)
I27 = np.eye(27, dtype=complex)
P1 = ((C_bar - 3*I27) @ (C_bar - 6*I27)) / 18
P8 = -(C_bar @ (C_bar - 6*I27)) / 9
P10 = (C_bar @ (C_bar - 3*I27)) / 18

# Explicit epsilon singlet
eps = np.zeros(27, complex)
def idx(i,j,k): return 9*i + 3*j + k
for i,j,k,s in [
    (0,1,2,1),(1,2,0,1),(2,0,1,1),
    (0,2,1,-1),(2,1,0,-1),(1,0,2,-1)
]:
    eps[idx(i,j,k)] = s / np.sqrt(6)
P_eps = np.outer(eps, eps.conj())

# Contraction Gamma^n -> singlet projector
K2 = C_bar @ C_bar
epsilon = 1/36
Gamma = I27 - epsilon*K2
Gamma80 = np.linalg.matrix_power(Gamma, 80)

results = {
    "valid": True,
    "fundamental_C2_error": opnorm(sum(g@g for g in T) - (4/3)*I3),
    "meson_spectrum": clusters(C_mes),
    "meson_ranks": [round(np.trace(P1_mes).real), round(np.trace(P8_mes).real)],
    "meson_projector_errors": {
        "P1_idempotence": opnorm(P1_mes@P1_mes-P1_mes),
        "P8_idempotence": opnorm(P8_mes@P8_mes-P8_mes),
        "orthogonality": opnorm(P1_mes@P8_mes),
        "completeness": opnorm(P1_mes+P8_mes-I9),
    },
    "baryon_spectrum": clusters(C_bar),
    "baryon_ranks": [round(np.trace(P1).real), round(np.trace(P8).real), round(np.trace(P10).real)],
    "baryon_projector_errors": {
        "P1_idempotence": opnorm(P1@P1-P1),
        "P8_idempotence": opnorm(P8@P8-P8),
        "P10_idempotence": opnorm(P10@P10-P10),
        "completeness": opnorm(P1+P8+P10-I27),
        "explicit_singlet_match": opnorm(P1-P_eps),
        "singlet_generator_annihilation": max(opnorm(G@eps) for G in G_bar),
    },
    "contraction": {
        "epsilon": epsilon,
        "iterations": 80,
        "limit_error": opnorm(Gamma80-P1),
    },
}

tol = 1e-8
results["valid"] = (
    results["fundamental_C2_error"] < tol
    and results["meson_ranks"] == [1,8]
    and results["baryon_ranks"] == [1,16,10]
    and max(results["meson_projector_errors"].values()) < tol
    and max(results["baryon_projector_errors"].values()) < tol
    and results["contraction"]["limit_error"] < tol
)

print(json.dumps(results, indent=2))
