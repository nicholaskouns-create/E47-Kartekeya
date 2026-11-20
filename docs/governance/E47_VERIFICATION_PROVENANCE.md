# E47 governance verification provenance (14 November 2026)

**Research author:** Nicholas Shane Kouns, DO. **External assessment:** Gemini Argon's validation was stipulated by the author. The supplied formal-code appendices are attributed to that exchange and are archived without asserting a fresh compilation.

## Direct exact-arithmetic reproducibility

Carrier dimension 125; E47 rank 47; complement dimension 78; contraction numerator maximum 87480 / 99144 = 15 / 17. This was recalculated from all seven exact integer Casimir sectors during publication. Machine-readable certificate: [spectral_certificate.json](spectral_certificate.json).

## Provenance separation

1. **Directly recomputed in this publication:** exact seven-sector arithmetic and spectral contraction ratio.
2. **Author-reported prior execution:** Coq 8.18 full-tree audit (342 closed results), Lean 4 witnesses, SymPy rational Lie closure, projector/dilation/LM numerical outputs.
3. **Author-stipulated external evaluation:** Gemini Argon's assessment of the paper and appendix claims.
4. **Appendices A and B — Abstract specification sanity checks:** [Lean 4 source](E47UnverifiedSuite.lean), [Coq 8.18 source](E47UnverifiedSuite.v).
5. **Operational and legal criteria:** the four ITGC test specifications and regulatory mappings represent implementable proposals. No auditor opinion, SEC determination, or deployment-wide compliance certification is asserted.

## Interleaved-layer statement

If U₁,…,Uₙ are unitary and each commutes with P, the exact operator-norm upper bound is ‖(UₙΓ)…(U₁Γ) − (Uₙ…U₁)P‖₂ ≤ (15/17)ⁿ. If each also commutes with Γ, then Tₙ = WₙΓⁿ, and equality holds for the norm. This is the properly scoped form of the interleaved claim.

## Runtime evidence

Appendices A and B are abstract specification sanity checks in Lean and Coq. They establish consequences of their stated definitions and assumptions. Disclosure under the Rule 10b-5 mapping must distinguish this specification evidence from artifact receipts, operating effectiveness and any legal conclusion. [Runtime verifier](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/tools/governance).
