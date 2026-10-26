# RUB5-C17 Rev B — Corrected Plate

**Supersedes:** [`RUB5-C17-PLATE.md`](./RUB5-C17-PLATE.md) (input of record, left unaltered)
**Derivation:** [`RUB5-C17-DERIVATION.md`](./RUB5-C17-DERIVATION.md)
**Machine check:** `python3 -I certificates/rub5_c17_descent_derivation.py` — 25 pass, 0 fail
**Formal check:** `Identity/formal/e47/E47Commutant.{lean,v}` — 17 theorems, no axioms

Four of the six certificates in Rev A were exact and are carried over unchanged.
Two were wrong, one was stated against an unreachable threshold, and the §III
trajectory contradicted its own bound column. Those are corrected here.

---

## Title

**Tenfold Recursive Canonical Closure and Observable Descent Theorem: 125 → 47 → 5 ⊕ 2**

Certified Carrier → Canonical Projector → Full 𝕆_can = M₅(ℂ) ⊕ M₂(ℂ) →
28-dimensional State Geometry → Unique Gibbs Equilibrium

*Changed from Rev A: `125 → 47 → 5` becomes `125 → 47 → 5 ⊕ 2`; `M₅(ℂ)` becomes
`M₅(ℂ) ⊕ M₂(ℂ)`; `24D` becomes `28D`.*

## I–II. Carrier, filter and constants — unchanged

`V = V₂ ⊗ V₂ ⊗ V₂`, `dim V = 125`. Multiplicities `m = (1,3,5,4,3,2,1)` for
j = 0..6, read off the Casimir spectrum rather than supplied.

`K = (C − 6I)(C − 30I)`, `E₄₇ = ker K = (V₂ ⊗ ℂ⁵) ⊕ (V₅ ⊗ ℂ²)`, `dim = 25 + 22 = 47`.

| Constant | Value | Status |
|---|---|---|
| Normalizer | 99144 | **exact** — `2/(11664 + 186624) = 1/99144`, the minimax step |
| Spectral radius on `E₄₇⊥` | 15/17 | **exact in ℚ** — equioscillating `+15/17` at j=3, `−15/17` at j=6 |
| Gap (Primer B10) | 11664 = 108² | **exact** — attained at j=3 |
| `‖K²‖` | 186624 = 432² | **exact** — attained at j=6 |
| Coherence fraction | Ω_c = 47/125 = 0.376 | **exact in ℚ** |

The interval check holds: `spec(K²)\{0} / 99144 ⊂ [0.117647, 1.882353] ⊂ (0,2)`.

## III. Dissipative convergence trajectory — regenerated

Rev A's table was not output of the iteration it described, and 5 of its 8 rows
exceeded the `(15/17)^k` bound printed beside them.

**The bound was the error, not the rate.** Under `ρ → ΓρΓ / tr(·)` the operator
Γ acts on *both* sides and is the identity on E₄₇, so the correct invariant is
the odds ratio, which contracts by exactly `(15/17)² = 225/289` per step:

> **R_k / (1 − R_k) ≤ [R₀ / (1 − R₀)] · (15/17)^{2k}**

Regenerated from `Γ = I − K²/99144`, seed 17:

| Step k | Coherence C_k = Tr(P ρ_k) | Residual R_k | Odds R_k/(1−R_k) | Bound | Status |
|---|---|---|---|---|---|
| 0 | 0.372942879180540 | 6.271e-01 | 1.681e+00 | 1.681e+00 | Initial State |
| 1 | 0.450316359071236 | 5.497e-01 | 1.221e+00 | 1.309e+00 | Contracting |
| 2 | 0.527822343464296 | 4.722e-01 | 8.946e-01 | 1.019e+00 | Contracting |
| 5 | 0.730863359283643 | 2.691e-01 | 3.682e-01 | 4.809e-01 | Contracting |
| 10 | 0.915191180723982 | 8.481e-02 | 9.267e-02 | 1.376e-01 | High Coherence |
| 20 | 0.993149976632300 | 6.850e-03 | 6.897e-03 | 1.126e-02 | Near-Closure |
| 50 | 0.999996485882069 | 3.514e-06 | 3.514e-06 | 6.165e-06 | Subspace Trapped |
| 100 | 0.999999999987722 | 1.228e-11 | 1.228e-11 | 2.260e-11 | Subspace Trapped |
| 150 | 1.000000000000000 | 0 (float64) | 0 | 8.286e-17 | Full Asymptotic Closure |

