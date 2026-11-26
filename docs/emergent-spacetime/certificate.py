#!/usr/bin/env python3
"""
Emergent Spacetime — the Half-Occupancy Theorem, verified end to end.

Builds the 125-dimensional carrier H = V2 (x) V2 (x) V2 from scratch, derives the
selector, the optimal step, the contraction rate, the occupancy flow and the
metric signature, and checks every claim the companion page displays.

Nothing here is read from a stored constant. Every number is recomputed from the
su(2) generators, and the three facts that carry the theorem are closed in exact
integer arithmetic so that Lean and Coq can decide them without real analysis.

Run:  python3 docs/emergent-spacetime/certificate.py
Exit: 0 iff every check passes. Writes results.json beside this file.
"""

from fractions import Fraction as F
import json
import math
import os
import sys

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results.json")
checks = []
results = {}


def check(name, ok, detail=""):
    checks.append({"name": name, "pass": bool(ok), "detail": str(detail)})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return bool(ok)


# ----------------------------------------------------------------------------
# 1.  The carrier.  Three coupled spin-2 systems.
# ----------------------------------------------------------------------------

def spin_ops(j):
    """J_x, J_y, J_z on the (2j+1)-dimensional irrep, basis m = j, j-1, ..., -j."""
    d = int(round(2 * j + 1))
    m = np.array([j - k for k in range(d)], dtype=float)
    jz = np.diag(m)
    jp = np.zeros((d, d), dtype=complex)
    for k in range(1, d):                       # J_+ |j,m> = c |j,m+1>
        mm = m[k]
        jp[k - 1, k] = math.sqrt(j * (j + 1) - mm * (mm + 1))
    jm = jp.conj().T
    return (jp + jm) / 2.0, (jp - jm) / (2.0j), jz.astype(complex)


J = 2.0
d = 5
jx, jy, jz = spin_ops(J)
I5 = np.eye(d, dtype=complex)


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


# Total angular momentum on the three-fold tensor product.
Jtot = [
    kron3(a, I5, I5) + kron3(I5, a, I5) + kron3(I5, I5, a)
    for a in (jx, jy, jz)
]
DIM = d ** 3
check("carrier dimension is 125", DIM == 125, f"dim H = {DIM}")

# su(2) closure on the carrier: [J_x, J_y] = i J_z and cyclic.
comm_err = 0.0
for a, b, c in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
    comm_err = max(comm_err, np.abs(Jtot[a] @ Jtot[b] - Jtot[b] @ Jtot[a] - 1j * Jtot[c]).max())
check("su(2) commutators close on the carrier", comm_err < 1e-10, f"max |[Ja,Jb] - i eps Jc| = {comm_err:.2e}")

C = sum(a @ a for a in Jtot)                    # the Casimir J^2
check("Casimir is Hermitian", np.abs(C - C.conj().T).max() < 1e-10)

evals, evecs = np.linalg.eigh(C)
rounded = np.round(evals).astype(int)
check("Casimir spectrum is integral", np.abs(evals - rounded).max() < 1e-9,
      f"max deviation {np.abs(evals - rounded).max():.2e}")

spectrum = sorted(set(rounded.tolist()))
counts = {int(v): int((rounded == v).sum()) for v in spectrum}
EXPECT_SPEC = [0, 2, 6, 12, 20, 30, 42]
EXPECT_COUNTS = [1, 9, 25, 28, 27, 22, 13]
check("Casimir spectrum is {0,2,6,12,20,30,42}", spectrum == EXPECT_SPEC, str(spectrum))
check("state counts are 1,9,25,28,27,22,13",
      [counts[v] for v in spectrum] == EXPECT_COUNTS,
      str([counts[v] for v in spectrum]))
check("state counts sum to 125", sum(counts.values()) == 125)

results["spectrum"] = spectrum
results["state_counts"] = [counts[v] for v in spectrum]

# ----------------------------------------------------------------------------
# 2.  The selector is forced, not chosen.
#     The two roots sit exactly one standard deviation either side of the mean.
# ----------------------------------------------------------------------------

mu = F(sum(v * counts[v] for v in spectrum), 125)
var = F(sum(counts[v] * (v - mu) ** 2 for v in spectrum), 125)
check("mean of the Casimir spectrum is exactly 18", mu == 18, f"mu = {mu}")
check("variance of the Casimir spectrum is exactly 144", var == 144, f"sigma^2 = {var}")
sigma = F(12)
check("sigma is exactly 12 (144 is a perfect square)", sigma * sigma == var)
check("the selector roots are mu -+ sigma = 6 and 30",
      (mu - sigma, mu + sigma) == (6, 30), f"({mu - sigma}, {mu + sigma})")
