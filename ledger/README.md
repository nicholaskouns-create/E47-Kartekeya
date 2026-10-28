# KKP-E47 Failure Ledger

A machine-readable record of every claim in this corpus that was tested and failed, corrected,
superseded, or blocked — alongside the results that still stand.

> A claim's epistemic type is part of the claim. A failure is a record, not an erasure.

## Why this exists

A research programme that only publishes what worked cannot be audited. This ledger is the
other half: 42 records, each typed by evidence class, each carrying either the correction
that replaced it or the obstruction that stops it.

Eighteen were found by the author's own audits, several against the corpus's signature
constant. The rest came from external review. Both are recorded the same way.

## Files

| file | what it is |
|---|---|
| `FAILURE_LEDGER.json` | the data — one record per claim, typed and stated |
| `FAILURE_LEDGER.md` | rendered table, for reading |
| `validate_ledger.py` | stdlib-only validator; exits non-zero on any malformed record |
| `ledger.yml` | GitHub Actions workflow — put in `.github/workflows/` |

## The invariant the validator enforces

- every entry is typed `E0` / `E1` / `P` / `C`
- every `CORRECTED` or `SUPERSEDED` entry carries the value that replaced it
- every `FALSIFIED` entry carries the test that killed it
- every `BLOCKED` entry names its obstruction

A ledger that cannot say *how* a claim died is not a ledger.

## Run

```sh
python3 -I validate_ledger.py FAILURE_LEDGER.json
```
