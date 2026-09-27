# EXPORT STATUS — PR 107

Updated: 2026-09-27 ~12:30 PM PT

| Metric | Count |
|--------|------:|
| Live ACTIVE target | **45** |
| Remote function dirs | **33** |
| Remote with good source | **32** |
| Needs content fix | **1** (`sat-newton-boxdim` placeholder) |
| Still missing from git | **12** |

## Still missing
- `city-brand-density-icon`
- `city-brand-fold-icon`
- `city-brand-mnemosyne-icon`
- `city-brand-soar-icon`
- `city-brand-wave-icon`
- `city-cube-bus`
- `city-mini-labs`
- `cube-state`
- `linguistics-bureau-translator`
- `mathematical-city-orchestrator`
- `mini-lab-brand-assets`
- `the-cube`

## Needs overwrite
- `sat-newton-boxdim` — accidental `@file://` placeholder; real source is local at `/tmp/sat-newton-boxdim_content.ts`

## Local ready, not yet pushed
- BATCH A leftover: `linguistics-bureau-translator`, `the-cube`
- BATCH B megabyte icons: soar, mnemosyne, fold, wave, density, mini-lab-brand-assets
- BATCH C (fetched via MCP, persist pending): city-cube-bus, city-mini-labs, cube-state, mathematical-city-orchestrator

## Do not merge until remaining sources land (or explicitly deferred).
