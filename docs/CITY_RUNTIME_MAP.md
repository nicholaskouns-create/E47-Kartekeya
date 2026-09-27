# City runtime map

Live project: `gpkjvihkyectnenvnbng`

Exported 2026-09-27. Status reflects this sync PR.

| function slug | band | purpose | site/caller if known | status |
|---|---|---|---|---|
| `city-app-host` | host | Static app host + Syntax Jacob ephemeris proxy from storage | website/index.html, city-live/labs.js, nexus/app.js, kouns-core/app.html, readme-router.json | exported |
| `city-app-migrator` | host | Crawl grok.me origins into city-apps storage bucket | — | exported |
| `city-app-route-patch` | host | Patch SEE registry/suite routes into storage | — | exported |
| `city-graphics-accelerator` | host | Graphics contract + adaptive canvas ES module | website/interfaces/syntax-jacob/app.js | exported |
| `city-mini-labs` | labs/brand | Mini AI Labs registry, HTML gateway, octet packet actions | city-formalism-rescue links | exported |
| `city-mini-labs-editorial-light` | labs/brand | Quiet editorial entry to city-unified-game | — | exported |
| `mini-lab-brand-assets` | labs/brand | Brand asset CDN for mini labs | — | exported |
| `mini-lab-brand-upload` | labs/brand | Disabled upload endpoint (410) | — | exported |
| `city-brand-identity-icon` | labs/brand | Brand WebP icon — Identity | — | exported |
| `city-brand-build-icon` | labs/brand | Brand WebP icon — BUILD | — | exported |
| `city-brand-soar-icon` | labs/brand | Brand WebP icon — SOAR | — | exported |
| `city-brand-spectra-icon` | labs/brand | Brand WebP icon — SPECTRA | — | exported |
| `city-brand-fold-icon` | labs/brand | Brand WebP icon — Fold | — | exported |
| `city-brand-murmuration-icon` | labs/brand | Brand WebP icon — Murmuration | — | exported |
| `city-brand-mnemosyne-icon` | labs/brand | Brand WebP icon — Mnemosyne | — | exported |
| `city-brand-density-icon` | labs/brand | Brand WebP icon — Density | — | exported |
| `city-brand-horizon-icon` | labs/brand | Brand WebP icon — Horizon | — | exported |
| `city-brand-wave-icon` | labs/brand | Brand WebP icon — Wave | — | exported |
| `city-brand-scalar-icon` | labs/brand | Brand JPEG icon — SCALAR | — | exported |
| `the-cube` | cube/commons | Interactive Professor's Cube / E47 teaching instrument | — | exported |
| `cube-instance` | cube/commons | Server-side scramble/solve cube instance API | — | exported |
| `cube-state` | cube/commons | Authenticated persistent cube ledger API | — | exported |
| `city-cube-bus` | cube/commons | Cube ↔ octet packet bus + lab adapters | — | exported |
| `city-agent-commons` | cube/commons | Owner-scoped agent commons threads/messages | — | exported |
| `city-unified-game` | cube/commons | Unified district game client host | city-mini-labs-editorial-light | exported |
| `p47-bus` | cube/commons | P47 bus runtime | — | exported |
| `coherence-runtime` | coherence/runtime | Coherence / CIRP / amnesty execute gate | contracts/nemo-guardrails/README.md | in_git_before |
| `city-recursive-engine` | coherence/runtime | Recursive automation registry engine | — | exported |
| `eidolon-city-adapter` | coherence/runtime | Eidolon citizen bridge adapter | — | exported |
| `skyrmion-world-runtime` | coherence/runtime | Skyrmion multi-domain flight runtime | — | exported |
| `e47-recursive-note` | coherence/runtime | Public E47 recursive system note surface | docs/notes/e47-recursive-system.md | exported |
| `density-reconstruct` | coherence/runtime | Density sensitivity reconstruction API | docs/density-sensitivity-tomography.md | exported |
| `city-query-store` | coherence/runtime | Density query bus store | docs/density-sensitivity-tomography.md | exported |
| `city-route-packets` | coherence/runtime | City route packet transport | — | in_git_before |
| `sat-newton-boxdim` | coherence/runtime | SAT-Newton boxdim research mirror | research/sat_newton_fractal/README.md | exported |
| `pip-manta` | coherence/runtime | PIP MANTA HTML mirror from GitHub Pages source | mirrors website/interfaces/pip-manta/ | exported |
| `matrix-cube-adapter` | coherence/runtime | 125-amp MATRIX ↔ cube witness adapter | syntax-jacob/app.js, matrix/matrix.js, kouns-core/matrix-cube-bridge.js, scripts/ | in_git_before |
| `mathematical-city-orchestrator` | research/access | Transit-event agent orchestrator | — | exported |
| `city-research-lab` | research/access | Research lab snapshot / proof-search surface | — | exported |
| `city-access-sentinel` | research/access | Multi-tenant ownership / audit posture | — | exported |
| `city-owner-signup` | research/access | Token-gated owner magic-link bootstrap | — | exported |
| `city-formalism-rescue` | research/access | Stranded formalism rescue status page | — | exported |
| `linguistics-bureau-translator` | research/access | Invariant grammar translator UI | — | exported |
| `qutip-runtime-relay` | research/access | Token-gated QuTiP wheel relay | — | exported |
| `syntax-jacob-ephemeris` | research/access | JPL Horizons 3I/ATLAS ephemeris mirror | syntax-jacob/app.js, provenance.json | exported |

## Notes

- Host apps are served under `/functions/v1/city-app-host/<app>/`.
- Brand icons are often pulled by `city-mini-labs` for the lab grid.
- Deploy wiring: `docs/CITY_RUNTIME_DEPLOY.md`.
- Export completeness: this PR includes docs/deploy wiring plus function sources; remaining large sources continue in follow-up commits on the same branch if needed.
