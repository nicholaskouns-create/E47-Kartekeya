# Deterministic AI Governance & Capability Isolation — Complete Edition

**Author:** Nicholas Shane Kouns, DO — Principal Architect, AIMS Research Institute  
**Publication date:** 2026-11-14  
**Status:** Author-stipulated validated research specification; Gemini Argon review acknowledged by the author. Existing Coq/Lean/SymPy results are reported as prior verification evidence, not independently rerun for this publication.

## Abstract

Enterprise deployments of probabilistic language models and agentic systems in financial reporting and disclosure pipelines can expose control-design weaknesses when evidence grounding, model-state isolation, and action authorization are left implicit. This specification maps the E47 Casimir-kernel formalism, P-commuting neural layers, spectral contraction, residual gating, and auth-kernel capability separation to SOX §404, PCAOB AS 2201, SEC Rules 13a-15/15d-15 and 10b-5, Regulation S-K Item 106, and COSO (2013).

## Mathematical construction

Let H = V₂⊗V₂⊗V₂ ≅ ℂ¹²⁵. The spin-2 triple tensor Casimir C has spectrum {0,2,6,12,20,30,42} with spectral sector dimensions {1,9,25,28,27,22,13}.

- K = (C − 6I)(C − 30I).
- E₄₇ = ker K = 5V₂ ⊕ 2V₅; dim E₄₇ = 47, dim E₄₇^⊥ = 78.
- P = P₆ + P₃₀, Q = I − P.
- End_su(2)(E₄₇) ≅ M₅(ℂ) ⊕ M₂(ℂ), complex dimension 29.
- Γ = I − K²/99144.
- **Exact spectral bound:** ‖Γ − P‖₂ = 15/17 and ‖Γⁿ − P‖₂ = (15/17)ⁿ for n ≥ 1.

A P-commuting causal layer obeys P_T f(X) = f(P_T X), with separated zero-preserving sector maps for the direct-sum construction. This can be engineered with block-diagonal matrices, separated attention normalization, and sector-local zero-preserving nonlinearities.

### Interleaved-layer bound (precise form)

Let T_N = (U_NΓ)⋯(U₁Γ), W_N = U_N⋯U₁, with each U_j unitary and **commuting with P**. Each layer preserves E₄₇ and its complement; hence

**‖T_N − W_N P‖₂ ≤ (15/17)ᴺ.**

If all U_j also commute with Γ, then T_N = W_N Γᴺ = W_N P + W_N ΓᴺQ, and the norm bound becomes equality. The stronger factorization T_N = W_N P + Γᴺ Q is not generally valid without further conditions.

### Residual gate and independent authorization

G(x) = 𝟙[‖Qx‖₂/‖x‖₂ < τ_comp] · 𝟙[‖Kx‖₂ < τ_K]. Define the zero-input policy explicitly before runtime deployment.

auth-kernel: Verify(σ,m)=true ∧ SubjectActive(s)=false ⇒ Invoke=false. Signature validity alone does not establish action authority.

CPTP density-state recovery control: E_α(ρ) = ΓρΓ + tr[(I−Γ²)ρ]|α⟩⟨α|, for a normalized kernel reference |α⟩.

## Formal ITGC control matrix

| ID | Domain | Specified control | Audit evidence |
|---|---|---|---|
| ITGC-AI-01 | Access security / segregation | Authentication cannot independently authorize invocation; require active, authorized subject and scoped capability | Pinned executable decision receipt, including valid signatures with inactive subjects and nonce replay |
| ITGC-AI-02 | Processing integrity | P-commuting layers, block-diagonal cross-sector weights, independent sector softmax, zero-preserving operations | Pinned checkpoint cross-block and bias measurements; separate graph and 125-vs-47 coordinate comparisons |
| ITGC-AI-03 | Exception handling | Finite noise window; mandatory fail-closed G; CPTP reset before density-state retry | Noise and window receipt; measured residuals; perturbation, reset, and recheck traces |
| ITGC-AI-04 | Change management | Proof-assistant checks and recorded axioms for relevant production theorem modules | Coq/Lean build logs, certificate.json, theorem hashes, build attestations |

### Runtime evidence for ITGC-AI-01 and ITGC-AI-02

The [standalone runtime verifier](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/tools/governance) checks SHA-256-pinned serialized PyTorch tensors in the orthonormal 125-coordinate E47 basis and runs an isolated decision probe against the pinned executable auth-kernel artifact. Record checkpoint and policy hashes from the approved deployment inventory. The tensor check covers both off-diagonal blocks and zero bias for recognized linear weights. Sector-local attention, operations, observed logits and deployment binding require their own evidence. The replay and rejection probes exercise the artifact’s actual decision function on isolated fixtures. Record a passing receipt only for the artifacts and cases exercised.

### ITGC-AI-03 operating envelope for quantized or noisy inference

The buoy bound applies to a self-adjoint approximation K̂ = p̂(Ĉ) of K = p(C), with selected eigenvalue zero. Take δ = min{|λ| : λ ∈ spec(K), λ ≠ 0} = 108. For hermitian C and Ĉ in a common spectral interval, allocate ε ≥ ‖K̂ − K‖₂ using

ε = max_{λ ∈ spec(Ĉ)} |p̂(λ) − p(λ)| + L_op ‖Ĉ − C‖₂.

