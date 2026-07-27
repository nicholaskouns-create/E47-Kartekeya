# E47-Kartekeya Maintenance Policy

## Overview

This document describes the automated and manual maintenance procedures for the
`nicholaskouns-create/E47-Kartekeya` repository.

The mathematical definitions and validated constants in `src/e47/` are frozen.
Maintenance activities may only change tooling, documentation, certificates, and
CI configuration — never the algebraic definitions or canonical invariants.

---

## Canonical invariants (frozen)

The following values are part of the mathematical object and **must never be
changed** by any maintenance commit:

| Invariant | Value |
|---|---|
| `dim(V)` | `125` |
| `dim(E₄₇)` | `47` |
| Coherence fraction | `47 / 125 = 0.376` |
| K² spectral gap | `11664` |
| K² max eigenvalue | `186624` |
| K² spectrum | `{0, 11664, 12544, 19600, 32400, 186624}` |
| Casimir roots | `{6, 30}` |

Every CI run enforces these invariants via the drift-detection job.

---

## Automated workflows

### CI (`ci.yml`)

Triggered on every push to `main` and on every pull request targeting `main`.

1. **test** – Runs `python -m pytest tests/ -v` on Python 3.12.
   All 16 test cases in `tests/test_qutip_validation.py` must pass.

2. **drift-check** – Recomputes the canonical invariants from scratch (without
   relying on cached state) and asserts they match the frozen constants.
   A failing drift-check means the implementation has diverged from the
   mathematical specification and must be investigated before merging.

### Certificate regeneration (`cert-regen.yml`)

Runs every Monday at 03:00 UTC and on manual dispatch
(`workflow_dispatch`).

The workflow:
1. Runs `scripts/generate_validation_certificate.py`.
2. Writes the result to `artifacts/e47_validation_certificate.json`.
3. Commits and pushes the updated certificate only if the content changed.

To trigger a manual regeneration, navigate to
**Actions → Regenerate validation certificate → Run workflow**.

### Dependency updates (`dependabot.yml`)

Dependabot opens weekly pull requests for:

- Python dependencies pinned in `requirements.txt` / `requirements-dev.txt`
- GitHub Actions versions used in `.github/workflows/`

Dependency PRs are safe to merge as long as CI passes (both the test job and
the drift-check job).

---

## Manual maintenance checklist

When making a maintenance change:

- [ ] Verify that `python -m pytest` passes locally before opening a PR.
- [ ] Confirm no canonical invariants in `src/e47/su2_kernel.py` were modified.
- [ ] Confirm the drift-check CI job is green.
- [ ] If a new certificate was generated, confirm `artifacts/e47_validation_certificate.json`
      matches the invariant table above.
- [ ] Update `docs/provenance.md` if the validation chain changed.

---

## Files that must not be modified without explicit review

| Path | Reason |
|---|---|
| `src/e47/su2_kernel.py` | Canonical operator algebra and kernel construction |
| `src/e47/projector.py` | Orthogonal projector onto E₄₇ |
| `src/e47/contraction.py` | Discrete dephasing channel validator |
| `src/e47/semigroup.py` | Continuous-time semigroup validator |
| `src/e47/validation_results.py` | Five-layer aggregate certificate |
| `certificates/e47_pipeline.json` | Canonical pipeline snapshot |
| `certificates/qutip_validation.json` | Canonical QuTiP certificate snapshot |

Changes to these files require explicit sign-off that the mathematical
definitions and canonical constants are preserved.

---

## Certificate provenance

The certificate at `artifacts/e47_validation_certificate.json` is a
**derivative artifact** regenerated automatically from the Python source.
The authoritative record is the source code and the repository commit history.

See `docs/provenance.md` for the full canonical implementation chain.

---

**Policy last updated:** 2026-07-24  
**Repository:** https://github.com/nicholaskouns-create/E47-Kartekeya
