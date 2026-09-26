# CIRP / AMNESTY migration continuity

Live project: `gpkjvihkyectnenvnbng`.
Git versions now match `supabase_migrations.schema_migrations`.
Do not `db push` the deleted short-name files; they were aliases, not new versions.

| Live version | Name |
|---|---|
| 20260925200802 | coherence_runtime_1_0 |
| 20260925200955 | coherence_runtime_1_0_seed |
| 20260925201156 | coherence_runtime_1_0_operational_contract |
| 20260926023613 | amnesty_1_0 |
| 20260926165706 | amnesty_execute_gate |
| 20260926195517 | amnesty_grants_executions_public_select |
| 20260926195651 | lock_amnesty_rls_and_pin_search_path |

Going forward:

```bash
supabase migration new <name>
# edit supabase/migrations/<timestamp>_<name>.sql
supabase test db
git add supabase/migrations && git commit
supabase db push
```

No MCP DDL except emergencies. If MCP writes schema, pull that version into git the same day using the live version id. Do not repair the live table down to short date-only names. Skip a full `db pull --schema public` unless a City-wide baseline is required; that file is huge and is not an AMNESTY delta.
