# Emergent Spacetime — the Half-Occupancy Theorem

**g₀₀ = p̈ ⁄ 4.** The time–time component of the induced metric is a quarter of
the coherence acceleration, so the metric signature is the sign of (1 − 2p) and
turns from Euclidean to Lorentzian exactly at half occupancy.

Live page: <https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/emergent-spacetime/>

## The statement

Let ℋ = V₂ ⊗ V₂ ⊗ V₂ with total Casimir C, let K = (C − 6)(C − 30) and
E₄₇ = ker K, and let p = ‖P₄₇Ψ‖² ⁄ ‖Ψ‖² be the kernel occupancy under the
minimax filter Λ = I − ε∗K². Then the induced coframe metric is

```
g = diag( κ² p(1−p)(1−2p),  2p,  2p,  2p ),      κ = ln(17/15)
```

and its signature is

| occupancy | signature | regime                            |
|-----------|-----------|-----------------------------------|
| p < ½     | (4,0,0)   | Euclidean — coherence accelerating |
| p = ½     | (3,0,1)   | degenerate — the signature change  |
| p > ½     | (3,1,0)   | Lorentzian — coherence decelerating |

Since g₀₀ = p̈/4 and the flow is logistic, the signature change *is* the
inflection of the occupancy. That is why the critical point is ½ and not a
tuned number.

## What is forced rather than chosen

- **The selector roots.** The Casimir spectrum weighted by block dimension has
  mean μ = 18 and variance σ² = 144 exactly, so σ = 12 and the roots 6 and 30
  are precisely μ ∓ σ. Nothing else in the spectrum sits there.
- **The step.** With A = K², the extreme eigenvalues off the kernel are 11664
  and 186624. The minimax step is where they equioscillate: 2 = ε(11664+186624),
  giving ε∗ = 1/99144 uniquely, and ρ∗ = 1 − 11664/99144 = 15/17, attained twice.
  Their ratio is exactly 16.
- **The spatial legs.** All three live in the C = 6 sector and
  (1/5)·tr_{V₂}(J_aJ_b) = 2δ_ab exactly, so they are equal, not merely similar.

## Files

| file | what it does | result |
|------|--------------|--------|
| `certificate.py` | Builds the carrier from the su(2) generators and derives every constant. No stored values. | 68/68 |
| `HalfOccupancy.lean` | Lean 4.35.0, core only — no Mathlib, no `sorry`. | 20 theorems, **0 axioms** |
| `HalfOccupancy.v` | Coq 8.18, independent kernel, same twenty statements. | 20 theorems, closed under the global context |
| `quantum_simulation.py` | Kraus channel, 250-dimensional Stinespring dilation, occupancy run with success probability. | 21/21 |

The browser engine and its tests live in
[`website/interfaces/emergent-spacetime`](../../website/interfaces/emergent-spacetime),
and are checked against the same integers the provers decide.

## Running them

```sh
python3 docs/emergent-spacetime/certificate.py
python3 docs/emergent-spacetime/quantum_simulation.py
lean docs/emergent-spacetime/HalfOccupancy.lean      # prints the axiom audit
coqc -q docs/emergent-spacetime/HalfOccupancy.v      # prints Print Assumptions
node --test website/interfaces/emergent-spacetime/flow.test.mjs
```

## The decidable core

Three facts carry the theorem and all three are integer arithmetic, which is why
both provers close them by kernel computation with no real analysis:

```
2 · 99144 = 11664 + 186624                     the minimax step
(99144 − 11664) · 17 = 15 · 99144              the rate is 15/17
2·3925487 < 7874237  and  2·1134465743 > 2022934493
                                               Euclidean at step 2, Lorentzian at step 3
```

The occupancy map in integers is `(a,b) ↦ (289a, 289a + 225(b−a))`, started at
Ω_c = 47/125.

## Scope and limits

- This is the induced coframe metric of a contraction's fixed-point flow. It is
  **not** a solution of the Einstein field equations and no claim is made that
  it is one.
- The transition step is an **upper bound**. Off the kernel Λ has five distinct
  contraction factors and only the two equioscillation sectors (C = 12, C = 42)
  are as slow as ρ∗; a generic state crosses sooner. The random state tested in
  `certificate.py` crossed at step 2.
- κ = ln(17/15) is the continuum envelope of an exactly rational map. An earlier
  figure of 50/153 circulated for this constant; it does not reproduce from the
  spectrum and has been dropped rather than carried forward.
- The quantum track is an exact noiseless simulation. No quantum hardware was
  involved and no quantum advantage is claimed.

Original work of Nicholas Shane Kouns.
