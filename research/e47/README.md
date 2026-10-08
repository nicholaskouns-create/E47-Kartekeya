# E47 Research Notes

This directory holds theorem plates, exact notes, and open proof obligations adjacent to the executable `src/e47/` implementation.

## Current notes

- [Grassmann–Casimir compatibility and spectral stabilization](E47_Grassmann_Casimir_Proof.md) — explicit 90/82 intersection and rank-47 Casimir core; 34/34 exact checks. [Python](validation/e47_grassmann_validation.py) · [machine record](../../artifacts/e47_grassmann_validation.json) · [web proof](https://nicholaskouns-create.github.io/E47-Kartekeya/notes/e47-grassmann-casimir/)

- [E47 45-check harness correction](E47_45_Check_Harness_Correction_20260930.md) — preserves two first-run harness failures and their exact repairs: operator 2-norm contraction, exact Pell √5 identity, Lagrange denominators, 47/1/10 kernel separation, 8√3 twist defect, and the explicit finite-search E1 boundary; [machine record](../../certificates/MC-E47-HARNESS-CORRECTION-20260930-001.json)
- [E47 exact spectral core](E47_Core_Spectral_Certificate.md)
- [E47 Prism Spectral Formalism](E47_Prism_Spectral_Formalism.md) — seven-band Casimir decomposition, THE MATRIX typed lift, and E1 parity receipt
- [E47 × KKP-RADAR spectral operator bridge](E47_KKP_RADAR_Spectral_Operator_Bridge.md) — explicit 5×5×5 complex I/Q → C^125 carrier map, seven-shell Casimir observables, isotropic-null 47/125 identity, and synthetic E1 benchmark; [validator](validation/e47_radar_bridge_validator.py) · [certificate](../../certificates/MC-E47-RADAR-BRIDGE-20260927-001.json) · [live proof](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-radar-bridge/)
- [Projection flow theorem](E47_Projection_Flow_Theorem.md)
- [Convergence + noiseless multiplicity validator](validation/e47_convergence_noiseless_validator.py) — uniform operator-norm threshold first passes at n=270 and explicitly factorizes the E47 multiplicity spaces `C^5` and `C^2` as noiseless subsystems for collective SU(2); [certificate](../../certificates/MC-E47-CONVERGENCE-NOISELESS-20260928-001.json)
- [E47 condition lock](E47_Condition_Lock_Theorem.md) — condition-4 lock, equioscillation optimality of 15/17, five-factor exact projector, five-step termination, Chebyshev rate 3/5 (25/25 PASS)
- [E47 signature and symmetry](E47_Signature_Symmetry_Theorem.md) — exact SU(2)×S₃ resolution, fermion exclusion, bosonic slice V₂, 42-dim mixed core, K inertia (23,55,47), Krein form and its isometries (28/28 PASS)
- [E47 Casimir census](E47_Casimir_Census_Theorem.md) — census (1,3,5,4,3,2,1), selector rule, E47 as the unique quadratic selector of dimension 47 (12/12 PASS)
- [Profile-injection lemma](E47_Profile_Injection_Lemma.md) — vacuum plane-wave family for any n; injective for odd n, parity obstruction for even n; conditional on one imported fact (9/9 PASS)
- [Evidence monotonicity](Evidence_Monotonicity.md) — how evidence classes and assumptions propagate; enforced over an 18-claim [ledger](evidence_ledger.json)
- [Cross-plate validation](validation/e47_extracted_invariants_validation.py) — 47/47 exact and NumPy checks across the supplied E47 plates; [receipt](../../artifacts/E47_EXTRACTED_INVARIANTS_CERTIFICATE.json) records image-derived observations and separate unvalidated claims.
- [Linearized Einstein intertwiner candidate](E47_Linearized_Einstein_Intertwiner_Theorem.md)
- [Gauge-inequivalent Einstein conditional construction](E47_Gauge_Inequivalent_Einstein_Conditional_Construction.md)
- [Einstein full executable closure certificate](E47_Einstein_Full_Executable_Closure_Certificate.md)
- [E47 intrinsic Lorentzian spacetime and unmarked Einstein-moduli embedding](E47_Intrinsic_Lorentzian_Unmarked_Proof.md)
- [E47 Casimir-spectral Lorentzian signature](E47_Casimir_Spectral_Lorentzian_Signature.md) — `eta=P6-P0`, explicit 125D pullback, 12/12 machine PASS
- [E47 Prima-Facie Spacetime Closure — 26/26 Casimir pullback](E47_Prima_Facie_Spacetime_Closure_26.md) — metric derived as `B4†(P6-P0)B4`
- [Proof obligation ledger: nontrivial Einstein sector](NEXT_PROOF_OBLIGATION_Nontrivial_Einstein_Sector.md)

## Relationship to executable code

The canonical finite-dimensional implementation remains `src/e47/`.

These documents can state mathematical constructions, candidates, or open obligations. Their status is determined by their own evidence record and the repository validation scope, not by their location in this directory.
