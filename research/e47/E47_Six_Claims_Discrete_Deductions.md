# E47 Six Claims — Discrete Deductions

**Certificate:** `MC-E47-SIX-CLAIMS-DEDUCTIONS/1.0` · 22/22 PASS
**Executable:** [`validation/e47_six_claims_deductions.py`](validation/e47_six_claims_deductions.py) (standard library only)
**Record:** [`artifacts/E47_SIX_CLAIMS_DEDUCTIONS_CERTIFICATE.json`](../../artifacts/E47_SIX_CLAIMS_DEDUCTIONS_CERTIFICATE.json)
**Evidence:** E0 exact rational arithmetic; A5 characters rounded from floats; one seeded Haar sample.
**Derivation:** Nicholas Shane Kouns with Claude, 5 November 2026.

This note takes six interpretive claims made about the E47 kernel and writes each as a discrete deduction. Every step is either a premise (P), a definition (Def), or a line that follows from earlier lines. Where a claim does not follow, the note names the missing premise.

**Notation.** ⊢ proves · ⊬ does not prove · ∴ therefore · λ(J) = J(J+1) · H = V₂^⊗3 · C = J²_tot · K = (C−6I)(C−30I) · E = ker K · P = orthogonal projector onto E.

## Verdicts

| # | Claim | Verdict | Valid form |
|---|---|---|---|
| 1 | The kernel is parameter-free and stands alone | **Holds** | j = 2 is the first proper member of the Fibonacci–Lucas family |
| 2 | E is a quantum error-correcting code | **Holds, narrower** | Noiseless subsystem for collective SU(2) noise |
| 3 | Public computability of P is a trapdoor | **Does not follow** | Contradicts the definition of a trapdoor |
| 4 | The A5 failure proves SU(2) is unique | **Does not follow** | Proves the forcing is not generic |
| 5 | The median theorem is a statement about entanglement | **Conditional** | Median = mean under a measure-preserving antisymmetry |
| 6 | The Horner form is the fastest subspace filter | **Holds, narrower** | Degree 6 is the minimum among polynomials in C |

## Base lemmas

**B1 (census).** H ≅ V₀ ⊕ 3V₁ ⊕ 5V₂ ⊕ 4V₃ ⊕ 3V₄ ⊕ 2V₅ ⊕ V₆, so the state counts are w = (1, 9, 25, 28, 27, 22, 13), Σw = 125. [D1.1–D1.2]

**B2 (moments).** For V_j^⊗3 with uniform state weighting:
C = 3λ(j)·I + 2 Σ_{a<b} J⁽ᵃ⁾·J⁽ᵇ⁾.
Each pair term has mean 0 and second moment λ(j)²/3, and distinct pair terms are uncorrelated.
∴ μ = 3λ(j) and σ² = 4·3·λ(j)²/3 = 4λ(j)², so σ = 2λ(j). [D3.1, checked for all 2j ≤ 80]

**B3 (sector values).** K acts on the sector c = λ(J) as k_c = (c−6)(c−30) = (180, 112, 0, −108, −140, 0, 432). [D4.1]

## Claim 1 — the kernel stands alone

1. μ − σ = λ(j). ⇒ The lower edge always lands on the sector J = j. (B2)
2. μ + σ = 5λ(j) = λ(J) ⟺ (2J+1)² − 5(2j+1)² = −4. (algebra) [D3.2]
3. The positive solutions of x² − 5y² = −4 are (x, y) = (L_k, F_k) with k odd, the norm −1 units of ℤ[φ]. [D3.3]
4. k = 3 gives j = ½ and selects the whole carrier (8/8). k = 5 gives j = 2, J = 5 and selects 47/125. [D3.4]
5. ∴ The cube is the first proper member. The next is j = 6 with 314/2197.
6. Γ_math ⊢ (1–5) without any physical axiom. ∴ The kernel's theorems are independent of every physical interpretation placed on them.

⊬ that j = 2 is the only solution. The family is infinite. Already recorded in the [Moment Selector Theorem](E47_Moment_Selector_Theorem.md).

## Claim 2 — error correction

- P2.1: The noise is collective: errors are U^⊗3 with U ∈ SU(2).
- P2.2: H ≅ ⊕_J V_J ⊗ ℂ^{m_J}, and U^⊗3 acts as ⊕_J U_J ⊗ I. (Schur–Weyl / B1)

1. E ≅ (V₂ ⊗ ℂ⁵) ⊕ (V₅ ⊗ ℂ²). (B1, B3)
2. Every collective error acts as identity on ℂ⁵ and ℂ². (P2.2)
3. ∴ ℂ⁵ and ℂ² are noiseless subsystems. The protected logical algebra is M₅(ℂ) ⊕ M₂(ℂ), dim 29. Protection is passive: no syndrome measurement is needed against this error set.

