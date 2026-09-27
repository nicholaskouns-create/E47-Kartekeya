# Supabase → GitHub export status (2026-09-27)

Complementary sync: GitHub = source of truth for code/migrations; Supabase stays runtime.

See `EXPORT_STATUS.json` for machine-readable lists.

## Counts
- Live ACTIVE edge functions: **45**
- Already in git before: **3** (`city-route-packets`, `coherence-runtime`, `matrix-cube-adapter`)
- Exported onto this PR branch so far: **~17** function dirs (+ docs/workflow)
- Still missing from git: **~28** (including large brand icons and host/cube/research bands)

## Migrations
- Live: 96 · Git SQL files: 7 · Shared: 7 · Missing SQL in git: **89** (`MISSING_SQL` — do not invent)

## Deploy
- Workflow: `.github/workflows/supabase-functions.yml`
- Docs: `docs/CITY_RUNTIME_DEPLOY.md` (secrets: `SUPABASE_ACCESS_TOKEN`, `SUPABASE_PROJECT_ID`)

## Do not merge yet
Remaining live function sources should land in follow-up commits on this branch (especially ~1.5–2MB brand icon `index.ts` files and host/cube/research functions already fetched via MCP).
