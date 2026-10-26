# RUB5-C17 — Recursive Canonical Closure Proof Plate

**Status:** input of record. Transcribed as supplied, 2026-10-26.
**Derivation and audit:** [`RUB5-C17-DERIVATION.md`](./RUB5-C17-DERIVATION.md)
**Executable check:** [`rub5_c17_descent_derivation.py`](./rub5_c17_descent_derivation.py)

This file records the plate exactly as it was stated, so that the derivation
note can be read against an unaltered source. Items marked here are *claims*;
their verification status is settled in the derivation note, not in this file.

---

## Title

Tenfold Recursive Canonical Closure and Observable Descent Theorem: 125 → 47 → 5

Certified Carrier → Canonical Projector → Full 𝕆_can = M₅(ℂ) Algebra →
24D State Geometry → Unique Gibbs Equilibrium

## I–II. Certified theorem, spectral mechanics, dimensional descent

Carrier `V = V₂ ⊗ V₂ ⊗ V₂`, `dim V = 125`.
Casimir filter `K = (C − 6I)(C − 30I)`, `E₄₇ = ker K`, `dim E₄₇ = 47`.

### JSSC certificate and parameter constants, as declared

| Constant | Declared value | Declared role |
|---|---|---|
| Normalizer | 99144 | maps spec(A)\\{0} into (0,2) so `I − A/99144` contracts |
| Spectral radius | 15/17 | exact upper bound on `P⊥` (stated as proven, non-estimated) |
| Gap from Primer B10 | 11664 | minimum non-zero eigenvalue of `K²` on `E₄₇⊥` (= 108²) |
| Coherence fraction | Ω_c = 47/125 | ratio of protected kernel to total tensor capacity |

## III. Simulated dissipative convergence trajectory, as printed

| Step k | Coherence C_k = Tr(P_E47 ρ_k) | Residual R_k = 1 − C_k | Contraction bound (15/17)^k | Status |
|---|---|---|---|---|
| 0 | 0.291403 | 0.708597 | 1.000000 | Initial State |
| 1 | 0.336356 | 0.663644 | 0.882353 | Contracting |
| 2 | 0.364245 | 0.635755 | 0.778547 | Contracting |
| 5 | 0.422568 | 0.577432 | 0.531711 | Contracting |
| 10 | 0.512355 | 0.487645 | 0.282717 | Contracting |
| 20 | 0.677735 | 0.322265 | 0.079929 | High Coherence |
| 50 | 0.935264 | 0.064736 | 0.000511 | Near-Closure |
| 100 | 0.996494 | 0.003506 | 0.00000026 | Subspace Trapped |
| 150 | 1.000000 | < 10⁻¹⁴ | < 10⁻¹² | Full Asymptotic Closure (C_∞ = 1.0) |

## IV. Machine certificates, as declared (Float64, PASS 6/6)

```
[1] CARRIER DIMENSION CHECK     : dim(V) = 125  -->  dim(E47) = 47              [PASS]
[2] COHERENCE FRACTION CONSTANT : Omega_c = 47 / 125 = 0.376000 Exact           [PASS]
[3] IDEMPOTENCY DEFECT NORM     : ||P_E47^2 - P_E47|| = 2.14e-16 < 1e-14        [PASS]
[4] KERNEL NULL-SPACE DEFECT    : ||K @ P_E47|| = 4.31e-15 < 1e-14              [PASS]
[5] RICHARDSON SPECTRAL RADIUS  : Exact Bound (15/17)^n = 0.882353^n Verified   [PASS]
[6] ALGEBRAIC DESCENT PATHWAY   : 125-dim Carrier --> 47-dim Kernel --> M5(C)   [PASS]
```

## Boundary note, as supplied

> The content above represents exact mathematical emergence and recursive
> closure of M₅(ℂ). Any mapping onto physical observables requires an explicit
> bridge operator 𝒪_physical ↦ P𝒪P with declared empirical units.
