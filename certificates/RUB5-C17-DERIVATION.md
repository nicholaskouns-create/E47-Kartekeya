# RUB5-C17 — Descent Derivation and Audit

**Derived:** 2026-10-26 · **Checks:** 25 passed, 0 failed
**Source plate:** [`RUB5-C17-PLATE.md`](./RUB5-C17-PLATE.md)
**Reproduce:** `python3 -I certificates/rub5_c17_descent_derivation.py`

The plate asserts a descent `125 → 47 → M₅(ℂ)` with a 24-dimensional canonical
state geometry. This note derives the descent from the collective SU(2)
structure rather than assuming it. The carrier, the kernel and every declared
constant hold exactly. The terminal algebra does not: it is larger than
stated, and the plate's own §III table contradicts the bound printed beside
it.

---

## 1 · Setup, with multiplicities read off rather than supplied

Carrier `V = V₂ ⊗ V₂ ⊗ V₂`, `dim V = 125`, with the collective action
`J_a = j_a ⊗ 1 ⊗ 1 + 1 ⊗ j_a ⊗ 1 + 1 ⊗ 1 ⊗ j_a`.

Diagonalising `C = J² = J_x² + J_y² + J_z²` and grouping eigenvalues by
`C = j(j+1)` gives the Schur–Weyl decomposition

```
V = ⊕_j  V_j ⊗ ℂ^{m_j},     m = (m_0 … m_6) = (1, 3, 5, 4, 3, 2, 1)
```

| j | C = j(j+1) | dim V_j | m_j | sector dim |
|---|---|---|---|---|
| 0 | 0 | 1 | 1 | 1 |
| 1 | 2 | 3 | 3 | 9 |
| 2 | 6 | 5 | 5 | 25 |
| 3 | 12 | 7 | 4 | 28 |
| 4 | 20 | 9 | 3 | 27 |
| 5 | 30 | 11 | 2 | 22 |
| 6 | 42 | 13 | 1 | 13 |

Σ m_j(2j+1) = 125. These multiplicities are an output of the eigendecomposition,
not an input.

## 2 · The kernel

`K = (C − 6I)(C − 30I)` annihilates exactly the sectors with `C = 6` (j=2) and
`C = 30` (j=5). Hence

```
E₄₇ = ker K = (V₂ ⊗ ℂ⁵) ⊕ (V₅ ⊗ ℂ²)
dim E₄₇ = 5·5 + 11·2 = 25 + 22 = 47
Ω_c = 47/125 = 0.376            (exact in rational arithmetic)
```

`P₄₇` is self-adjoint, idempotent to `7.2 × 10⁻¹⁵`, and commutes with the
collective generators to `< 10⁻¹²`.

## 3 · Declared constants — all confirmed exactly

`spec(K²) \ {0} = {11664, 12544, 19600, 32400, 186624}`.

| Claim | Status |
|---|---|
| gap = 11664 = 108² | **exact** — attained at j=3, since (12−6)(12−30) = −108 |
| ‖K²‖ = 186624 = 432² | **exact** — attained at j=6 |
| normalizer 99144 maps spec(A)\\{0} into (0,2) | **exact** — interval [0.117647, 1.882353] |
| 1/99144 is the minimax step | **exact** — 2/(11664 + 186624) = 1/99144 |
| spectral radius on E₄₇⊥ = 15/17 | **exact** in ℚ, not estimated |

The radius is attained twice with opposite sign — `+15/17` at j=3 and `−15/17`
at j=6. That equioscillation is what certifies 1/99144 as optimal: no smaller
bound exists for this spectrum.

## 4 · The descent, derived

By the double commutant theorem, the algebra of observables on `E₄₇` commuting
with the collective SU(2) action is the multiplicity algebra of the retained
branches:

```
𝕆_can = End(ℂ⁵) ⊕ End(ℂ²) = M₅(ℂ) ⊕ M₂(ℂ),      dim = 25 + 4 = 29
```

No off-diagonal block survives: an intertwiner between `V₂ ⊗ ℂ⁵` and
`V₅ ⊗ ℂ²` would be an SU(2)-equivariant map between inequivalent irreps, hence
zero by Schur's lemma. The algebra is block-diagonal by representation theory,
not by assumption.

**Verified independently.** The commutant is the kernel of the adjoint-action
Casimir superoperator `L(X) = Σ_a [J_a, [J_a, X]]` on `End(E₄₇)`. Its numerical
nullity is **29**, matching `m_2² + m_5² = 25 + 4`. The same law on the full
carrier gives `Σ_j m_j² = 65`.

### Certificate [6] is incomplete

The plate's descent pathway reads `125 → 47 → M₅(ℂ)`. `M₅(ℂ)` alone has
dimension 25. The derived terminal algebra has dimension 29. The missing
`M₂(ℂ)` is the j=5 branch — **one protected logical qubit**.

The correct statement is

