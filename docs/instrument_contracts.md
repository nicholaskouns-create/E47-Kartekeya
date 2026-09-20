# Instrument Contracts and Telemetry

Each major research instrument owns a compact local contract.

The shared layer standardizes **observability**, not scientific authority. A component remains independently addressable and keeps its own evidence boundary.

## Local files

Every major instrument carries:

- `component.json` — identity, version, maturity, evidence classes, entrypoint, smoke/benchmark commands, provenance sources, failure schema, and boundaries
- `VERSION` — plain semantic version string
- `smoke.py` or `smoke.mjs` — independent operational entrypoint

Current components:

| Component | Version | Smoke entrypoint |
|---|---:|---|
| E47 core | 0.1.0 | `python -m e47.smoke` |
| AETHERIS | 0.1.0 | `python -m aetheris.smoke` |
| MANTA Python model | 0.1.0 | `python -m manta.smoke` |
| MANTA flight interface | 1.0.0 | `node website/interfaces/manta/smoke.mjs` |
| SKYRMION Runtime 2 | 2.3.0 | `node website/interfaces/skyrmion/smoke.mjs` |
| Syntax Jacob | 1.2.0 | `node website/interfaces/syntax-jacob/smoke.mjs` |
| CITY CORE | 0.1.0 | `node website/interfaces/kouns-core/smoke.mjs` |
| Visualizer Portal | 0.1.0 | `node website/interfaces/visualizers/smoke.mjs` |

Python commands assume the repository environment has been installed with `pip install -e .` or that `PYTHONPATH=src`.

The MANTA flight command inspects the source and interface contract and emits the existing shared receipt format. It does not run a browser or certify rendered flight behavior.

## Provenance receipt

Every smoke/benchmark entrypoint emits one JSON object using:

`CITY-INSTRUMENT-RECEIPT/1.0`

The receipt records:

- component ID and version
- smoke vs benchmark mode
- PASS / FAIL status
- UTC timestamp
- elapsed runtime
- Git commit SHA when available
- SHA-256 of the local component contract
- runtime environment
- named checks
- quantitative metrics
- standardized failure telemetry when present

The receipt therefore binds a result to **code revision + component contract + runtime environment**.

## Failure telemetry

Failures use:

`CITY-INSTRUMENT-FAILURE/1.0`

The minimum fields are:

- component ID
- component version
- failure phase
- error type
- message
- recoverability flag
- structured context

Browser instruments additionally install `website/interfaces/shared/instrument-telemetry.js`, which catches uncaught errors and unhandled promise rejections locally and emits a `city:instrument-failure` event. The helper does not transmit telemetry to a remote service.

## Run all smoke tests

```bash
python scripts/check_instrument_contracts.py
python scripts/run_instrument_smokes.py
```

Receipts are written to:

```text
artifacts/instrument-receipts/
```

CI uploads this directory as the `instrument-smoke-receipts` workflow artifact even when a smoke entrypoint fails.

## Run benchmarks

For an individual instrument, use the `benchmark_command` in its `component.json`.

Run the full benchmark set locally:

```bash
python scripts/run_instrument_smokes.py --benchmark \
  --receipt-dir artifacts/instrument-benchmarks
```

GitHub Actions also exposes a manual **Instrument Benchmarks** workflow. Benchmark receipts are uploaded as an artifact and are not merge gates.

## Schemas

- `contracts/instrument-contract.schema.json`
- `contracts/provenance-receipt.schema.json`
- `contracts/failure-telemetry.schema.json`

## Design rule

A component contract describes what an instrument promises to expose and how to inspect it.

It does not decide whether the instrument's scientific model is true, nor does it promote simulation evidence into empirical evidence.
