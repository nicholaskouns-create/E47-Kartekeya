# E₄₇ transport–gradient: compilation and numerical validation receipt

Date: 2026-11-20.

## GitHub Actions compile
- Workflow: https://github.com/nicholaskouns-create/Identity/actions/runs/44822476703
- Run status: **completed / success**.
- Lean 4.35.0 installation: PASS.
- Lean source: `formal/e47/E47TransportGradient.lean`, compile: PASS (6 closed statements: closed arithmetic and two integer witnesses).
- Coq source: `formal/e47/E47TransportGradient.v`, compile: PASS (6 closed statements: dimension arithmetic and symbolic two-mode transport/gradient identities).
- Coq `Print Assumptions` recorded **standard Reals-library axioms**, including `ClassicalDedekindReals.sig_forall_dec`. No new project-specific axiom was introduced in this module. Not an axiom-free Real-number proof.
- Python `research/e47_transport_gradient.py` execution: PASS.
- CI downloadable artifact: https://github.com/nicholaskouns-create/Identity/actions/runs/44822476703/artifacts ; name `e47-transport-gradient-proof-receipts`, artifact ID 14670753716, logs and Python results.

## Independent local NumPy/SciPy rerun
- dim E₄₇: 47.
- λ_min(QᵀLQ) = 1.757179786610739.
- λ_max(QᵀLQ) = 10.7263296601493.
- ‖A + Aᵀ‖F = 6.4880873043417734e-15.
- ‖P² − P‖F = 2.3722984945692305e-14.
- max tested energy-identity residual = 6.661338147750939e-16.
- max tested complement leakage = 1.644951430595996e-15.
- max Re(spec(G)) = -0.4223874437860444.

## Independent 7-qubit-equivalent statevector dilation
- Model: Halmos unitary dilation of a 64x64 contraction built by embedding a 47x47 dissipative step in 64 states; one additional ancilla qubit makes 128 total states.
- dt=0.1, γ=0.2; no hardware or gate-level compilation.
- ‖UᵀU−I₁₂₈‖F = 1.4100122273101503e-13.
- Successful branch error = 1.072060511650706e-16.
- Idle 17-state sector leakage = 0.
- Probability success = 0.7962582917251668; probability failure = 0.20374170827483548; sum ≈ 1.
- Reproducible script: `research/e47_quantum_dilation_check.py`.
- Saved numerical receipt: `research/e47_quantum_dilation_results_2026-11-20.json`.

## Evidence boundary
The Lean and Coq modules prove a **two-mode scalar-algebra reduction**, not the complete construction and spectral properties of the concrete 47x47 Casimir-compressed operator. The latter is proven analytically in the accompanying exposition and numerically inspected with Python. A full matrix-level Lean/Coq formalization remains open.

The website-hosted browser proof page was examined in source, but was not executed in a local interactive browser session. The actual formal compiler execution was GitHub Actions, not the browser UI.
