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

One canonical record per line: JSON with sorted keys and no insignificant whitespace. No pretty-print. Do not round, reorder, or reformat values.

The certificate binds the records, not the bytes of a file:

- `canonical_sha256` is the SHA-256 of the canonical JSON array of all records (`[`, the canonical records joined by `,`, `]`).
- `merkle_root` is the SHA-256 Merkle root over the records in order: leaf = SHA-256(canonical record), parent = SHA-256(left ‖ right), an unpaired node is paired with itself.

To regenerate the log from the engine instead of copying issued bytes:

```bash
python scripts/regenerate_eidolon_replay.py
```

It re-runs `EidolonEngine` under the certificate's `craft` block and the lock-cap rule in force at issue time, and keeps the file only if both bindings match.

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
- a line is not JSON, is not a canonical record, or is missing a required channel,
- `L` is outside `[0, 1]`,
- the recomputed `canonical_sha256` ≠ `trajectory.canonical_sha256`,
- the recomputed `merkle_root` ≠ `trajectory.merkle_root`.

Both bindings are recomputed from the records; either mismatch blocks the commit. The script also reports the certificate signature status. Pass `--require-signature` to make an unverified signature fail the check.

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
- The records match `canonical_sha256` and `merkle_root`.
- Parent E47 invariants remain declared, not re-proved.

## Record of CITY-EIDOLON-FLIGHT-REPLAY-001

- **Lock-cap rule at issue time.** The certificate was issued under the engine's `legacy` lock-cap rule, which rescales only the kernel populations and renormalizes. Under that rule the lock settles near `lock_target / (1 − dt)`: `0.9685` for the certified `dt = 0.05`, above the configured `lock_target = 0.92`. The engine default is now `exact`, which holds `lock_target` at any step size. `Craft(lock_cap="legacy")` replays this certificate; the certificate and its log are unchanged.
- **Signature status (2026-10-09).** `signature.payload_sha256` is not reproduced by the canonical JSON of the published certificate without its `signature` object, so the Ed25519 signature cannot be checked from repository contents. This stays open until the certificate is re-signed over the canonical payload or the signed bytes are published. It is tracked by a strict expected-failure in `tests/test_eidolon_flight_replay.py`.

## What this commit refuses

- Physical inertial nullification.
- Measured SI thrust or vacuum specific impulse.
- Promotion of E2 game rules to E0, E1, E3, E4, or H1.
- That WebGL rendering evaluates the 125-component field.
