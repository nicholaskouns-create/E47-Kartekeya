#!/usr/bin/env python3
"""29-dimensional SU(2) intertwiner algebra on E47.

    A_inv = End_SU(2)(H_2) ⊕ End_SU(2)(H_5) ≅ M_5(C) ⊕ M_2(C)

Register: R = C^5 ⊕ C^2, dim 7.
Lift:     E47 = (C^5 ⊗ V_2) ⊕ (C^2 ⊗ V_5), dim 25+22=47.

Matrix units
    E2[i,j]  i,j = 0..4     (25 units)
    E5[a,b]  a,b = 0..1     (4 units)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

M2 = 5
M5 = 2
D2 = 5   # dim V_2
D5 = 11  # dim V_5
DIM_REG = M2 + M5          # 7
DIM_E47 = M2 * D2 + M5 * D5  # 47
N_UNITS = M2 * M2 + M5 * M5  # 29


def _e(n: int, i: int, j: int) -> np.ndarray:
    m = np.zeros((n, n), dtype=np.int8)
    m[i, j] = 1
    return m


def register_units() -> Dict[str, np.ndarray]:
    """29 matrix units on the multiplicity register C^5 ⊕ C^2."""
    units: Dict[str, np.ndarray] = {}
    for i in range(M2):
        for j in range(M2):
            block = np.zeros((DIM_REG, DIM_REG), dtype=np.int8)
            block[:M2, :M2] = _e(M2, i, j)
            units[f"E2[{i},{j}]"] = block
    for a in range(M5):
        for b in range(M5):
            block = np.zeros((DIM_REG, DIM_REG), dtype=np.int8)
            block[M2:, M2:] = _e(M5, a, b)
            units[f"E5[{a},{b}]"] = block
    return units


def lifted_units() -> Dict[str, np.ndarray]:
    """29 units lifted to E47 as (A ⊗ I_5) ⊕ (B ⊗ I_11)."""
    units: Dict[str, np.ndarray] = {}
    for i in range(M2):
        for j in range(M2):
            m = np.zeros((DIM_E47, DIM_E47), dtype=np.int8)
            r0, c0 = i * D2, j * D2
            m[r0 : r0 + D2, c0 : c0 + D2] = np.eye(D2, dtype=np.int8)
            units[f"E2[{i},{j}]"] = m
    off = M2 * D2
    for a in range(M5):
        for b in range(M5):
            m = np.zeros((DIM_E47, DIM_E47), dtype=np.int8)
            r0, c0 = off + a * D5, off + b * D5
            m[r0 : r0 + D5, c0 : c0 + D5] = np.eye(D5, dtype=np.int8)
            units[f"E5[{a},{b}]"] = m
    return units


def unit_names() -> List[str]:
    names = [f"E2[{i},{j}]" for i in range(M2) for j in range(M2)]
    names += [f"E5[{a},{b}]" for a in range(M5) for b in range(M5)]
    return names


@dataclass(frozen=True)
class IntertwinerLock:
    n_units: int
    dim_register: int
    dim_e47: int
    dim_algebra: int
    product_ok: bool
    trace_ok: bool
    commute_blocks_ok: bool
    completeness_ok: bool
    lift_traces: Tuple[int, int]


def validate_units(units: Dict[str, np.ndarray], dim: int, lift: bool) -> IntertwinerLock:
    names2 = [f"E2[{i},{j}]" for i in range(M2) for j in range(M2)]
    names5 = [f"E5[{a},{b}]" for a in range(M5) for b in range(M5)]
    all_names = names2 + names5
    assert len(units) == N_UNITS == len(all_names)

    product_ok = True
    for i in range(M2):
        for j in range(M2):
            for k in range(M2):
                for l in range(M2):
                    left = units[f"E2[{i},{j}]"] @ units[f"E2[{k},{l}]"]
                    right = (units[f"E2[{i},{l}]"] if j == k else np.zeros((dim, dim), dtype=np.int8))
                    if not np.array_equal(left, right):
                        product_ok = False
    for a in range(M5):
        for b in range(M5):
            for c in range(M5):
                for d in range(M5):
                    left = units[f"E5[{a},{b}]"] @ units[f"E5[{c},{d}]"]
                    right = (units[f"E5[{a},{d}]"] if b == c else np.zeros((dim, dim), dtype=np.int8))
                    if not np.array_equal(left, right):
                        product_ok = False

    commute_ok = True
    for n2 in names2:
        for n5 in names5:
            if not np.array_equal(units[n2] @ units[n5], units[n5] @ units[n2]):
                commute_ok = False
            if not np.array_equal(units[n2] @ units[n5], np.zeros((dim, dim), dtype=np.int8)):
                commute_ok = False

    p2 = sum((units[f"E2[{i},{i}]"] for i in range(M2)), np.zeros((dim, dim), dtype=np.int8))
    p5 = sum((units[f"E5[{a},{a}]"] for a in range(M5)), np.zeros((dim, dim), dtype=np.int8))
    ident = np.eye(dim, dtype=np.int8)
    completeness_ok = np.array_equal(p2 + p5, ident)

    if lift:
        tr2 = int(np.trace(units["E2[0,0]"]))
        tr5 = int(np.trace(units["E5[0,0]"]))
        trace_ok = tr2 == D2 and tr5 == D5
        lift_traces = (tr2, tr5)
    else:
        tr2 = int(np.trace(units["E2[0,0]"]))
        tr5 = int(np.trace(units["E5[0,0]"]))
        trace_ok = tr2 == 1 and tr5 == 1
        lift_traces = (tr2, tr5)

    lin_ind = np.stack([units[n].reshape(-1) for n in all_names])
    dim_algebra = int(np.linalg.matrix_rank(lin_ind.astype(float)))

    return IntertwinerLock(
        n_units=len(units),
        dim_register=DIM_REG,
        dim_e47=DIM_E47,
        dim_algebra=dim_algebra,
        product_ok=product_ok,
        trace_ok=trace_ok,
        commute_blocks_ok=commute_ok,
        completeness_ok=completeness_ok,
        lift_traces=lift_traces,
    )


def lock() -> Tuple[IntertwinerLock, IntertwinerLock]:
    return validate_units(register_units(), DIM_REG, lift=False), validate_units(
        lifted_units(), DIM_E47, lift=True
    )


if __name__ == "__main__":
    reg, lift = lock()
    print("register", reg)
    print("lift    ", lift)
    assert reg.n_units == 29 and lift.n_units == 29
    assert reg.dim_algebra == 29 and lift.dim_algebra == 29
    assert reg.product_ok and lift.product_ok
    assert reg.trace_ok and lift.trace_ok
    assert reg.commute_blocks_ok and lift.commute_blocks_ok
    assert reg.completeness_ok and lift.completeness_ok
    print("INTERTWINER LOCK PASS")
