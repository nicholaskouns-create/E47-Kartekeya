# Supabase Edge Functions — Mathematical City

Live project: `gpkjvihkyectnenvnbng`  
GitHub is source of truth for code; Supabase remains the runtime. Do not delete live functions when syncing.

## Bands

| Band | Slugs |
|------|-------|
| **host** | `city-app-host`, `city-app-migrator`, `city-app-route-patch`, `city-graphics-accelerator` |
| **labs/brand** | `city-mini-labs*`, `mini-lab-brand*`, `city-brand-*` |
| **cube/commons** | `the-cube`, `cube-*`, `city-cube-bus`, `city-agent-commons`, `city-unified-game`, `p47-bus` |
| **coherence/runtime** | `coherence-runtime`, `city-recursive-engine`, `eidolon-city-adapter`, `skyrmion-world-runtime`, `e47-recursive-note`, `density-reconstruct`, `city-query-store`, `city-route-packets`, `sat-newton-boxdim`, `pip-manta`, `matrix-cube-adapter` |
| **research/access** | `mathematical-city-orchestrator`, `city-research-lab`, `city-access-sentinel`, `city-owner-signup`, `city-formalism-rescue`, `linguistics-bureau-translator`, `qutip-runtime-relay`, `syntax-jacob-ephemeris` |

## Layout

Each function lives under `supabase/functions/<slug>/` with its entrypoint (usually `index.ts`) and any local modules (`deno.json`, helpers).

## Deploy

Push to `main` under `supabase/functions/**` triggers `.github/workflows/supabase-functions.yml`.  
Secrets: `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_ID` (see `docs/CITY_RUNTIME_DEPLOY.md`).

## Secrets policy

Never commit service-role keys, JWTs, or launch tokens. Use `Deno.env.get(...)`.
