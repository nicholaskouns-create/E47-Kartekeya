#!/usr/bin/env python3
"""First-Principles N-VQE / E47 Hilbert-Lifted Multiradix Validator.

Evidence boundary
-----------------
E0: Heron fixed-point identity, SU(2) Casimir spectrum, E47 kernel,
    projector, spectral gap/norm, and contraction constants.
E1: floating-point 125x125 reconstruction and 128-state Hilbert simulation.
Not established: consciousness equivalence, phenomenology = computation,
                 or any derivation of Omega_c = 47/125 from phi^(-5).

Requires: Python >= 3.11, NumPy >= 1.26
"""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
EXPECTED_C = np.array([0, 2, 6, 12, 20, 30, 42], dtype=int)
EXPECTED_MULT = np.array([1, 9, 25, 28, 27, 22, 13], dtype=int)
EXPECTED_K2_POS = np.array([11664, 12544, 19600, 32400, 186624], dtype=int)
EPSILON_STAR = Fraction(1, 99144)
RHO_STAR = Fraction(15, 17)
TOL = 1e-8


def int_to_base(n: int, base: int) -> str:
    if not 2 <= base <= 64:
        raise ValueError("base must lie in [2, 64]")
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    out: list[str] = []
    while n:
        n, r = divmod(n, base)
        out.append(DIGITS[r])
    return sign + "".join(reversed(out))


def build_spin2_generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    j = 2
    m = np.arange(j, -j - 1, -1, dtype=float)
    d = 2 * j + 1
    jz = np.diag(m).astype(complex)
    jp = np.zeros((d, d), dtype=complex)
    for col in range(1, d):
        mm = m[col]
        jp[col - 1, col] = np.sqrt(j * (j + 1) - mm * (mm + 1))
    jm = jp.conj().T
    return (jp + jm) / 2.0, (jp - jm) / (2.0j), jz


def kron3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.kron(np.kron(a, b), c)


def build_e47_operators() -> dict[str, np.ndarray]:
    jx, jy, jz = build_spin2_generators()
    i5 = np.eye(5, dtype=complex)
    jx_t = kron3(jx, i5, i5) + kron3(i5, jx, i5) + kron3(i5, i5, jx)
    jy_t = kron3(jy, i5, i5) + kron3(i5, jy, i5) + kron3(i5, i5, jy)
    jz_t = kron3(jz, i5, i5) + kron3(i5, jz, i5) + kron3(i5, i5, jz)
    c = jx_t @ jx_t + jy_t @ jy_t + jz_t @ jz_t
    i125 = np.eye(125, dtype=complex)
    k = (c - 6 * i125) @ (c - 30 * i125)
    h = k @ k
    return {"C": c, "K": k, "H": h, "I": i125}


def heron_invariants() -> tuple[dict[str, float], bool, bool, bool]:
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    a = phi ** -5
    x_star = np.sqrt(a)

    def t(x: float) -> float:
        return 0.5 * (x + a / x)

    def tp(x: float) -> float:
        return 0.5 * (1.0 - a / (x * x))

    x = 1.0
    max_identity_resid = 0.0
    for _ in range(7):
        x_next = t(x)
        e = x - x_star
        e_next = x_next - x_star
        predicted = e * e / (2.0 * x)
        max_identity_resid = max(max_identity_resid, abs(e_next - predicted))
        x = x_next

    vals = {
        "phi": float(phi),
        "a_phi_minus_5": float(a),
        "fixed_point_phi_minus_5_over_2": float(x_star),
        "Tprime_at_fixed_point": float(tp(x_star)),
        "max_quadratic_error_identity_residual": float(max_identity_resid),
    }
    return (
        vals,
        abs(x_star * x_star - a) < 1e-14,
        abs(tp(x_star)) < 1e-14,
        max_identity_resid < 1e-14,
    )


def multiradix() -> dict[str, object]:
    values = {
        "dim_V": 125,
        "dim_E47": 47,
        "complement": 78,
        "selector_root_1": 6,
        "selector_root_2": 30,
        "gap_K2": 11664,
        "norm_K2": 186624,
        "epsilon_denominator": 99144,
        "qubit_lift_dimension": 128,
    }
    out: dict[str, object] = {
        "alphabet_base64": DIGITS,
        "values": {},
        "core_identity": {},
    }
    for base in (5, 10, 12, 64):
        out["core_identity"][str(base)] = (
            f"{int_to_base(47, base)}_{base} + "
            f"{int_to_base(78, base)}_{base} = "
            f"{int_to_base(125, base)}_{base}"
        )
    for name, value in values.items():
        out["values"][name] = {
            str(base): int_to_base(value, base) for base in (5, 10, 12, 64)
        }
    out["omega_c"] = {
        "exact": "47/125",
        "base5_exact_fractional": "0.142_5",
        "base10": 47 / 125,
        "base12_fraction": f"{int_to_base(47,12)}/{int_to_base(125,12)}",
        "base64_fraction": f"{int_to_base(47,64)}/{int_to_base(125,64)}",
    }
    return out


