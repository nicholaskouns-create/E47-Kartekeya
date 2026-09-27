# EXPORT_STATUS — PR #107 (do not merge)

Updated: **2026-09-27 20:04 UTC**  
Branch tip: `2338a2684e48602c6f443cb21acac9d04b2b07f4`  
**Do not merge.**

## Goal A — @file placeholder fixes
### Still literal `@file:///workspace/...` on remote
| path | local bytes | local sha256 |
|------|------------:|--------------|
| `supabase/functions/city-brand-density-icon/index.ts` | 1938141 | `0179dcb5d51209f2…` |
| `supabase/functions/city-brand-wave-icon/index.ts` | 1930678 | `30a1ac1883e0e43d…` |
| `supabase/functions/city-brand-fold-icon/index.ts` | 1835041 | `f852e405b3f7a628…` |
| `supabase/functions/city-brand-mnemosyne-icon/index.ts` | 1714379 | `0cde29055b8aed2e…` |
| `supabase/functions/city-brand-soar-icon/index.ts` | 1494426 | `10b3a1fcfcad4c67…` |
| `supabase/functions/mini-lab-brand-assets/index.ts` | 1901849 | `ff55f869e7d495b5…` |

### linguistics-bureau-translator
- local bytes: **17796** sha256 `dd4c0cd1586fa1900e357a7559c947958ef8789380508f5996de5ac5ae2c11ac`
- remote: **NOT_EXACT** (prior base64 corruption). Staging assemble started but part push also corrupted under transcription — **do not run assemble** until parts re-pushed exactly.

### Blocker
`gh` CLI unauthenticated. Device login waiting: code **EA77-312E** → https://github.com/login/device  
Once authorized: from `/workspace/E47-repo` on branch `sync/supabase-runtime-source-20260927`, copy exact local `index.ts` for the 6 icons + linguistics and `git push`.  
Drive staging: https://drive.google.com/drive/folders/1XPSu88q4YgP0V6fUZ_Gp3QjxezIMhrLV

## Goal B — city-cube-bus / city-mini-labs
| function | status |
|----------|--------|
| city-cube-bus `deno.json` | on branch, **exact** |
| city-cube-bus `lab-adapters.ts` | on branch, **exact** (7277 B) |
| city-cube-bus `index.ts` | MCP fetched; **not on branch yet** |
| city-mini-labs `octet_packet_core.ts` | local 12631 B ready |
| city-mini-labs `city-mini-labs-v7.ts` | live MCP OK; keep live filename (no invented index.ts) |

## Constraints
- Did not merge PR #107
- Live Supabase untouched
- No invented migration SQL
