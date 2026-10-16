# E47 Symmetry-Selected Quantum Information Validation

This package records the October 16, 2026 PyTorch validation pass for the E47 spectral-projector construction and two illustrative noise studies.

## Formal core

\[
H=V_2^{\otimes 3},\quad \dim H=125,
\]
\[
C=J_{\rm tot}^2,\qquad K=(C-6I)(C-30I),
\]
\[
E_{47}=\ker K=E_6\oplus E_{30},\qquad \dim E_{47}=47,
\]
\[
\Gamma_*=I-K^2/99144,\qquad \|\Gamma_*^n-P_{47}\|_2=(15/17)^n.
\]

## Files

- `e47_torch.py` — finite-dimensional construction and projector checks.
- `e47_noise_experiment.py` — collective-vs-local random-unitary dephasing experiment.
- `e47_logical_benchmark.py` — logical-qubit benchmark with an unencoded control.
- `e47_logical_benchmark_results.json` — selected numerical results, environment and source hashes.

## Evidence boundary

The exact finite-dimensional algebra and projector identities are E0-style mathematical statements. The PyTorch runs are E1 numerical validations of those statements and of the specified channel models. The observed protection under collective dephasing is a symmetry-protection result for that model only. It is **not** universal quantum error correction, experimental validation, a hardware demonstration, or evidence that E47 outperforms established error-correcting codes under realistic device noise.

No canonical-status or evidence-class promotion is implied by this repository update.
