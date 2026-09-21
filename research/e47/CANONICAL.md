# The Kartekeya Isolation Lock

**Canonical title.** The Kartekeya Isolation Lock: Finite Spectral Isolation of E47 = ker((C-6I)(C-30I)) with 29-Unit Intertwiner Algebra A_inv ≅ M5 ⊕ M2 at Ω_c = 47/125.

**Version.** E47-v1.0
**Date.** 2026-09-21
**Immutable branch.** `release/E47-v1.0`
**Tag.** `E47-v1.0`

This plate names the locked object. It does not reopen the derivation.

## Locked objects

| Symbol | Statement |
|---|---|
| Carrier | H = V2^{\otimes 3}, dim H = 125 |
| Pencil | K = (C-6I)(C-30I) |
| Kernel | E47 = ker K = E6 \u2295 E30, dim = 47 |
| Attractor | \u03a9_c = 47/125 = 0.376 |
| Projector | P47 Lagrange interpolant on spec(C), Tr(P47) = 47 |
| Reduced algebras | A47 ≅ M47(C), A_C ≅ M25 \u2295 M22, A_inv ≅ M5 \u2295 M2 |
| Intertwiners | 29 matrix units spanning A_inv |
| Chevalley | sl(5)\u2295sl(2) on those units |
| Dynamics | \u03c1\u0307 = -K^{2}\u03c1, gap \u0394 = 11664, stiffness \u03ba = 16 |

## Executable witnesses

- `research/e47/validation/e47_gestalt_invariants.py` \u2014 89/89
- `src/e47/intertwiners.py` \u2014 29 units
- `src/e47/chevalley.py` \u2014 16/16
- `src/eidolon/eidolon_engine.py` \u2014 7-sector ODE
- `research/e47/validation/tomographic_visualizer.py`
- `research/e47/validation/density_app.py`
- `research/e47/validation/spectral_engine.py`

## Citation

See `CITATION.cff`, `codemeta.json`, and the public surface
https://nicholaskouns-create.github.io/E47-Kartekeya/cite/.
