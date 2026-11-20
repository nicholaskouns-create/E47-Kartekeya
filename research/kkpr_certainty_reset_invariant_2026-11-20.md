# KKP-R Certainty–Reset Invariant Theorem
**Σ → Γ → Λ → Ψ → Ωₑ → α · 2026-11-20**

## Finite-dimensional construction
Set H=ℝ¹²⁵ and E₄₇=ker[(C−6I)(C−30I)]. Let Q∈ℝ¹²⁵ˣ⁴⁷ be an orthonormal embedding of E₄₇, so QᵀQ=I, P₄₇=QQᵀ and P₄₇Q=Q.

Let L=Σₐ(Sₐ−I)ᵀ(Sₐ−I) be the periodic 5³ lattice Laplacian and B=QᵀLQ≻0. Let A=3QᵀDQ be skew-symmetric, where D is a combination of centered periodic differences.

Specify the six stages concretely:
- Σ(ρ)=(I−0.01L)ρ, a finite spatial aggregation.
- Γ(ρ)=(I−K²/99144)ρ, spectral contraction, K=(C−6I)(C−30I).
- Λ(ρ)=Qᵀρ, coordinate projection into E₄₇.
- Ψ(y)=exp[0.1(A−0.2B)]y, internal transport-gradient evolution.
- Ωₑ(y)=accept iff s(y)=yᵀBy≤θ, where θ=0.5.
- α(y,accept)=Qy and α(y,reject)=Qb, for a chosen certified baseline b satisfying s(b)≤θ.

Define z(ρ)=ΨΛΓΣ(ρ) and F(ρ)=Qz(ρ) if Ωₑ(z(ρ)) accepts, otherwise F(ρ)=Qb.

## Exact behavioral invariant
**Theorem.** For every ρ∈ℝ¹²⁵ and every n≥1:
(1) P₄₇Fⁿ(ρ)=Fⁿ(ρ).
(2) s(QᵀFⁿ(ρ))≤θ.
(3) Acceptance returns the candidate; rejection returns the fixed certified baseline.

**Proof.** Let w(ρ) equal z(ρ) on acceptance and b on rejection. Then F(ρ)=Qw(ρ). As P₄₇Q=Q, P₄₇F(ρ)=P₄₇Qw=Qw=F(ρ). Since this holds for arbitrary input, apply the same identity to Fⁿ⁻¹(ρ) to obtain invariance at all n≥1. By construction, either Ωₑ accepts and s(w)=s(z)≤θ, or Ωₑ rejects and w=b with s(b)≤θ. Since QᵀQ=I, QᵀF(ρ)=w, establishing the output score bound; reapply at every iterate. ∎

The complete cycle enforces invariant outputs even when Σ or Γ individually fail to preserve E₄₇; this differs from proving that each intermediate state stays in E₄₇. Output subspace invariance does not entail unchanged individual states.

## Concrete NumPy/SciPy numerical check
- Concrete Casimir matrix dimension 125, E₄₇ dimension 47.
- Baseline b chosen as the lowest-B-eigenvalue mode, scaled so s(b)≈0.1.
- θ=0.5, γ=0.2, Δτ=0.1, aggregation factor 0.01.
- 25 trials × 20 cycles = 500 complete recursive cycles.
- 484 acceptances; 16 resets.
- Max ‖(I−P₄₇)Fⁿ(ρ)‖₂ ≈ 2.83×10⁻¹⁶.
- Max output gradient energy ≈0.1; max reset mismatch 0.
- Explicit branch witnesses s(y_low)=0.2 (accept) and s(y_high)=1.5 (reject).

## Formal-proof boundary
Lean 4 and Coq modules in `formal/e47/KKPRCertaintyCycle.lean` and `formal/e47/KKPRCertaintyCycle.v` prove, with 125-/47-coordinate integer-vector types, a natural-number threshold gate, protected reset, and cycle invariance under the explicitly assumed projector/embedding law P(Qy)=Qy. Their Nat-valued certificate is an abstraction of the concrete Python real quadratic score; neither formal module constructs the entire real Casimir matrix.

Python: `research/kkpr_certainty_cycle.py`. CI workflow: `.github/workflows/kkpr-certainty-cycle.yml`. The numerical matrix computations are not a substitute for a complete machine-check of the real Casimir spectral model.

**Result:** An explicit accept-or-reset cycle with a provable E₄₇ output invariant and a certified error/gradient-energy bound.
