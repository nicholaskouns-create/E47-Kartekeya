"""Derive the selected total-spin sectors from representation structure.

The canonical E47 construction uses ``K = (C - 6I)(C - 30I)`` on
``V_2 tensor V_2 tensor V_2``, i.e. total-spin sectors ``{2, 5}``. Historically
that pair was supplied as input. This module derives it instead, from two
parameter-free conditions on the symmetric-group action carried by the
multiplicity spaces.

For ``V_s^{\\otimes 3}`` the group ``S_3`` commutes with the diagonal SU(2)
action, so each multiplicity space ``M_j = Hom_{SU(2)}(V_j, V_s^{\\otimes 3})``
is an ``S_3``-representation. Decomposing by characters gives:

    (A) exactly one total spin attains the maximal multiplicity;
    (B) exactly one total spin has ``M_j`` isomorphic to the standard
        two-dimensional irrep of ``S_3``.

Condition (A) yields ``j = s``; condition (B) yields ``j = 3s - 1``. For
``s = 2`` this is ``{2, 5}``, recovering ``K = (C - 6I)(C - 30I)`` and
``dim ker K = 47``. In general the kernel dimension is ``4s^2 + 16s - 1``.

Neither condition contains a free constant, so the selection is determined by
the carrier rather than chosen. The choice of carrier itself (``s = 2``,
``copies = 3``) remains an input; see ``docs/validation_scope.md``.
"""

from __future__ import annotations

from fractions import Fraction

from .spectral_compilation import clebsch_gordan_multiplicities, spin_dimension

__all__ = [
    "S3_IRREPS",
    "SelectionDerivation",
    "derive_selection",
    "kernel_dimension_closed_form",
    "s3_multiplicity_space_content",
]

# Character table of S_3 on the classes (identity, transposition, 3-cycle).
S3_IRREPS: dict[str, tuple[int, int, int]] = {
    "trivial": (1, 1, 1),
    "sign": (1, -1, 1),
    "standard": (2, 0, -1),
}

_CLASS_SIZES = (1, 3, 2)


class SelectionDerivation:
    """Result of deriving the selected total-spin sectors."""

    __slots__ = ("carrier_spin", "copies", "multiplicities", "s3_content", "selected")

    def __init__(
        self,
        carrier_spin: Fraction,
        copies: int,
        multiplicities: dict[Fraction, int],
        s3_content: dict[Fraction, dict[str, int]],
        selected: tuple[Fraction, ...],
    ) -> None:
        self.carrier_spin = carrier_spin
        self.copies = copies
        self.multiplicities = multiplicities
        self.s3_content = s3_content
        self.selected = selected

    @property
    def kernel_roots(self) -> tuple[Fraction, ...]:
        """Casimir eigenvalues ``j(j+1)`` of the selected sectors."""

        return tuple(j * (j + 1) for j in self.selected)

    @property
    def kernel_dimension(self) -> int:
        """Total dimension of the selected isotypic components."""

        return sum(
            self.multiplicities[j] * spin_dimension(j) for j in self.selected
        )

    def to_json_dict(self) -> dict[str, object]:
        """Serialise the derivation for inclusion in a certificate."""

        return {
            "carrier_spin": str(self.carrier_spin),
            "copies": self.copies,
            "selected_spins": [str(j) for j in self.selected],
            "kernel_roots": [str(root) for root in self.kernel_roots],
            "kernel_dimension": self.kernel_dimension,
            "derivation": {
                "maximal_multiplicity_spin": str(self.selected[0]),
                "standard_irrep_spin": str(self.selected[-1]),
            },
            "s3_content": {
                str(j): dict(content) for j, content in self.s3_content.items()
            },
        }


