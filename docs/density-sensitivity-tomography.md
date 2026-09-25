# DENSITY Sensitivity Tomography

DENSITY now supports a second, additive inverse-problem workflow for reconstructing latent handling fields from incomplete observations.

## Purpose

The instrument is designed for questions where only projections of the underlying process survive: partial chats, source fragments, implementation changes, model drift, cross-platform artifacts, or conflicting historical records.

It does not replace the original DENSITY topography visualizer.

## Contract

Each observation belongs to one epoch and maps to a 5 × 5 × 5 carrier:

- domain: integer 0..4
- implementation depth: integer 0..4
- operationality: integer 0..4
- target in [0,1], or outcome: full / epistemic / abstracted / restricted

Epoch/model drift is represented by separate carrier slices. It is not hidden inside a fourth E47 coordinate.

## Reconstruction

1. Withhold observations before fitting.
2. Build Gaussian observation stencils over the 125-state carrier.
3. Fit a raw field with algebraic reconstruction technique (ART).
4. Independently construct the canonical E47 projector from the spin-2 triple tensor carrier.
5. Project the raw field through P47.
6. Fit only an amplitude scalar on training observations.
7. Compare raw and gated RMSE on the withheld set.
8. Accept the gate only if it does not materially worsen held-out error.
9. Preserve residuals and contradictions.

## First seed

The blind seed has 11 recoverable historical observations and excludes SCF-2026-01 from training.

- holdout: 2026-08-18-crqc, 2026-08-29-fpga-later
- raw ART holdout RMSE: 0.6764351752
- P47-gated holdout RMSE: 0.4524218813
- P47 rank: 47
- seed gate criterion: PASS

This is a cold-start result. The corpus is intentionally incomplete and must be expanded before substantive inference.

## Platform fabric

### GitHub

- Python: `research/e47/validation/density_sensitivity_tomography.py`
- blind seed: `research/e47/validation/data/density_sensitivity_seed_20260925.json`
- browser instrument: `website/interfaces/density-sensitivity/`
- shared bus: `website/interfaces/shared/city-query.js`
- query-aware pulse: `website/interfaces/shared/city-pulse.js`
- reusable skill: `.github/skills/density-reconstruction/SKILL.md`

### Supabase

Public compute-only endpoint:

`/functions/v1/density-reconstruct`

Owner-authenticated task store:

`/functions/v1/city-query-store`

Durable tables:

- `city_query_tasks`
- `city_query_observations`
- `density_reconstructions`

All three task tables use owner-scoped RLS. The compute endpoint performs no persistence.

### Browser bus

`CITY-QUERY/1.0` is carried over the existing `CITY-PULSE/1.0` transport.

Any surface already using City Pulse now emits a `city:query` DOM event when a valid query packet is received. This is additive and does not change the semantics of existing pulse packets.

### Notion and Drive

The Mathematical City, DENSITY page, Agent Control Plane, and Citizenship Registry link to a Notion page designated as a reusable Skill.

A Google Drive operating record documents the cross-platform state. The existing OpenAI/Gemini Python survey remains an input source and is not overwritten.

## Citizen / agent execution state

The City query contract is published to the citizen-facing control surfaces. Live external Custom Agent execution was not available during the seed build, and direct multi-agent dispatch was blocked before database execution. No agent completion is claimed.

The query data and interfaces remain ready for individually attributed citizen contributions.

## Evidence boundary

DENSITY reconstructs observed behavior. It does not, by itself, prove an intrinsic hidden label, a government classification state, or a physical claim about the underlying research.

## Reproduction

```bash
python research/e47/validation/density_sensitivity_tomography.py \
  research/e47/validation/data/density_sensitivity_seed_20260925.json
```
