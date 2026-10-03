#!/usr/bin/env python3
"""
RUBIK UNIFICATION MAPPING INVESTIGATION
Exact Professor's Cube Permutation Algebra, C5^3 Laplacian Spectrum,
Eigenmode Impact Table, and Corrected Continuity Theorem
"""
from __future__ import annotations
import numpy as np

N = 5
DIM = N**3
OMEGA_C = 47 / 125

def idx(x: int, y: int, z: int) -> int:
    return 25 * x + 5 * y + z

def cycle_laplacian(n: int = 5) -> np.ndarray:
    L1 = 2.0 * np.eye(n)
    for i in range(n):
        L1[i, (i - 1) % n] -= 1.0
        L1[i, (i + 1) % n] -= 1.0
    return L1

def torus_laplacian() -> np.ndarray:
    I = np.eye(N)
    L1 = cycle_laplacian(N)
    return (
        np.kron(np.kron(L1, I), I)
        + np.kron(np.kron(I, L1), I)
        + np.kron(np.kron(I, I), L1)
    )

def make_permutation(mapper) -> np.ndarray:
    P = np.zeros((DIM, DIM), dtype=np.int8)
    for x in range(N):
        for y in range(N):
            for z in range(N):
                xx, yy, zz = mapper(x, y, z)
                P[idx(xx, yy, zz), idx(x, y, z)] = 1
    return P
