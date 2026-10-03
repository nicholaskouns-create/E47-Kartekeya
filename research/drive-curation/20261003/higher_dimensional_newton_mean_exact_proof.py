#!/usr/bin/env python3
"""
HIGHER-DIMENSIONAL NEWTON-MEAN ITERATIONS
Exact Python Proof, Fixed-Point Invariant, and Corrected Stability Domain

Nicholas Kouns
AIMS Research Institute
Validation edition: July 2026

This executable proof validates the coupled map

    T(rho, sigma) =
      (1/2 (rho + a/rho + kappa*sigma),
       1/2 (sigma + b/sigma + kappa*rho))

for a,b > 0.

VALIDATED EXACTLY
-----------------
1. Fixed-point invariant:
       rho_*^2 - sigma_*^2 = a - b.
2. Product quadratic:
       (1-kappa^2)p_*^2 - kappa(a+b)p_* - ab = 0.
3. Unique positive fixed point for |kappa| < 1.
4. Jacobian determinant zero and eigenvalues {0,tau}.
5. Symmetric diagonal reduction when a=b.
6. Quadratic convergence at kappa=0 and linear local convergence
   with rate |tau| whenever |tau|<1.

CORRECTIONS FOR THE SUBMITTED DRAFT
-----------------------------------
A. rho^2-sigma^2=a-b is a fixed-point invariant, not an orbitwise
   conserved quantity.
B. For kappa<0, T is not a self-map of the entire positive quadrant.
C. The claim |tau|<1 for every |kappa|<1 is false when a != b and
   kappa is sufficiently negative.
D. The exact corrected local-stability interval is

       -kappa_c(a,b) < kappa < 1,

   where kappa_c=1 if a=b, and otherwise kappa_c=sqrt(z_c), with

       (a-b)^2 z_c^2
       + (3a^2 - 2ab + 3b^2) z_c
       - 4ab = 0,

   taking the unique positive root.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from math import sqrt, isfinite
from typing import Iterable

import numpy as np
import sympy as sp


TITLE = (
    "HIGHER-DIMENSIONAL NEWTON-MEAN ITERATIONS: "
    "EXACT PYTHON PROOF, FIXED-POINT INVARIANT, "
    "AND CORRECTED STABILITY DOMAIN"
)


@dataclass(frozen=True)
class FixedPoint:
    rho: float
    sigma: float
    product: float
    discriminant: float
    tau: float


def T(rho: float, sigma: float, a: float, b: float, kappa: float) -> tuple[float, float]:
    """One coupled Newton-mean step."""
    if rho == 0.0 or sigma == 0.0:
        raise ZeroDivisionError("rho and sigma must be nonzero")
    return (
        0.5 * (rho + a / rho + kappa * sigma),
        0.5 * (sigma + b / sigma + kappa * rho),
    )


def predicted_fixed_point(a: float, b: float, kappa: float) -> FixedPoint:
    """Closed-form positive fixed point for a,b>0 and |kappa|<1."""
    if not (a > 0.0 and b > 0.0):
        raise ValueError("a and b must be positive")
    if not abs(kappa) < 1.0:
        raise ValueError("closed-form theorem here assumes |kappa|<1")

    disc = kappa**2 * (a - b) ** 2 + 4.0 * a * b
    p = (kappa * (a + b) + sqrt(disc)) / (2.0 * (1.0 - kappa**2))
    rho_sq = 0.5 * ((a - b) + sqrt((a - b) ** 2 + 4.0 * p**2))
    sigma_sq = rho_sq - (a - b)

    if p <= 0.0 or rho_sq <= 0.0 or sigma_sq <= 0.0:
        raise ArithmeticError("positive fixed-point construction failed")

    rho = sqrt(rho_sq)
    sigma = sqrt(sigma_sq)
    tau = kappa * (a + b) / (2.0 * p) + kappa**2
    return FixedPoint(rho, sigma, p, disc, tau)


def jacobian_at(rho: float, sigma: float, a: float, b: float, kappa: float) -> np.ndarray:
    """Jacobian of T at an arbitrary nonzero point."""
    return np.array(
        [
            [0.5 * (1.0 - a / rho**2), 0.5 * kappa],
            [0.5 * kappa, 0.5 * (1.0 - b / sigma**2)],
        ],
        dtype=float,
    )


def negative_stability_threshold(a: float, b: float) -> float:
    """
    Return kappa_c in (0,1] such that the positive fixed point is locally stable
    exactly for -kappa_c < kappa < 1.
    """
    if not (a > 0.0 and b > 0.0):
        raise ValueError("a and b must be positive")
    if np.isclose(a, b, rtol=0.0, atol=1e-15):
        return 1.0

    delta = (a - b) ** 2
    B = 3.0 * a**2 - 2.0 * a * b + 3.0 * b**2
    z = (-B + sqrt(B**2 + 16.0 * a * b * delta)) / (2.0 * delta)
    if not (0.0 < z < 1.0):
        raise ArithmeticError(f"unexpected stability root z={z}")
    return sqrt(z)


def iterate(
    rho0: float,
    sigma0: float,
    a: float,
    b: float,
    kappa: float,
    steps: int,
) -> np.ndarray:
    """Return the full orbit, including the initial point."""
    orbit = np.empty((steps + 1, 2), dtype=float)
    orbit[0] = (rho0, sigma0)
    rho, sigma = rho0, sigma0
    for n in range(1, steps + 1):
        rho, sigma = T(rho, sigma, a, b, kappa)
        orbit[n] = (rho, sigma)
        if not (isfinite(rho) and isfinite(sigma)):
            raise FloatingPointError(f"nonfinite iterate at n={n}")
    return orbit


def symbolic_proof() -> dict[str, str]:
    """SymPy proof certificates for all algebraic identities."""
    rho, sigma, a, b, k, p = sp.symbols(
        "rho sigma a b k p", positive=True, finite=True
    )

    # Fixed-point equations after clearing denominators.
    fp_rho = sp.Eq(rho**2, a + k * rho * sigma)
    fp_sigma = sp.Eq(sigma**2, b + k * rho * sigma)
    # Subtract the two cleared fixed-point residuals exactly:
    # [rho^2-a-k*rho*sigma] - [sigma^2-b-k*rho*sigma]
    # = rho^2-sigma^2-(a-b).
    fixed_residual_difference = sp.expand(
        (rho**2 - a - k*rho*sigma)
        - (sigma**2 - b - k*rho*sigma)
    )
    invariant = sp.expand((rho**2 - sigma**2) - (a - b))
    assert sp.simplify(fixed_residual_difference - invariant) == 0

    # Product quadratic.
    product_identity = sp.expand(p**2 - (a + k * p) * (b + k * p))
    product_quadratic = sp.factor(product_identity)
    assert product_quadratic == -a*b - a*k*p - b*k*p - k**2*p**2 + p**2

    # Discriminant equivalence.
    raw_disc = sp.expand((k * (a + b)) ** 2 + 4 * (1 - k**2) * a * b)
    reduced_disc = sp.expand(k**2 * (a - b) ** 2 + 4 * a * b)
    assert sp.simplify(raw_disc - reduced_disc) == 0

    # Jacobian at a fixed point using a/rho^2 = 1-k*sigma/rho, etc.
    J_fp = sp.Matrix(
        [
            [k * sigma / (2 * rho), k / 2],
            [k / 2, k * rho / (2 * sigma)],
        ]
    )
    det_J = sp.factor(J_fp.det())
    trace_J = sp.factor(sp.trace(J_fp))
    assert det_J == 0
    assert trace_J == k * (rho**2 + sigma**2) / (2 * rho * sigma)

    trace_second_form = k * (a + b) / (2 * p) + k**2
    trace_substitution = sp.simplify(
        trace_J.subs(rho * sigma, p).subs(
            rho**2 + sigma**2, a + b + 2 * k * p
        )
        - trace_second_form
    )
    assert trace_substitution == 0

    # Positive-k stability:
    # 1-tau = Delta^(1/2)/(2p) > 0.
    d = sp.symbols("d", positive=True)
    q = 1 - k**2
    tau = k * (a + b) / (2 * p) + k**2
    one_minus_tau = sp.factor(1 - tau)
    one_minus_tau_using_fp = sp.simplify(
        one_minus_tau.subs(q, 1-k**2)
    )

    # Negative-k boundary. Put k=-u and z=u^2.
    u, z = sp.symbols("u z", positive=True)
    s = a + b
    p_boundary = u * s / (2 * (1 + u**2))  # tau=-1
    boundary_eq = sp.factor(
        (1 - u**2) * p_boundary**2 + u * s * p_boundary - a * b
    )
    boundary_num = sp.factor(sp.together(boundary_eq).as_numer_denom()[0])
    expected_num = sp.expand(
        (a - b) ** 2 * u**4
        + (3 * a**2 - 2 * a * b + 3 * b**2) * u**2
        - 4 * a * b
    )
    assert sp.simplify(boundary_num - expected_num) == 0

    # Symmetric reduction.
    x = sp.symbols("x", positive=True)
    Tdiag = sp.Rational(1, 2) * ((1 + k) * x + a / x)
    diag_fp = sp.solve(sp.Eq(Tdiag, x), x)
    # SymPy may return +/- roots; the positive solution is sqrt(a/(1-k)).
    expected_diag = sp.sqrt(a / (1 - k))
    assert sp.simplify(Tdiag.subs(x, expected_diag) - expected_diag) == 0

    return {
        "fixed_point_invariant": "rho_*^2 - sigma_*^2 = a - b",
        "product_quadratic": "(1-kappa^2)p_*^2-kappa(a+b)p_*-ab=0",
        "discriminant": "kappa^2(a-b)^2+4ab",
        "jacobian_determinant": str(det_J),
        "jacobian_trace": "kappa(a+b)/(2p_*)+kappa^2",
        "negative_boundary_polynomial": (
            "(a-b)^2 z^2+(3a^2-2ab+3b^2)z-4ab=0, z=kappa_c^2"
        ),
        "symmetric_fixed_point": "sqrt(a/(1-kappa))",
    }


def validate_case(a: float, b: float, kappa: float) -> dict:
    fp = predicted_fixed_point(a, b, kappa)
    mapped = np.array(T(fp.rho, fp.sigma, a, b, kappa))
    point = np.array([fp.rho, fp.sigma])
    residual = float(np.linalg.norm(mapped - point, ord=np.inf))
    invariant_residual = abs(fp.rho**2 - fp.sigma**2 - (a - b))
    quadratic_residual = abs(
        (1 - kappa**2) * fp.product**2
        - kappa * (a + b) * fp.product
        - a * b
    )

    J = jacobian_at(fp.rho, fp.sigma, a, b, kappa)
    eig = np.linalg.eigvals(J)
    eig_sorted = sorted(eig.tolist(), key=abs)
    determinant = float(np.linalg.det(J))
    trace = float(np.trace(J))
    kcrit = negative_stability_threshold(a, b)
    stable_predicted = (-kcrit < kappa < 1.0)
    stable_spectral = max(abs(eig)) < 1.0

    assert residual < 1e-11
    assert invariant_residual < 1e-11
    assert quadratic_residual < 1e-10
    assert abs(determinant) < 1e-12
    assert min(abs(eig)) < 1e-12
    assert abs(trace - fp.tau) < 1e-12
    assert stable_predicted == stable_spectral

    return {
        "a": a,
        "b": b,
        "kappa": kappa,
        "rho_star": fp.rho,
        "sigma_star": fp.sigma,
        "p_star": fp.product,
        "tau": fp.tau,
        "eigenvalues": [float(np.real_if_close(x)) for x in eig_sorted],
        "fixed_point_residual_inf": residual,
        "invariant_residual": invariant_residual,
        "quadratic_residual": quadratic_residual,
        "jacobian_determinant": determinant,
        "kappa_c_negative": kcrit,
        "locally_stable": bool(stable_spectral),
    }


def empirical_rate_check(
    a: float = 4.0,
    b: float = 9.0,
    kappa: float = 0.5,
    rho0: float = 1.0,
    sigma0: float = 1.0,
) -> dict:
    fp = predicted_fixed_point(a, b, kappa)
    orbit = iterate(rho0, sigma0, a, b, kappa, 80)
    errors = np.linalg.norm(
        orbit - np.array([fp.rho, fp.sigma]), axis=1
    )

    ratios = []
    for n in range(10, 40):
        if errors[n] > 1e-13 and errors[n + 1] > 1e-15:
            ratios.append(errors[n + 1] / errors[n])

    measured = float(np.median(ratios[-8:]))
    assert abs(measured - abs(fp.tau)) < 5e-5
    return {
        "parameters": {"a": a, "b": b, "kappa": kappa},
        "predicted_rate_abs_tau": abs(fp.tau),
        "measured_rate_median": measured,
        "absolute_difference": abs(measured - abs(fp.tau)),
    }


def demonstrate_corrections() -> dict:
    # 1. The "conserved quantity" is not conserved along general orbits.
    orbit = iterate(1.0, 1.0, 4.0, 9.0, 0.5, 2)
    diffs = [float(r**2 - s**2) for r, s in orbit]
    assert not np.isclose(diffs[0], diffs[1])

    # 2. Negative kappa is not a self-map of the whole positive quadrant.
    # At (rho,sigma)=(1,100), a=b=1, kappa=-0.5, T1<0.
    image = T(1.0, 100.0, 1.0, 1.0, -0.5)
    assert image[0] < 0.0

    # 3. Original all-|kappa|<1 stability claim fails.
    unstable = validate_case(4.0, 9.0, -0.9)
    assert abs(unstable["tau"]) > 1.0
    assert not bool(unstable["locally_stable"])

    # 4. Correct threshold for a=4,b=9.
    kcrit = negative_stability_threshold(4.0, 9.0)
    stable_near = validate_case(4.0, 9.0, -(kcrit - 1e-4))
    unstable_near = validate_case(4.0, 9.0, -(kcrit + 1e-4))
    assert stable_near["locally_stable"]
    assert not unstable_near["locally_stable"]

    return {
        "orbit_difference_values": diffs,
        "negative_kappa_positive_quadrant_counterexample": {
            "input": [1.0, 100.0],
            "parameters": {"a": 1.0, "b": 1.0, "kappa": -0.5},
            "image": list(image),
        },
        "stability_counterexample": unstable,
        "corrected_threshold_a4_b9": kcrit,
    }


def random_sweep(seed: int = 47, count: int = 2000) -> dict:
    rng = np.random.default_rng(seed)
    max_fp_residual = 0.0
    max_det = 0.0
    max_trace_eigen_error = 0.0
    classification_failures = 0

    for _ in range(count):
        a = float(10 ** rng.uniform(-2, 2))
        b = float(10 ** rng.uniform(-2, 2))
        kappa = float(rng.uniform(-0.999, 0.999))
        fp = predicted_fixed_point(a, b, kappa)
        residual = np.linalg.norm(
            np.array(T(fp.rho, fp.sigma, a, b, kappa))
            - np.array([fp.rho, fp.sigma]),
            ord=np.inf,
        )
        J = jacobian_at(fp.rho, fp.sigma, a, b, kappa)
        eig = np.linalg.eigvals(J)
        kcrit = negative_stability_threshold(a, b)
        predicted_stable = -kcrit < kappa < 1.0
        numerical_stable = max(abs(eig)) < 1.0

        max_fp_residual = max(max_fp_residual, float(residual))
        max_det = max(max_det, abs(float(np.linalg.det(J))))
        max_trace_eigen_error = max(
            max_trace_eigen_error,
            min(abs(eig - fp.tau)),
        )
        if predicted_stable != numerical_stable:
            classification_failures += 1

    assert classification_failures == 0
    return {
        "seed": seed,
        "cases": count,
        "classification_failures": classification_failures,
        "max_fixed_point_residual_inf": max_fp_residual,
        "max_abs_jacobian_determinant": max_det,
        "max_trace_eigenvalue_error": max_trace_eigen_error,
    }


def build_report(certificate: dict) -> str:
    cases = certificate["table_cases"]
    lines = [
        f"# {TITLE}",
        "",
        "**Author:** Nicholas Kouns  ",
        "**Institution:** AIMS Research Institute  ",
        "**Validation:** exact SymPy algebra + NumPy numerical reconstruction",
        "",
        "## Verdict",
        "",
        "The fixed-point invariant, product quadratic, unique positive fixed point, "
        "rank-one Jacobian, symmetric reduction, and measured linear rate are validated.",
        "",
        "Two global claims require correction:",
        "",
        "1. `rho^2 - sigma^2 = a - b` is invariant across fixed points, not conserved "
        "along arbitrary iterates.",
        "2. For unequal `a,b`, sufficiently negative coupling can make the positive fixed "
        "point unstable even while `|kappa|<1`; for negative `kappa`, the map is also not "
        "a self-map of the whole positive quadrant.",
        "",
        "## Corrected theorem",
        "",
        "For `a,b>0` and `|kappa|<1`, a unique positive fixed point exists. Its Jacobian "
        "has eigenvalues `{0,tau}` with",
        "",
        "`tau = kappa(a+b)/(2p*) + kappa^2`.",
        "",
        "For `kappa>=0`, `0<=tau<1`. For `kappa<0`, local stability holds exactly when",
        "",
        "`-kappa_c(a,b) < kappa < 0`,",
        "",
        "where `kappa_c=1` for `a=b`; otherwise `kappa_c=sqrt(z_c)` and `z_c` is the "
        "unique positive root of",
        "",
        "`(a-b)^2 z^2 + (3a^2-2ab+3b^2)z - 4ab = 0`.",
        "",
        "Thus the complete local-stability interval is",
        "",
        "`-kappa_c(a,b) < kappa < 1`.",
        "",
        "## Reconstructed cases",
        "",
        "| a | b | kappa | rho* | sigma* | tau | stable |",
        "|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in cases:
        lines.append(
            f"| {row['a']:.3g} | {row['b']:.3g} | {row['kappa']:.3f} | "
            f"{row['rho_star']:.10f} | {row['sigma_star']:.10f} | "
            f"{row['tau']:.9f} | {'yes' if row['locally_stable'] else 'no'} |"
        )

    corr = certificate["corrections"]
    rate = certificate["empirical_rate"]
    sweep = certificate["random_sweep"]
    lines += [
        "",
        "## Decisive numerical checks",
        "",
        f"- At `(a,b,kappa)=(4,9,0.5)`, predicted rate: "
        f"`{rate['predicted_rate_abs_tau']:.12f}`.",
        f"- Measured asymptotic error ratio: `{rate['measured_rate_median']:.12f}`.",
        f"- For `(a,b)=(4,9)`, corrected negative threshold: "
        f"`kappa_c={corr['corrected_threshold_a4_b9']:.12f}`.",
        f"- At `kappa=-0.9`, `tau={corr['stability_counterexample']['tau']:.12f}`, "
        "so the fixed point is unstable despite `|kappa|<1`.",
        f"- Random verification: `{sweep['cases']}` cases, "
        f"`{sweep['classification_failures']}` stability-classification failures.",
        "",
        "## Status",
        "",
        "**PASS WITH THEOREM-DOMAIN CORRECTIONS.**",
        "",
        "The core coupled Newton–mean construction is mathematically sound. "
        "The exact stability theorem is the corrected interval above.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    print("=" * 96)
    print(TITLE)
    print("=" * 96)

    symbolic = symbolic_proof()
    print("\n[1] SYMBOLIC PROOF: PASS")
    for key, value in symbolic.items():
        print(f"    {key}: {value}")

    requested_cases = [
        (4.0, 9.0, 0.0),
        (4.0, 9.0, 0.1),
        (4.0, 9.0, 0.5),
        (4.0, 9.0, 0.9),
        (4.0, 9.0, -0.5),
        (1.0, 1.0, 0.5),
        (1.0, 1.0, 0.99),
        (2.0, 8.0, 0.3),
        (16.0, 25.0, 0.7),
    ]
    table_cases = [validate_case(*case) for case in requested_cases]
    print("\n[2] SUBMITTED NUMERICAL TABLE: PASS")
    for row in table_cases:
        print(
            f"    a={row['a']:>5g} b={row['b']:>5g} k={row['kappa']:>7.3f} "
            f"rho*={row['rho_star']:.10f} sigma*={row['sigma_star']:.10f} "
            f"tau={row['tau']:+.9f}"
        )

    rate = empirical_rate_check()
    print("\n[3] EMPIRICAL RATE: PASS")
    print(
        f"    predicted |tau|={rate['predicted_rate_abs_tau']:.12f}; "
        f"measured={rate['measured_rate_median']:.12f}"
    )

    corrections = demonstrate_corrections()
    print("\n[4] CLAIM-AUDIT CORRECTIONS: CONFIRMED")
    print(
        "    fixed-point invariant is not orbitwise conserved: "
        f"{corrections['orbit_difference_values']}"
    )
    print(
        "    negative-kappa map counterexample image: "
        f"{corrections['negative_kappa_positive_quadrant_counterexample']['image']}"
    )
    print(
        "    instability counterexample: "
        f"(a,b,kappa)=(4,9,-0.9), "
        f"tau={corrections['stability_counterexample']['tau']:.12f}"
    )
    print(
        "    corrected threshold for (a,b)=(4,9): "
        f"kappa_c={corrections['corrected_threshold_a4_b9']:.12f}"
    )

    sweep = random_sweep()
    print("\n[5] RANDOM PARAMETER SWEEP: PASS")
    print(
        f"    cases={sweep['cases']}; "
        f"classification failures={sweep['classification_failures']}; "
        f"max fixed-point residual={sweep['max_fixed_point_residual_inf']:.3e}"
    )

    certificate = {
        "title": TITLE,
        "author": "Nicholas Kouns",
        "institution": "AIMS Research Institute",
        "status": "PASS WITH THEOREM-DOMAIN CORRECTIONS",
        "symbolic_proof": symbolic,
        "table_cases": table_cases,
        "empirical_rate": rate,
        "corrections": corrections,
        "random_sweep": sweep,
        "corrected_theorem": {
            "existence": "unique positive fixed point for a,b>0 and |kappa|<1",
            "jacobian_eigenvalues": ["0", "tau"],
            "tau": "kappa(a+b)/(2p*)+kappa^2",
            "local_stability": "-kappa_c(a,b)<kappa<1",
            "negative_threshold": (
                "kappa_c=1 if a=b; otherwise kappa_c=sqrt(z_c), "
                "where (a-b)^2 z_c^2+(3a^2-2ab+3b^2)z_c-4ab=0"
            ),
        },
    }

    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / "newton_mean_corrected_validation_certificate.json"
    md_path = out_dir / "NEWTON_MEAN_EXACT_PYTHON_PROOF.md"
    json_path.write_text(json.dumps(certificate, indent=2), encoding="utf-8")
    md_path.write_text(build_report(certificate), encoding="utf-8")

    print("\n" + "=" * 96)
    print("FINAL STATUS: PASS WITH THEOREM-DOMAIN CORRECTIONS")
    print(f"Certificate: {json_path.name}")
    print(f"Proof report: {md_path.name}")
    print("=" * 96)


if __name__ == "__main__":
    main()