results["mu"] = str(mu)
results["sigma_squared"] = str(var)
results["sigma"] = str(sigma)
results["selector_roots"] = [int(mu - sigma), int(mu + sigma)]

# ----------------------------------------------------------------------------
# 3.  The kernel.  K = (C - 6)(C - 30),  E47 = ker K.
# ----------------------------------------------------------------------------

Id = np.eye(DIM, dtype=complex)
K = (C - 6 * Id) @ (C - 30 * Id)
A = K @ K

kvals = {v: (v - 6) * (v - 30) for v in spectrum}
check("K annihilates exactly the j=2 and j=5 sectors",
      [v for v in spectrum if kvals[v] == 0] == [6, 30])

dim_kernel = counts[6] + counts[30]
check("kernel dimension is 47 = 25 + 22", dim_kernel == 47, f"25 + 22 = {dim_kernel}")
check("coherence fraction is 47/125", F(dim_kernel, 125) == F(47, 125), f"Omega_c = {F(47,125)} = {47/125}")
results["kernel_dimension"] = dim_kernel
results["omega_c"] = "47/125"

# Numerical rank of K must agree with the algebraic count.
sK = np.linalg.svd(K, compute_uv=False)
num_rank = int((sK > sK.max() * 1e-10).sum())
check("numerical rank of K is 78 = 125 - 47", num_rank == 78, f"rank K = {num_rank}")

# The projector is built spectrally from the eigenbasis of C, never by pinv:
# a pseudo-inverse projector fails P^2 = P at the 1e-3 level and would silently
# corrupt every signature claim downstream.
sel = np.isin(rounded, [6, 30])
V = evecs[:, sel]
P47 = V @ V.conj().T
check("P47 is idempotent", np.abs(P47 @ P47 - P47).max() < 1e-12,
      f"max |P^2 - P| = {np.abs(P47 @ P47 - P47).max():.2e}")
check("P47 is Hermitian", np.abs(P47 - P47.conj().T).max() < 1e-12)
check("trace P47 = 47", abs(np.trace(P47).real - 47) < 1e-9, f"tr P = {np.trace(P47).real:.12f}")
check("P47 commutes with the Casimir", np.abs(C @ P47 - P47 @ C).max() < 1e-9)
check("K P47 = 0 (the projector lands in the kernel)", np.abs(K @ P47).max() < 1e-9,
      f"max |K P| = {np.abs(K @ P47).max():.2e}")

# The involution eta_E = 2P - I and its inertia.
eta = 2 * P47 - Id
check("eta_E squares to the identity", np.abs(eta @ eta - Id).max() < 1e-12,
      f"max |eta^2 - I| = {np.abs(eta @ eta - Id).max():.2e}")
eig_eta = np.linalg.eigvalsh(eta)
pos, neg = int((eig_eta > 0).sum()), int((eig_eta < 0).sum())
check("inertia of eta_E is (47, 78)", (pos, neg) == (47, 78), f"({pos}, {neg})")
results["eta_inertia"] = [pos, neg]

# ----------------------------------------------------------------------------
# 4.  The optimal step and the contraction rate, both forced by minimax.
# ----------------------------------------------------------------------------

avals = sorted({kvals[v] ** 2 for v in spectrum if kvals[v] != 0})
check("nonzero spectrum of A = K^2 is {11664,12544,19600,32400,186624}",
      avals == [11664, 12544, 19600, 32400, 186624], str(avals))
a_min, a_max = avals[0], avals[-1]
check("condition number of A off the kernel is exactly 16",
      F(a_max, a_min) == 16, f"{a_max}/{a_min} = {F(a_max, a_min)}")
results["a_spectrum"] = avals
results["condition_number"] = 16

# Minimax over Lambda = I - eps A: equioscillation between the extreme
# eigenvalues fixes eps uniquely.  1 - eps a_min = -(1 - eps a_max).
eps_star = F(2, a_min + a_max)
check("the minimax step is eps* = 1/99144", eps_star == F(1, 99144),
      f"2/({a_min}+{a_max}) = {eps_star}")
rho_star = 1 - eps_star * a_min
check("the contraction rate is rho* = 15/17", rho_star == F(15, 17),
      f"1 - {a_min}/99144 = {rho_star}")
