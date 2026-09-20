# Documentation

[Repository home](../README.md) · [Open an instrument](instruments.md) · [Research notes](../research/README.md)

## Start and reproduce

| Guide | Use it for |
|---|---|
| [Reproducibility](reproducibility.md) | Install, run tests, regenerate certificates, serve the website |
| [Source map](../src/README.md) | Find the E47, AETHERIS, and MANTA implementations |
| [Command directory](../scripts/README.md) | Choose an existing check or compilation command |
| [Certificate directory](../certificates/README.md) | Inspect committed results and their provenance |
| [Validation scope](validation_scope.md) | Identify the claims each result supports |
| [Provenance](provenance.md) | Follow implementation lineage |

## Instruments and runtimes

| Guide | Use it for |
|---|---|
| [Instrument directory](instruments.md) | Direct app links, source paths, companion views |
| [AETHERIS](aetheris_runtime.md) | State transitions and receipt machinery |
| [CITY 125](city_125_runtime.md) | The 125-state runtime and visual debugger |
| [THE MATRIX](matrix_quantum_simulator.md) | Quantum simulator architecture |
| [Matrix → CITY 125 → E47 → AETHERIS](matrix_city125_e47_aetheris.md) | State translation and witness bindings |
| [Cube platform map](cube_platform_map.md) | Cube interfaces and adapters |
| [EIDOLON replay](eidolon_flight_replay_ndjson.md) | Certificate-bound NDJSON flight records |
| [Syntax Jacob](../website/interfaces/syntax-jacob/README.md) | Ephemeris inputs, visualization, and model provenance |

## Components and integration

| Guide | Use it for |
|---|---|
| [Lab architecture](lab_architecture.md) | Component locations and existing boundaries |
| [Instrument contracts](instrument_contracts.md) | Versions, smoke commands, receipts, and local failure events |
| [External workers](../city/external-agents/README.md) | Existing five-worker integration |
| [Skills and agents](skills-and-agents.md) | Repository-provided Copilot tools |
| [Maintenance policy](maintenance_policy.md) | Existing maintenance rules and frozen constants |
| [Contributing](../CONTRIBUTING.md) | Make changes to a local component |
| [Supabase Python migration](migrations/SUPABASE_PYTHON_TO_GITHUB_20260917.md) | Recorded September 17 source import |
| [September 20 branch-cleanup proposal](maintenance/branch-cleanup-2026-09-20.md) | Proposed branch removals and recoverable commit IDs |

## Graphics references

These documents describe graphics contracts and prior rollout work. Their dated status records are snapshots.

- [Application matrix](city_graphics_app_matrix.md) and [targets](city_graphics_targets.md)
- [Acceptance criteria](city_graphics_acceptance.md), [proof checks](city_graphics_proof_gates.md), and [non-goals](city_graphics_non_goals.md)
- [Rollout](city_graphics_rollout.md) and [September 17 status](city_graphics_status_20260917.md)
- [Shared browser runtime](../web/README.md)
