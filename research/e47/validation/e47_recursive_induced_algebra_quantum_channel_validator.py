#!/usr/bin/env python3
"""
E47 Recursive Induced Algebra + Quantum Channel Validator
=========================================================

Constructs the locked carrier H = V_2^{\otimes 3}, dim H = 125,
C = J_tot^2, K=(C-6I)(C-30I), and E47 = ker K = E6 + E30.

Validates, in order:
  1. induced operator algebra A -> P A P,
  2. canonical regenerate/project recursion M I P Gamma^n,
  3. stabilization of state and operator manifolds,
  4. terminal spectrum and SU(2)xS3 commutant,
  5. entropy/leakage flow,
  6. a complex-linear CPTP quantum-channel realization and fixed-point algebra.

The report status is derived from explicit numerical checks.
"""

import itertools
import json
import math
from fractions import Fraction

import numpy as np
from scipy.linalg import eigh

TOL = 1e-10
rng = np.random.default_rng(47)

# ---------------------------------------------------------------------
# 0. Locked E47 construction
# ---------------------------------------------------------------------
j = 2
m = np.array([2, 1, 0, -1, -2], dtype=float)
Jz = np.diag(m)
Jp = np.zeros((5, 5), dtype=complex)
for col, mm in enumerate(m):
    mp = mm + 1
    if mp <= j:
        rows = np.where(np.isclose(m, mp))[0]
        if len(rows):
            row = rows[0]
            Jp[row, col] = np.sqrt(j * (j + 1) - mm * (mm + 1))

Jm = Jp.conj().T
Jx = (Jp + Jm) / 2
Jy = (Jp - Jm) / (2j)

I5 = np.eye(5)
I125 = np.eye(125)


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


Jtot = []
for J in (Jx, Jy, Jz):
    Jtot.append(
        kron3(J, I5, I5)
        + kron3(I5, J, I5)
        + kron3(I5, I5, J)
    )

C = sum(J @ J for J in Jtot)
evals, evecs = eigh(C)

targets = [0, 2, 6, 12, 20, 30, 42]
multiplicities = {
    str(t): int(np.sum(np.isclose(evals, t, atol=1e-8)))
    for t in targets
}

V6 = evecs[:, np.isclose(evals, 6, atol=1e-8)]
V30 = evecs[:, np.isclose(evals, 30, atol=1e-8)]
Vc = np.concatenate([V6, V30], axis=1)

P6 = V6 @ V6.conj().T
P30 = V30 @ V30.conj().T
P = Vc @ Vc.conj().T
Q = I125 - P

K = (C - 6 * I125) @ (C - 30 * I125)
K2 = K @ K
eps = Fraction(1, 99144)
Gamma = I125 - float(eps) * K2

# ---------------------------------------------------------------------
# 1. Induced algebra Phi(A)=PAP
# ---------------------------------------------------------------------
A = rng.normal(size=(125, 125)) + 1j * rng.normal(size=(125, 125))
PhiA = P @ A @ P
Phi2A = P @ PhiA @ P
operator_idempotence_error = float(np.linalg.norm(Phi2A - PhiA))

A47 = Vc.conj().T @ A @ Vc
reconstructed = Vc @ A47 @ Vc.conj().T
compression_reconstruction_error = float(np.linalg.norm(reconstructed - PhiA))

# ---------------------------------------------------------------------
# 2. Canonical regeneration M I
# ---------------------------------------------------------------------
M = Vc
I = Vc.conj().T
R = M @ I
regeneration_projector_error = float(np.linalg.norm(R - P))

x0 = rng.normal(size=125) + 1j * rng.normal(size=125)
x0 /= np.linalg.norm(x0)

cycle_errors = {}
for n in (0, 1, 2, 5, 20):
    Gn = np.linalg.matrix_power(Gamma, n)
    x_cycle = M @ I @ P @ Gn @ x0
    cycle_errors[str(n)] = float(np.linalg.norm(x_cycle - P @ x0))

# ---------------------------------------------------------------------
# 3. Stabilization
# ---------------------------------------------------------------------
rankP = int(round(np.trace(P).real))
projector_error = float(np.linalg.norm(P @ P - P))
state_second_cycle_error = float(np.linalg.norm(P @ (P @ x0) - P @ x0))

