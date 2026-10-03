#!/usr/bin/env python3
"""Portable numerics for algebraic-visualizations.

Mirrors src/lib/algebra/{matrix,eigen,lattice,compute}.ts. If they disagree,
the TypeScript lab is source of truth.
"""

from __future__ import annotations

import math
from typing import Literal

Family = Literal["cycle", "path", "complete", "band", "star", "goe"]
OMEGA_NUM = 47
OMEGA_DEN = 125
OMEGA = OMEGA_NUM / OMEGA_DEN


def zeros(n: int) -> list[list[float]]:
    return [[0.0] * n for _ in range(n)]


def identity(n: int) -> list[list[float]]:
    I = zeros(n)
    for i in range(n):
        I[i][i] = 1.0
    return I


def add(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    n = len(A)
    return [[A[i][j] + B[i][j] for j in range(n)] for i in range(n)]


def scale(A: list[list[float]], s: float) -> list[list[float]]:
    n = len(A)
    return [[s * A[i][j] for j in range(n)] for i in range(n)]


def mul(A: list[list[float]], B: list[list[float]]) -> list[list[float]]:
    n = len(A)
    C = zeros(n)
    for i in range(n):
        for k in range(n):
            aik = A[i][k]
            if aik == 0:
                continue
            for j in range(n):
                C[i][j] += aik * B[k][j]
    return C


def frobenius(A: list[list[float]]) -> float:
    s = 0.0
    for row in A:
        for x in row:
            s += x * x
    return math.sqrt(s)


def trace(A: list[list[float]]) -> float:
    return sum(A[i][i] for i in range(len(A)))


def copy_mat(A: list[list[float]]) -> list[list[float]]:
    return [row[:] for row in A]


def build_C(n: int, family: Family, seed: int = 47) -> list[list[float]]:
    A = zeros(n)
    if family == "cycle":
        for i in range(n):
            A[i][(i + 1) % n] = 1.0
            A[i][(i + n - 1) % n] = 1.0
        return A
    if family == "path":
        for i in range(n - 1):
            A[i][i + 1] = A[i + 1][i] = 1.0
        return A
    if family == "complete":
        for i in range(n):
            for j in range(n):
                if i != j:
                    A[i][j] = 1.0
        return A
    if family == "band":
        for i in range(n):
            for d in (1, 2):
                A[i][(i + d) % n] = 1.0
                A[i][(i + n - d) % n] = 1.0
        return A
    if family == "star":
        for i in range(1, n):
            A[0][i] = A[i][0] = 1.0
        return A
    # GOE — deterministic mulberry32 + Box-Muller, matching matrix.ts
    rng = mulberry32(seed)
    for i in range(n):
        A[i][i] = gaussian(rng)
        for j in range(i + 1, n):
            v = gaussian(rng)
            A[i][j] = A[j][i] = v
    return A


def mulberry32(seed: int):
    a = seed & 0xFFFFFFFF

    def rng() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = (a ^ (a >> 15)) * (1 | a)
        t &= 0xFFFFFFFF
        t = (t + ((t ^ (t >> 7)) * (61 | t))) & 0xFFFFFFFF
        t ^= t >> 14
        return (t & 0xFFFFFFFF) / 4294967296.0

    return rng


def gaussian(rng) -> float:
    u = max(1e-12, rng())
    v = rng()
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)


def shifted_product(C: list[list[float]], lam1: float, lam2: float) -> list[list[float]]:
    n = len(C)
    I = identity(n)
    return mul(add(C, scale(I, -lam1)), add(C, scale(I, -lam2)))


