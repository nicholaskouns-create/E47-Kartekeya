# Session store quick reference

## Cloud (DuckDB)

Time filter examples:

```sql
SELECT id, agent_name, created_at, updated_at,
       date_diff('second', created_at, updated_at) AS duration_sec
FROM sessions
WHERE created_at > now() - INTERVAL '30 days'
ORDER BY created_at DESC
LIMIT 50;
```

```sql
SELECT tool_start_name, COUNT(*) AS cnt
FROM events
WHERE timestamp > now() - INTERVAL '30 days'
  AND type = 'tool.execution_start'
  AND tool_start_name IS NOT NULL
GROUP BY tool_start_name
ORDER BY cnt DESC
LIMIT 30;
```

```sql
SELECT file_path, COUNT(DISTINCT session_id) AS sessions
FROM session_files
GROUP BY file_path
ORDER BY sessions DESC
LIMIT 40;
```

## Local (SQLite)

- Use `source: local` when available.
- FTS: `SELECT * FROM search_index WHERE search_index MATCH 'query' LIMIT 20;`
- Usage: `assistant_usage_events` for token/duration rows.

## Interpretation heuristics for E47-Kartekeya

- Short session clusters on `allow-*-access` branches → settings/permission tasks, not code.
- Repeated CI PR titles (`verify_citizens`, `qutip`, `ModuleNotFoundError`) → unify install path.
- Hot paths under `src/e47/` + workflows → require tests + cert/drift checks together.
