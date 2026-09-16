---
name: validate-invariants
description: >-
  Run and explain E47 canonical invariant validation, QuTiP checks, drift
  detection, and pytest for the spectral kernel package. Use when asked to
  validate E47, verify invariants, run the test suite, check coherence fraction,
  spectral gap, or mathematical city citizens precision.
argument-hint: 'optional test path or invariant name'
user-invocable: true
---

# validate-invariants

Verify the frozen E47 algebraic object and report results clearly.

## Frozen invariants

| Invariant | Value |
|---|---|
| dim(V) | 125 |
| dim(E₄₇) | 47 |
| Coherence fraction | 47/125 |
| K² spectral gap | 11664 |
| K² max eigenvalue | 186624 |

Source of policy: `docs/maintenance_policy.md`, `docs/validation_scope.md`.

## Commands

```bash
pip install -e . -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v --tb=short
```

Programmatic validation (as in CI drift-check):

```bash
python - <<'EOF'
import sys
sys.path.insert(0, "src")
from e47.validation_results import run_all_validations, require_all_validations
results = run_all_validations()
require_all_validations(results)
assert results.qutip_validation.carrier_dimension == 125
assert results.qutip_validation.kernel_dimension == 47
print(results.summarize())
EOF
```

## Workflow

1. Install deps editable.
2. Run pytest; if user named a file, run that first.
3. Run validation summary and compare to frozen table.
4. On failure: locate mismatch in `src/e47/` / tests, explain whether it is
   environment, test harness, or implementation drift.
5. **Never “fix” drift by editing the canonical constants** unless the user
   explicitly requests a mathematical change (out of scope for maintenance).

## Output

- Pass/fail per invariant
- Failing test node ids
- Next action (env fix vs real drift investigation)