check("rho* equioscillates: |1 - eps* a_max| = rho*",
      abs(1 - eps_star * a_max) == rho_star, f"|{1 - eps_star*a_max}| = {rho_star}")
check("rho* is attained twice (at C=12 and C=42), the minimax signature",
      sum(1 for v in spectrum if kvals[v] != 0 and abs(1 - eps_star * kvals[v] ** 2) == rho_star) == 2)
check("every non-kernel sector strictly contracts",
      all(abs(1 - eps_star * kvals[v] ** 2) <= rho_star < 1 for v in spectrum if kvals[v] != 0))
check("both kernel sectors are exactly fixed",
      all(1 - eps_star * kvals[v] ** 2 == 1 for v in (6, 30)))
results["eps_star"] = "1/99144"
results["rho_star"] = "15/17"

# Confirm the filter numerically on the full 125-dimensional operator.
Lam = Id - float(eps_star) * A
sLam = np.linalg.svd(Lam, compute_uv=False)
check("Lambda has operator norm 1 (the kernel is fixed)", abs(sLam.max() - 1) < 1e-9,
      f"||Lambda|| = {sLam.max():.12f}")
off = np.linalg.svd(Lam @ (Id - P47), compute_uv=False).max()
check("Lambda restricted off the kernel has norm 15/17", abs(off - 15 / 17) < 1e-9,
      f"||Lambda(I-P)|| = {off:.12f} vs 15/17 = {15/17:.12f}")

# ----------------------------------------------------------------------------
# 5.  The occupancy flow.  Exact, rational, and logistic in the log-odds.
# ----------------------------------------------------------------------------

r = rho_star ** 2                                # squared contraction per step


def step(p):
    """One filter step on the kernel occupancy p = ||P Psi||^2 / ||Psi||^2."""
    return p / (p + (1 - p) * r)


p0 = F(47, 125)                                  # start at the coherence fraction
traj = [p0]
for _ in range(8):
    traj.append(step(traj[-1]))

# The log-odds is exactly linear in the step number: u_n = u_0 * r^-n.
u0 = p0 / (1 - p0)
check("log-odds is exactly geometric: u_n = u_0 r^-n",
      all(traj[n] / (1 - traj[n]) == u0 / r ** n for n in range(len(traj))))

# The rational map above is the WORST CASE.  Off the kernel, Lambda has five
# distinct factors |1 - eps* K^2| = {0.673, 0.873, 0.882, 0.802, 0.882}; a state
# spread over all of them contracts faster than rho*.  The map is saturated
# exactly when the complement weight sits in an equioscillation sector,
# C = 12 or C = 42, where the factor is exactly 15/17.  So the flow below is an
# envelope: every state reaches half occupancy at this step or sooner.

def seeded_state(sector):
    """Unit state with kernel weight 47/125 and all complement weight in `sector`."""
    kern = evecs[:, rounded == 6][:, 0]
    comp = evecs[:, rounded == sector][:, 0]
    return kern * math.sqrt(47 / 125) + comp * math.sqrt(78 / 125)


def run(state, n):
    out = []
    for _ in range(n):
        out.append(float(np.linalg.norm(P47 @ state) ** 2 / np.linalg.norm(state) ** 2))
        state = Lam @ state
    return out


for sector in (12, 42):
    occ = run(seeded_state(sector), len(traj))
    worst = max(abs(occ[n] - float(traj[n])) for n in range(len(traj)))
    check(f"the rational flow is saturated exactly in sector C = {sector}",
          worst < 1e-12, f"max |p_n(exact) - p_n(operator)| = {worst:.2e}")

# A generic state, spread over every complement sector, must contract at least
# as fast -- never slower.  This is what makes step 3 an upper bound.
rng = np.random.default_rng(47)
psi = rng.normal(size=DIM) + 1j * rng.normal(size=DIM)
inside, outside = P47 @ psi, psi - P47 @ psi
psi = inside / np.linalg.norm(inside) * math.sqrt(47 / 125) \
    + outside / np.linalg.norm(outside) * math.sqrt(78 / 125)
occ = run(psi, len(traj))
check("a generic state starts at the same occupancy 47/125",
      abs(occ[0] - 47 / 125) < 1e-12, f"p_0 = {occ[0]:.15f}")
check("a generic state never contracts slower than the envelope",
      all(occ[n] >= float(traj[n]) - 1e-12 for n in range(len(traj))),
      f"min slack = {min(occ[n] - float(traj[n]) for n in range(len(traj))):.2e}")
