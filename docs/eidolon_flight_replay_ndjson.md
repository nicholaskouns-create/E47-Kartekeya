# EIDOLON flight-replay NDJSON — commit instructions

This is the commit contract for a trajectory bound to an E2 flight-replay certificate.

The live certificate is [`artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json`](../artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json) (force-added; `artifacts/` is gitignored). Its declared trajectory URI is:

```
trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
```

Evidence class is locked at **E2**. Committing the NDJSON does not promote the replay to E0, E1, E3, E4, or H1.

## Lineage

- Parent certificate: `artifacts/e47_validation_certificate.json` (E0/E1).
- Replay certificate: `artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json` (E2).
- Trajectory: `trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson`.
- Public mirror of the certificate: `website/data/CITY-EIDOLON-FLIGHT-REPLAY-001.json`.

Data Lifetime: no deletion of the certificate or its trajectory without review of the entire upstream/downstream set.

## 1. Place the file

The NDJSON must occupy the exact URI in the certificate. `trajectories/` is tracked; do **not** put the log under `artifacts/` (that directory is gitignored).

```bash
install -D -m 0644 CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson \
  trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
```

Optional Pages mirror, so the public surface can fetch the same bytes:

```bash
install -D -m 0644 trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson \
  website/data/trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
```

One record per line. No pretty-print. No trailing blank line unless it was in the issued bytes. Do not rewrite field order or float formatting — `canonical_sha256` is over the exact file.

## 2. Bind-check before `git add`

Required channels, in the certificate order:

```
t, W, L, m_eff, mode, lab_mode
```

Issued bindings for `CITY-EIDOLON-FLIGHT-REPLAY-001`:

| Check | Value |
|---|---|
| `n_samples` | `961` |
| `canonical_sha256` | `8a8f7d40deb882f5e6d163a157babfdc59e0a6fd6e1c2583438e7ffb5e763b81` |
| `merkle_root` | `36da7d47568e75d112b45c0fbc27163550a12e7c8c530cbd8f0a6dabe7c42b06` |
| `dt` | `0.05` |
| `t0` / `t1` | `0.0` / `48.0` |

Run:

```bash
python scripts/check_eidolon_replay_ndjson.py \
  --cert artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json \
  --ndjson trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
```

The script refuses the commit if:

- the file is missing,
- line count ≠ `n_samples`,
- a line is not JSON or is missing a required channel,
- `L` is outside `[0, 1]`,
- SHA-256 of the exact file bytes ≠ `trajectory.canonical_sha256`.

`merkle_root` is the issuing lab's sample-sequence commitment. Recompute it only with the same leaf canonicalization used at issue time. The SHA-256 bind is the commit gate; the Merkle root is recorded, not re-derived here.

## 3. Stage

```bash
git add trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
git add website/data/trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson   # if mirrored
```

Do not `git add artifacts/…` for the NDJSON. If you ever replace the certificate itself:

```bash
git add -f artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json
git add website/data/CITY-EIDOLON-FLIGHT-REPLAY-001.json
```

## 4. Commit and push

```bash
git commit -m "$(cat <<'EOF'
Add CITY-EIDOLON-FLIGHT-REPLAY-001 trajectory NDJSON.

Merkle-bound to artifacts/CITY-EIDOLON-FLIGHT-REPLAY-001.json.
Evidence class locked at E2. No promotion of game rules.
EOF
)"

git push origin main
```

## 5. After the push

Confirm the blob:

- https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson
- https://raw.githubusercontent.com/nicholaskouns-create/E47-Kartekeya/main/trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson

Pages mirror (after the Pages workflow):

- `https://nicholaskouns-create.github.io/E47-Kartekeya/data/trajectories/CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson`

## What this commit asserts

- The attached log has 961 samples of `W`, `L`, `m_eff`, and `mode`.
- File bytes match `canonical_sha256`.
- Parent E47 invariants remain declared, not re-proved.

## What this commit refuses

- Physical inertial nullification.
- Measured SI thrust or vacuum specific impulse.
- Promotion of E2 game rules to E0, E1, E3, E4, or H1.
- That WebGL rendering evaluates the 125-component field.
