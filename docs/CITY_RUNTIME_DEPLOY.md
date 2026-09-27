# City runtime deploy (edge functions)

## Complementary model

- **GitHub** = source of truth for function source and migrations checked into `supabase/`
- **Supabase** (`gpkjvihkyectnenvnbng`) = live runtime
- Syncing code into git does **not** delete or replace live functions until you deploy

## Required GitHub Actions secrets

Configure in the repo settings (never commit values):

| Secret | Purpose |
|--------|---------|
| `SUPABASE_ACCESS_TOKEN` | Personal access token / CLI token with Edge Functions deploy |
| `SUPABASE_PROJECT_ID` | Project ref, e.g. `gpkjvihkyectnenvnbng` |

## Workflow

File: `.github/workflows/supabase-functions.yml`

- Triggers on push to `main` when `supabase/functions/**` changes
- Uses `supabase/setup-cli`
- Deploys each changed function directory under `supabase/functions/`

## Manual deploy

```bash
npx supabase login   # or export SUPABASE_ACCESS_TOKEN
npx supabase functions deploy <slug> --project-ref "$SUPABASE_PROJECT_ID"
```

## Env vars on the project (dashboard / CLI secrets)

Functions may expect runtime secrets such as:

- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY` / publishable key
- `SUPABASE_DB_URL` (cube-state, city-cube-bus)
- `OPENAI_API_KEY`, `OPENAI_MODEL` (orchestrator)
- `FUNCTION_TOKEN`, `OWNER_EMAIL` (token-gated helpers — set in dashboard; stripped from git)

## Safety

- Do not put real secrets in source
- Prefer `Deno.env.get` over hardcoding
- Review PRs that touch `city-owner-signup`, `qutip-runtime-relay`, `linguistics-bureau-translator` for leaked tokens
