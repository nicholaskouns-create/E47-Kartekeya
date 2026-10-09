#!/usr/bin/env python3
"""Certify the corrected E47 K^2 pipeline against the Casimir sector theorem.

Carrier V = V2 ⊗ V2 ⊗ V2, dim 125.
K = (C - 6I)(C - 30I) annihilates J=2 (dim 25) and J=5 (dim 22).
dim ker K = 47. Complement dim 78 contracts under x <- x - ε K² x, ε = 2^{-18}.
Format matches the Verilog: signed Q16.48.
"""

from __future__ import annotations

FRAC = 48
SCALE = 1 << FRAC
EPS_SHIFT = 18
SIX = 6 * SCALE
THIRTY = 30 * SCALE
OMEGA = int(round((47 / 125) * SCALE))  # 47/125 exactly represented to Q16.48 rounding
RES = 1 << 16  # 2^{-32} in Q16.48


def qmul(a: int, b: int) -> int:
    return (a * b) >> FRAC


def k_squared(lam: int) -> int:
    k = qmul(lam - SIX, lam - THIRTY)
    return qmul(k, k)


def couple() -> list[tuple[int, int, int]]:
    """Return (J, multiplicity, degeneracy 2J+1) for 2⊗2⊗2."""
    counts = {J: 0 for J in range(7)}
    for j in range(5):
        for J in range(abs(j - 2), j + 2 + 1):
            counts[J] += 1
    return [(J, counts[J], 2 * J + 1) for J in range(7)]


def main() -> None:
    sectors = couple()
    dim = sum(m * d for _, m, d in sectors)
    assert dim == 125, dim

    rows = []
    ker = 0
    for J, m, d in sectors:
        lam = J * (J + 1) * SCALE
        k2 = k_squared(lam)
        dimJ = m * d
        if k2 == 0:
            ker += dimJ
        rows.append((J, dimJ, J * (J + 1), k2 / SCALE))

    assert ker == 47, ker

    # Fixed test amplitudes. Kernel lanes must be invariant.
    amps = [int(round(v * SCALE)) for v in (0.4, -0.7, 1.25, 0.3, -0.9, 0.55, 0.8)]
    kernel_before = (amps[2], amps[5])

    def step(xs: list[int]) -> list[int]:
        out = []
        for J, x in enumerate(xs):
            lam = J * (J + 1) * SCALE
            k2 = k_squared(lam)
            if k2 == 0:
                out.append(x)
            else:
                out.append(x - (qmul(k2, x) >> EPS_SHIFT))
        return out

    xs = amps[:]
    history = []
    for n in range(1, 481):
        xs = step(xs)
        comp = max(abs(xs[J]) for J in range(7) if k_squared(J * (J + 1) * SCALE) != 0)
        history.append((n, comp / SCALE))
        if comp <= RES:
            break

    assert (xs[2], xs[5]) == kernel_before
    # Uniform ε = 2^{-18} is stable. The slowest complement sector is J=3, ρ ≈ 0.9555.
    assert history[-1][1] < 1e-6

    # Exact mask lands on the same invariant, complement at the null sink.
    exact = [amps[J] if k_squared(J * (J + 1) * SCALE) == 0 else 0 for J in range(7)]
    assert exact[2] == kernel_before[0] and exact[5] == kernel_before[1]
    assert exact[0] == exact[1] == exact[3] == exact[4] == exact[6] == 0

    omega = OMEGA / SCALE
    print(f"dim V = {dim}")
    print(f"dim ker K = {ker}")
    print(f"Omega_c literal = {omega:.15f}  (47/125 = {47/125:.15f})")
    print("J   dim  C=J(J+1)   K^2")
    for J, dimJ, c, k2 in rows:
        mark = "  KERNEL" if k2 == 0 else ""
        print(f"{J}  {dimJ:4d}  {c:8d}   {k2:12.1f}{mark}")
    print(f"converged in {history[-1][0]} iterations, complement residual {history[-1][1]:.3e}")
    print("kernel lanes invariant: J=2 and J=5 unchanged")
    print("exact mask and iterated projector agree on ker K")


if __name__ == "__main__":
    main()
