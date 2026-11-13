# E₄₇: Changing Learned Gates, Fixed Contraction
Nicholas Shane Kouns's E₄₇ QGNN architecture · Derivation and computational receipt · 13 November 2026

## Result
Let B: C^47 → C^125 be an isometry onto E₄₇, P=BB†, Q=I−P,
K=(C−6I)(C−30I), and Γ=I−K²/99144.
For any sequence of 47-dimensional unitary matrices V₁,…,Vₙ, set Uⱼ=BVⱼB†+Q.
Then
\[
(U_n\Gamma)\cdots(U_1\Gamma)
=B(V_n\cdots V_1)B^\dagger+\Gamma^nQ.
\]
Consequently, for every integer n≥0,
\[
\|(U_n\Gamma)\cdots(U_1\Gamma)-B(V_n\cdots V_1)B^\dagger\|_2=(15/17)^n.
\]

## Proof
ΓB=B, B†Q=0, QΓ=ΓQ, and B†B=I.
Thus UⱼΓ=BVⱼB†+ΓQ. Cross terms in the product vanish; induction gives the identity.
The complementary eigenvalues of K² are 32400, 12544, 11664, 19600, 186624.
The corresponding eigenvalues of Γ are 1−λ/99144. Their largest absolute value is
15/17, attained at λ=11664 and λ=186624. Since ΓQ is Hermitian,
||ΓⁿQ||₂=(15/17)ⁿ. This proves the equality.

## Meaning for training
Every layer can apply a different learned unitary inside E₄₇ while complement suppression
follows the same exact law. The algebraic theorem permits arbitrary Vⱼ∈U(47).
The included numerical test samples Vⱼ from the four-generator gate family in the supplied
QGNN implementation. The theorem does not require that this particular family generate all U(47).

The protected term is a moving computation B(Vₙ⋯V₁)B†, so the error tracks that computation.
All formulas concern linear operators before postselection normalization.
Conditional state fidelity also depends on the input's retained weight.

## Execution
Install NumPy and SciPy, then run:
~~~bash
OPENBLAS_NUM_THREADS=1 python validate_changing_gates.py
~~~
The validator writes receipt.json with all 640 per-layer records, sampled angles,
source SHA-256, runtime versions, tolerances, and PASS/FAIL status.
The source snapshot e47_qgnn.py is included unchanged; the validator imports it
without invoking its original training entry point.

## Evidence
- Proved here: the operator identity and exact contraction equality under the stated assumptions.
- Computed: 10 seeded changing-gate sequences, 64 layers each, full 125×125 operator comparisons.
- These runs use quantum-state/matrix simulation. They validate the identity rather than retraining the optimizer.
- Original conversation execution: largest identity residual 3.3718538852082306e−14;
  largest contraction equality error 6.106226635438361e−16;
  largest gate leakage 2.0923565315269426e−15.
- receipt.json is the separately executed packaged validator's reproducible receipt.

## Source and attribution
Existing architecture and implementation: Nicholas Shane Kouns, E47-Kartekeya.
Source: https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/observatory-inputs/e47_qgnn.py
Source ownership and applicable rights remain unchanged.
Derivation and numerical extension prepared in this conversation.

