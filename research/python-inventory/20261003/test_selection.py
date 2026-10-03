"""Tests for the derived spin-sector selection."""

from __future__ import annotations
from fractions import Fraction
import pytest

from e47.selection import (
    derive_selection,
    kernel_dimension_closed_form,
    s3_multiplicity_space_content,
)

def test_canonical_selection_is_two_and_five() -> None:
    """The canonical carrier forces sectors {2, 5}, hence roots 6 and 30."""
    derivation = derive_selection(Fraction(2), 3)
    assert derivation.selected == (Fraction(2), Fraction(5))
    assert derivation.kernel_roots == (Fraction(6), Fraction(30))
    assert derivation.kernel_dimension == 47

def test_canonical_multiplicities() -> None:
    """Multiplicities of (spin 2)^3 are 1, 3, 5, 4, 3, 2, 1."""
    derivation = derive_selection(Fraction(2), 3)
    counts = [derivation.multiplicities[Fraction(j)] for j in range(7)]
    assert counts == [1, 3, 5, 4, 3, 2, 1]
    assert sum(count * (2 * j + 1) for j, count in enumerate(counts)) == 125

def test_s3_content_of_canonical_carrier() -> None:
    """Spin 5 carries exactly the standard irrep; spin 2 is trivial + 2 standard."""
    content = s3_multiplicity_space_content(Fraction(2), 3)
    assert content[Fraction(5)] == {"trivial": 0, "sign": 0, "standard": 1}
    assert content[Fraction(2)] == {"trivial": 1, "sign": 0, "standard": 2}
    assert content[Fraction(1)]["sign"] == 1
    assert content[Fraction(3)]["sign"] == 1

@pytest.mark.parametrize("spin", range(1, 9))
def test_selection_generalises(spin: int) -> None:
    """Conditions (A) and (B) yield (s, 3s-1) for every integer carrier tested."""
    derivation = derive_selection(Fraction(spin), 3)
    assert derivation.selected == (Fraction(spin), Fraction(3 * spin - 1))

@pytest.mark.parametrize("spin", range(1, 9))
def test_kernel_dimension_matches_closed_form(spin: int) -> None:
    """Explicit dimension agrees with 4s^2 + 16s - 1."""
    derivation = derive_selection(Fraction(spin), 3)
    assert derivation.kernel_dimension == kernel_dimension_closed_form(Fraction(spin))

def test_conditions_are_independently_unique() -> None:
    """Each condition must select exactly one sector, not merely intersect to one."""
    derivation = derive_selection(Fraction(2), 3)
    content = derivation.s3_content
    peak = max(derivation.multiplicities.values())
    maximal = [j for j, c in derivation.multiplicities.items() if c == peak]
    standard = [
        j
        for j, entry in content.items()
        if entry == {"trivial": 0, "sign": 0, "standard": 1}
    ]
    assert maximal == [Fraction(2)]
    assert standard == [Fraction(5)]

def test_unsupported_copies_are_rejected() -> None:
    """The derivation is only defined for three copies and says so."""
    with pytest.raises(NotImplementedError):
        s3_multiplicity_space_content(Fraction(2), 4)
