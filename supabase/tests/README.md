# CIRP / AMNESTY pgTAP

Production `pgtap` stays off. These files run on a local Supabase stack.

```bash
supabase test db
```

Each file is `BEGIN` / `ROLLBACK`. Fixtures never remain. Assertions use `anon` and `authenticated`, not `postgres` and not `service_role`.

Locked lattice:

- public SELECT: `amnesty_declarations` (access_scope=public), `amnesty_grants`, `amnesty_executions`, active public `coherence_runtime_contracts`
- deny-all clients: `amnesty_nonces`, `coherence_runtime_state`, `coherence_runtime_evaluations`
- no client INSERT/UPDATE/DELETE on the AMNESTY ledger tables
