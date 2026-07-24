# E47-Kartekeya

E47 Recursive Intelligence Code

[![CI](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml)

## Overview

This repository validates the finite-dimensional algebraic construction of the
E47 spectral kernel on V₂⊗V₂⊗V₂.

### Canonical invariants

| Invariant | Value |
|---|---|
| `dim(V)` | `125` |
| `dim(E₄₇)` | `47` |
| Coherence fraction | `47 / 125` |
| K² spectral gap | `11664` |
| K² max eigenvalue | `186624` |

## Quick start

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

## Certificate regeneration

```bash
python scripts/generate_validation_certificate.py
```

Output: `artifacts/e47_validation_certificate.json`

## Documentation

- [`docs/provenance.md`](docs/provenance.md) — Canonical implementation chain and reproducibility record
- [`docs/validation_scope.md`](docs/validation_scope.md) — What is and is not validated
- [`docs/maintenance_policy.md`](docs/maintenance_policy.md) — Automated and manual maintenance procedures
