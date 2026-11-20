# KKP-R E₄₇ Certainty–Reset Invariant: Verified CI Receipt

**Date:** 2026-11-20

**Successful run:** https://github.com/nicholaskouns-create/Identity/actions/runs/44824529692

- Status: completed / **success**
- Lean: **PASS**, version 4.35.0, file `formal/e47/KKPRCertaintyCycle.lean`.
- Coq: **PASS**, version 8.18.0, file `formal/e47/KKPRCertaintyCycle.v`.
- Coq `Print Assumptions`: **“Closed under the global context”** for `cycle_invariant`, `cycle_certified`, and `full_cycle_repeated_invariant` (no added axioms).
- Python: **PASS**, file `research/kkpr_certainty_cycle.py`.
- Downloadable workflow artifact `kkpr-certainty-cycle-lean-coq-python`, ID 14673187425; generated source files and numerical JSON archived in GitHub Actions.

**Numerical results, CI machine (NumPy/SciPy):**
- 25 trials × 20 recursive cycles = 500 outputs.
- 484 gate accepts; 16 gate resets.
- Max E₄₇ complement leakage ≈ 2.8348080481059137×10⁻¹⁶.
- Max reset mismatch = 0.
- Output energy satisfies selected threshold 0.5, baseline energy ≈0.1.

**Exact formal theorem scope:** Given an embedding `q` and projection `P` satisfying `P(q(y))=q(y)`, and a Nat-valued certificate/gate with a certified fallback, the complete six-stage map lands in the image of `q` after one step and every positive iterate. Gate soundness and fallback score soundness are separately proved.

**Evidence boundary:** Lean and Coq prove an abstract behavior theorem using integer-coordinate 125/47-dimensional types. They **do not** build a real 125×125 Casimir matrix, verify the actual real quadratic score `yᵀBy`, or prove an implementation-refinement theorem between abstract Nat certificate and Python floating-point gate. Those are separate tasks. The Python numerical test instantiates the Casimir projector and real gradient-energy score.

The earlier CI run 44824313282 failed because Coq could not infer untyped stage parameters in one theorem statement. That source elaboration error was corrected, and the succeeding run 44824529692 is the basis for this receipt.
