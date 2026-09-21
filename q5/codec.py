"""Q5 codec: the 125-word alphabet of {0,1,2,3,4}^3.

No new operator. The packing map is the existing bijection
π(x,y,z) = 25x + 5y + z. Each word is the three-digit quinary
string of that address. Residuals are the values already
measured by the Drive L_IG witness and the poster validator.
"""

from __future__ import annotations

from fractions import Fraction

RADIX = 5
DIM = RADIX**3  # 125
KERNEL = 47
COMPLEMENT = DIM - KERNEL  # 78

# Magnetic labels of V₂: digit d ∈ {0,1,2,3,4} ↔ m = d − 2.
M_OFFSET = 2


def pi(x: int, y: int, z: int) -> int:
    """Address bijection π(x,y,z) = 25x + 5y + z."""
    if not all(0 <= c < RADIX for c in (x, y, z)):
        raise ValueError(f"coordinates must lie in {{0,...,{RADIX - 1}}}")
    return (x * RADIX + y) * RADIX + z


def unpi(i: int) -> tuple[int, int, int]:
    """Inverse of π. i = 25x + 5y + z."""
    if not 0 <= i < DIM:
        raise ValueError(f"index must lie in {{0,...,{DIM - 1}}}")
    z = i % RADIX
    y = (i // RADIX) % RADIX
    x = i // (RADIX * RADIX)
    return x, y, z


def word(x: int, y: int, z: int) -> str:
    """The alphabet word: three quinary digits, high place first."""
    if not all(0 <= c < RADIX for c in (x, y, z)):
        raise ValueError(f"coordinates must lie in {{0,...,{RADIX - 1}}}")
    return f"{x}{y}{z}"


def unword(w: str) -> tuple[int, int, int]:
    """Parse a three-digit quinary word."""
    if len(w) != 3 or any(ch not in "01234" for ch in w):
        raise ValueError(f"word must be three digits in 0..4, got {w!r}")
    return int(w[0]), int(w[1]), int(w[2])


def mag(d: int) -> int:
    """Digit → magnetic number of V₂."""
    return d - M_OFFSET


def encode(x: int, y: int, z: int) -> dict:
    """One ledger cell. Word plus the packing address. Nothing else."""
    return {"i": pi(x, y, z), "x": x, "y": y, "z": z, "word": word(x, y, z)}


def cells() -> list[dict]:
    """All 125 words, x slowest, z fastest, matching π."""
    out = []
    for x in range(RADIX):
        for y in range(RADIX):
            for z in range(RADIX):
                out.append(encode(x, y, z))
    return out


# Already-measured residuals. Exact identities first; machine
# residuals copied from the committed certificate / L_IG witness.
# Not recomputed here. Not a new credential.

CASIMIR_SPECTRUM = (0, 2, 6, 12, 20, 30, 42)
CASIMIR_MULTIPLICITIES = (1, 9, 25, 28, 27, 22, 13)

_K_FROM_C = tuple((lam - 6) * (lam - 30) for lam in CASIMIR_SPECTRUM)
K2_SPECTRUM = tuple(sorted({k * k for k in _K_FROM_C}))
K2_GAP = 11664
K2_MAX = 186624

OMEGA = Fraction(KERNEL, DIM)  # 47/125 = 0.142_5
EPS_STAR = Fraction(1, 99144)
EPS_MAX = Fraction(1, 93312)
RHO_STAR = Fraction(15, 17)

# Quinary spellings already certified: 47 = 142_5, 78 = 303_5, 125 = 1000_5.
WORD_47 = "142"
WORD_78 = "303"
WORD_125 = "1000"

RESIDUALS = {
    "witness": {
        "drive_lig": "validate_lig_proof.py",
        "drive_id": "1zJYxmjiNbiuZB94Q5tTjz_zHLGmWMsMC",
        "poster": "E47 INVARIANT poster validator",
        "repo_certificate": "artifacts/e47_validation_certificate.json",
    },
    "exact": {
        "dim": DIM,
        "kernel": KERNEL,
        "complement": COMPLEMENT,
        "omega": "47/125",
        "omega_quinary": "0.142_5",
        "v5_125": 3,
        "abs_5_125": "1/125",
        "v5_47": 0,
        "casimir_spectrum": list(CASIMIR_SPECTRUM),
        "casimir_multiplicities": list(CASIMIR_MULTIPLICITIES),
        "k2_spectrum": list(K2_SPECTRUM),
        "k2_gap": K2_GAP,
        "k2_max": K2_MAX,
        "eps_star": "1/99144",
        "eps_max": "1/93312",
        "rho_star": "15/17",
        "cube_laplacian_frobenius": "8*sqrt(3)",
        "cube_laplacian_spectral": "2*sqrt(2)",
        "word_47": WORD_47,
        "word_78": WORD_78,
        "word_125": WORD_125,
    },
    "measured": {
        # artifacts/e47_validation_certificate.json
        "projector_idempotence": 4.906691467917368e-14,
        "projector_hermiticity": 0.0,
        "kernel_annihilation": 2.306547804400579e-11,
        "kernel_annihilation_K_on_kerK2": 3.66356143212542e-13,
        "projector_trace_error": 7.105427357601002e-15,
        "asymptotic_projector_residual": 9.841760953537459e-11,
        "contraction_hermitian_residual": 4.5614838681767503e-14,
        "kernel_fixed_residual": 5.2903539071262844e-15,
        # validate_lig_proof.py declared bounds (not new measurements)
        "lig_tol": 2.0e-10,
        "lig_annihilation_tol": 1.0e-8,
        "lig_contraction_n250_tol": 1.0e-10,
        "lig_coalgebra_limit_tol": 1.0e-10,
    },
}


def quinary(n: int, width: int | None = None) -> str:
    """Nonnegative integer as a base-5 digit string."""
    if n < 0:
        raise ValueError("quinary encoding is defined for n >= 0")
    if n == 0:
        digits = "0"
    else:
        digits = ""
        while n:
            n, r = divmod(n, RADIX)
            digits = str(r) + digits
    if width is not None:
        digits = digits.zfill(width)
        if len(digits) > width:
            raise ValueError("value exceeds requested width")
    return digits