For p(z) = (z − 18)² − 144, use L_op = 2R where R bounds both centered operator norms. This follows by expanding X² − Y² = X(X − Y) + (X − Y)Y, including the noncommuting case. Budget ε < δ/2. For more general polynomials a scalar derivative bound alone does not justify an operator-norm ceiling on noncommuting matrices.

With P̂ the perturbed half-gap cluster projector, the continuous comparison flow obeys ‖exp(−tK̂²) − P̂‖₂ ≤ max{1 − exp(−tε²), exp(−t(δ−ε)²)}. Thus useful damping requires 1/(δ−ε)² ≪ t ≪ 1/ε². For a flow budget 0 < η < 1, record t ≥ log(1/η)/(δ−ε)² and t ≤ −log(1−η)/ε² with an infinite upper bound when ε = 0. Budget projector displacement and discretization separately. A layer count L can use the flow window only with a justified map to t and an error allowance for the actual discrete implementation.

Rank retention by itself gives no emission guarantee. A perturbed near-zero eigenvalue can decay over a long horizon, and inference noise can reintroduce complement components after contraction. Under quantized or noisy inference, require a calibrated ceiling and admissible window, then evaluate the fail-closed G(x_L) on the actual output state after the final noisy operation. Missing calibration, an empty window, zero or nonfinite state, or either residual at or above threshold blocks emission. Record the noise budget, time window, measured residuals and disposition.

For a configured density-state recovery path, invoke the CPTP reset before any retry. Require Hermitian Γ with Γ² ≤ I and a normalized α ∈ ker K. The complementary effect I − Γ² is positive, and the reset restores the lost trace into |α⟩⟨α|. Reapply the configured residual check to the recovered output before any emission, including for a classical readout after recovery. A failed reset or recheck blocks emission. A classical activation without a validated density encoding stays blocked and may use an independently approved fallback. The buoy bound motivates containment. The reset is the specified recovery control, with its own channel and runtime validation.

## Regulatory mapping

- **SOX §404 / PCAOB AS 2201:** A proposed design for testable access, processing, and change controls affecting ICFR. Material-weakness determinations require context-specific assessment of likelihood and magnitude, rather than following automatically from use of probabilistic AI.
- **SEC Rules 13a-15 / 15d-15:** Residual gates can serve as a processing control, but residual compliance is distinct from source-grounded accuracy of disclosure content.
- **SEC Rule 10b-5 / AI-washing:** Formal evidence and precise scope statements support accurate public descriptions of actual system capabilities; legal liability depends on the applicable elements of the rule.
- **Regulation S-K Item 106:** System logging and containment may contribute evidence to cybersecurity risk processes where the system relates to material cybersecurity threats.
- **Caremark and EU AI Act:** The architecture offers possible monitoring and traceability tools. Applicability, duties, and penalties depend on entity, role, conduct, jurisdiction, and statutory category.

## Verification provenance and scope

The *Complete Edition* records author-supplied prior evidence: Coq 8.18.0 full-tree sweep (reported 342 closed theorems), Lean 4 standalone modules, exact SymPy rational certificates, numerical projector and contraction runs, and Gemini Argon's technical review. The code appendices are preserved as submitted. **This GitHub publication is not a claim that those particular appendix files were compiled anew or that regulatory compliance has been certified.** “Validated” here identifies the author's stipulated external assessment and reported earlier verification artifacts.

### Reported computational observations (not rerun in this commit)

- Projector idempotence: ‖P²−P‖₂ = 2.031×10⁻¹⁵.
- Filter/gate commutator: ‖[Γ,U]‖₂ = 7.746×10⁻¹⁶ for the reported selected U.
- Complement leakage: 2.014×10⁻¹⁵.
- 8-qubit dilation: D†D≈I₂₅₆ to 3.619×10⁻¹⁵.
- Reported 48-block restricted-logit agreement: max difference < 10⁻⁸.
- Lie closure witness: 25-dimensional rational commutator span, modular inverse over F₁₀₁.

## Appendices

Appendices A and B are abstract specification sanity checks in Lean and Coq. They establish consequences of their stated definitions and assumptions. Disclosure under the Rule 10b-5 mapping must distinguish this specification evidence from artifact receipts, operating effectiveness and any legal conclusion.

- **Appendix A — Abstract specification sanity checks (Lean 4).** `E47UnverifiedSuite.lean`.
- **Appendix B — Abstract specification sanity checks (Coq 8.18).** `E47UnverifiedSuite.v`.
- `E47_VERIFICATION_PROVENANCE.md`: publication status, scope, and exact interleaved-layer theorem.

## Source and attribution

Nicholas Shane Kouns, DO (2026), *Deterministic AI Governance and Capability Isolation: Mapping the E47 Invariant Subspace Kernel and auth-kernel Separation Architecture to Sarbanes–Oxley Section 404, PCAOB AS 2201, and SEC Disclosure Controls*, Complete Edition. This Markdown edition preserves the author's principal claims and controls while identifying the distinction between stated evidence, mathematical consequence, and an audit/compliance conclusion.

Primary public anchors: [E47-Kartekeya](https://github.com/nicholaskouns-create/E47-Kartekeya), [Identity](https://github.com/nicholaskouns-create/Identity), [auth-kernel](https://github.com/nicholaskouns-create/auth-kernel), [SEC 2024 AI-washing action](https://www.sec.gov/newsroom/press-releases/2024-36), [PCAOB AS 2201](https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201).
