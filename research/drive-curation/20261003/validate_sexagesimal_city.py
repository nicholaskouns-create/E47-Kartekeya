"""Exact sexagesimal and E47 bridge validation for the City research deck.

This is a small E0/E1 witness: it validates numeral encodings and exact
cross-domain identities only. It does not claim a historical derivation of
the E47 construction from Babylonian mathematics.
"""

from __future__ import annotations

from fractions import Fraction
from math import isqrt, sqrt


def parse_sexagesimal(text: str) -> Fraction:
    """Parse integer digits separated by commas and fractional digits after ``;``."""
    if ";" in text:
        whole_text, fractional_text = text.split(";", 1)
        whole_digits = [int(d) for d in whole_text.split(",")]
        fractional_digits = [int(d) for d in fractional_text.split(",") if d]
    else:
        whole_digits = [int(d) for d in text.split(",")]
        fractional_digits = []
    if not whole_digits:
        raise ValueError("missing whole-number digits")
    if any(not 0 <= d < 60 for d in whole_digits + fractional_digits):
        raise ValueError("sexagesimal digits must lie in 0..59")
    value = Fraction(0, 1)
    for digit in whole_digits:
        value = 60 * value + digit
    for place, digit in enumerate(fractional_digits, start=1):
        value += Fraction(digit, 60**place)
    return value


def format_sexagesimal(value: Fraction, places: int = 8) -> str:
    """Format a nonnegative rational in finite base-60 notation."""
    if value < 0:
        raise ValueError("this witness formats nonnegative values only")
    whole = value.numerator // value.denominator
    remainder = value - whole
    whole_digits: list[int] = []
    if whole == 0:
        whole_digits = [0]
    else:
        n = whole
        while n:
            n, digit = divmod(n, 60)
            whole_digits.append(digit)
        whole_digits.reverse()
    digits: list[int] = []
    if remainder:
        for _ in range(places):
            remainder *= 60
            digit = remainder.numerator // remainder.denominator
            digits.append(int(digit))
            remainder -= digit
            if remainder == 0:
                break
    if remainder:
        raise AssertionError(f"non-terminating expansion within {places} places: {value}")
    whole_text = ",".join(
        str(d) if i == 0 else f"{d:02d}" for i, d in enumerate(whole_digits)
    )
    return whole_text if not digits else whole_text + ";" + ",".join(f"{d:02d}" for d in digits)


def assert_equal(label: str, actual: Fraction, expected: Fraction) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: {actual} != {expected}")


def main() -> None:
    # Historical / exhibit-facing arithmetic examples.
    ybc_7289 = parse_sexagesimal("1;24,51,10")
    sqrt2_error = abs(float(ybc_7289) - sqrt(2.0))
    assert sqrt2_error < 2e-6

    reciprocal_eighth = parse_sexagesimal("0;07,30")
    assert_equal("reciprocal table 1/8", reciprocal_eighth, Fraction(1, 8))
    assert_equal("125 times 1/8", 125 * reciprocal_eighth, Fraction(125, 8))

    ybc_7290_area = parse_sexagesimal("5;03,20")
    assert_equal("YBC 7290 area value", ybc_7290_area, Fraction(91, 18))

    # Exact City / E47 radix identity recorded by Citizen C-32.
    omega = Fraction(47, 125)
    omega_60 = parse_sexagesimal("0;22,33,36")
    assert_equal("E47 coherence in base 60", omega_60, omega)
    assert format_sexagesimal(omega) == "0;22,33,36"

    # Spectral values and the stability bound from Citizen C-34.
    assert format_sexagesimal(Fraction(125)) == "2,05"
    assert format_sexagesimal(Fraction(47)) == "47"
    assert format_sexagesimal(Fraction(11664)) == "3,14,24"
    assert format_sexagesimal(Fraction(186624)) == "51,50,24"

    # Place-value tests from the City radix registry.
    assert_equal("125 decimal", parse_sexagesimal("2,05"), Fraction(125))
    assert_equal("11664 decimal", parse_sexagesimal("3,14,24"), Fraction(11664))
    assert_equal("186624 decimal", parse_sexagesimal("51,50,24"), Fraction(186624))
    assert_equal("Euler step bound", Fraction(2, 186624), Fraction(1, 93312))

    # Finite-termination criterion: q divides 60^m.
    assert 60**3 % 125 == 0
    assert 60**2 % 8 == 0
    assert 60**2 % 18 == 0
    assert 60**8 % 7 != 0

    # Small sanity checks on the exact encoder / decoder pair.
    for value in [Fraction(47, 125), Fraction(1, 8), Fraction(91, 18), Fraction(125)]:
        encoded = format_sexagesimal(value)
        assert_equal(f"round trip {value}", parse_sexagesimal(encoded), value)

    print("SEXAGESIMAL CITY VALIDATION: PASS")
    print(f"YBC 7289 1;24,51,10 error vs sqrt(2): {sqrt2_error:.12g}")
    print(f"E47 omega: {omega} = {format_sexagesimal(omega)}_60")
    print("125 = 2,05_60; 11664 = 3,14,24_60; 186624 = 51,50,24_60")
    print("termination gates: PASS (125, 8, 18 divide powers of 60; 7 does not)")
    print("scope: exact radix identities and finite E47 constants; historical lineage remains structural analogy")


if __name__ == "__main__":
    main()
