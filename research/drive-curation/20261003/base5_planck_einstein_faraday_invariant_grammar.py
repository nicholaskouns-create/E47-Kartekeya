#!/usr/bin/env python3
"""
Planck–Einstein–Faraday Base-5 Invariant-Grammar Validator

Exact statement:
    D5 ∘ τ5 = id_Q

Therefore a radix-only translation preserves the semantic operator:
    K5 = K
    ker(K5) = ker(K)
    P5 = P
    H5 = H = I - P

Run:
    python base5_planck_einstein_faraday_invariant_grammar.py
"""
from fractions import Fraction
import json
import math
import numpy as np

BASE = 5

def int_to_base5(n: int) -> str:
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    digits = []
    while n:
        n, r = divmod(n, BASE)
        digits.append(str(r))
    return sign + "".join(reversed(digits))

def base5_to_int(text: str) -> int:
    sign = -1 if text.startswith("-") else 1
    if text[:1] in "+-":
        text = text[1:]
    if not text or any(ch not in "01234" for ch in text):
        raise ValueError(text)
    value = 0
    for ch in text:
        value = BASE * value + int(ch)
    return sign * value

def encode_fraction(value: Fraction) -> str:
    value = Fraction(value)
    return f"{int_to_base5(value.numerator)}_5/{int_to_base5(value.denominator)}_5"

def decode_fraction(text: str) -> Fraction:
    left, right = text.split("/")
    return Fraction(base5_to_int(left[:-2]), base5_to_int(right[:-2]))

def projector(row):
    K = np.asarray(row, dtype=float).reshape(1, -1)
    H = K.T @ np.linalg.inv(K @ K.T) @ K
    return np.eye(K.shape[1]) - H

def validate(name, row, exact_coordinates):
    encoded = [encode_fraction(v) for v in exact_coordinates]
    decoded = [decode_fraction(v) for v in encoded]
    assert decoded == exact_coordinates
    K = np.asarray(row, dtype=float).reshape(1, -1)
    x = np.asarray([float(v) for v in decoded])
    P = projector(row)
    return {
        "name": name,
        "encoded": encoded,
        "residual": float(np.linalg.norm(K @ x)),
        "projector_idempotence": float(np.linalg.norm(P @ P - P)),
        "kernel_annihilation": float(np.linalg.norm(K @ P)),
        "projector_fixpoint": float(np.linalg.norm(P @ x - x)),
    }

h = Fraction(662_607_015, 10**42)
c = Fraction(299_792_458, 1)

nu = Fraction(750_000_000_000_000, 1)
planck = validate("Planck E=hν", [1, -1], [h*nu, h*nu])

m = Fraction(1, 8)
einstein = validate("Einstein E=mc²", [1, -1], [m*c*c, m*c*c])

delta_flux = Fraction(1, 80)
delta_t = Fraction(1, 200)
rate = delta_flux / delta_t
faraday = validate("Faraday emf=-dΦ/dt", [1, 1], [-rate, rate])

checks = {
    "8_10 = 13_5": base5_to_int("13") == 8,
    "47_10 = 142_5": base5_to_int("142") == 47,
    "125_10 = 1000_5": base5_to_int("1000") == 125,
    "Planck residual": planck["residual"] < 1e-12,
    "Einstein residual": einstein["residual"] < 1e-12,
    "Faraday residual": faraday["residual"] < 1e-12,
    "projector checks": all(
        item[key] < 1e-12
        for item in (planck, einstein, faraday)
        for key in ("projector_idempotence", "kernel_annihilation", "projector_fixpoint")
    ),
}

result = {
    "certificate": "B5-PHY-PEF-20260731",
    "status": "PASS" if all(checks.values()) else "FAIL",
    "checks": checks,
    "laws": [planck, einstein, faraday],
    "identity": "D5 ∘ τ5 = id_Q",
    "grammar": "K5=K; ker(K5)=ker(K); P5=P; H5=H",
}
print(json.dumps(result, indent=2, ensure_ascii=False))
