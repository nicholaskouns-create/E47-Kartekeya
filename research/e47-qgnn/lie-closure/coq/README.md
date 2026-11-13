# U(5) Lie closure — kernel-checked provenance and rank

`U5Closure.v` compiles under **Coq 8.18.0** in about 31 seconds. It needs no
Mathlib, no external library beyond Coq's own `ZArith` and `List`, and no
build system — `coqc U5Closure.v` is the whole command.

All six theorems report **Closed under the global context**. The file contains
no `Axiom`, `Parameter`, `Hypothesis`, `Admitted`, `admit` or `native_decide`.

```
coqc U5Closure.v
```

## What it proves

| Theorem | Statement |
|---|---|
| `provenance` | The 25 bracket words, computed inside Coq from `D` and `B` by the published recurrence, assemble to exactly the column matrix `MLIT`. |
| `M_ADJ` | `M · ADJ = DET · I₂₅`, all 625 entries. |
| `ADJ_M` | `ADJ · M = DET · I₂₅`, all 625 entries. |
| `DET_nonzero` | `DET ≠ 0`. |
| `words_independent` | If every coordinate of `M·c` vanishes then every `c k` vanishes — the 25 words are linearly independent. |
| `words_span` | `M · (ADJ · v) = DET · v` for every `v` — every target is reached, with the coefficients given explicitly by `ADJ/DET`. |

The commutators are **not** supplied as data. `W3 := cm W2 W1`, `W8 := cm W4 W3`
and the rest are definitions, `Mlist` is assembled from them by `map`, and
`provenance` is what ties that computation to the matrix the rank argument uses.
That link is the thing the parent README listed as missing.

## Three departures from the published certificate

**`B` is scaled by 140.** Scaling a generator by a nonzero scalar cannot change
the Lie algebra it generates — each word is merely multiplied by `140^(#B)`,
which is nonzero — and it clears every denominator. The whole file therefore runs
in exact integer arithmetic, with no rationals and no normalisation.

**The adjugate replaces the modular inverse.** Over ℤ we check
`M · ADJ = DET · I` with `DET` the 189-digit integer determinant of the scaled
matrix. This is stronger than a non-vanishing residue mod 101: it establishes
invertibility over ℚ outright, and it hands back the spanning coefficients.

**Both products are checked.** `M·ADJ` yields spanning, `ADJ·M` yields
independence. Neither leans on "a square matrix with a right inverse has a left
inverse", so no such lemma is needed.

## What remains open

The real-form implication. This file works in the integral similarity picture
and establishes that the 25 words are a basis of the 25-dimensional matrix
space. The step from there to `Lie_ℝ{−iD, −iB} = 𝔲(5)` is:

```
1 · D real diagonal   ⟹  (−iD)* = −(−iD)
    B real symmetric  ⟹  (−iB)* = −(−iB)
    skew-Hermitian matrices are closed under [·,·] and ℝ-span
                      ⟹  𝔤 ⊆ 𝔲(5)

2 · dim_ℝ 𝔲(5) = 5² = 25

3 · span_ℝ{w₁ … w₂₅}  ⊆  𝔤  ⊆  𝔲(5)
           25          ≤      =  25          ⟹  𝔤 = 𝔲(5)
```

Formalising it needs skew-Hermitian matrices over ℂ and `dim_ℝ 𝔲(5) = 25` in
Coq, which is a different build from this one. It is four lines a reader can
check by eye, and the kernel has not seen them.

## Cross-check against the published certificate

The recurrence encoded here reproduces, over 𝔽₁₀₁, the `basis_mod_p` and
`column_matrix_mod_p` arrays of `../certificate.json` entry for entry, and that
file's `inverse_mod_p` satisfies `M · W ≡ I₂₅ (mod 101)` as claimed. The exact
determinant of the unscaled matrix reproduces to all 58 digits.

---

Written 13 November 2026 by Claude (Anthropic, Opus 5) at the request of
Nicholas Shane Kouns. The mathematics and the certificate are his.
