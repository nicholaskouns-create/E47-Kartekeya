#!/usr/bin/env python3
"""Q5 ledger validator.

Checks the 125 words against the packing bijection and the residuals
already measured by validate_lig_proof.py / the poster validator.
Does not construct C, K, or P. Does not mint a credential.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import codec  # noqa: E402


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load_cells(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                _fail(f"cells.jsonl line {n}: {exc}")
            rows.append(row)
    return rows


def check_cells(rows: list[dict]) -> None:
    if len(rows) != codec.DIM:
        _fail(f"expected {codec.DIM} cells, got {len(rows)}")

    seen_i, seen_xyz, seen_word = set(), set(), set()
    for n, row in enumerate(rows):
        try:
            i, x, y, z, w = row["i"], row["x"], row["y"], row["z"], row["word"]
        except KeyError as exc:
            _fail(f"cell {n} missing field {exc}")
        if (x, y, z) != codec.unpi(i):
            _fail(f"unpi({i}) != {(x, y, z)}")
        if codec.pi(x, y, z) != i:
            _fail(f"pi{(x, y, z)} != {i}")
        if codec.word(x, y, z) != w:
            _fail(f"word{(x, y, z)} != {w!r}")
        if codec.unword(w) != (x, y, z):
            _fail(f"unword({w!r}) != {(x, y, z)}")
        if i in seen_i:
            _fail(f"duplicate index {i}")
        if (x, y, z) in seen_xyz:
            _fail(f"duplicate coordinate {(x, y, z)}")
        if w in seen_word:
            _fail(f"duplicate word {w!r}")
        seen_i.add(i)
        seen_xyz.add((x, y, z))
        seen_word.add(w)

    if seen_i != set(range(codec.DIM)):
        _fail("indices are not exactly {0,...,124}")
    expected_xyz = {
        (x, y, z)
        for x in range(codec.RADIX)
        for y in range(codec.RADIX)
        for z in range(codec.RADIX)
    }
    if seen_xyz != expected_xyz:
        _fail("coordinates do not cover {0,1,2,3,4}^3")


def check_residuals() -> None:
    r = codec.RESIDUALS["exact"]

    if sum(codec.CASIMIR_MULTIPLICITIES) != codec.DIM:
        _fail("Casimir multiplicities do not sum to 125")
    if codec.CASIMIR_MULTIPLICITIES[2] + codec.CASIMIR_MULTIPLICITIES[5] != codec.KERNEL:
        _fail("mult(C=6)+mult(C=30) != 47")
    if codec.KERNEL + codec.COMPLEMENT != codec.DIM:
        _fail("47+78 != 125")

    if codec.quinary(codec.KERNEL) != codec.WORD_47:
        _fail("47 is not 142_5")
    if codec.quinary(codec.COMPLEMENT) != codec.WORD_78:
        _fail("78 is not 303_5")
    if codec.quinary(codec.DIM) != codec.WORD_125:
        _fail("125 is not 1000_5")
    if int(codec.WORD_47, 5) + int(codec.WORD_78, 5) != int(codec.WORD_125, 5):
        _fail("142_5 + 303_5 != 1000_5")

    if codec.OMEGA.numerator != 47 or codec.OMEGA.denominator != 125:
        _fail("Ω_c is not 47/125")
    if float(codec.OMEGA) != 0.376:
        _fail("47/125 is not 0.376")
    if codec.EPS_STAR.denominator != 99144 or codec.EPS_STAR.numerator != 1:
        _fail("ε* is not 1/99144")
    if codec.EPS_MAX.denominator != 93312 or codec.EPS_MAX.numerator != 1:
        _fail("ε_max is not 1/93312")
    if codec.RHO_STAR.numerator != 15 or codec.RHO_STAR.denominator != 17:
        _fail("ρ* is not 15/17")

    k_from_c = [(lam - 6) * (lam - 30) for lam in codec.CASIMIR_SPECTRUM]
    k2 = sorted({k * k for k in k_from_c})
    if tuple(k2) != codec.K2_SPECTRUM:
        _fail("K² spectrum does not match (C−6I)(C−30I)")
    if 0 not in k2 or codec.K2_GAP not in k2 or codec.K2_MAX not in k2:
        _fail("K² missing 0, 11664, or 186624")
    positive = [v for v in k2 if v]
    if min(positive) != 11664 or max(positive) != 186624:
        _fail("K² gap/max mismatch")
    # ε* = 2/(μ_min+μ_max) = 2/(11664+186624) = 2/198288 = 1/99144
    if 2 * 99144 != 11664 + 186624:
        _fail("ε* identity 2/(μ_min+μ_max) failed")
    # ε_max = 2/μ_max = 2/186624 = 1/93312
    if 2 * 93312 != 186624:
        _fail("ε_max identity 2/μ_max failed")
    # ρ* = (μ_max−μ_min)/(μ_max+μ_min) = 174960/198288 = 15/17
    if (186624 - 11664) * 17 != (186624 + 11664) * 15:
        _fail("ρ* identity (max−min)/(max+min) = 15/17 failed")

    if r["cube_laplacian_frobenius"] != "8*sqrt(3)":
        _fail("cube Frobenius residual is not the measured 8√3")
    if r["cube_laplacian_spectral"] != "2*sqrt(2)":
        _fail("cube spectral residual is not the measured 2√2")

    m = codec.RESIDUALS["measured"]
    if not (0 <= m["projector_idempotence"] < m["lig_tol"]):
        _fail("measured projector idempotence exceeds L_IG tolerance")
    if not (0 <= m["kernel_annihilation"] < m["lig_annihilation_tol"]):
        _fail("measured kernel annihilation exceeds L_IG tolerance")
    if not (0 <= m["asymptotic_projector_residual"] < m["lig_contraction_n250_tol"]):
        _fail("measured asymptotic projector residual exceeds L_IG n=250 class")


def main() -> None:
    cells_path = HERE / "cells.jsonl"
    if not cells_path.is_file():
        _fail(f"missing {cells_path}")
    rows = load_cells(cells_path)
    check_cells(rows)
    check_residuals()
    print("Q5 LEDGER: PASS")
    print(f"words: {codec.DIM}")
    print(f"map: π(x,y,z)=25x+5y+z")
    print(f"Ω_c: {codec.OMEGA} = {float(codec.OMEGA)}")
    print(f"ε*: {codec.EPS_STAR}")
    print(f"ρ*: {codec.RHO_STAR}")
    print("witness: validate_lig_proof.py / poster validator")
    print("authority: none added")


if __name__ == "__main__":
    main()
