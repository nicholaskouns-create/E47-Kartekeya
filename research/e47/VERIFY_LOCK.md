# Verify the lock

From the repository root:

```bash
python3 research/e47/validation/spectral_engine.py
```

Required line:

```text
[LOCK] PASS  dimH=125  dimE47=47  rankK=78  Omega_c=47/125  Delta=11664  kappa=16  rho=15/17  TrP47=47
```

That file is the engine. `research/python-inventory/` copies are archives. Electroweak ratios and Foundry lifetime algebra are instruments; they import this lock and do not redefine it. Evidence classes stay as in [docs/validation_scope.md](../../docs/validation_scope.md): E0 algebra, E1 reconstruction, E2 simulation, E3 observation, E4 hardware.
