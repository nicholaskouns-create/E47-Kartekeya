# Evidence Monotonicity

**Ledger:** [`evidence_ledger.json`](evidence_ledger.json) · 18 claims
**Checker:** [`scripts/check_evidence_ledger.py`](../../scripts/check_evidence_ledger.py) (run by `tests/test_evidence_ledger.py`)

The repository types evidence as E0 exact proof, E1 executable reconstruction, E2 simulation, E3 external benchmark, E4 experiment and H0 hardware ([validation scope](../../docs/validation_scope.md)). This note states the rule for how those classes combine when one claim depends on another. The ledger applies it to the claims of the condition-lock, signature-symmetry, Casimir-census and profile-injection certificates, and to the unmarked Einstein-moduli claim.

## Rule

1. **Mathematical chain.** E0 > E1 > E2. A claim may not be stronger on this chain than any claim it depends on. For example, a statement built on a float64 check is at most E1.
2. **Empirical classes.** E3, E4 and H0 measure contact with the world, not strength of derivation, so they are not ranked against the chain. A claim carries every empirical class that any of its dependencies carries.
3. **Assumptions.** A claim carries every assumption its dependencies are conditional on. Every assumption must be declared, with its source, in the ledger.
4. **Structure.** Every dependency exists, and the dependency graph is acyclic.
5. **Records.** Every claim names a committed certificate record, and a check in it that is true.

The checker enforces all five. Its tests confirm that each kind of violation is rejected.

## What the ledger records

- **E1 claims:** five-step termination and the Krein isometries of SU(2) rotations are checked numerically, so they are recorded as E1, even though exact proofs exist.
- **Conditional claims:**
  - The unmarked Einstein-moduli embedding depends on the profile-injection lemma, which is conditional on an imported fact about plane-wave isometries. Rule 3 makes the embedding conditional too.
  - The intrinsic-spacetime certificate states the embedding without that condition. The ledger is where the condition becomes explicit.

## Boundary

The rule does not change the evidence classes or the lab contract. It describes how existing classes propagate, and it is enforced only for claims entered in the ledger.