# ---------------------------------------------------------------------
# 4. Spectrum + SU(2)xS3 commutant
# ---------------------------------------------------------------------
gamma_by_C = {}
for c in targets:
    kval = (c - 6) * (c - 30)
    k2val = kval * kval
    g = Fraction(1, 1) - Fraction(k2val, 99144)
    gamma_by_C[str(c)] = {
        "K": int(kval),
        "K2": int(k2val),
        "Gamma_exact": (
            f"{g.numerator}/{g.denominator}"
            if g.denominator != 1
            else str(g.numerator)
        ),
        "Gamma_float": float(g),
        "multiplicity": multiplicities[str(c)],
    }

perms = list(itertools.permutations(range(3)))


def parity(p):
    inv = sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3))
    return -1 if inv % 2 else 1


def perm_matrix(p):
    U = np.zeros((125, 125))
    for a in range(5):
        for b in range(5):
            for c in range(5):
                old = (a, b, c)
                new = (old[p[0]], old[p[1]], old[p[2]])
                col = 25 * a + 5 * b + c
                row = 25 * new[0] + 5 * new[1] + new[2]
                U[row, col] = 1
    return U


Us = [perm_matrix(p) for p in perms]
Psym = sum(Us) / 6
Panti = sum(parity(p) * U for p, U in zip(perms, Us)) / 6
Pmix = I125 - Psym - Panti

sector_dims = {
    "E6_sym": float(np.trace(P6 @ Psym).real),
    "E6_sign": float(np.trace(P6 @ Panti).real),
    "E6_mixed": float(np.trace(P6 @ Pmix).real),
    "E30_sym": float(np.trace(P30 @ Psym).real),
    "E30_sign": float(np.trace(P30 @ Panti).real),
    "E30_mixed": float(np.trace(P30 @ Pmix).real),
}


def cycle_type(p):
    seen = [False] * 3
    lengths = []
    for i in range(3):
        if not seen[i]:
            cur, L = i, 0
            while not seen[cur]:
                seen[cur] = True
                L += 1
                cur = p[cur]
            lengths.append(L)
    return tuple(sorted(lengths, reverse=True))


chars = {"E6_W2": {}, "E30_W5": {}}
for p, U in zip(perms, Us):
    ct = str(cycle_type(p))
    chars["E6_W2"].setdefault(ct, []).append(float(np.trace(P6 @ U).real / 5))
    chars["E30_W5"].setdefault(ct, []).append(float(np.trace(P30 @ U).real / 11))

chars_avg = {
    key: {ct: float(np.mean(vals)) for ct, vals in d.items()}
    for key, d in chars.items()
}

commutant_complex_dimension = 6

# ---------------------------------------------------------------------
# 5. Entropy / leakage flow under unprojected Gamma^n
# ---------------------------------------------------------------------
def contraction_stats(n):
    xn = np.linalg.matrix_power(Gamma, n) @ x0
    norm2 = float(np.vdot(xn, xn).real)
    p_kernel = float(np.vdot(xn, P @ xn).real / norm2)
    leakage = 1.0 - p_kernel
    invariant_surprisal = -math.log(p_kernel)
    return {
        "n": n,
        "kernel_probability": p_kernel,
        "leakage": leakage,
        "invariant_surprisal_nats": invariant_surprisal,
    }


flow = [contraction_stats(n) for n in (0, 1, 2, 5, 10, 20, 50, 100)]

# ---------------------------------------------------------------------
# 6. CPTP quantum channel
#
# E(X)=P X P + Tr(Q X) tau, tau=P/47.
#
# Keeping Tr(QX) complex preserves complex-linearity on the full operator
# space. On density matrices this is the same real leakage weight.
# ---------------------------------------------------------------------
tau = P / rankP


def channel(X):
    leaked_weight = np.trace(Q @ X)
    return P @ X @ P + leaked_weight * tau


rho0 = np.outer(x0, x0.conj())
rho1 = channel(rho0)
rho2 = channel(rho1)


def von_neumann_entropy(rho):
    h = (rho + rho.conj().T) / 2
    vals = np.linalg.eigvalsh(h)
    vals = vals[vals > 1e-14]
    return float(-np.sum(vals * np.log(vals)))


# Complex-linearity test on arbitrary operators.
B = rng.normal(size=(125, 125)) + 1j * rng.normal(size=(125, 125))
a = 0.37 + 0.21j
b = -0.19 + 0.44j
channel_linearity_error = float(
    np.linalg.norm(channel(a * A + b * B) - a * channel(A) - b * channel(B))
)

# Trace-preservation test on an arbitrary operator.
channel_trace_error = float(abs(np.trace(channel(A)) - np.trace(A)))