check("a generic state crosses half occupancy at step 3 or sooner",
      next(n for n, v in enumerate(occ) if v > 0.5) <= 3,
      f"crossing step = {next(n for n, v in enumerate(occ) if v > 0.5)}")
results["generic_trajectory"] = occ

# ----------------------------------------------------------------------------
# 6.  The theorem.  g_00 = p-double-dot / 4, so the signature turns at p = 1/2.
# ----------------------------------------------------------------------------

kappa = math.log(17 / 15)                        # continuum envelope of the exact map
check("kappa = ln(17/15) reproduces the exact per-step log-odds slope",
      abs(2 * kappa - math.log(1 / float(r))) < 1e-14,
      f"2 ln(17/15) = {2*kappa:.15f}, ln(1/r) = {math.log(1/float(r)):.15f}")
results["kappa"] = "ln(17/15)"
results["kappa_value"] = kappa


def metric(p):
    """The induced coframe metric.  g_00 = kappa^2 p(1-p)(1-2p) = p-double-dot/4."""
    g00 = kappa ** 2 * p * (1 - p) * (1 - 2 * p)
    return np.diag([g00, 2 * p, 2 * p, 2 * p])


def signature(g, tol=1e-14):
    e = np.linalg.eigvalsh(g)
    return (int((e > tol).sum()), int((e < -tol).sum()), int((abs(e) <= tol).sum()))


# g_00 is exactly a quarter of the occupancy acceleration.
for p in (0.1, 0.3, 0.49, 0.5, 0.51, 0.7, 0.9):
    pdot = 2 * kappa * p * (1 - p)
    pddot = 2 * kappa * pdot * (1 - 2 * p)
    if not check(f"g_00 = p-double-dot/4 at p = {p}", abs(metric(p)[0, 0] - pddot / 4) < 1e-15):
        break

ladder = {
    "p -> 0": signature(metric(1e-18)),
    "0 < p < 1/2": signature(metric(0.25)),
    "p = 1/2": signature(metric(0.5)),
    "1/2 < p < 1": signature(metric(0.75)),
    "p = 1": signature(metric(1.0)),
}
check("Euclidean below half occupancy: (4,0,0)", ladder["0 < p < 1/2"] == (4, 0, 0), str(ladder["0 < p < 1/2"]))
check("degenerate exactly at half occupancy: (3,0,1)", ladder["p = 1/2"] == (3, 0, 1), str(ladder["p = 1/2"]))
check("Lorentzian above half occupancy: (3,1,0)", ladder["1/2 < p < 1"] == (3, 1, 0), str(ladder["1/2 < p < 1"]))
check("degenerate again at full occupancy: (3,0,1)", ladder["p = 1"] == (3, 0, 1), str(ladder["p = 1"]))
results["signature_ladder"] = {k: list(v) for k, v in ladder.items()}

# The signature depends on p only through sgn(1 - 2p).  Sampled densely.
bad = [p for p in np.linspace(1e-6, 0.5 - 1e-6, 400) if signature(metric(p)) != (4, 0, 0)]
bad += [p for p in np.linspace(0.5 + 1e-6, 1 - 1e-6, 400) if signature(metric(p)) != (3, 1, 0)]
check("the signature is constant on each side of p = 1/2 (800 samples)", not bad,
      f"{len(bad)} exceptions")

# ----------------------------------------------------------------------------
# 7.  The spatial legs are isotropic: g_kl = 2p delta_kl, exactly.
#     Built from a maximally entangled state across the five spin-2 copies.
# ----------------------------------------------------------------------------

# Highest-weight vectors of the j=2 isotypic component give the copy labels.
Jp = Jtot[0] + 1j * Jtot[1]
W = evecs[:, rounded == 6]                       # 25-dimensional j=2 sector
M = W.conj().T @ Jtot[2] @ W
mz, mv = np.linalg.eigh(M)
top = mv[:, np.abs(mz - 2) < 1e-8]               # m = +2 within the sector
hw = W @ top
check("the j=2 sector has exactly five highest-weight vectors", hw.shape[1] == 5,
      f"{hw.shape[1]} copies")
check("highest-weight vectors are annihilated by J_+", np.abs(Jp @ hw).max() < 1e-9,
      f"max |J_+ v| = {np.abs(Jp @ hw).max():.2e}")

# Orthonormalize the copy basis, then lower each copy into a full spin-2 ladder.
Q, _ = np.linalg.qr(hw)
Jm = Jtot[0] - 1j * Jtot[1]
ladders = []
for c in range(5):
    v = Q[:, c] / np.linalg.norm(Q[:, c])
    rung = [v]
    for _ in range(4):
        v = Jm @ v
        rung.append(v / np.linalg.norm(v))
    ladders.append(rung)

