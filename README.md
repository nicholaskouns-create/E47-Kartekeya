# E47-Kartekeya

E47 Recursive Intelligence Code

[![CI](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml)

## Overview

This repository validates the finite-dimensional algebraic construction of the
E47 spectral kernel on V₂⊗V₂⊗V₂.

## Installation

Install the published package from PyPI:

```bash
pip install e47-kartekeya
```

The distribution name is `e47-kartekeya`, and the import package is `e47`.

To work from a local checkout instead:

```bash
pip install -e .
```

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

## Spectral kernel compilation

```bash
python scripts/compile_spectral_kernel.py --spin 2 --copies 3 --select 2 5
```

Outputs:

- `artifacts/spectral_kernel_certificate.json`
- `artifacts/spectral_kernel_passport.md`

## Documentation

- [`docs/provenance.md`](docs/provenance.md) — Canonical implementation chain and reproducibility record
- [`docs/validation_scope.md`](docs/validation_scope.md) — What is and is not validated
- [`docs/maintenance_policy.md`](docs/maintenance_policy.md) — Automated and manual maintenance procedures

## Package publishing

Publishing is handled by `.github/workflows/publish.yml`.

- Create a GitHub release to build and publish `e47-kartekeya` to PyPI
- Configure PyPI trusted publishing for this repository before the first release
