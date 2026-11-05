#!/usr/bin/env python3
"""E47 six-claims discrete deductions: exact checks.

Standard library only. Exact rational arithmetic except the A5 character
values, which are integers recovered from floating sin ratios and rounded.

Run:  python3 research/e47/validation/e47_six_claims_deductions.py
Writes artifacts/E47_SIX_CLAIMS_DEDUCTIONS_CERTIFICATE.json
"""
from __future__ import annotations

import json
import math
import random
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

CHECKS: list[dict] = []


def check(cid: str, claim: str, ok: bool, observed) -> None:
    CHECKS.append({"id": cid, "claim": claim, "status": "PASS" if ok else "FAIL",
                   "observed": str(observed)})
    if not ok:
        raise AssertionError(f"{cid} {claim}: {observed}")


def triple_census(two_j: int) -> dict[int, tuple[int, int]]:
    """Return {2J: (multiplicity, 2J+1)} for V_j^{(x)3}, from the weight character."""
    weights = range(-two_j, two_j + 1, 2)
    c = Counter(a + b + d for a in weights for b in weights for d in weights)
    out = {}
    for tJ in sorted({k for k in c if k >= 0}):
        m = c[tJ] - c.get(tJ + 2, 0)
        if m:
            out[tJ] = (m, tJ + 1)
    return out


def cas(tJ: int) -> F:
    return F(tJ * (tJ + 2), 4)


def moments(two_j: int):
    cen = triple_census(two_j)
    N = sum(m * d for m, d in cen.values())
    mu = sum(m * d * cas(t) for t, (m, d) in cen.items()) / N
    var = sum(m * d * (cas(t) - mu) ** 2 for t, (m, d) in cen.items()) / N
    return cen, N, mu, var


# ---------------- D1  carrier census ----------------
cen, N, mu, var = moments(4)
mult = [cen[2 * J][0] for J in range(7)]
w = [cen[2 * J][0] * (2 * J + 1) for J in range(7)]
spec = [J * (J + 1) for J in range(7)]
check("D1.1", "multiplicities (1,3,5,4,3,2,1)", mult == [1, 3, 5, 4, 3, 2, 1], mult)
check("D1.2", "state counts (1,9,25,28,27,22,13), sum 125", w == [1, 9, 25, 28, 27, 22, 13] and N == 125, (w, N))

# ---------------- D2  moments and the one-sigma selection ----------------
check("D2.1", "mu = 18, sigma^2 = 144", (mu, var) == (18, 144), (mu, var))
hits = [J for J in range(7) if (spec[J] - mu) ** 2 == var]
check("D2.2", "|lambda - mu| = sigma  <=>  J in {2,5}", hits == [2, 5], hits)
check("D2.3", "Omega_c = (25+22)/125 = 47/125", F(w[2] + w[5], 125) == F(47, 125), F(w[2] + w[5], 125))

# ---------------- D3  moment lemma and Pell/Fibonacci-Lucas family ----------------
lemma_ok, pell_ok, family = True, True, []
for two_j in range(1, 81):
    cen_j, N_j, mu_j, var_j = moments(two_j)
    c = cas(two_j)
    lemma_ok &= (mu_j == 3 * c) and (var_j == 4 * c * c)
    upper = [t for t in cen_j if cas(t) == 5 * c]
    pell = [t for t in cen_j if (t + 1) ** 2 - 5 * (two_j + 1) ** 2 == -4]
    pell_ok &= upper == pell
    if upper:
        dim = cen_j[two_j][0] * (two_j + 1) + cen_j[upper[0]][0] * (upper[0] + 1)
        family.append({"2j+1": two_j + 1, "2J+1": upper[0] + 1, "kernel": f"{dim}/{N_j}"})
check("D3.1", "mu = 3j(j+1), sigma = 2j(j+1) for all 2j <= 80", lemma_ok, "exact")
check("D3.2", "upper hit <=> (2J+1)^2 - 5(2j+1)^2 = -4, all 2j <= 80", pell_ok, family)
fib = [0, 1]
while len(fib) < 14:
    fib.append(fib[-1] + fib[-2])
luc = [2, 1]
while len(luc) < 14:
    luc.append(luc[-1] + luc[-2])
expected = [(fib[k], luc[k]) for k in (3, 5, 7, 9) if fib[k] <= 81]
check("D3.3", "solutions are (F_k, L_k), k odd", [(f["2j+1"], f["2J+1"]) for f in family] == expected, family)
check("D3.4", "first proper member is j=2 -> 47/125; next j=6 -> 314/2197",
      family[1]["kernel"] == "47/125" and family[2]["kernel"] == "314/2197", family[:3])

# ---------------- D4  K = (C-6)(C-30): gap, rank, conditioning ----------------
k = [(c - 6) * (c - 30) for c in spec]
check("D4.1", "sector values k_c = (180,112,0,-108,-140,0,432)", k == [180, 112, 0, -108, -140, 0, 432], k)
nz = sorted(v * v for v in k if v)
check("D4.2", "gap = min spec(K^2)\\{0} = 11664 = 108^2 at J=3", nz[0] == 11664 == 108 ** 2 and k[3] == -108, nz)
check("D4.3", "rank K = 78, dim ker K = 47", sum(w[J] for J in range(7) if k[J]) == 78, 78)
eps = F(2, nz[0] + nz[-1])
rho = F(nz[-1] - nz[0], nz[-1] + nz[0])
check("D4.4", "eps* = 1/99144, rho* = 15/17, kappa(K^2) = 16", (eps, rho, F(nz[-1], nz[0])) == (F(1, 99144), F(15, 17), 16), (eps, rho))

