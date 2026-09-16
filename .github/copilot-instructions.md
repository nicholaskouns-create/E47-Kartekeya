# Copilot instructions — E47-Kartekeya

## Project

Finite-dimensional algebraic validation of the E47 spectral kernel on V₂⊗V₂⊗V₂.
Distribution name: `e47-kartekeya`. Import package: `e47` (under `src/`).

## Environment

- Python **>=3.12** (`pyproject.toml`)
- Install: `pip install -e . -r requirements.txt -r requirements-dev.txt`
- Tests: `python -m pytest tests/ -v --tb=short`
- Single test: `python -m pytest tests/test_qutip_validation.py -k <name> -v`

## Frozen canonical invariants

Do **not** change these during maintenance/CI fixes:

| Invariant | Value |
|---|---|
| dim(V) | 125 |
| dim(E₄₇) | 47 |
| Coherence fraction | 47/125 |
| K² spectral gap | 11664 |
| K² max eigenvalue | 186624 |

Policy: `docs/maintenance_policy.md`. Scope: `docs/validation_scope.md`.

## Key commands

```bash
# validation certificate
python scripts/generate_validation_certificate.py \
  --output artifacts/e47_validation_certificate.json

# spectral kernel compile / verify
python scripts/compile_spectral_kernel.py --spin 2 --copies 3 --select 2 5
python scripts/compile_spectral_kernel.py --verify
```

## Workflows

- `.github/workflows/ci.yml` — pytest + drift-check on 3.12
- `.github/workflows/verify_citizens.yml` — matrix precision tests
- `.github/workflows/cert-regen.yml` — scheduled/manual certificate regen
- `.github/workflows/publish.yml` — PyPI publish on release
- `.github/workflows/copilot-setup-steps.yml` — cloud agent bootstrap

## Skills and agents

Reusable workflows live in `.github/skills/*/SKILL.md` (invoke as `/name`).
Specialized agents live in `.github/agents/`.
Platform glue: `/platform-interconnect`. Session retrospectives: `/chronicle`.

## Working rules

1. Prefer editable install over ad-hoc `PYTHONPATH` hacks in new automation.
2. Fix CI at the root cause; unify dependency installs across jobs.
3. Math-core changes require tests + invariant/cert consideration together.
4. GitHub App / org permission requests are settings tasks — explain steps, don’t noop-PR.
5. Keep diffs minimal; don’t rewrite unrelated proofs or docs.
