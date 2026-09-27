# EXPORT_STATUS — PR #107 (do not merge)

Updated: **2026-09-27 19:51 UTC**
Branch tip: `710acbd9e27764d23f868fe5924e0b4c91303aeb`

## Goal A — @file placeholder fixes
### Exact match verified (raw.githubusercontent.com == local)
| path | bytes |
|------|------:|
| `supabase/functions/cube-state/index.ts` | 11232 |
| `supabase/functions/mathematical-city-orchestrator/index.ts` | 12824 |

### Replaced @file but NOT exact (needs re-push)
| path | bytes | issue |
|------|------:|-------|
| `supabase/functions/linguistics-bureau-translator/index.ts` | 17796 | ~232 byte corruption in HTML_B64 vs local |

### Still literal `@file:///workspace/...` on remote
- `supabase/functions/city-brand-density-icon/index.ts`
- `supabase/functions/city-brand-wave-icon/index.ts`
- `supabase/functions/mini-lab-brand-assets/index.ts`
- `supabase/functions/city-brand-fold-icon/index.ts`
- `supabase/functions/city-brand-mnemosyne-icon/index.ts`
- `supabase/functions/city-brand-soar-icon/index.ts`

**Blocker:** Inline `push_files` content for MB-scale / dense base64 files corrupts under LLM transcription. Exact local bytes staged at Drive folder `https://drive.google.com/drive/folders/1XPSu88q4YgP0V6fUZ_Gp3QjxezIMhrLV`.

## Goal B — city-cube-bus / city-mini-labs
- MCP `get_edge_function` succeeded for both.
- **city-cube-bus:** local has `deno.json` + `lab-adapters.ts`; **missing `index.ts`** on disk (not pushed).
- **city-mini-labs:** live names `city-mini-labs-v7.ts` + `octet_packet_core.ts` (no invented `index.ts`). Disk incomplete.

## Constraints honored
- Did not merge PR #107
- Did not delete live Supabase functions
- Did not invent migration SQL
- Prefer `user-GitHub-xai` (gh token 401)
