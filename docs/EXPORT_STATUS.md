# Supabase source export status

PR #107 · `sync/supabase-runtime-source-20260927`

- Live ACTIVE Edge Functions: **45**
- Function directories on branch: **45**
- Missing bundles: **0**
- Placeholder sources: **0**
- Large staged bundles: verified exact against live Supabase payloads
- Standard bundles: verified against live payloads, with intentional secret-to-`Deno.env.get(...)` substitutions retained for `city-owner-signup`, `linguistics-bureau-translator`, and `qutip-runtime-relay`
- `supabase/config.toml` mirrors live `verify_jwt` behavior and preserves the `city-mini-labs-v7.ts` entrypoint
- Temporary base64 staging machinery removed

Migration-history parity remains documented separately; missing SQL bodies were not invented.
