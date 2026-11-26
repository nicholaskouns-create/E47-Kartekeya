#!/usr/bin/env python3
"""
Emergent Spacetime -- quantum simulation of the coherence filter.

The filter Lambda = I - eps* A is contractive, not unitary, so it is not a gate.
It is realized here as a genuine quantum process in three equivalent ways, and
all three are checked against each other:

  1. A two-outcome Kraus channel  {K0 = Lambda, K1 = sqrt(I - Lambda^2)}.
     Completeness K0*K0 + K1*K1 = I is verified, so this is a legal channel.

  2. Its Stinespring dilation: a single unitary U on the 250-dimensional space
     H (x) C^2.  U is verified unitary to machine precision.  Tracing out the
     ancilla reproduces the channel exactly; post-selecting the ancilla on |0>
     reproduces the occupancy flow.

  3. A circuit-level run on density matrices, tracking the kernel occupancy
     p = tr(P rho) / tr(rho) and reading the metric signature off sgn(1 - 2p)
     at every step, together with the post-selection success probability.

Nothing is post-selected away silently: the success probability is reported at
each step, because that is the real cost of driving the occupancy up.

Run:  python3 docs/emergent-spacetime/quantum_simulation.py
Exit: 0 iff every check passes.  Writes quantum_results.json beside this file.
"""

from fractions import Fraction as F
import json
import math
import os
import sys

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quantum_results.json")
checks = []
results = {}


def check(name, ok, detail=""):
    checks.append({"name": name, "pass": bool(ok), "detail": str(detail)})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return bool(ok)


# --------------------------------------------------------------------------
# The carrier and the filter.
# --------------------------------------------------------------------------

def spin_ops(j):
    d = int(round(2 * j + 1))
    m = np.array([j - k for k in range(d)], dtype=float)
    jp = np.zeros((d, d), dtype=complex)
    for k in range(1, d):
        jp[k - 1, k] = math.sqrt(j * (j + 1) - m[k] * (m[k] + 1))
    jm = jp.conj().T
    return (jp + jm) / 2, (jp - jm) / (2j), np.diag(m).astype(complex)


jx, jy, jz = spin_ops(2.0)
I5 = np.eye(5, dtype=complex)
k3 = lambda a, b, c: np.kron(np.kron(a, b), c)
Jtot = [k3(a, I5, I5) + k3(I5, a, I5) + k3(I5, I5, a) for a in (jx, jy, jz)]

DIM = 125
Id = np.eye(DIM, dtype=complex)
C = sum(a @ a for a in Jtot)
K = (C - 6 * Id) @ (C - 30 * Id)
A = K @ K

EPS = F(1, 99144)
RHO = F(15, 17)
Lam = Id - float(EPS) * A

evals, evecs = np.linalg.eigh(C)
rounded = np.round(evals).astype(int)
V = evecs[:, np.isin(rounded, [6, 30])]
P = V @ V.conj().T

check("kernel projector has trace 47", abs(np.trace(P).real - 47) < 1e-9,
      f"tr P = {np.trace(P).real:.12f}")
check("the filter is Hermitian", np.abs(Lam - Lam.conj().T).max() < 1e-12)
check("the filter is contractive (all singular values <= 1)",
      np.linalg.svd(Lam, compute_uv=False).max() <= 1 + 1e-12,
      f"||Lambda|| = {np.linalg.svd(Lam, compute_uv=False).max():.15f}")
check("the filter is NOT unitary, so it is not a gate",
      np.abs(Lam.conj().T @ Lam - Id).max() > 1e-3,
      f"max |Lambda*Lambda - I| = {np.abs(Lam.conj().T @ Lam - Id).max():.6f}")

# --------------------------------------------------------------------------
# 1.  The Kraus channel.
# --------------------------------------------------------------------------

LtL = Lam.conj().T @ Lam
w, U0 = np.linalg.eigh(Id - LtL)
w = np.clip(w, 0, None)                              # kill -1e-17 round-off
check("I - Lambda*Lambda is positive semidefinite", w.min() >= -1e-12,
      f"min eigenvalue = {w.min():.2e}")
K1 = U0 @ np.diag(np.sqrt(w)) @ U0.conj().T
K0 = Lam

completeness = np.abs(K0.conj().T @ K0 + K1.conj().T @ K1 - Id).max()
check("the Kraus pair is complete: K0*K0 + K1*K1 = I", completeness < 1e-12,
      f"max deviation = {completeness:.2e}")
check("K1 annihilates the kernel (no leakage from E47)",
      np.abs(K1 @ P).max() < 1e-7, f"max |K1 P| = {np.abs(K1 @ P).max():.2e}")

# --------------------------------------------------------------------------
# 2.  The Stinespring dilation: one unitary on 125 x 2 = 250 dimensions.
# --------------------------------------------------------------------------

Visom = np.vstack([K0, K1])                          # 250 x 125 isometry
check("the dilation column block is an isometry: V*V = I",
      np.abs(Visom.conj().T @ Visom - Id).max() < 1e-12,
      f"max deviation = {np.abs(Visom.conj().T @ Visom - Id).max():.2e}")

# Complete the isometry to a unitary on the full 250-dimensional space.
Q, _ = np.linalg.qr(np.hstack([Visom, np.random.default_rng(47).normal(size=(250, 125))]))
Udil = np.hstack([Visom, Q[:, 125:]])
check("the dilation is a 250-dimensional unitary", Udil.shape == (250, 250),
      f"shape {Udil.shape}")
