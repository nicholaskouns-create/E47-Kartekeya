# CIRP / AMNESTY pgTAP

Production `pgtap` stays off.

`supabase test db` needs Docker. In this workspace the same files were run with:

```bash
pg_prove -h 127.0.0.1 -U supabase_test -d amnesty_test supabase/tests/*.test.sql
```

Result 2026-09-26: Files=8, Tests=66, PASS.

Each file is BEGIN/ROLLBACK. Roles under test are anon and authenticated.