def validate(seed: int = 47, imaginary_time: float = 1e-3) -> dict[str, object]:
    heron, heron_fixed, heron_derivative, heron_error = heron_invariants()
    ops = build_e47_operators()
    c, k, h, i125 = ops["C"], ops["K"], ops["H"], ops["I"]

    c_eval = np.linalg.eigvalsh(c)
    c_round = np.rint(np.real(c_eval)).astype(int)
    unique_c, mult_c = np.unique(c_round, return_counts=True)

    h_eval, h_vec = np.linalg.eigh(h)
    h_eval = np.real_if_close(h_eval).real
    zero = np.isclose(h_eval, 0.0, atol=TOL)
    positive = np.sort(np.unique(np.rint(h_eval[~zero]).astype(int)))

    v0 = h_vec[:, zero]
    p47 = v0 @ v0.conj().T
    gap = int(np.rint(np.min(h_eval[~zero])))
    norm_k2 = int(np.rint(np.max(h_eval)))
    gamma = i125 - float(EPSILON_STAR) * h
    gamma_eval = np.linalg.eigvalsh(gamma)
    transient = np.abs(gamma_eval[np.abs(gamma_eval - 1.0) > TOL])
    rho_num = float(np.max(transient))

    p_idem = float(np.linalg.norm(p47 @ p47 - p47, ord="fro"))
    p_herm = float(np.linalg.norm(p47.conj().T - p47, ord="fro"))
    kp = float(np.linalg.norm(k @ p47, ord="fro"))

    h128 = np.zeros((128, 128), dtype=complex)
    h128[:125, :125] = h
    h128[125:, 125:] = norm_k2 * np.eye(3)
    e128, v128 = np.linalg.eigh(h128)
    gmask = np.isclose(e128, 0.0, atol=TOL)
    vg = v128[:, gmask]
    pg = vg @ vg.conj().T

    rng = np.random.default_rng(seed)
    psi0 = rng.normal(size=128) + 1j * rng.normal(size=128)
    psi0 /= np.linalg.norm(psi0)
    coeff = v128.conj().T @ psi0
    psi_t = v128 @ (np.exp(-imaginary_time * e128) * coeff)
    psi_t /= np.linalg.norm(psi_t)

    def energy(psi: np.ndarray) -> float:
        return float(np.real(np.vdot(psi, h128 @ psi)))

    def ground_weight(psi: np.ndarray) -> float:
        return float(np.real(np.vdot(psi, pg @ psi)))

    e0, et = energy(psi0), energy(psi_t)
    w0, wt = ground_weight(psi0), ground_weight(psi_t)

    checks = {
        "Heron fixed point solves x^2=a": heron_fixed,
        "Heron derivative at fixed point is zero": heron_derivative,
        "Heron exact quadratic error identity": heron_error,
        "dim(V2^tensor3)=125": c.shape == (125, 125),
        "Casimir spectrum exact": np.array_equal(unique_c, EXPECTED_C),
        "Casimir multiplicities exact": np.array_equal(mult_c, EXPECTED_MULT),
        "K^2 positive semidefinite": float(np.min(h_eval)) > -TOL,
        "ground energy = 0": abs(float(np.min(h_eval))) < TOL,
        "ground multiplicity = 47": int(np.sum(zero)) == 47,
        "positive K^2 spectrum": np.array_equal(positive, EXPECTED_K2_POS),
        "spectral gap = 11664": gap == 11664,
        "spectral norm = 186624": norm_k2 == 186624,
        "P47^2=P47": p_idem < 1e-10,
        "P47^dagger=P47": p_herm < 1e-10,
        "K P47 = 0": kp < 1e-8,
        "rho*=15/17": abs(rho_num - float(RHO_STAR)) < 1e-10,
        "7-qubit lift keeps ground multiplicity 47": int(np.sum(gmask)) == 47,
        "7-qubit lift keeps gap 11664": int(np.rint(np.min(e128[~gmask]))) == 11664,
        "imaginary-time energy decreases": et < e0,
        "imaginary-time ground weight increases": wt > w0,
    }

    result = {
        "schema": "E47-NVQE-HILBERT-MULTIRADIX/1.0",
        "title": "First-Principles N-VQE / E47 Hilbert-Lifted Multiradix Validation",
        "seed": seed,
        "imaginary_time": imaginary_time,
        "heron": heron,
        "e47": {
            "dim_V": 125,
            "dim_E47": int(np.sum(zero)),
            "omega_c": 47 / 125,
            "casimir_spectrum": unique_c.tolist(),
            "casimir_multiplicities": mult_c.tolist(),
            "positive_K2_spectrum": positive.tolist(),
            "gap_K2": gap,
            "norm_K2": norm_k2,
            "epsilon_star": "1/99144",
            "rho_star": "15/17",
            "projector_idempotence_fro": p_idem,
            "projector_hermiticity_fro": p_herm,
            "K_P47_fro": kp,
        },
        "qubit_lift": {
            "dimension": 128,
            "padding_dimension": 3,
            "padding_penalty": norm_k2,
            "ground_multiplicity": int(np.sum(gmask)),
            "gap": int(np.rint(np.min(e128[~gmask]))),
            "initial_energy": e0,
            "final_energy": et,
            "initial_ground_weight": w0,
            "final_ground_weight": wt,
        },
        "multiradix": multiradix(),
        "checks": {name: bool(ok) for name, ok in checks.items()},
        "certificate": {
            "passed": int(sum(checks.values())),
            "total": len(checks),
            "status": "PASS" if all(checks.values()) else "FAIL",
        },
        "evidence_boundary": {
            "E0": "finite-dimensional algebra and exact fixed-point/spectral identities",
            "E1": "floating-point matrix reconstruction and 128-state Hilbert simulation",
            "not_established": [
                "consciousness equivalence",
                "phenomenology equals computation",
                "phi-derived Omega_c",
            ],
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=47)
    parser.add_argument("--imaginary-time", type=float, default=1e-3)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args()

    result = validate(seed=args.seed, imaginary_time=args.imaginary_time)
    for name, ok in result["checks"].items():
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
    cert = result["certificate"]
    print(f"\nCERTIFICATE: {cert['passed']}/{cert['total']} {cert['status']}")
    if args.json is not None:
        args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"JSON: {args.json}")
    return 0 if cert["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
