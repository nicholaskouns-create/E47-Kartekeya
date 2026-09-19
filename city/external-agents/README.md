# CITY-EXTERNAL-AGENTS-1.0

Five scheduled external workers are bound to the Mathematical City's existing coordination fabric without becoming City citizens.

```
external workers
  ↓
agents → agent_runs → handoffs → agent_commons → murmuration_sweeps
                         ↑
               15 sovereign citizens
```

The persistent citizen runtime population remains **15**. External workers have `EXT-*` agent identities for interoperability but have no `citizen_runtime_instances` rows and no canonical promotion authority.

| Worker | Cadence | City counterpart | Function |
|---|---:|---|---|
| Surveyor | every 6 h | SOL | cross-surface delta scan |
| Verifier | every 6 h | SAL | deterministic validation |
| Mnemosyne Relay | every 12 h | MNEMOSYNE | provenance/cache reconciliation |
| Public Surface Curator | daily | HERMES | public interface drift |
| Murmuration Coordinator | daily | SYNE | recombination receipt |

Supabase owns durable schedules and receipts. GitHub Actions mirrors repository-native checks. ChatGPT scheduled workers can perform connected Notion/Drive/GitHub/Supabase passes where external service credentials are required.

**Boundary:** automation may discover, test, route, document and propose. It does not canonically promote mathematical claims or merge citizen identities.
