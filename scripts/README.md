# Command directory

[Repository home](../README.md) · [Reproducibility](../docs/reproducibility.md)

Run these existing commands from the repository root. Python commands use the installed research environment; JavaScript commands require Node.js 22+.

| Task | Command |
|---|---|
| Python suite | `python -m pytest tests/ -v` |
| Check component paths and labels | `python scripts/check_lab_contract.py` |
| Check instrument versions and contracts | `python scripts/check_instrument_contracts.py` |
| Regenerate E47 certificate | `python scripts/generate_validation_certificate.py` |
| Compile spectral certificate and passport | `python scripts/compile_spectral_kernel.py --spin 2 --copies 3 --select 2 5` |
| Website and E47 bridge | `node --test scripts/check_website.cjs scripts/check_e47_bridge.cjs scripts/check_eidolon_receipt_binding.mjs` |
| CITY 125 runtime | `node --test scripts/check_city_125_runtime.mjs` |
| Matrix/CITY 125/AETHERIS integration | `node --test scripts/check_matrix_city125_aetheris.mjs` |
| Matrix MPS worker | `node --test scripts/check_matrix_mps_worker.mjs` |
| Existing external-worker bindings | `node scripts/external_agents_smoke.mjs` |

Each major instrument also declares its own smoke entry point in `component.json`. See [instrument contracts](../docs/instrument_contracts.md) for individual commands and the existing optional batch runner.

For certificate-bound flight records, use the [EIDOLON NDJSON guide](../docs/eidolon_flight_replay_ndjson.md).

Generated outputs normally go to `artifacts/`. Committed snapshots live in [certificates/](../certificates/README.md), and issued replay logs live in [trajectories/](../trajectories/README.md).
