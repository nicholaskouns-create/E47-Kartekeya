# E47-style projection in temporal graph link prediction

**Status:** research integration and reproducibility scaffold. The two benchmark results below are **user-reported**, not reproduced by this commit. Neither experiment uses the official TGBL datasets or published A2QTGN code.

## Architecture

Given node representations H in R^(N x d), select a rank-k orthonormal basis Q in R^(d x k), with Q^T Q = I. Apply P = QQ^T and H_protected = HP before the link predictor. Choose k = floor(d * 47/125). **The projector acts on the representation feature dimension d**, not the number of graph nodes, unless those dimensions happen to coincide.

This is a **random occupancy-matched analogue** of E47, not the Casimir-derived spectral projector P6 + P30 on V2^(tensor 3). The exact E47 formalism uses C = J_tot^2, K = (C-6I)(C-30I), dim ker K = 47, and Gamma = I-K^2/99144. A separate equivariant representation map is needed to use the exact 125-dimensional projector in a learned embedding space.

## Reported experiments (not independently verified here)

| Condition | Baseline AUC | Projected AUC | Delta AUC | Baseline approximate MRR | Projected approximate MRR |
|---|---:|---:|---:|---:|---:|
| Synthetic dynamic graph, N=64, T=20, F=128, 40 epochs | 0.9896 | 1.0000 | +0.0104 | n/a | n/a |
| Scale-matched TGBL-style synthetic graph, N=4000, 80000 edges, F=64, 5000 test edges and 20 negatives/positive | 0.5082 | 0.5072 | -0.0010 from displayed rounded scores | 0.5076 | 0.5138 |

The second experiment was described as delta AUC -0.0009; displayed four-decimal AUC values subtract to -0.0010, presumably due to rounding. Do not infer significance, non-inferiority, or universal no-degradation from one run. The second result is near chance AUC; approximate MRR depends on ranking and negative-sampling definitions.

## Code and evidence

- [projection.py](projection.py): deterministic fixed orthogonal projection, NumPy only.
- [test_projection.py](test_projection.py): mathematical property tests, not model benchmark replication.
- [RESULTS.json](RESULTS.json): machine-readable *reported* observations and provenance boundaries.

Run: `python -m unittest discover -s temporal-graph-learning -p 'test_*.py'`

## Verification roadmap

1. Obtain official TGBL datasets, code and temporal train/validation/test splits; record versions and checksums.
2. Fix negative sampling and ranking metric definitions, including MRR versus approximate MRR.
3. Compare no projection, random fixed rank-k projection, learned rank-k projection, and an explicitly mapped Casimir projector at matched rank and parameter budget.
4. Repeat across seeds, graph regimes and leakage-safe chronological splits; publish raw predictions, uncertainty intervals and resource costs.
5. Only then attribute any improvement specifically to E47 structure.

See also [Time](https://github.com/nicholaskouns-create/Time) for the clock/TQGNN engine and [tower](https://github.com/nicholaskouns-create/tower) for Fibonacci–Lucas extension. Neither is silently duplicated here.
