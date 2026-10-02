# E47 Formalism — Python Rerun, 2026-10-02

162/162 named checks passed: 135 in seven original-script runs and 27 in an independent supplemental reconstruction. Counts are executable checks, not counts of independent theorems. Source assertions also completed without error. Every original script returned exit code 0.

| Original validator | Named checks passed |
|---|---:|
| First-principles spectral core | 19/19 |
| Spectral matrix and contraction | 14/14 |
| Signature and SU(2) × S3 symmetry | 28/28 |
| Noiseless ququint / Heisenberg–Weyl gates | 13/13 |
| Newton–Mean × E47 product and quantum channel | 23/23 |
| Spacetime / exact symbolic curvature | 25/25 |
| Twisted spectral triple | 13/13 |

Repository snapshot: https://github.com/nicholaskouns-create/E47-Kartekeya/tree/7657a6cbc61c89a50767f65278e74a0372c09b42

The five repository scripts were executed unchanged. The spacetime and twisted-triple scripts were extracted from the already retrieved Google Docs, preserving executable code and normalizing line endings. Source hashes and paths are in original_runs.json. Reported counts reflect the scripts actually retrieved, rather than historical counts in document summaries.

## Key measured values

- Kernel dimension 47; complement dimension 78; Ωc = 47/125.
- K² gap 11664; maximum 186624; optimal step 1/99144; complement rate 15/17.
- Spectral matrix: ||Γ^300 − P||₂ = 5.6121665676893966e-14.
- Logical Weyl relation residual: 3.0495823011369447e-15.
- Logical density preservation residual under simulated collective rotation: 4.466330808781477e-15.
- Maximum collective logical-gate commutator: 5.041844500989733e-14.
- Twisted commutator residual: 0; Lorentzian frame residual: 8.942438818975743e-15.
- Spacetime exact sectional curvatures: (1/2, 1/2, −1); scalar curvature 0; covariant divergence [0,0,0].

## Supplemental reconstruction

supplemental_validation.py reconstructs the equations from these Drive sources; it is newly written, not a rerun of an original executable:

- Hodge–E47 Tensor-Kernel Theorem: https://docs.google.com/document/d/1knkNWFEmeW1whs8NJJtPxgHfNlyMpOhEtIlV5aiX9qU/edit
- Higher-Dimensional Newton-Mean Iterations: https://docs.google.com/document/d/1Bcs-gRv3TyoOni8CDxq6d34553BekqN-0r4bun310uk/edit
- Deterministic Hodge–de Rham Swarm Safety Identities: https://docs.google.com/document/d/11jQ7_aeshCrbshWrLBLKqGfzSiKmoWTxQWmJyq7ZDwE/edit

Hodge: 13 checks on an oriented cycle and filled triangle; tensor-kernel ranks 47 and 0, projector and semigroup factorization, and long-time limits. Maximum projector discrepancy 3.60e-11, below declared 1e-9 tolerance.

Newton–Mean: 7 checks, including three exact symbolic identities and 2,000 deterministic random parameter cases. Zero stability-classification disagreements; maximum fixed-point residual 4.99e-13 and Jacobian-spectrum discrepancy 1.29e-11.

Swarm: 7 algebraic witness checks for the stated reserve policy, speed bound, mixing inequality, affine error unrolling, matched-endpoint drift bound, and fallback identities. These check the stated algebra under its assumptions; trajectory-level topology preservation was not simulated.

## Reproduce

Python dependencies: numpy, scipy, sympy (versions in environment.json).

```bash
python -m pip install numpy scipy sympy
python run_originals.py
OPENBLAS_NUM_THREADS=1 python supplemental_validation.py
```

This packet includes finite-dimensional quantum-state and channel simulations. All logs record actual execution during this session. Source files were not changed to obtain a passing result.
