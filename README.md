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
- [`docs/skills-and-agents.md`](docs/skills-and-agents.md) — Copilot skills, agents, and platform interconnect

## Copilot skills (quick invoke)

| Command | Use |
|---|---|
| `/chronicle tips` | Personalized session-history tips |
| `/fix-ci` | Repair failing GitHub Actions |
| `/validate-invariants` | Run tests + frozen invariant checks |
| `/regenerate-certificate` | Refresh validation certificates |
| `/platform-interconnect status` | Audit skills/agents/setup surface |

## Project website

A static project site lives in [`website/`](website/) and presents the E47 construction,
canonical invariants, validation pipeline, package API, and documentation links.

```bash
# Serve locally
python -m http.server 8000 --directory website
# then open http://127.0.0.1:8000/
```

Run the website checks with Node.js 22 or newer:

```bash
node --test scripts/check_website.cjs
```

These checks cover local assets and links, certificate rendering (including
unavailable data), and equality between the JSON snapshots in `website/data/`
and `certificates/`. When updating either source snapshot, refresh its website
copy in the same change. The site displays committed snapshots; it does not
run the Python validators in the browser.

GitHub Pages deployment is handled by [`.github/workflows/pages.yml`](.github/workflows/pages.yml)
on relevant pushes to `main`, or by manually running **Deploy website** on `main`.
Pull requests run **Validate website** without deploying. Deployment runs only
after the website checks pass.

**Before the first deployment**, enable **Settings → Pages → Source: GitHub Actions**
if it is not already configured. After merging, check the **Deploy GitHub Pages**
job; if Pages was enabled after a failed run, rerun the workflow on `main`.
The published URL after a successful deployment will be:

`https://nicholaskouns-create.github.io/E47-Kartekeya/`

## Package publishing

Publishing is handled by `.github/workflows/publish.yml`.

- Create a GitHub release to build and publish `e47-kartekeya` to PyPI
- Configure PyPI trusted publishing for this repository before the first release