unit_err = np.abs(Udil.conj().T @ Udil - np.eye(250)).max()
check("U is unitary to machine precision", unit_err < 1e-11,
      f"max |U*U - I| = {unit_err:.2e}")
results["dilation_dimension"] = 250
results["dilation_unitarity_error"] = float(unit_err)

# --------------------------------------------------------------------------
# 3.  Run the channel.  Track occupancy, signature and success probability.
# --------------------------------------------------------------------------

KAPPA = math.log(17 / 15)


def signature_of(p, tol=1e-14):
    g00 = KAPPA ** 2 * p * (1 - p) * (1 - 2 * p)
    e = np.linalg.eigvalsh(np.diag([g00, 2 * p, 2 * p, 2 * p]))
    pos, neg = int((e > tol).sum()), int((e < -tol).sum())
    return (pos, neg, 4 - pos - neg)


def rational_flow(n, p0=F(47, 125)):
    r = RHO ** 2
    p = p0
    for _ in range(n):
        p = p / (p + (1 - p) * r)
    return p


# Worst-case initial state: kernel weight 47/125, complement weight entirely in
# an equioscillation sector (C = 12), which is where the envelope is saturated.
kern = evecs[:, rounded == 6][:, 0]
comp = evecs[:, rounded == 12][:, 0]
psi = kern * math.sqrt(47 / 125) + comp * math.sqrt(78 / 125)
rho = np.outer(psi, psi.conj())

check("the initial state is a valid density matrix",
      abs(np.trace(rho).real - 1) < 1e-12 and np.linalg.eigvalsh(rho).min() > -1e-12)

trace_out_err = 0.0
rows = []
for n in range(7):
    p = float((P @ rho).trace().real / rho.trace().real)
    sig = signature_of(p)
    rows.append({
        "step": n,
        "occupancy": p,
        "occupancy_exact": str(rational_flow(n)),
        "signature": list(sig),
        "regime": "Euclidean" if sig == (4, 0, 0) else ("Lorentzian" if sig == (3, 1, 0) else "degenerate"),
        "success_probability": float((K0 @ rho @ K0.conj().T).trace().real / rho.trace().real),
    })

    # The full channel (no post-selection) must equal tracing the ancilla out
    # of the dilation. This is the check that the dilation is faithful.
    chan = K0 @ rho @ K0.conj().T + K1 @ rho @ K1.conj().T
    # vstack puts the ancilla in the MAJOR index (a*125 + i), so the input
    # product state must be built the same way round: ancilla (x) system.
    inp = np.kron(np.diag([1.0, 0.0]), rho).astype(complex)
    big = (Udil @ inp @ Udil.conj().T).reshape(2, 125, 2, 125)
    traced = big[0, :, 0, :] + big[1, :, 1, :]
    trace_out_err = max(trace_out_err, np.abs(traced - chan).max())

    # Post-select the success branch and renormalize: this is the filter step.
    rho = K0 @ rho @ K0.conj().T
    rho = rho / np.trace(rho).real

check("tracing the ancilla out of U reproduces the Kraus channel exactly",
      trace_out_err < 1e-11, f"max deviation = {trace_out_err:.2e}")

worst = max(abs(r["occupancy"] - float(F(r["occupancy_exact"]))) for r in rows)
check("the quantum run reproduces the exact rational envelope",
      worst < 1e-10, f"max |p_quantum - p_exact| = {worst:.2e}")

check("the simulated signature is Euclidean at step 2",
      rows[2]["regime"] == "Euclidean", f"p_2 = {rows[2]['occupancy']:.9f}")
check("the simulated signature is Lorentzian at step 3",
      rows[3]["regime"] == "Lorentzian", f"p_3 = {rows[3]['occupancy']:.9f}")
check("the signature changes exactly once over the run",
      sum(1 for i in range(1, len(rows)) if rows[i]["regime"] != rows[i - 1]["regime"]) == 1)

# The success probability is bounded below, so the process is not a
# post-selection artefact hiding an exponentially small branch.
pmin = min(r["success_probability"] for r in rows)
check("the post-selection branch never becomes improbable", pmin > 0.5,
      f"min success probability = {pmin:.6f}")

# Independent of the starting point, the signature turns at half occupancy.
for p0 in (F(1, 100), F(1, 4), F(47, 125), F(2, 5)):
    n_cross = next(n for n in range(200) if rational_flow(n, p0) > F(1, 2))
    below = rational_flow(n_cross - 1, p0) < F(1, 2)
    if not check(f"from p0 = {p0} the turn is the first step past half occupancy "
                 f"(step {n_cross})", below):
        break

results["rows"] = rows
results["kraus_completeness_error"] = float(completeness)
results["min_success_probability"] = pmin
results["kappa"] = KAPPA

failed = [c["name"] for c in checks if not c["pass"]]
results["checks"] = checks
results["total"] = len(checks)
results["failed"] = failed
with open(OUT, "w") as f:
    json.dump(results, f, indent=2, sort_keys=True)

print("\n" + "=" * 70)
print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
for r in rows:
    print(f"  step {r['step']}:  p = {r['occupancy']:.9f}   "
          f"signature {tuple(r['signature'])}  {r['regime']:<11} "
          f"P(success) = {r['success_probability']:.6f}")
if failed:
    print("FAILED:")
    for n in failed:
        print("  -", n)
print(f"results written to {OUT}")
sys.exit(1 if failed else 0)
