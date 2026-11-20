# E47 reproducibility packet

Run `./reproduce.sh` from this directory. It fetches the pinned Git source, creates a temporary Python environment with pinned dependencies, and executes three validators. Git, Python 3.12 with venv, network access, and a compatible NumPy wheel are required. The supplied log records a fresh run.

| Claim | Evidence to inspect |
| --- | --- |
| On the 125-dimensional carrier, the polynomial K = (C − 6I)(C − 30I) has rank 78 and nullity 47 | Exact census and exact-rational Tower validator |
| The selected sectors at eigenvalues 6 and 30 have dimensions 25 and 22 | Casimir census and Tower validator |
| The native projector is self-adjoint in the physical metric | Exact witness checks PᵀG = GP |
| The rank-43 Grassmann map A has nullity 82 and its constrained intersection with E equals ker K | The witness checks the two restricted blocks, including the off-sector injectivity condition |
| The scaled concrete projector is idempotent, annihilated by K, and has trace 47 × 1814400 | Identity's Lean concrete matrix certificate and successful CI run 44105525416 |
| Hardware protection and measured predictive effects | Require application-specific experimental evidence |

## Worked example

Start with the corrected Grassmann–Casimir formalism in the pinned E47-Kartekeya tree at `research/e47/E47_Grassmann_Casimir_Formalism_Corrected_20261008.md`. Follow `e47_grassmann_casimir_witness_20261008.py` from the construction of the exact Casimir and its metric through construction of the Grassmann constraint map. Check the selector rank, then the constraint-map rank, then the restriction checks. The two nullities refer to different maps. The restriction checks provide the intersection witness.

The Python validators use exact arithmetic for the rank and restriction statements. The Lean certificate uses native decision for finite matrix computations as recorded in the source's axiom report. Its concrete equalities imply the dimension statement over the rationals by scaling to an idempotent and applying rank equals trace.
