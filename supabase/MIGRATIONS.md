# CIRP / AMNESTY migration continuity

Live project: `gpkjvihkyectnenvnbng`.

## Git vs live (2026-09-27 sync)

See `MIGRATIONS_PARITY.json` for the machine-readable compare.

| Scope | Count |
|-------|------:|
| Live migrations (`list_migrations`) | 96 |
| SQL files in `supabase/migrations/` | 7 |
| Shared version prefixes | 7 |
| Live versions **missing SQL in git** | 89 (`MISSING_SQL`) |

### Shared (SQL present in git)

| Live version | Name |
|---|---|
| 20260925200802 | coherence_runtime_1_0 |
| 20260925200955 | coherence_runtime_1_0_seed |
| 20260925201156 | coherence_runtime_1_0_operational_contract |
| 20260926023613 | amnesty_1_0 |
| 20260926165706 | amnesty_execute_gate |
| 20260926195517 | amnesty_grants_executions_public_select |
| 20260926195651 | lock_amnesty_rls_and_pin_search_path |

### Missing SQL in git

`list_migrations` returns **version + name only**. Bodies for the other 89 live versions are **not** available via the Supabase MCP tools used in this sync. They are flagged `MISSING_SQL` in `MIGRATIONS_PARITY.json` — **do not invent SQL**.

To recover SQL later: export from the dashboard / `supabase db pull` / management API when available, then commit under `supabase/migrations/<version>_<name>.sql` using the live version id.

Going forward:

```bash
supabase migration new <name>
# edit supabase/migrations/<timestamp>_<name>.sql
supabase test db
git add supabase/migrations && git commit
supabase db push
```

No MCP DDL except emergencies. If MCP writes schema, pull that version into git the same day using the live version id.
