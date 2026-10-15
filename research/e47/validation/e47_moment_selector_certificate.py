#!/usr/bin/env python3
"""MC-E47-MOMENT-SELECTOR/1.0 — the moment selector and its Fibonacci–Lucas carriers.

On a carrier H = V_j^(x)n with total Casimir C, let mu and sigma^2 be the mean and
variance of spec(C) under the normalized trace. The moment selector is

    K_mom = (C - (mu - sigma) I)(C - (mu + sigma) I).

On the cube (j = 2, n = 3) mu = 18, sigma = 12 and K_mom = (C - 6I)(C - 30I) = K.

Lemma:   mu = n j(j+1),  sigma^2 = (2n(n-1)/3) [j(j+1)]^2.
         sigma is rational only for n = 3, 25, 243, ...; three factors come first.
Theorem: on V_j^(x)3, mu - sigma = j(j+1) and mu + sigma = 5 j(j+1). Both roots are
         Casimir values iff (2J+1)^2 - 5(2j+1)^2 = -4, i.e. (2J+1, 2j+1) = (L_k, F_k)
         with k odd. Spin 1/2 selects the whole carrier; the first proper member is
         spin 2, sectors {2, 5}, dim ker = 47 of 125.

Exact layer: Clebsch–Gordan decompositions in rational arithmetic. Machine layer:
float64 replay on the 125x125 carrier.
"""
from __future__ import annotations

import json
import math
import os
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import sympy as sp

ROOT = Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) > 3 else Path.cwd()
OUT = (ROOT / "artifacts" / "E47_MOMENT_SELECTOR_CERTIFICATE.json") if (ROOT / "artifacts").exists() \
    else Path(__file__).with_name("E47_MOMENT_SELECTOR_CERTIFICATE.json")
if os.environ.get("E47_CERT_OUT"):
    OUT = Path(os.environ["E47_CERT_OUT"])

ODD_K = (3, 5, 7, 9, 11, 13)


# ---------------------------------------------------------------- exact layer

def decompose(j2: int, n: int) -> Counter:
    """Multiplicities {2J: m_J} of V_j^(x)n, with j = j2/2."""
    mult = Counter({j2: 1})
    for _ in range(n - 1):
        nxt = Counter()
        for J2, m in mult.items():
            for K2 in range(abs(J2 - j2), J2 + j2 + 1, 2):
                nxt[K2] += m
        mult = nxt
    return mult


def casimir(J2: int) -> F:
    return F(J2 * (J2 + 2), 4)                      # J(J+1) with J = J2/2


def moments(j2: int, n: int):
    dims = {J2: m * (J2 + 1) for J2, m in decompose(j2, n).items()}
    D = sum(dims.values())
    mu = sum(d * casimir(J2) for J2, d in dims.items()) / D
    var = sum(d * casimir(J2) ** 2 for J2, d in dims.items()) / D - mu ** 2
    return dims, D, mu, var


def rational_sqrt(q: F) -> F | None:
    a, b = math.isqrt(q.numerator), math.isqrt(q.denominator)
    return F(a, b) if a * a == q.numerator and b * b == q.denominator else None


def fibonacci_lucas(kmax: int):
    fib, luc = [0, 1], [2, 1]
    while len(fib) <= kmax:
        fib.append(fib[-1] + fib[-2])
        luc.append(luc[-1] + luc[-2])
    return fib, luc


def upper_root_spin2(j2: int) -> int | None:
    """2J for the J with J(J+1) = 5 j(j+1), if such a half-integer J >= 0 exists."""
    y = j2 + 1                                       # 2j + 1
    x2 = 5 * y * y - 4
    x = math.isqrt(x2)
    return x - 1 if x * x == x2 else None           # 2J = x - 1