def jacobi_symmetric(
    A: list[list[float]], tol: float = 1e-12, max_sweeps: int = 48
) -> tuple[list[float], list[list[float]]]:
    n = len(A)
    M = copy_mat(A)
    V = identity(n)
    for _ in range(max_sweeps):
        off = 0.0
        for p in range(n):
            for q in range(p + 1, n):
                off += M[p][q] * M[p][q]
        if math.sqrt(2.0 * off) < tol:
            break
        for p in range(n):
            for q in range(p + 1, n):
                apq = M[p][q]
                if abs(apq) < tol:
                    continue
                app, aqq = M[p][p], M[q][q]
                tau = (aqq - app) / (2.0 * apq)
                t = (1.0 if tau >= 0 else -1.0) / (abs(tau) + math.sqrt(1.0 + tau * tau))
                c = 1.0 / math.sqrt(1.0 + t * t)
                s = t * c
                for k in range(n):
                    if k == p or k == q:
                        continue
                    mkp, mkq = M[k][p], M[k][q]
                    M[k][p] = M[p][k] = c * mkp - s * mkq
                    M[k][q] = M[q][k] = s * mkp + c * mkq
                M[p][p] = c * c * app - 2 * s * c * apq + s * s * aqq
                M[q][q] = s * s * app + 2 * s * c * apq + c * c * aqq
                M[p][q] = M[q][p] = 0.0
                for k in range(n):
                    vkp, vkq = V[k][p], V[k][q]
                    V[k][p] = c * vkp - s * vkq
                    V[k][q] = s * vkp + c * vkq
    pairs = sorted(((M[i][i], i) for i in range(n)), key=lambda x: -x[0])
    values = [p[0] for p in pairs]
    vectors = zeros(n)
    for j, (_, src) in enumerate(pairs):
        for i in range(n):
            vectors[i][j] = V[i][src]
    return values, vectors


def kernel_mask(values: list[float], frob: float) -> list[bool]:
    peak = max((abs(v) for v in values), default=0.0)
    eps = max(1e-7, 1e-4 * max(frob, peak, 1e-6))
    return [abs(v) <= eps for v in values]


def multiplicity_near(values: list[float], lam: float, rel: float = 1e-6) -> int:
    tol = max(1e-8, rel * max(abs(lam), 1.0))
    return sum(1 for v in values if abs(v - lam) <= tol)


def compute_operator(
    n: int,
    family: Family = "cycle",
    seed: int = 47,
    lock: bool = True,
    lam1_input: float = 0.0,
    lam2_input: float = 0.0,
    eig_index1: int = 0,
    eig_index2: int = 1,
) -> dict:
    C = build_C(n, family, seed)
    eigC, vecC = jacobi_symmetric(C)
    i1 = max(0, min(n - 1, eig_index1))
    i2 = max(0, min(n - 1, eig_index2))
    lam1 = eigC[i1] if lock else lam1_input
    lam2 = eigC[i2] if lock else lam2_input
    K = shifted_product(C, lam1, lam2)
    eigK, vecK = jacobi_symmetric(K)
    frobK = frobenius(K)
    ker_raw = kernel_mask(eigK, frobK)
    same = abs(lam1 - lam2) < max(1e-6, 1e-5 * max(abs(lam1), abs(lam2), 1.0))
    from_c = multiplicity_near(eigC, lam1) + (0 if same else multiplicity_near(eigC, lam2))
    dim_ker = min(n, max(sum(ker_raw), from_c if lock else 0))
    order = sorted(range(n), key=lambda i: abs(eigK[i]))
    kerK = [False] * n
    for k in range(dim_ker):
        kerK[order[k]] = True
    residual = None
    if dim_ker > 0:
        v = [0.0] * n
        for j in range(n):
            if not kerK[j]:
                continue
            for i in range(n):
                v[i] += vecK[i][j]
        nv = math.sqrt(sum(x * x for x in v))
        if nv > 0:
            unit = [x / nv for x in v]
            Kv = [sum(K[i][j] * unit[j] for j in range(n)) for i in range(n)]
            residual = math.sqrt(sum(x * x for x in Kv))
    return {
        "n": n,
        "family": family,
        "C": C,
        "K": K,
        "eigC": eigC,
        "eigK": eigK,
        "lam1": lam1,
        "lam2": lam2,
        "dimKer": dim_ker,
        "rank": n - dim_ker,
        "trK": trace(K),
        "frobK": frobK,
        "residual": residual,
        "kerK": kerK,
        "vecC": vecC,
    }


def cube_cells(n: int = 5) -> list[dict]:
    cells = []
    tau = 2.0 * math.pi / n
    index = 0
    for k in range(n):
        for j in range(n):
            for i in range(n):
                phi = math.cos(tau * i) + math.cos(tau * j) + math.cos(tau * k)
                cells.append({"i": i, "j": j, "k": k, "index": index, "phi": phi})
                index += 1
    return cells


def kernel_sector(cells: list[dict], count: int = 47) -> set[int]:
    ranked = sorted(cells, key=lambda c: (-abs(c["phi"]), c["index"]))
    return {c["index"] for c in ranked[:count]}


def diagonal_sector(cells: list[dict]) -> set[int]:
    return {c["index"] for c in cells if c["i"] == c["j"] == c["k"]}
