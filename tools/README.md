# tools/

## `e47_outdir.py` — where generated evidence goes

Validation scripts resolve their output path through `resolve_out(filename)` or
`resolve_out_dir()`. The default is **outside the repository**, so a plain run
can never overwrite the committed certificate it is meant to be checked
against, and never leaves the working tree dirty.

Precedence, highest first:

| source | form | use |
|---|---|---|
| `--out FILE` | file path | one named destination |
| `--out-dir DIR` | directory | several files, or deliberate regeneration |
| `E47_CERT_OUT` | file path | what the test suite sets |
| `E47_OUT_DIR` | directory | pin a whole run |
| *(default)* | `<tempdir>/e47-out` | ordinary run |

The resolved path is announced on **stderr** (`[e47-out] …`), so stdout stays
clean for the certificate JSON.

```bash
# ordinary run — writes to <tempdir>/e47-out, repo untouched
python3 research/e47/validation/e47_condition_lock_certificate.py

# pin a whole suite
E47_OUT_DIR=~/e47-run-20261026 python3 -m pytest tests/

# deliberately regenerate committed evidence
python3 research/e47/validation/e47_condition_lock_certificate.py \
    --out-dir artifacts
```

### Routed through the resolver

- `research/e47/validation/e47_condition_lock_certificate.py`
- `research/e47/validation/e47_einstein_full_closure_certificate.py`
- `research/e47/validation/e47_extracted_invariants_validation.py`
- `research/e47/validation/e47_signature_symmetry_certificate.py`
- `research/e47/validation-rerun-20261002/supplemental_validation.py`

Other scripts still emit beside themselves; `.gitignore` covers the paths they
are known to touch. Route a script here when you next edit it.

## Certificates are not byte-reproducible

The committed JSONs embed raw float residuals, so regenerating one on
different hardware or a different BLAS produces a diff even when the
mathematics is unchanged. A round trip against `HEAD` on 2026-10-26 gave:

| certificate | leaves | differing residuals (all < 1e-9) | substantive |
|---|---|---|---|
| `E47_CONDITION_LOCK` | 86 | 1 | 0 |
| `E47_EINSTEIN_FULL_CLOSURE` | 87 | 13 | 1 |
| `E47_EXTRACTED_INVARIANTS` | 96 | 2 | 2 |
| `E47_SIGNATURE_SYMMETRY` | 90 | 4 | 0 |

The key set, every `PASS` verdict and every exact rational field were
identical. The three "substantive" entries were noise around exact values —
`product_kernel.gap` moved from `0.5857864375298685` to `0.5857864375762728`
against a true `2 − √2 = 0.58578643762690…`, so the fresh value is the more
accurate one, and two `s3_dimensions` entries moved between `5.000000000000001`
and `5.0`.

So compare certificates on their verdicts and their exact fields, not with
`diff`. A byte comparison will report a change that is not one.
