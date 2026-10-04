#!/usr/bin/env python3
"""The Kouns Constants in Python and First Principles Notation.

Derives the isolation constants from the carrier and the kernel.
Does not import a locked table. Multiplicities are computed by
successive coupling of three spin-2 representations.
"""

from __future__ import annotations

from fractions import Fraction


def couple(j1: int, j2: int) -> list[tuple[int, int]]:
    """Irreducible content of j1 ⊗ j2. Returns (J, multiplicity)."""
    lo = abs(j1 - j2)
    hi = j1 + j2
    return [(J, 1) for J in range(lo, hi + 1)]


def tensor(content: list[tuple[int, int]], j: int) -> list[tuple[int, int]]:
    """Tensor a multiplicity list by one spin-j factor."""
    acc: dict[int, int] = {}
    for J, m in content:
        for Jp, mp in couple(J, j):
            acc[Jp] = acc.get(Jp, 0) + m * mp
    return sorted(acc.items())


def three_spin(j: int = 2) -> list[tuple[int, int]]:
    one = [(j, 1)]
    two = tensor(one, j)
    return tensor(two, j)


def lucas(n: int) -> int:
    a, b = 2, 1  # L0, L1
    if n == 0:
        return a
    for _ in range(n - 1):
        a, b = b, a + b
    return b


def main() -> None:
    j = 2
    d = 2 * j + 1
    dim_h = d ** 3
    census = three_spin(j)
    rows = []
    for J, m in census:
        sector = m * (2 * J + 1)
        casimir = J * (J + 1)
        mu = (casimir - 6) * (casimir - 30)
        rows.append((J, m, 2 * J + 1, sector, casimir, mu, mu * mu))

    assert sum(r[3] for r in rows) == dim_h == 125
    kernel = [r for r in rows if r[5] == 0]
    complement = [r for r in rows if r[5] != 0]
    dim_e = sum(r[3] for r in kernel)
    rank_k = sum(r[3] for r in complement)
    assert dim_e == 47 and rank_k == 78 and dim_e + rank_k == dim_h
    omega = Fraction(dim_e, dim_h)

    mu2 = [r[6] for r in complement]
    delta = min(mu2)
    lam = max(mu2)
    kappa = lam // delta
    rho = Fraction(kappa - 1, kappa + 1)
    eps = Fraction(2, delta + lam)
    assert delta == 11664 and lam == 186624 and kappa == 16
    assert rho == Fraction(15, 17) and eps == Fraction(1, 99144)

    # First-principles projector: Lagrange interpolant, 1 on kernel roots, 0 off them.
    comp_roots = [r[4] for r in complement]
    kernel_roots = [r[4] for r in kernel]

    all_roots = [r[4] for r in rows]

    def lagrange_denominator(root: int) -> int:
        out = 1
        for other in all_roots:
            if other != root:
                out *= root - other
        return out

    denominators = {root: lagrange_denominator(root) for root in kernel_roots}

    def projector(value: int) -> Fraction:
        total = Fraction(0)
        for root in kernel_roots:
            term = Fraction(1)
            for other in all_roots:
                if other == root:
                    continue
                term *= Fraction(value - other, root - other)
            total += term
        return total

    for root in kernel_roots:
        assert projector(root) == 1
    for root in comp_roots:
        assert projector(root) == 0
    trace = sum(Fraction(r[3]) * projector(r[4]) for r in rows)
    assert trace == 47

    # Engine presentation. (C-31) is not a Casimir root. It is the polynomial
    # written in spectral_engine.py. Verified here, not derived as the unique projector.
    def engine_poly(value: int) -> int:
        return (value - 31) * value * (value - 2) * (value - 12) * (value - 20) * (value - 42)

    engine_normalizer = 1_814_400
    for root in kernel_roots:
        assert engine_poly(root) == engine_normalizer
    for root in comp_roots:
        assert engine_poly(root) == 0

    # Commutant of collective SU(2) on inequivalent kernel irreps.
    mult = {r[0]: r[1] for r in kernel}
    assert set(mult) == {2, 5}
    units = mult[2] ** 2 + mult[5] ** 2
    assert units == 29

    l8, l9 = lucas(8), lucas(9)
    assert l8 == 47 and l9 == 76 and l9 != rank_k

    print("THE KOUNS CONSTANTS")
    print("carrier V2⊗3  dimH", dim_h)
    print("J m d sector C mu mu2")
    for row in rows:
        print(*row)
    print("dimE47", dim_e)
    print("rankK", rank_k)
    print("Omega_c", omega)
    print("Delta", delta)
    print("Lambda", lam)
    print("kappa", kappa)
    print("rho", rho)
    print("eps", eps)
    print("P47_lagrange_denominators", denominators)
    print("P47_engine_normalizer", engine_normalizer)
    print("TrP47", trace)
    print("A_inv_units", units)
    print("L8", l8, "L9", l9)
    print("PASS")


if __name__ == "__main__":
    main()
