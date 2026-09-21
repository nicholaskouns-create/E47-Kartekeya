# E47 validation Python (gestalt lock)

Run from repo root:

```bash
python3 research/e47/validation/e47_gestalt_invariants.py
python3 research/e47/validation/intertwiners.py
python3 research/e47/validation/chevalley.py
python3 research/e47/validation/spectral_engine.py
python3 tests/test_e47_intertwiners.py
python3 tests/test_e47_chevalley.py
```

Locked objects:

- `H = V2⊗3`, dim 125
- `K = (C-6I)(C-30I)`, `ker K = E47`, dim 47
- `Ω_c = 47/125`
- `A_inv ≅ M5 ⊕ M2`, 29 units
- Chevalley `sl(5)⊕sl(2)` on those units
