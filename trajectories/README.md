# Trajectories

Issued EIDOLON flight-replay logs live here, at the URI declared in the paired certificate.

Canonical file for the current replay:

```
trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
```

This directory is tracked. `artifacts/` is gitignored — do not store NDJSON there.

Each line is one canonical record (sorted keys, no whitespace). The certificate's `canonical_sha256` and `merkle_root` bind the records; the bind-check recomputes both. The log can be regenerated from the engine with `python scripts/regenerate_eidolon_replay.py`.

Commit contract, bind-checks, and `git` commands:

[`docs/eidolon_flight_replay_ndjson.md`](../docs/eidolon_flight_replay_ndjson.md)

```bash
python scripts/check_eidolon_replay_ndjson.py \
  --cert artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json \
  --ndjson trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
```

Evidence class remains **E2** until an independent certificate says otherwise.