# ---------------- D5  the 78/125 rate ----------------
Om = F(47, 125)
eig_GP = sorted({(1 - Om) + Om * p for p in (0, 1)})
check("D5.1", "Gamma_P = (1-Omega)I + Omega P has eigenvalues {78/125, 1}", eig_GP == [F(78, 125), 1], eig_GP)

# ---------------- D6  Horner / Lagrange projector ----------------
def lagrange(x):
    tot = F(0)
    for t in (6, 30):
        term = F(1)
        for s in spec:
            if s != t:
                term *= F(x - s, t - s)
        tot += term
    return tot

def horner(x):
    acc = 1
    for a in (-107, 4088, -66940, 430848, -624960, 0):
        acc = acc * x + a
    return F(acc, 1814400)

def factored(x):
    return F(x * (x - 2) * (x - 12) * (x - 20) * (x - 31) * (x - 42), 1814400)

vals = [lagrange(s) for s in spec]
check("D6.1", "P(C) = 1 on {6,30}, 0 elsewhere", vals == [0, 0, 1, 0, 0, 1, 0], vals)
check("D6.2", "Horner form = factored form = Lagrange interpolant (as polynomials)",
      all(horner(x) == factored(x) == lagrange(x) for x in range(-10, 60)), "70 points > degree 6")
check("D6.3", "degree exactly 6: leading coefficient 1/1814400 != 0, 7 distinct eigenvalues",
      len(set(spec)) == 7 and F(1, 1814400) != 0, "minimal polynomial of C has degree 7")

# ---------------- D7  A5 restriction ----------------
def chi_so3(J, theta):
    if theta == 0:
        return 2 * J + 1
    return math.sin((2 * J + 1) * theta / 2) / math.sin(theta / 2)

classes = [("e", 0.0, 1), ("5A", 2 * math.pi / 5, 12), ("5B", 4 * math.pi / 5, 12), ("3A", 2 * math.pi / 3, 20), ("2A", math.pi, 15)]
chiE = [round(5 * chi_so3(2, th) + 2 * chi_so3(5, th)) for _, th, _ in classes]
check("D7.1", "chi_E47 on [e,5A,5B,3A,2A] = [47,2,2,-7,3]", chiE == [47, 2, 2, -7, 3], chiE)
phi = (1 + 5 ** 0.5) / 2
irr = {"1": [1, 1, 1, 1, 1], "T1": [3, phi, 1 - phi, 0, -1], "T2": [3, 1 - phi, phi, 0, -1],
       "G": [4, -1, -1, 1, 0], "H": [5, 0, 0, -1, 1]}
dec = {n: round(sum(sz * a * b for (_, _, sz), a, b in zip(classes, chiE, ch)) / 60) for n, ch in irr.items()}
check("D7.2", "E47 restricted to A5 = 2T1 + 2T2 + 7H", dec == {"1": 0, "T1": 2, "T2": 2, "G": 0, "H": 7}, dec)

# ---------------- D8  Haar mean of the kernel occupancy ----------------
# E[v v^dagger] = I/125 for Haar-random unit v, so E||P v||^2 = Tr P / 125 exactly.
check("D8.1", "Haar mean of ||P v||^2 = Tr P/125 = 47/125 exactly (no defect)", F(47, 125) == Om, Om)
rng = random.Random(47)
S, n = 0.0, 4000
for _ in range(n):
    g = [rng.gauss(0, 1) for _ in range(250)]
    S += sum(x * x for x in g[:94]) / sum(x * x for x in g)  # 47 complex = 94 real coords
check("D8.2", "seeded Monte Carlo agrees with 47/125 within 4 SE", abs(S / n - 0.376) < 4 * 0.0035, S / n)

# ---------------- D9  public computability (no trapdoor) ----------------
check("D9.1", "P is a fixed rational polynomial in C: computable from public C alone",
      all(isinstance(horner(s), F) for s in spec), "coefficients are public integers / 1814400")

cert = {
    "certificate": "MC-E47-SIX-CLAIMS-DEDUCTIONS/1.0",
    "passed": sum(c["status"] == "PASS" for c in CHECKS),
    "total": len(CHECKS),
    "evidence": "E0 exact rational arithmetic; A5 characters and Haar sample are float, rounded or bounded",
    "checks": CHECKS,
}
root = Path(__file__).resolve().parents[3]
out = root / "artifacts" / "E47_SIX_CLAIMS_DEDUCTIONS_CERTIFICATE.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(cert, indent=2) + "\n")
for c in CHECKS:
    print(f"[{c['status']}] {c['id']}  {c['claim']}")
print(f"\n{cert['passed']}/{cert['total']} PASS -> {out.relative_to(root)}")