```
125 → 47 → 5 ⊕ 2
```

This is not a new result for the corpus: `E47_SPECTRAL_ADVANTAGES_2026-10-24`
already states `E₄₇ ≅ (V₂ ⊗ ℂ⁵) ⊕ (V₅ ⊗ ℂ²)` and names the protected qubit in
`ℂ²`. RUB5-C17 is the one place where that second branch is dropped. This is a
consistency repair, not a correction of the underlying algebra.

## 5 · State geometry is 28-dimensional, not 24

For a block algebra `⊕_i M_{n_i}`, the unit-trace positive elements form a
convex body of real affine dimension `(Σ n_i²) − 1`.

| algebra | dim 𝒟 |
|---|---|
| M₅(ℂ) alone | **24** |
| M₅(ℂ) ⊕ M₂(ℂ) | **28** |

The plate's 24 is the Bloch body of the j=2 branch only. Carrying both
protected branches, `𝒟_can` is 28-dimensional: 24 (ℂ⁵ body) + 3 (ℂ² ball) + 1
(population split between branches). The uniqueness of a projected Gibbs
equilibrium must therefore be stated on the 28-dimensional body; on 24 it is a
statement about a face of it.

## 6 · §III convergence table contradicts its own bound column

Running the real iteration `ρ → Γ ρ Γ / tr(·)` with `Γ = I − K²/99144`:

| k | plate R_k | bound (15/17)^k | plate ≤ bound? | true R_k |
|---|---|---|---|---|
| 0 | 0.708597 | 1.00e+00 | yes | 6.27e-01 |
| 1 | 0.663644 | 8.82e-01 | yes | 5.50e-01 |
| 2 | 0.635755 | 7.79e-01 | yes | 4.72e-01 |
| 5 | 0.577432 | 5.35e-01 | **no** | 2.69e-01 |
| 10 | 0.487645 | 2.86e-01 | **no** | 8.48e-02 |
| 20 | 0.322265 | 8.18e-02 | **no** | 6.85e-03 |
| 50 | 0.064736 | 1.92e-03 | **no** | 3.51e-06 |
| 100 | 0.003506 | 3.67e-06 | **no** | 1.23e-11 |

**5 of 8 printed rows exceed the contraction bound printed beside them**, first
at k=5, by a factor of ~10³ at k=50 and ~10⁵ at k=100. Every one is labelled
"Contracting".

Meanwhile the true trajectory *beats* the quoted bound, because `Γ` acts on both
sides of a density matrix, so the residual decays like `(15/17)^{2k}`, not
`(15/17)^k`. At k=50 the real residual is 3.5 × 10⁻⁶ against a bound of
1.9 × 10⁻³.

So the §III table is neither output of this iteration nor consistent with its
own bound. The bound itself is sound and in fact conservative; the tabulated
trajectory should be regenerated from the operator.

## 7 · Certificate [4] is quoted below float64 resolution

`‖K‖₂ = 432` (attained at j=6). The float64 floor for a residual of an
operator that size is `432 · ε ≈ 9.6 × 10⁻¹⁴`.

| | value |
|---|---|
| plate's quoted ‖K P₄₇‖ | 4.31 × 10⁻¹⁵ |
| measured ‖K P₄₇‖ | 3.13 × 10⁻¹² |
| measured relative, ‖K P₄₇‖/‖K‖ | 7.2 × 10⁻¹⁵ |

The quoted figure sits an order of magnitude below what the arithmetic can
resolve for this operator. The property holds — the relative defect is at
machine precision — but the test should be stated relative to `‖K‖`, and the
absolute `< 1e-14` threshold is not meaningful here.

---

## Revised certificate block

```
[1] CARRIER DIMENSION          : dim V = 125  -->  dim E47 = 47            [PASS]
[2] COHERENCE FRACTION         : Omega_c = 47/125 = 0.376 exact in Q       [PASS]
[3] IDEMPOTENCY                : ||P^2 - P|| = 7.2e-15                     [PASS]
[4] KERNEL NULL-SPACE          : ||K P||/||K|| = 7.2e-15  (relative)       [PASS]
[5] CONTRACTION RADIUS         : 15/17 exact, equioscillating j=3, j=6     [PASS]
[6] ALGEBRAIC DESCENT          : 125 --> 47 --> M5(C) (+) M2(C), dim 29    [AMENDED]
[7] CANONICAL STATE GEOMETRY   : dim D_can = 28 = 24 + 3 + 1               [AMENDED]
[8] SECTION III TRAJECTORY      : 5/8 rows exceed (15/17)^k; regenerate    [FAIL]
```

## Boundary

Everything above is finite-dimensional representation theory and exact rational
arithmetic on a 125-dimensional complex vector space. No physical observable,
unit, or measurement is derived or implied. The bridge operator
`𝒪_physical ↦ P𝒪P` named in the plate's boundary note remains undefined, and
nothing here supplies it.
