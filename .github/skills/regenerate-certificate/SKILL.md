---
name: regenerate-certificate
description: >-
  Regenerate E47 validation certificates and spectral kernel certificates, fix
  cert-regen workflow issues, and check certificate drift. Use when asked to
  regenerate certificates, update artifacts/e47_validation_certificate.json,
  run generate_validation_certificate.py, or repair cert automation.
argument-hint: 'optional --allow-invalid or output path'
user-invocable: true
---

# regenerate-certificate

Regenerate and verify E47 validation certificates without altering frozen math.

## When to use

- Certificate regeneration or drift
- `cert-regen.yml` failures
- Updating `artifacts/e47_validation_certificate.json`
- Spectral kernel certificate/passport refresh

## Commands

```bash
pip install -e . -r requirements.txt -r requirements-dev.txt
python scripts/generate_validation_certificate.py \
  --output artifacts/e47_validation_certificate.json
```

Spectral kernel (when requested):

```bash
python scripts/compile_spectral_kernel.py --spin 2 --copies 3 --select 2 5
# optional verify mode used in CI:
python scripts/compile_spectral_kernel.py --verify
```

## Workflow

1. Install package editable so imports resolve.
2. Run certificate generation script.
3. Confirm invariants still match `docs/maintenance_policy.md`:
   - dim(V)=125, dim(E47)=47, gap=11664, max eigenvalue=186624
4. If workflow automation is broken, fix `.github/workflows/cert-regen.yml`
   (PYTHONPATH/`pip install -e .`, artifact path, `git add -f` if needed).
5. Do **not** commit secrets. Only commit certificate JSON when content changed
   and validation succeeded (unless user explicitly wants `--allow-invalid`).

## Guardrails

- Mathematical definitions in `src/e47/` are frozen for maintenance tasks.
- Prefer fixing environment/import/CI issues over changing validation thresholds.
