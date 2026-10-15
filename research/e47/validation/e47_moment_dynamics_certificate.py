#!/usr/bin/env python3
"""MC-E47-MOMENT-DYNAMICS/1.0 — contraction dynamics of the moment selector.

On a Fibonacci–Lucas carrier V_j^(x)3 (2j+1 = F_k, k odd >= 5) the moment selector
K = (C - j(j+1)I)(C - 5j(j+1)I) acts on the spin-J sector as the scalar
mu_J = (J(J+1) - a)(J(J+1) - 5a), a = j(j+1). The dynamics are

    flow       x' = -K^2 x,           x(t) = e^{-tK^2} x0 -> P x0,   ||e^{-tK^2} - P|| = e^{-Delta t}
    iteration  x_{n+1} = (I - eps K^2) x_n,   stable iff 0 < eps < 2/Lambda
    optimum    eps* = 2/(Delta + Lambda),   rho* = (kappa - 1)/(kappa + 1),   Chebyshev (sqrt(kappa) - 1)/(sqrt(kappa) + 1)

with closed forms on every member

    gap at J = j+1:   |mu| = 4(j+1)^2 (2j-1)          Delta  = 16 (j+1)^4 (2j-1)^2
    top at J = 3j:    |mu| = 4 j^2 (4j+1)(2j-1)        Lambda = 16 j^4 (4j+1)^2 (2j-1)^2
    sqrt(kappa) = ||K|| / gap = j^2 (4j+1) / (j+1)^2
    eps* = 1 / (8 (2j-1)^2 [(j+1)^4 + j^4 (4j+1)^2])

On the cube (j = 2): sqrt(kappa) = 4, rho* = 15/17, Chebyshev 3/5, eps* = 1/99144. sqrt(kappa) rises
along the family, and it is an integer only on the cube.

Exact layer: rational arithmetic over every sector of each member k = 5..13. Machine layer:
float64 replay of the flow, the iteration, and finite termination on the 125x125 carrier.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) > 3 else Path.cwd()
OUT = (ROOT / "artifacts" / "E47_MOMENT_DYNAMICS_CERTIFICATE.json") if (ROOT / "artifacts").exists() \
    else Path(__file__).with_name("E47_MOMENT_DYNAMICS_CERTIFICATE.json")
if os.environ.get("E47_CERT_OUT"):
    OUT = Path(os.environ["E47_CERT_OUT"])

MEMBERS = (5, 7, 9, 11, 13)


# ---------------------------------------------------------------- exact layer

def fibonacci_lucas(kmax: int):
    fib, luc = [0, 1], [2, 1]
    while len(fib) <= kmax:
        fib.append(fib[-1] + fib[-2])
        luc.append(luc[-1] + luc[-2])
    return fib, luc


def sectors(j2: int) -> Counter:
    """Multiplicities {2J: m_J} of V_j^(x)3, with j = j2/2."""
    mult = Counter({j2: 1})
    for _ in range(2):
        nxt = Counter()
        for J2, m in mult.items():
            for K2 in range(abs(J2 - j2), J2 + j2 + 1, 2):
                nxt[K2] += m
        mult = nxt
    return mult


def casimir(J2: int) -> F:
    return F(J2 * (J2 + 2), 4)


def member(k: int, fib, luc) -> dict:
    j2, Js2 = fib[k] - 1, luc[k] - 1
    j = F(j2, 2)
    a = j * (j + 1)
    mu = {J2: (casimir(J2) - a) * (casimir(J2) - 5 * a) for J2 in sectors(j2)}
    nonzero = {J2: v for J2, v in mu.items() if v != 0}
    gap_J2 = min(nonzero, key=lambda J2: abs(nonzero[J2]))
    top_J2 = max(nonzero, key=lambda J2: abs(nonzero[J2]))
    gap, top = abs(nonzero[gap_J2]), abs(nonzero[top_J2])
    Delta, Lam = gap ** 2, top ** 2
    kappa, root_kappa = Lam / Delta, F(top, gap)
    return dict(
        k=k, j=j, j2=j2, Js2=Js2, a=a, mu=mu, kernel=sorted(set(mu) - set(nonzero)),
        gap_J2=gap_J2, top_J2=top_J2, gap=gap, top=top, Delta=Delta, Lam=Lam,
        kappa=kappa, root_kappa=root_kappa, eps=2 / (Delta + Lam),
        rho=(kappa - 1) / (kappa + 1), cheb=(root_kappa - 1) / (root_kappa + 1),
        degree=len({v * v for v in nonzero.values()}),
    )


def exact():
    fib, luc = fibonacci_lucas(15)
    rows = [member(k, fib, luc) for k in MEMBERS]
    closed = lambda r: dict(
        gap=4 * (r["j"] + 1) ** 2 * (2 * r["j"] - 1),
        top=4 * r["j"] ** 2 * (4 * r["j"] + 1) * (2 * r["j"] - 1),
        root_kappa=r["j"] ** 2 * (4 * r["j"] + 1) / (r["j"] + 1) ** 2,
        eps=1 / (8 * (2 * r["j"] - 1) ** 2 * ((r["j"] + 1) ** 4 + r["j"] ** 4 * (4 * r["j"] + 1) ** 2)),
    )
    # sqrt(kappa) = j^2(4j+1)/(j+1)^2 as a function of j alone: integral for j >= 1/2 only at j = 2
    f = lambda j: j * j * (4 * j + 1) / (j + 1) ** 2
    integral_j2 = [j2 for j2 in range(1, 4001) if f(F(j2, 2)).denominator == 1]
    return rows, closed, integral_j2


# ---------------------------------------------------------------- machine layer

def machine(cube: dict):
    j = 2.0
    m = np.arange(j, -j - 1, -1)
    Jp = np.zeros((5, 5), complex)
    for i, mi in enumerate(m[:-1]):
        Jp[i, i + 1] = np.sqrt(j * (j + 1) - mi * (mi - 1))
    Jx, Jy, Jz = .5 * (Jp + Jp.conj().T), -.5j * (Jp - Jp.conj().T), np.diag(m).astype(complex)
    I5, I = np.eye(5), np.eye(125)
    tot = lambda A: np.kron(np.kron(A, I5), I5) + np.kron(np.kron(I5, A), I5) + np.kron(np.kron(I5, I5), A)
    C = sum(tot(A) @ tot(A) for A in (Jx, Jy, Jz))
    C = ((C + C.conj().T) / 2).real
    K = (C - 6 * I) @ (C - 30 * I)
    K2 = K @ K

    # Finite termination: the product over the distinct nonzero mu^2 is the exact projector.
    levels = sorted({float(v * v) for v in cube["mu"].values() if v != 0})
    P = I.copy()
    for lev in levels:
        P = P @ (I - K2 / lev)
    P = (P + P.T) / 2
    proj_ok = (np.linalg.norm(P @ P - P, 2) < 1e-9 and abs(np.trace(P) - 47) < 1e-9
               and np.linalg.norm(K @ P, 2) < 1e-6)

    # Discrete iteration at eps*: ||Gamma^n - P|| = (15/17)^n.
    eps, rho = float(cube["eps"]), float(cube["rho"])
    G = I - eps * K2
    Gn, discrete = I.copy(), []
    for n in range(1, 21):
        Gn = Gn @ G
        discrete.append(np.linalg.norm(Gn - P, 2) / rho ** n)
    discrete_ok = max(abs(r - 1) for r in discrete) < 1e-8

    # Continuous flow: ||e^{-tK^2} - P|| = e^{-Delta t}, from the spectral decomposition of K^2.
    w, V = np.linalg.eigh(K2)
    Delta = float(cube["Delta"])
    flow = []
    for t in (1e-5, 5e-5, 1e-4, 3e-4):
        Et = (V * np.exp(-w * t)) @ V.T
        flow.append(np.linalg.norm(Et - P, 2) / math.exp(-Delta * t))
    flow_ok = max(abs(r - 1) for r in flow) < 1e-8

    # Stability boundary: I - eps K^2 contracts the complement iff eps < 2/Lambda.
    Lam = float(cube["Lam"])
    radius = lambda e: max(abs(1 - e * float(v * v)) for v in cube["mu"].values() if v != 0)
    stable_ok = radius(2 / Lam * (1 - 1e-6)) < 1 < radius(2 / Lam * (1 + 1e-3))

    # Outcomes only, so the committed record is byte-stable across machines.
    return dict(projector=bool(proj_ok), discrete=bool(discrete_ok), flow=bool(flow_ok),
                stability=bool(stable_ok), termination_steps=len(levels),
                tolerance="relative deviation < 1e-8 for 20 iteration steps and 4 flow times")


def main():
    rows, closed, integral_j2 = exact()
    cube = rows[0]
    mc = machine(cube)
    checks = {
        "kernel_is_j_and_upper_root": all(r["kernel"] == sorted({r["j2"], r["Js2"]}) for r in rows),
        "gap_at_J_equals_j_plus_1": all(r["gap_J2"] == r["j2"] + 2 for r in rows),
        "top_at_J_equals_3j": all(r["top_J2"] == 3 * r["j2"] for r in rows),
        "gap_closed_form": all(r["gap"] == closed(r)["gap"] for r in rows),
        "top_closed_form": all(r["top"] == closed(r)["top"] for r in rows),
        "lower_neighbours_differ_by_4": all(abs(r["mu"][r["j2"] - 2]) - abs(r["mu"][r["j2"] + 2]) == 4 for r in rows),
        "root_kappa_closed_form": all(r["root_kappa"] == closed(r)["root_kappa"] for r in rows),
        "optimal_step_closed_form": all(r["eps"] == closed(r)["eps"] for r in rows),
        "cube_rates_16_15_17_3_5_99144": (cube["kappa"], cube["root_kappa"], cube["rho"], cube["cheb"], cube["eps"])
                                         == (16, 4, F(15, 17), F(3, 5), F(1, 99144)),
        "cube_best_conditioned_in_family": all(x["root_kappa"] < y["root_kappa"] for x, y in zip(rows, rows[1:])),
        "integral_ratio_only_on_cube": integral_j2 == [4],
        "machine_flow_and_iteration_rates": mc["flow"] and mc["discrete"] and mc["stability"],
        "machine_five_step_exact_projector": mc["projector"] and mc["termination_steps"] == 5,
    }
    checks = {k: bool(v) for k, v in checks.items()}
    family = [dict(k=r["k"], j=str(r["j"]), J_upper=str(F(r["Js2"], 2)),
                   gap_sector=str(F(r["gap_J2"], 2)), top_sector=str(F(r["top_J2"], 2)),
                   gap_abs_mu=str(r["gap"]), top_abs_mu=str(r["top"]),
                   Delta=str(r["Delta"]), Lambda=str(r["Lam"]),
                   sqrt_kappa=str(r["root_kappa"]), kappa=str(r["kappa"]),
                   eps_star=str(r["eps"]), rho_star=str(r["rho"]), chebyshev=str(r["cheb"]),
                   finite_termination_steps=r["degree"]) for r in rows]
    cert = {
        "schema": "MC-E47-MOMENT-DYNAMICS/1.0",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "exact": {
            "evidence": "exact rational arithmetic over every sector of each Fibonacci–Lucas member k = 5..13",
            "dynamics": {
                "flow": "x' = -K^2 x; ||e^{-tK^2} - P|| = e^{-Delta t}",
                "iteration": "x_{n+1} = (I - eps K^2) x_n; stable iff 0 < eps < 2/Lambda",
                "optimum": "eps* = 2/(Delta+Lambda), rho* = (kappa-1)/(kappa+1), Chebyshev (sqrt(kappa)-1)/(sqrt(kappa)+1)",
            },
            "closed_forms": {
                "gap": "|mu_(j+1)| = 4(j+1)^2(2j-1)",
                "top": "|mu_(3j)| = 4j^2(4j+1)(2j-1)",
                "sqrt_kappa": "j^2(4j+1)/(j+1)^2",
                "eps_star": "1/(8(2j-1)^2[(j+1)^4 + j^4(4j+1)^2])",
                "lower_neighbours": "|mu_(j-1)| = |mu_(j+1)| + 4",
            },
            "integral_sqrt_kappa_for_2j_up_to_4000": [str(F(j2, 2)) for j2 in integral_j2],
            "family": family,
        },
        "machine": {"evidence": "float64 replay on the 125x125 carrier", **mc},
        "boundary": ("Dynamics of the moment selector on the Fibonacci–Lucas triple products k = 5..13, with closed "
                     "forms proved in the note for every member. Linear flow and iteration only; no physical time "
                     "scale or physical identification is claimed."),
    }
    OUT.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    print(json.dumps(cert, indent=2, sort_keys=True))
    if cert["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
