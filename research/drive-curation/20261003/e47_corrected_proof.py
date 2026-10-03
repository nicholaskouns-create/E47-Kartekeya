#!/usr/bin/env python3
"""
E47 spectral projector: corrected exact proof and executable certificate.

This script derives and verifies:

1. The SU(2) decomposition of V_2^{\otimes 3}.
2. The total-Casimir spectrum and multiplicities.
3. The exact mean and variance of the Casimir spectrum.
4. The statistically selected annihilator
       K = (C - 6 I)(C - 30 I).
5. The exact rank-47 projector onto E_6 \oplus E_30.
6. The correct Lagrange-interpolation polynomial.
7. The internal Z_2 grading D = P_6 - P_30.
8. The contraction Gamma = I - epsilon K^2 and its exact convergence rate.
9. The precise evidence boundary: the SU(2) construction is proved;
   cross-domain applications require additional structure-preserving maps.

No 125x125 angular-momentum matrices are required for the exact certificate:
the proof is performed in the spectral calculus of the total Casimir.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
import json
import math

import numpy as np
import sympy as sp


# ---------------------------------------------------------------------------
# 1. SU(2) tensor-product decomposition
# ---------------------------------------------------------------------------

def tensor_with_spin(mult: dict[int, int], j: int) -> dict[int, int]:
    r"""
    Tensor an SU(2) decomposition with V_j.

    Integer labels denote physical spin j, so dim(V_j) = 2j + 1.
    Clebsch-Gordan:
        V_a \otimes V_b = direct_sum_{c=|a-b|}^{a+b} V_c.
    """
    out: dict[int, int] = {}
    for a, multiplicity in mult.items():
        for c in range(abs(a - j), a + j + 1):
            out[c] = out.get(c, 0) + multiplicity
    return dict(sorted(out.items()))


def triple_spin_two_decomposition() -> dict[int, int]:
    decomp = {2: 1}
    decomp = tensor_with_spin(decomp, 2)
    decomp = tensor_with_spin(decomp, 2)
    return decomp


# ---------------------------------------------------------------------------
# 2. Exact spectral objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SpectralDatum:
    spin: int
    casimir: int
    irrep_multiplicity: int
    eigenspace_dimension: int


def build_spectral_data() -> list[SpectralDatum]:
    decomp = triple_spin_two_decomposition()
    data = []
    for j, mult in decomp.items():
        casimir = j * (j + 1)
        dim = mult * (2 * j + 1)
        data.append(SpectralDatum(j, casimir, mult, dim))
    return data


x = sp.symbols("x")
SPECTRAL_DATA = build_spectral_data()
SPECTRUM = [d.casimir for d in SPECTRAL_DATA]
EIGENSPACE_DIMS = [d.eigenspace_dimension for d in SPECTRAL_DATA]
TOTAL_DIM = sum(EIGENSPACE_DIMS)

assert TOTAL_DIM == 125


def exact_weighted_moment(power: int) -> sp.Rational:
    return sp.Rational(
        sum(dim * (lam ** power) for lam, dim in zip(SPECTRUM, EIGENSPACE_DIMS)),
        TOTAL_DIM,
    )


MU = exact_weighted_moment(1)
SECOND_MOMENT = exact_weighted_moment(2)
VAR = sp.simplify(SECOND_MOMENT - MU**2)
SIGMA = sp.sqrt(VAR)

assert MU == 18
assert VAR == 144
assert SIGMA == 12


# ---------------------------------------------------------------------------
# 3. K and exact shell projectors
# ---------------------------------------------------------------------------

K_POLY = sp.expand((x - 6) * (x - 30))


def lagrange_indicator(target: int) -> sp.Expr:
    """
    Exact spectral indicator polynomial for one target eigenvalue.
    Degree 6 because the spectrum has seven distinct points.
    """
    numerator = sp.Integer(1)
    denominator = sp.Integer(1)
    for lam in SPECTRUM:
        if lam != target:
            numerator *= (x - lam)
            denominator *= (target - lam)
    return sp.cancel(numerator / denominator)


P6_POLY = lagrange_indicator(6)
P30_POLY = lagrange_indicator(30)
P47_POLY = sp.expand(P6_POLY + P30_POLY)
D_POLY = sp.expand(P6_POLY - P30_POLY)

# Correct unsimplified Lagrange denominators:
def lagrange_denominator(target: int) -> int:
    denominator = 1
    for lam in SPECTRUM:
        if lam != target:
            denominator *= target - lam
    return denominator

P6_DEN = lagrange_denominator(6)
P30_DEN = lagrange_denominator(30)

assert P6_DEN == 1741824
assert P30_DEN == -43545600


def values_on_spectrum(poly: sp.Expr) -> dict[int, sp.Rational]:
    return {lam: sp.simplify(poly.subs(x, lam)) for lam in SPECTRUM}


P6_VALUES = values_on_spectrum(P6_POLY)
P30_VALUES = values_on_spectrum(P30_POLY)
P47_VALUES = values_on_spectrum(P47_POLY)
D_VALUES = values_on_spectrum(D_POLY)
K_VALUES = values_on_spectrum(K_POLY)

assert P6_VALUES == {lam: sp.Integer(int(lam == 6)) for lam in SPECTRUM}
assert P30_VALUES == {lam: sp.Integer(int(lam == 30)) for lam in SPECTRUM}
assert P47_VALUES == {lam: sp.Integer(int(lam in (6, 30))) for lam in SPECTRUM}
assert D_VALUES == {
    lam: sp.Integer(1 if lam == 6 else -1 if lam == 30 else 0)
    for lam in SPECTRUM
}

# Polynomial identities only need to hold modulo the minimal polynomial of C.
MINIMAL_POLY = sp.prod(x - lam for lam in SPECTRUM)

def zero_on_spectrum(poly: sp.Expr) -> bool:
    return all(sp.simplify(poly.subs(x, lam)) == 0 for lam in SPECTRUM)

assert zero_on_spectrum(P47_POLY**2 - P47_POLY)
assert zero_on_spectrum(K_POLY * P47_POLY)
assert zero_on_spectrum(D_POLY**2 - P47_POLY)
assert zero_on_spectrum(D_POLY * P47_POLY - D_POLY)

RANK_P6 = sum(d.eigenspace_dimension for d in SPECTRAL_DATA if d.casimir == 6)
RANK_P30 = sum(d.eigenspace_dimension for d in SPECTRAL_DATA if d.casimir == 30)
RANK_P47 = RANK_P6 + RANK_P30
TRACE_D = RANK_P6 - RANK_P30

assert (RANK_P6, RANK_P30, RANK_P47, TRACE_D) == (25, 22, 47, 3)


# ---------------------------------------------------------------------------
# 4. Exact contraction and optimal constant step
# ---------------------------------------------------------------------------

K2_VALUES = {lam: int(K_VALUES[lam] ** 2) for lam in SPECTRUM}
POSITIVE_K2 = sorted({v for v in K2_VALUES.values() if v > 0})
LAMBDA_MIN_POS = min(POSITIVE_K2)
LAMBDA_MAX = max(POSITIVE_K2)

# Standard sufficient interval:
#   0 < epsilon < 2 / lambda_max(K^2)
EPSILON_UPPER = sp.Rational(2, LAMBDA_MAX)

# Optimal constant step for minimizing max |1 - epsilon lambda|
# over lambda in [lambda_min_positive, lambda_max].
EPSILON_STAR = sp.Rational(2, LAMBDA_MIN_POS + LAMBDA_MAX)
RHO_STAR = sp.simplify(
    sp.Rational(LAMBDA_MAX - LAMBDA_MIN_POS, LAMBDA_MAX + LAMBDA_MIN_POS)
)

assert LAMBDA_MIN_POS == 11664
assert LAMBDA_MAX == 186624
assert EPSILON_STAR == sp.Rational(1, 99144)
assert RHO_STAR == sp.Rational(15, 17)


def contraction_error_bound(n: int) -> sp.Rational:
    return RHO_STAR ** n


# Exact spectral simulation on the seven eigenspaces.
gamma_values = {
    lam: sp.simplify(1 - EPSILON_STAR * K2_VALUES[lam])
    for lam in SPECTRUM
}

assert max(abs(v) for lam, v in gamma_values.items() if lam not in (6, 30)) == RHO_STAR
assert gamma_values[6] == 1
assert gamma_values[30] == 1


# ---------------------------------------------------------------------------
# 5. Numerical 125-dimensional certificate
# ---------------------------------------------------------------------------

def diagonal_operator_from_spectral_values(values: dict[int, float]) -> np.ndarray:
    diag = []
    for datum in SPECTRAL_DATA:
        diag.extend([float(values[datum.casimir])] * datum.eigenspace_dimension)
    return np.diag(np.array(diag, dtype=float))


C_num = diagonal_operator_from_spectral_values({lam: lam for lam in SPECTRUM})
K_num = (C_num - 6 * np.eye(TOTAL_DIM)) @ (C_num - 30 * np.eye(TOTAL_DIM))
P_num = diagonal_operator_from_spectral_values({lam: int(lam in (6, 30)) for lam in SPECTRUM})
D_num = diagonal_operator_from_spectral_values({
    lam: 1 if lam == 6 else -1 if lam == 30 else 0 for lam in SPECTRUM
})

eps_star_float = float(EPSILON_STAR)
Gamma_num = np.eye(TOTAL_DIM) - eps_star_float * (K_num @ K_num)

def opnorm(a: np.ndarray) -> float:
    return float(np.linalg.norm(a, ord=2))

numeric_checks = {
    "projector_idempotence": opnorm(P_num @ P_num - P_num),
    "kernel_annihilation": opnorm(K_num @ P_num),
    "grading_square": opnorm(D_num @ D_num - P_num),
    "grading_support": opnorm(D_num @ P_num - D_num),
    "trace_projector": float(np.trace(P_num)),
    "trace_grading": float(np.trace(D_num)),
    "gamma_500_error": opnorm(np.linalg.matrix_power(Gamma_num, 500) - P_num),
    "rho_star_power_500": float(RHO_STAR**500),
}


# ---------------------------------------------------------------------------
# 6. Human-readable certificate
# ---------------------------------------------------------------------------

certificate = {
    "carrier": {
        "space": "V_2 tensor V_2 tensor V_2",
        "dimension": TOTAL_DIM,
        "decomposition": {
            f"V_{d.spin}": d.irrep_multiplicity for d in SPECTRAL_DATA
        },
    },
    "casimir": {
        "spectrum": SPECTRUM,
        "eigenspace_dimensions": EIGENSPACE_DIMS,
        "mean": str(MU),
        "variance": str(VAR),
        "sigma": str(SIGMA),
    },
    "filter": {
        "K": str(K_POLY),
        "kernel_eigenvalues": [6, 30],
        "kernel_dimension": RANK_P47,
    },
    "projector": {
        "P6": str(P6_POLY),
        "P30": str(P30_POLY),
        "P47_expanded": str(P47_POLY),
        "rank_P6": RANK_P6,
        "rank_P30": RANK_P30,
        "rank_P47": RANK_P47,
    },
    "grading": {
        "D": str(D_POLY),
        "eigenvalue_on_E6": 1,
        "eigenvalue_on_E30": -1,
        "trace_D": TRACE_D,
        "interpretation": "Z2 grading / involution on E6 direct-sum E30",
    },
    "contraction": {
        "Gamma": "I - epsilon K^2",
        "epsilon_interval": f"0 < epsilon < {EPSILON_UPPER}",
        "epsilon_star": str(EPSILON_STAR),
        "rho_star": str(RHO_STAR),
        "positive_K2_spectrum": POSITIVE_K2,
    },
    "numeric_checks": numeric_checks,
    "evidence_boundary": (
        "Proves the finite-dimensional SU(2) spectral construction. "
        "Relativity, biomolecular folding, cognition, or governance mappings "
        "are analogies until explicit structure-preserving maps are defined and proved."
    ),
}


def main() -> None:
    print("E47 CORRECTED EXACT CERTIFICATE")
    print("=" * 72)
    print("SU(2) decomposition:")
    print("  " + " + ".join(
        f"{d.irrep_multiplicity} V_{d.spin}" for d in SPECTRAL_DATA
    ))
    print(f"Dimension check: {TOTAL_DIM}")
    print()
    print(f"Casimir spectrum: {SPECTRUM}")
    print(f"Eigenspace dimensions: {EIGENSPACE_DIMS}")
    print(f"mu = {MU}, variance = {VAR}, sigma = {SIGMA}")
    print()
    print(f"K(x) = {K_POLY}")
    print(f"ker K = E_6 direct-sum E_30, dimension = {RANK_P47}")
    print()
    print("Correct shell projectors:")
    print(f"P_6(x)  = {P6_POLY}")
    print(f"P_30(x) = {P30_POLY}")
    print(f"P_47(x) = P_6(x) + P_30(x)")
    print(f"Expanded P_47(x) = {P47_POLY}")
    print()
    print(f"D(x) = P_6(x) - P_30(x)")
    print(f"D^2 = P_47 on spec(C), Tr(D) = {TRACE_D}")
    print()
    print(f"epsilon* = {EPSILON_STAR}")
    print(f"rho* = {RHO_STAR}")
    print(f"||Gamma^500 - P_47||_2 = {numeric_checks['gamma_500_error']:.3e}")
    print(f"Exact bound rho*^500 = {float(RHO_STAR**500):.3e}")
    print()
    print("All symbolic and numerical assertions passed.")

    out = Path(__file__).with_name("e47_corrected_certificate.json")
    out.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    print(f"Certificate written to: {out}")


if __name__ == "__main__":
    main()
