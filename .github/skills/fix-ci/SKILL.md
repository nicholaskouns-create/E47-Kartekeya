---
name: fix-ci
description: >-
  Investigate and fix GitHub Actions CI failures for E47-Kartekeya. Use when CI is
  red, workflows fail, pytest fails in Actions, certificate drift-check fails,
  verify_citizens fails, ModuleNotFoundError appears in CI, or the user asks to
  fix a failing workflow run.
argument-hint: 'optional run URL, workflow name, or error snippet'
user-invocable: true
---

# fix-ci — E47 CI recovery

Make CI green with the smallest durable fix. Prefer one hardening PR over
symptom-only patches.

## When to use

- Failing `CI`, `verify_citizens`, `cert-regen`, or `publish` workflows
- User pastes Actions logs / run IDs
- Import errors, missing deps, Python version mismatches, cert drift

## Workflow

1. **Collect failure evidence**
   - If the user gave a run URL/ID, fetch job logs with GitHub Actions tools.
   - Otherwise list recent failed workflow runs on this repo/branch.
   - Identify workflow file, job, step, and root error (not just the last line).

2. **Map to source of truth**
   - Primary CI: `.github/workflows/ci.yml` (Python **3.12**, pytest + drift-check)
   - Matrix/precision: `.github/workflows/verify_citizens.yml` (3.10–3.12)
   - Cert regen: `.github/workflows/cert-regen.yml`
   - Deps: `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`
   - Package import root: `src/` (`pip install -e .` or `PYTHONPATH=src`)

3. **Fix root cause once**
   - Install from requirements files; do not ad-hoc `pip install` one-off packages
     in only one job unless unavoidable.
   - Prefer `pip install -e .` so `import e47` works without path hacks.
   - Keep Python support aligned with `requires-python` in `pyproject.toml` (>=3.12)
     or intentionally document/matrix older versions.
   - Never change frozen canonical invariants in `src/e47/` to silence drift-check.

4. **Validate**
   - Run `python -m pytest tests/ -v --tb=short` locally in the agent environment.
   - If cert/drift related, run validation entrypoints used by CI.
   - Summarize which jobs should pass after the fix.

5. **PR hygiene**
   - One PR per root cause cluster.
   - Title/description must name workflow + root cause + regression guard.
   - Do not leave WIP titles when the fix is complete.

## Do / Don't

| Do | Don't |
|---|---|
| Paste/use full failing step logs | Relaunch identical agent sessions blindly |
| Unify install paths across workflows | Edit mathematical invariants to pass drift |
| Add regression coverage when logic broke | “Fix CI” with no stated success criteria |

## Success criteria

- Targeted workflow(s) logically fixed
- Tests pass in agent environment when runnable
- No secret commits; no unrelated refactors
