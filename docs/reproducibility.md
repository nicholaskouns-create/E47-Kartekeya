# Reproducibility

This document is the shortest path from a clean checkout to an inspectable E47 research environment.

## Python environment

Python 3.12 is the package baseline.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e . -r requirements.txt -r requirements-dev.txt
```

Run the complete Python test suite:

```bash
python -m pytest tests/ -v
```

## Canonical certificate

Regenerate the aggregate E47 certificate:

```bash
python scripts/generate_validation_certificate.py
```

Compile the spectral-kernel certificate and passport:

```bash
python scripts/compile_spectral_kernel.py --spin 2 --copies 3 --select 2 5
```

Generated artifacts are derivative outputs. Source, tests, and commit history remain the implementation record.

## Repository contract

Validate the machine-readable lab structure:

```bash
python scripts/check_lab_contract.py
```

This checks that the canonical web root, package root, declared components, maturity labels, and evidence classes are internally consistent.

## Browser and website checks

Node.js 22 or newer:

```bash
node --test \
  scripts/check_website.cjs \
  scripts/check_e47_bridge.cjs \
  scripts/check_eidolon_receipt_binding.mjs
```

Serve the public surface locally:

```bash
python -m http.server 8000 --directory website
```

Then open `http://127.0.0.1:8000/`.

## Interpretation

A passing test means the tested contract is reproduced.

It does not automatically promote:

- simulation to experiment,
- numerical agreement to theorem,
- a browser demonstration to hardware evidence,
- a component's local success to a claim about every other component.

The applicable evidence class is declared separately in `lab-manifest.json` and the corresponding validation record.

## EIDOLON E2 flight-replay NDJSON

The replay certificate is `artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json`.
The bound log URI is `trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson`.

Commit contract and git commands: [`docs/eidolon_flight_replay_ndjson.md`](eidolon_flight_replay_ndjson.md).

```bash
python scripts/check_eidolon_replay_ndjson.py \
  --cert artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json \
  --ndjson trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
```

The checker prints the `git add` / `git commit` / `git push` commands only on PASS.
It does not promote the replay above E2.

## Instrument smoke receipts

Validate every major lab's local component contract:

```bash
python scripts/check_instrument_contracts.py
```

Run each instrument through its own smoke entrypoint and retain normalized provenance receipts:

```bash
python scripts/run_instrument_smokes.py
```

For timed benchmark mode:

```bash
python scripts/run_instrument_smokes.py --benchmark \
  --receipt-dir artifacts/instrument-benchmarks
```

See `docs/instrument_contracts.md` for the receipt and failure telemetry schemas.
