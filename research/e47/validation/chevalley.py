#!/usr/bin/env python3
"""Chevalley relations for sl(5) ⊕ sl(2) in the E47 intertwiner units."""

from __future__ import annotations

from typing import Callable, List

import numpy as np

try:
    from intertwiners import register_units
except ImportError:
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from intertwiners import register_units

A4 = np.array(
    [[2, -1, 0, 0], [-1, 2, -1, 0], [0, -1, 2, -1], [0, 0, -1, 2]],
    dtype=int,
)

PASS: list[tuple[str, str]] = []
FAIL: list[tuple[str, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append((name, detail))
    tag = "PASS" if ok else "FAIL"
    extra = f"  {detail}" if detail else ""
    print(f"  [{tag}] {name}{extra}")


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def ad_power(x: np.ndarray, y: np.ndarray, n: int) -> np.ndarray:
    z = y
    for _ in range(n):
        z = comm(x, z)
    return z


def verify(units=None) -> None:
    u = units if units is not None else register_units()
    E2: Callable[[int, int], np.ndarray] = lambda i, j: u[f"E2[{i},{j}]"]
    E5: Callable[[int, int], np.ndarray] = lambda a, b: u[f"E5[{a},{b}]"]
    H2: List[np.ndarray] = [E2(i, i) - E2(i + 1, i + 1) for i in range(4)]
    Ep2: List[np.ndarray] = [E2(i, i + 1) for i in range(4)]
    Em2: List[np.ndarray] = [E2(i + 1, i) for i in range(4)]
    H5 = E5(0, 0) - E5(1, 1)
    Ep5 = E5(0, 1)
    Em5 = E5(1, 0)
    P2 = sum((E2(i, i) for i in range(5)), np.zeros_like(E2(0, 0)))
    P5 = E5(0, 0) + E5(1, 1)

    check("four Cartan generators", len(H2) == 4)
    check("Tr H2_i = 0", all(int(np.trace(h)) == 0 for h in H2))
    check("[H2_i, H2_j] = 0", all(np.array_equal(comm(H2[i], H2[j]), 0 * H2[0]) for i in range(4) for j in range(4)))
    a4_plus = a4_minus = a4_h = True
    for i in range(4):
        for j in range(4):
            if not np.array_equal(comm(H2[i], Ep2[j]), int(A4[i, j]) * Ep2[j]):
                a4_plus = False
            if not np.array_equal(comm(H2[i], Em2[j]), -int(A4[i, j]) * Em2[j]):
                a4_minus = False
        if not np.array_equal(comm(Ep2[i], Em2[i]), H2[i]):
            a4_h = False
    check("[H2_i, E2_+j] = A4_ij E2_+j", a4_plus)
    check("[H2_i, E2_-j] = -A4_ij E2_-j", a4_minus)
    check("[E2_+i, E2_-i] = H2_i", a4_h)
    serre = True
    for i in range(4):
        for j in range(4):
            if i == j:
                continue
            n = 1 - int(A4[i, j])
            if not np.allclose(ad_power(Ep2[i], Ep2[j], n), 0):
                serre = False
            if not np.allclose(ad_power(Em2[i], Em2[j], n), 0):
                serre = False
    check("Serre ad(E_ai)^{1-A_ij} E_aj = 0", serre)
    check("Tr H5 = 0", int(np.trace(H5)) == 0)
    check("[H5, E5_+] = 2 E5_+", np.array_equal(comm(H5, Ep5), 2 * Ep5))
    check("[H5, E5_-] = -2 E5_-", np.array_equal(comm(H5, Em5), -2 * Em5))
    check("[E5_+, E5_-] = H5", np.array_equal(comm(Ep5, Em5), H5))
    sl5 = H2 + Ep2 + Em2
    sl2 = [H5, Ep5, Em5]
    check("[sl(5), sl(2)] = 0", all(np.array_equal(comm(x, y), 0 * x) for x in sl5 for y in sl2))
    check("P2 + P5 = I_7", np.array_equal(P2 + P5, np.eye(7, dtype=P2.dtype)))
    check("[P2, sl]=[P5, sl]=0", all(np.array_equal(comm(P2, x), 0 * x) and np.array_equal(comm(P5, x), 0 * x) for x in sl5 + sl2))
    check("P2, P5 not in sl (traces 5, 2)", int(np.trace(P2)) == 5 and int(np.trace(P5)) == 2)
    print(f"CHEVALLY LOCK  {len(PASS)} PASS  /  {len(FAIL)} FAIL")
    if FAIL:
        raise SystemExit(1)
    print("ALL CHEVALLEY RELATIONS HOLD.")


if __name__ == "__main__":
    verify()