def _character_of_permutation_action(
    spin: Fraction,
    cycle_type: tuple[int, ...],
) -> dict[int, int]:
    """Character of ``sigma`` composed with the diagonal action, as a Laurent poly.

    The trace factorises over the cycles of ``sigma``: a cycle of length ``k``
    contributes ``tr(g^k)``, which is the spin character evaluated at ``u^k``.
    Exponents index powers of ``u``; ``chi_s = sum_{m=-s}^{s} u^m``.
    """

    dimension = spin_dimension(spin)
    weights = [m - (dimension - 1) // 2 for m in range(dimension)]
    if dimension % 2 == 0:
        raise ValueError("S_3 character derivation requires integer carrier spin")

    result: dict[int, int] = {0: 1}
    for length in cycle_type:
        factor = {weight * length: 1 for weight in weights}
        merged: dict[int, int] = {}
        for exponent_a, coeff_a in result.items():
            for exponent_b, coeff_b in factor.items():
                key = exponent_a + exponent_b
                merged[key] = merged.get(key, 0) + coeff_a * coeff_b
        result = {k: v for k, v in merged.items() if v}
    return result


def _decompose_into_su2_characters(
    polynomial: dict[int, Fraction],
    max_spin: int,
) -> dict[Fraction, int]:
    """Peel a Laurent polynomial into SU(2) characters, highest weight first."""

    remaining = dict(polynomial)
    multiplicities: dict[Fraction, int] = {}
    for weight in range(max_spin, -1, -1):
        coefficient = remaining.get(weight, Fraction(0))
        if not coefficient:
            continue
        if coefficient.denominator != 1:
            raise ValueError("non-integral multiplicity in character decomposition")
        count = int(coefficient)
        multiplicities[Fraction(weight)] = count
        for exponent in range(-weight, weight + 1):
            remaining[exponent] = remaining.get(exponent, Fraction(0)) - count
        remaining = {k: v for k, v in remaining.items() if v}
    if remaining:
        raise ValueError("character decomposition left a non-zero remainder")
    return multiplicities


def s3_multiplicity_space_content(
    spin: Fraction,
    copies: int = 3,
) -> dict[Fraction, dict[str, int]]:
    """Decompose every multiplicity space of ``V_spin^{copies}`` under ``S_3``.

    Returns a mapping from total spin to the multiplicity of each ``S_3`` irrep
    in that multiplicity space. Only ``copies == 3`` is supported.
    """

    if copies != 3:
        raise NotImplementedError("S_3 derivation is defined for copies == 3")

    characters = {
        (1, 1, 1): _character_of_permutation_action(spin, (1, 1, 1)),
        (2, 1): _character_of_permutation_action(spin, (2, 1)),
        (3,): _character_of_permutation_action(spin, (3,)),
    }
    ordered = [characters[(1, 1, 1)], characters[(2, 1)], characters[(3,)]]
    max_spin = int(3 * spin)

    content: dict[Fraction, dict[str, int]] = {}
    for name, irrep_character in S3_IRREPS.items():
        projected: dict[int, Fraction] = {}
        for value, size, character in zip(irrep_character, _CLASS_SIZES, ordered):
            if value == 0:
                continue
            for exponent, coefficient in character.items():
                projected[exponent] = projected.get(exponent, Fraction(0)) + Fraction(
                    value * size * coefficient, 6
                )
        projected = {k: v for k, v in projected.items() if v}
        for total_spin, count in _decompose_into_su2_characters(
            projected, max_spin
        ).items():
            content.setdefault(total_spin, {})[name] = count

    for total_spin in content:
        for name in S3_IRREPS:
            content[total_spin].setdefault(name, 0)
    return dict(sorted(content.items(), key=lambda item: item[0]))


def derive_selection(
    spin: Fraction,
    copies: int = 3,
) -> SelectionDerivation:
    """Derive the selected total-spin sectors from the carrier's structure.

    Condition (A) selects the unique total spin of maximal multiplicity.
    Condition (B) selects the unique total spin whose multiplicity space is
    isomorphic to the standard two-dimensional irrep of ``S_3``.

    Raises ``ValueError`` if either condition fails to be uniquely satisfied,
    so a carrier that does not admit a forced selection is reported rather than
    silently defaulted.
    """

    multiplicities = clebsch_gordan_multiplicities(spin, copies)
    content = s3_multiplicity_space_content(spin, copies)

    peak = max(multiplicities.values())
    maximal = [j for j, count in multiplicities.items() if count == peak]
    if len(maximal) != 1:
        raise ValueError(
            f"condition (A) is not unique for spin {spin}: candidates {maximal}"
        )

    standard_only = [
        j
        for j, entry in content.items()
        if entry["standard"] == 1 and entry["trivial"] == 0 and entry["sign"] == 0
    ]
    if len(standard_only) != 1:
        raise ValueError(
            f"condition (B) is not unique for spin {spin}: candidates {standard_only}"
        )

    selected = tuple(sorted({maximal[0], standard_only[0]}))
    return SelectionDerivation(spin, copies, multiplicities, content, selected)


def kernel_dimension_closed_form(spin: Fraction) -> int:
    """Return ``4s^2 + 16s - 1``, the derived kernel dimension for ``copies == 3``.

    Verified against the explicit decomposition for integer ``s`` in 1..8;
    ``s = 2`` gives 47.
    """

    value = 4 * spin * spin + 16 * spin - 1
    if value.denominator != 1:
        raise ValueError("closed form is stated for integer carrier spin")
    return int(value)

