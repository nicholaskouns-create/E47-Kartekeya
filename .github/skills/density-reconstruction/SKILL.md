---
name: density-reconstruction
description: >-
  Reconstruct latent structure from partial observations with DENSITY. Use for
  incomplete historical records, cross-platform evidence recovery, behavior
  boundary reconstruction, source drift, or matched-prompt audits.
argument-hint: 'task | observations.json | sources'
user-invocable: true
---

# density-reconstruction

Use DENSITY as an inverse-problem instrument, not as an authority layer.

## Contract

1. Normalize evidence into `CITY-QUERY/1.0`.
2. Keep source provenance and evidence class on every observation.
3. Separate epistemic qualification from altered technical handling.
4. Encode one 125-state slice as three 5-bin coordinates:
   `domain × implementation × operationality`.
5. Represent time/model changes as separate epochs, never as an extra hidden
   coordinate inside the E47 carrier.
6. Hold out observations before fitting.
7. Reconstruct the raw field with ART.
8. Independently project the raw field through canonical rank-47 `P47`.
9. Accept the gate only when held-out error is not materially worse than raw.
10. Inspect residuals and contradictions. Do not erase them.

## Blind-test rule

When testing whether a prior sensitivity map predicted behavior, do not train on
that map. For the 2026 handling audit, `SCF-2026-01` is evaluation-only.

## Interfaces

- Python: `research/e47/validation/density_sensitivity_tomography.py`
- Browser: `website/interfaces/density-sensitivity/`
- Shared task bus: `website/interfaces/shared/city-query.js`
- Public compute: Supabase Edge Function `density-reconstruct`
- Owner persistence: Supabase Edge Function `city-query-store`
- Durable tables: `city_query_tasks`, `city_query_observations`,
  `density_reconstructions`

## Evidence boundary

A reconstruction describes observed handling patterns. It does not, by itself,
establish an intrinsic platform label, external classification status, or a
physical claim about the underlying research.

## Related skills

- `/platform-interconnect` — platform wiring
- `/validate-invariants` — frozen algebra validation
- `/chronicle` — provenance/history recovery
