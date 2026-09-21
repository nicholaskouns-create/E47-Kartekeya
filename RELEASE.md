# E47-v1.0 \u2014 The Kartekeya Isolation Lock

Immutable snapshot of the finite E47 kernel lock and the wired engines.

## Canonical title

**The Kartekeya Isolation Lock: Finite Spectral Isolation of E47 = ker((C-6I)(C-30I)) with 29-Unit Intertwiner Algebra A_inv ≅ M5 ⊕ M2 at Ω_c = 47/125.**

## What this release freezes

- Carrier H = V2\u22973, dim = 125
- Kernel K = (C-6I)(C-30I), dim ker K = 47
- Attractor Ω_c = 47/125
- 29-unit intertwiner algebra A_inv ≅ M5 ⊕ M2
- Cartan\u2013Weyl / Chevalley basis of sl(5)\u2295sl(2) on those units
- Gestalt invariant lock (89/89)
- Wired Eidolon sector ODE, tomographic visualizer, density topography app
- Scholarly surface: CITATION.cff, codemeta.json, /cite/ JSON-LD, sitemap

## How to run the lock

```bash
python3 research/e47/validation/e47_gestalt_invariants.py
python3 research/e47/validation/intertwiners.py
python3 research/e47/validation/chevalley.py
python3 research/e47/validation/spectral_engine.py
python3 tests/test_e47_intertwiners.py
python3 tests/test_e47_chevalley.py
python3 scripts/run_e47_stack.py
```

## Immutability

- Branch: `release/E47-v1.0`
- Tag: `E47-v1.0`
- Repository rulesets block deletion and force-push on both the release branch and the E47-v1.0 tag.
- Later work continues on `main`. It does not rewrite this snapshot.

## Cite

Use `CITATION.cff` or the public page
https://nicholaskouns-create.github.io/E47-Kartekeya/cite/