The bound holds at **every** tabulated step. The naive `(15/17)^{2k}` bound on
`R_k` itself does *not* — it fails marginally at k = 10 — which is why the
statement is on the odds ratio.

Rev A's `C_∞ = 1.0` and `R < 10⁻¹⁴` at k = 150 were right; the route there was not.

## IV. Machine certificates — Rev B

```
[1] CARRIER DIMENSION          : dim V = 125  -->  dim E47 = 47            [PASS]
[2] COHERENCE FRACTION         : Omega_c = 47/125 = 0.376 exact in Q       [PASS]
[3] IDEMPOTENCY                : ||P^2 - P|| = 7.2e-15                     [PASS]
[4] KERNEL NULL-SPACE          : ||K P|| / ||K|| = 7.2e-15   (relative)    [PASS]
[5] CONTRACTION RADIUS         : 15/17 exact, equioscillating j=3, j=6     [PASS]
[6] ALGEBRAIC DESCENT          : 125 --> 47 --> M5(C) (+) M2(C), dim 29    [PASS]
[7] CANONICAL STATE GEOMETRY   : dim D_can = 28 = 24 + 3 + 1               [PASS]
[8] TRAJECTORY ODDS CONTRACTION: R/(1-R) factor (15/17)^2 = 225/289        [PASS]
```

### What changed from Rev A, line by line

| Line | Rev A | Rev B | Why |
|---|---|---|---|
| [1] | dim 125 → 47 | unchanged | exact |
| [2] | Ω_c = 0.376 | unchanged | exact |
| [3] | ‖P² − P‖ = 2.14e-16 | 7.2e-15 | measured value; both pass |
| [4] | ‖K P‖ = 4.31e-15 < 1e-14 | relative, 7.2e-15 | `‖K‖ = 432`, so the float64 floor is ~1e-13 — the Rev A figure was below what the arithmetic can resolve. The property holds; the threshold did not |
| [5] | radius 15/17 | unchanged | exact, and optimal |
| [6] | → M₅(ℂ) | → M₅(ℂ) ⊕ M₂(ℂ), dim 29 | M₅(ℂ) alone has dim 25. The j=5 branch — one protected logical qubit — was dropped |
| [7] | 24D (in title) | 28D = 24 + 3 + 1 | 24 is the spin-2 face of the body |
| [8] | — | new | the trajectory now has a bound it satisfies |

## Why [6] and [7] moved

`E₄₇ = (V₂ ⊗ ℂ⁵) ⊕ (V₅ ⊗ ℂ²)`. By double commutant, the algebra of observables
commuting with the collective SU(2) action is the multiplicity algebra of
**both** retained branches:

```
𝕆_can = End(ℂ⁵) ⊕ End(ℂ²) = M₅(ℂ) ⊕ M₂(ℂ),   dim = 25 + 4 = 29
```

No off-diagonal block survives: an intertwiner between `V₂ ⊗ ℂ⁵` and `V₅ ⊗ ℂ²`
is an SU(2)-equivariant map between inequivalent irreps, hence zero by Schur.

Confirmed three ways: by hand; numerically, as the nullity of the adjoint-action
Casimir superoperator `L(X) = Σₐ[Jₐ,[Jₐ,X]]` on `End(E₄₇)` (result 29); and
formally, in Lean 4.35.0 and Coq 8.18.0, where `commutant_dim_value : commutantDim = 29`
depends on no axioms.

The unit-trace body of `⊕ᵢ M_{nᵢ}` has real affine dimension `(Σ nᵢ²) − 1`, so
`dim 𝒟_can = 29 − 1 = 28`: 24 for the ℂ⁵ body, 3 for the ℂ² ball, 1 for the
population split between branches. Gibbs uniqueness must be stated on the
28-dimensional body; on 24 it is a statement about a face of it.

This is not new to the corpus. `E47_SPECTRAL_ADVANTAGES_2026-10-24` already
records `E₄₇ ≅ (V₂ ⊗ ℂ⁵) ⊕ (V₅ ⊗ ℂ²)` and names the protected qubit in ℂ².
RUB5-C17 was the one place the second branch was dropped.

## Boundary — unchanged from Rev A

> The content above represents exact mathematical emergence and recursive
> closure of M₅(ℂ) ⊕ M₂(ℂ). Any mapping onto physical observables requires an
> explicit bridge operator 𝒪_physical ↦ P𝒪P with declared empirical units.

That bridge remains undefined, and nothing in Rev B supplies it.