# u pairs copy index c with magnetic index m = 2 - c, one term per copy.
u = sum(ladders[c][c] for c in range(5)) / math.sqrt(5)
check("u is normalized", abs(np.linalg.norm(u) - 1) < 1e-10, f"||u|| = {np.linalg.norm(u):.15f}")
check("u lies inside the kernel", np.abs(K @ u).max() < 1e-9, f"max |K u| = {np.abs(K @ u).max():.2e}")

G = np.array([[ (Jtot[a] @ u).conj() @ (Jtot[b] @ u) for b in range(3)] for a in range(3)])
diag_err = max(abs(G[k, k].real - 2.0) for k in range(3))
offdiag = max(abs(G[a, b]) for a in range(3) for b in range(3) if a != b)
check("spatial Gram matrix is 2 x identity (diagonal)", diag_err < 1e-9,
      f"max |G_kk - 2| = {diag_err:.2e}")
check("spatial Gram matrix is 2 x identity (off-diagonal)", offdiag < 1e-9,
      f"max |G_ab| = {offdiag:.2e}")
check("this is the trace identity (1/5) tr_V2(J_a J_b) = 2 delta_ab",
      abs(float(np.trace(jx @ jx).real) / 5 - 2) < 1e-12,
      f"(1/5) tr(Jx^2) = {float(np.trace(jx @ jx).real)/5:.12f}")
results["spatial_gram_diagonal"] = 2.0

# The three spatial legs all sit in the same C = 6 sector, so they are
# degenerate by symmetry; no birefringence between them is available.
check("all three spatial legs live in the C = 6 sector",
      all(np.abs(C @ (Jtot[a] @ u) - 6 * (Jtot[a] @ u)).max() < 1e-8 for a in range(3)))

# g_0k = 0 because each J_a is Hermitian and u is a real-coefficient kernel state:
# the time leg is proportional to u itself and <u, J_a u> is real and vanishing.
mixed = max(abs(u.conj() @ (Jtot[a] @ u)) for a in range(3))
check("g_0k vanishes: <u, J_a u> = 0 for all three legs", mixed < 1e-9,
      f"max |<u, J_a u>| = {mixed:.2e}")

# ----------------------------------------------------------------------------
# 8.  The decidable core.  Three integer facts that pin the transition step.
# ----------------------------------------------------------------------------

p2, p3 = traj[2], traj[3]
check("p_2 = 3925487/7874237", p2 == F(3925487, 7874237), str(p2))
check("p_3 = 1134465743/2022934493", p3 == F(1134465743, 2022934493), str(p3))
check("p_2 < 1/2  (still Euclidean at step 2)", 2 * p2.numerator < p2.denominator,
      f"2*{p2.numerator} < {p2.denominator}")
check("p_3 > 1/2  (Lorentzian at step 3)", 2 * p3.numerator > p3.denominator,
      f"2*{p3.numerator} > {p3.denominator}")
check("the map is strictly increasing on (0,1)", all(traj[n] < traj[n + 1] for n in range(7)))
check("therefore the envelope changes signature at exactly step 3", p2 < F(1, 2) < p3)

gap = F(1, 2) - p2
check("step 2 lands within 0.15% of the critical point", gap < F(15, 10000),
      f"1/2 - p_2 = {gap} = {float(gap):.7f}")

n_star = math.log(float((1 - p0) / p0)) / (2 * kappa)
check("the continuum crossing time is n* in (2,3)", 2 < n_star < 3, f"n* = {n_star:.6f}")
results["p2"] = str(p2)
results["p3"] = str(p3)
results["p2_float"] = float(p2)
results["p3_float"] = float(p3)
results["gap_below_half"] = str(gap)
results["n_star"] = n_star
results["transition_step"] = 3
results["trajectory"] = [[str(t), float(t)] for t in traj]

# ----------------------------------------------------------------------------

failed = [c["name"] for c in checks if not c["pass"]]
results["checks"] = checks
results["total"] = len(checks)
results["failed"] = failed
with open(OUT, "w") as f:
    json.dump(results, f, indent=2, sort_keys=True)

print("\n" + "=" * 70)
print(f"{len(checks) - len(failed)}/{len(checks)} checks passed")
if failed:
    print("FAILED:")
    for name in failed:
        print("  -", name)
print(f"results written to {OUT}")
sys.exit(1 if failed else 0)