def exact():
    fib, luc = fibonacci_lucas(31)
    jw = lambda j2: F(j2, 2) * (F(j2, 2) + 1)       # j(j+1)

    variance_lemma = all(
        moments(j2, n)[2] == n * jw(j2)
        and moments(j2, n)[3] == F(2 * n * (n - 1), 3) * jw(j2) ** 2
        for n in range(2, 7) for j2 in range(1, 11)
    )
    triple_closed_forms = all(
        moments(j2, 3)[2] == 3 * jw(j2) and rational_sqrt(moments(j2, 3)[3]) == 2 * jw(j2)
        for j2 in range(1, 41)
    )
    rational_sigma_n = [n for n in range(2, 300) if rational_sqrt(F(2 * n * (n - 1), 3)) is not None]

    # lower root mu - sigma = j(j+1): the J = j sector, always present in V_j^(x)3
    lower_root = all(
        moments(j2, 3)[2] - 2 * jw(j2) == jw(j2) and decompose(j2, 3)[j2] > 0
        for j2 in range(1, 121)
    )

    # upper root mu + sigma = 5 j(j+1) lies in spec(C) exactly on the Fibonacci list
    in_spec = []
    for j2 in range(1, 401):
        J2 = upper_root_spin2(j2)
        if J2 is None or J2 > 3 * j2 or (J2 - 3 * j2) % 2:
            continue
        if j2 <= 120 and decompose(j2, 3)[J2] == 0:
            continue
        in_spec.append(j2)
    fib_list = [fib[k] - 1 for k in range(3, 31, 2) if fib[k] - 1 <= 400]

    norm_equation = all(luc[k] ** 2 - 5 * fib[k] ** 2 == -4 for k in range(1, 30, 2))
    phi = (1 + sp.sqrt(5)) / 2
    phi_powers = all(sp.expand(phi ** k - (luc[k] + fib[k] * sp.sqrt(5)) / 2) == 0 for k in range(1, 16))

    family = []
    for k in ODD_K:
        j2, J2 = fib[k] - 1, luc[k] - 1
        dims, D, mu, var = moments(j2, 3)
        sigma = rational_sqrt(var)
        hits = sigma is not None and casimir(j2) == mu - sigma and casimir(J2) == mu + sigma and J2 in dims
        ker = dims[j2] + dims.get(J2, 0)
        family.append(dict(k=k, F_k=fib[k], L_k=luc[k], j=str(F(j2, 2)), J=str(F(J2, 2)),
                           mu=str(mu), sigma=str(sigma), dim_kernel=ker, dim_carrier=D,
                           omega=str(F(ker, D)), selector_hits_both_sectors=bool(hits)))
    return dict(variance_lemma=variance_lemma, triple_closed_forms=triple_closed_forms,
                rational_sigma_n=rational_sigma_n, lower_root=lower_root, in_spec=in_spec,
                fib_list=fib_list, norm_equation=norm_equation, phi_powers=phi_powers, family=family)


# ---------------------------------------------------------------- machine layer

def machine():
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
    mu = np.trace(C) / 125
    var = np.trace(C @ C) / 125 - mu ** 2
    sigma = math.sqrt(var)
    Kmom = (C - (mu - sigma) * I) @ (C - (mu + sigma) * I)
    nullity = 125 - int(np.linalg.matrix_rank(Kmom, tol=1e-6 * max(1.0, np.linalg.norm(Kmom, 2))))
    return dict(mu=round(float(mu), 9), sigma=round(sigma, 9), nullity=nullity)  # rounded: byte-stable record


def main():
    e, mc = exact(), machine()
    fam = {row["k"]: row for row in e["family"]}
    checks = {
        "variance_lemma_n2_to_6": e["variance_lemma"],
        "triple_mu_3jj1_sigma_2jj1": e["triple_closed_forms"],
        "three_is_first_rational_sigma": e["rational_sigma_n"][:3] == [3, 25, 243],
        "lower_root_is_spin_j_sector": e["lower_root"],
        "upper_root_iff_fibonacci_to_j200": e["in_spec"] == e["fib_list"] == [1, 4, 12, 33, 88, 232],
        "norm_equation_lucas_fibonacci": e["norm_equation"],
        "phi_power_identity": e["phi_powers"],
        "selector_hits_both_sectors_k3_to_k13": all(r["selector_hits_both_sectors"] for r in e["family"]),
        "spin_half_selects_whole_carrier": fam[3]["dim_kernel"] == fam[3]["dim_carrier"] == 8,
        "first_proper_member_is_e47": (fam[5]["j"], fam[5]["J"], fam[5]["mu"], fam[5]["sigma"],
                                       fam[5]["dim_kernel"], fam[5]["dim_carrier"]) == ("2", "5", "18", "12", 47, 125),
        "proper_kernel_for_k5_to_k13": all(fam[k]["dim_kernel"] < fam[k]["dim_carrier"] for k in ODD_K[1:]),
        "machine_cube_moments_18_12": abs(mc["mu"] - 18) < 1e-9 and abs(mc["sigma"] - 12) < 1e-9,
        "machine_cube_kmom_nullity_47": mc["nullity"] == 47,
    }
    checks = {k: bool(v) for k, v in checks.items()}
    cert = {
        "schema": "MC-E47-MOMENT-SELECTOR/1.0",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "exact": {
            "evidence": "exact rational arithmetic over Clebsch–Gordan decompositions",
            "selector": "K_mom = (C - (mu - sigma)I)(C - (mu + sigma)I), moments of spec(C) under the normalized trace",
            "lemma": "mu = n j(j+1), sigma^2 = (2n(n-1)/3)[j(j+1)]^2",
            "rational_sigma_tensor_powers": e["rational_sigma_n"][:3],
            "triple_roots": "mu - sigma = j(j+1) (sector J = j); mu + sigma = 5 j(j+1)",
            "norm_equation": "(2J+1)^2 - 5(2j+1)^2 = -4  <=>  (2J+1, 2j+1) = (L_k, F_k), k odd",
            "carriers_with_both_roots_in_spectrum_2j_up_to_400": e["in_spec"],
            "family": e["family"],
        },
        "machine": {"evidence": "float64 replay on the 125x125 carrier", **mc},
        "boundary": ("Triple products V_j^(x)3 only. The moment rule is a chosen selector; the theorem shows the "
                     "carrier it forces, not that the rule is the only natural one. For n = 25, 243, ... sigma is "
                     "rational and the question is open. No physical identification is claimed."),
    }
    OUT.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    print(json.dumps(cert, indent=2, sort_keys=True))
    if cert["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