Executed in the [convergence + noiseless validator](validation/e47_convergence_noiseless_validator.py) and the [logical-qubit certificate](E47_Logical_Qubit_Multiplicity_Validation.md).

⊬ the 78-dimensional complement is "the error space". It is the other Casimir sectors.
⊬ protection against non-collective errors. Knill–Laflamme needs a named error set 𝓔 with P Eₐ† E_b P = c_ab P.
⊬ "transversal / finite-depth circuit". P is a projector, not a unitary. A physical implementation needs a dilation, a channel or postselection.

## Claim 3 — cryptographic trapdoor

- Def: f is a trapdoor function ⟺ f is easy to invert with a secret t, and hard to invert without t.
- P3: P = p(C) with p a fixed public rational polynomial, so P is computable from a public C in polynomial time. [D9.1]

1. P3 ⇒ the kernel adds no hardness without a secret.
2. Def ∧ (1) ⇒ ¬Trapdoor.

∴ The manuscript's statement that the kernel contributes no hardness is the correct reading.

## Claim 4 — the A5 restriction

- P4.1: χ_E on the A5 classes [e, 5A, 5B, 3A, 2A] = [47, 2, 2, −7, 3]. [D7.1]
- P4.2: Character projection gives E↓A5 = 2T₁ ⊕ 2T₂ ⊕ 7H. [D7.2]
- P4.3: The manuscript's forcing condition fails for A5 (selector 4.9952 ≠ 5).

1. P4.3 ⊢ ∃G: ¬Forcing(G). Equivalently ¬∀G Forcing(G). The forcing is **not generic**.
2. "SU(2) is unique" means ∀G ≠ SU(2): ¬Forcing(G).
3. (1) ⊬ (2). One counterexample does not cover every group. Proving (2) needs a classification of candidate groups G and carriers.

## Claim 5 — median and Haar measure

- P5.1: τ(θ) = π/2 − θ preserves dθ on [0, π/2].
- P5.2: f∘τ = 2Ω_c − f, where f is the occupancy along the curve.

1. P5.1 ∧ P5.2 ⇒ f − Ω_c has a distribution symmetric about 0.
2. ⇒ median(f) = mean(f) = 47/125 under dθ, assuming no point mass at Ω_c.
3. Haar-random unit v ∈ ℂ¹²⁵: E[vv†] = I/125 ⇒ E‖Pv‖² = Tr P/125 = 47/125 exactly. [D8.1, D8.2]

⊬ "the Haar defect is Fubini–Study curvature". On conjugacy classes the Haar density comes from the Weyl integration formula.
⊬ a statement about entanglement. "Half of states are more coherent" restates the median.

**Open source item.** The curve f(θ), the 4.9952 selector and the 7.42 × 10⁻⁴ defect are not defined in any committed file. P5.2 and P4.3 are taken as premises here until their source is added.

## Claim 6 — the Horner decoder

- P6: C has exactly 7 distinct eigenvalues {0, 2, 6, 12, 20, 30, 42}. Its minimal polynomial has degree 7.

1. Every polynomial in C is determined by its values on the 7 eigenvalues. ⇒ P = p(C) for a unique p with deg p ≤ 6 (Lagrange).
2. p(λ) = λ(λ−2)(λ−12)(λ−20)(λ−31)(λ−42)/1814400 = ((((((λ−107)λ+4088)λ−66940)λ+430848)λ−624960)λ)/1814400. [D6.1–D6.2]
3. The leading coefficient 1/1814400 ≠ 0. ∴ deg p = 6 is the minimum among polynomials in C. [D6.3]
4. Horner evaluation uses 6 applications of C and one scaling, with no branches.

⊬ "fastest possible". With P precomputed once as a 125×125 matrix, each projection is one matrix–vector product. The Horner form wins when C is only available as an operator (for example, sparse Σ J⁽ᵃ⁾·J⁽ᵇ⁾).

Related: the five-factor product in K² and five-step termination in the [Condition Lock](E47_Condition_Lock_Theorem.md) give the same P.

## Supporting constants

| Quantity | Value | Deduction |
|---|---|---|
| Gap | 11664 = 108² | min nonzero k_c² is at J = 3, where k = −108 [D4.2] |
| rank K | 78 | 1 + 9 + 28 + 27 + 13 [D4.3] |
| Minimax step, rate | 1/99144, 15/17 | 2/(108² + 432²), (16−1)/(16+1) [D4.4] |
| 78/125 rate | eigenvalue of Γ_P = (1−Ω_c)I + Ω_c P on E⊥ | 1 − 47/125 [D5.1] |

## Boundary

These are finite statements about a fixed 125-dimensional carrier and the triple-product family V_j^⊗3. They add no physical claim.