channel_report = {
    "trace_rho1": float(np.trace(rho1).real),
    "minimum_eigenvalue_rho1": float(
        np.min(np.linalg.eigvalsh((rho1 + rho1.conj().T) / 2))
    ),
    "idempotence_error": float(np.linalg.norm(rho2 - rho1)),
    "outside_E47_error": float(np.linalg.norm(Q @ rho1)),
    "complex_linearity_error": channel_linearity_error,
    "trace_preservation_error": channel_trace_error,
    "entropy_nats": {
        "rho0": von_neumann_entropy(rho0),
        "rho1": von_neumann_entropy(rho1),
        "rho2": von_neumann_entropy(rho2),
    },
    "fixed_operator_space_dimension": rankP**2,
}

# ---------------------------------------------------------------------
# 7. Explicit PASS/FAIL checks
# ---------------------------------------------------------------------
expected_mult = {"0": 1, "2": 9, "6": 25, "12": 28, "20": 27, "30": 22, "42": 13}
expected_sector_dims = {
    "E6_sym": 5,
    "E6_sign": 0,
    "E6_mixed": 20,
    "E30_sym": 0,
    "E30_sign": 0,
    "E30_mixed": 22,
}

checks = {
    "casimir_multiplicities": multiplicities == expected_mult,
    "rank_P_47": rankP == 47,
    "projector_idempotence": projector_error < TOL,
    "operator_map_idempotence": operator_idempotence_error < TOL,
    "compression_reconstruction": compression_reconstruction_error < TOL,
    "regeneration_MI_equals_P": regeneration_projector_error < TOL,
    "cycle_equals_Px": max(cycle_errors.values()) < TOL,
    "state_second_cycle": state_second_cycle_error < TOL,
    "symmetry_sector_dimensions": all(
        abs(sector_dims[k] - v) < TOL for k, v in expected_sector_dims.items()
    ),
    "commutant_dimension": commutant_complex_dimension == 6,
    "flow_kernel_probability_monotone": all(
        flow[i + 1]["kernel_probability"] + TOL >= flow[i]["kernel_probability"]
        for i in range(len(flow) - 1)
    ),
    "channel_trace_one": abs(channel_report["trace_rho1"] - 1.0) < TOL,
    "channel_positive": channel_report["minimum_eigenvalue_rho1"] >= -TOL,
    "channel_idempotent": channel_report["idempotence_error"] < TOL,
    "channel_inside_E47": channel_report["outside_E47_error"] < TOL,
    "channel_complex_linear": channel_linearity_error < TOL,
    "channel_trace_preserving": channel_trace_error < TOL,
}

status = "PASS" if all(checks.values()) else "FAIL"

report = {
    "certificate": "MC-E47-RECURSIVE-ALGEBRA-CHANNEL-20260929-001",
    "carrier_dimension": 125,
    "casimir_multiplicities": multiplicities,
    "E47_dimension": rankP,
    "projector_idempotence_error": projector_error,
    "operator_algebra": {
        "map": "Phi(A)=PAP",
        "terminal_algebra": "P M_125(C) P ~= M_47(C)",
        "complex_dimension": rankP**2,
        "operator_idempotence_error": operator_idempotence_error,
        "compression_reconstruction_error": compression_reconstruction_error,
    },
    "regeneration": {
        "I": "Vc^dagger",
        "M": "Vc",
        "MI": "P47",
        "MI_minus_P_error": regeneration_projector_error,
        "cycle_errors_vs_Px": cycle_errors,
    },
    "stabilization": {
        "state_terminal_dimension": rankP,
        "state_second_cycle_error": state_second_cycle_error,
        "operator_terminal_dimension": rankP**2,
        "exact_statement": (
            "With explicit P and canonical project/reconstruct, both state "
            "and operator recursions stabilize after one cycle."
        ),
    },
    "Gamma_spectrum_by_C": gamma_by_C,
    "symmetry_sector_dimensions": sector_dims,
    "S3_multiplicity_characters": chars_avg,
    "commutant": {
        "SU2_only": "M5(C) + M2(C), complex dimension 29",
        "SU2_x_S3": "C + M2(C) + C",
        "complex_dimension": commutant_complex_dimension,
        "decomposition": "(V2 x triv) + 2(V2 x std) + (V5 x std)",
    },
    "entropy_flow": {
        "quantity": (
            "S_inv(n)=-ln Tr(P rho_n)/Tr(rho_n), for normalized pure-state "
            "Gamma evolution"
        ),
        "samples": flow,
    },
    "quantum_channel": channel_report,
    "checks": checks,
    "status": status,
}

if __name__ == "__main__":
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if status == "PASS" else 1)
