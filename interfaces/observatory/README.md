# Mathematical City Observatory

A new browser application connecting the existing Mathematical City instruments through a playable discovery journey. Source version 1.0.0.

## Experience

- **City:** an orbitable constellation, with equivalent keyboard-accessible district buttons.
- **Signal Garden:** deterministic seven-sector E47 contraction, input-dependent probability, zero-overlap handling, and a text table.
- **Neural Lab:** real analytic gradient training for Circle, XOR, Spiral, and Linear synthetic datasets, with comparison and replay.
- **Atlas:** source-backed navigation to existing instruments. Unknown external interfaces are labelled as such rather than assigned invented functions.
- **Evidence:** model boundaries, sources, explicit public registry snapshot, and machine contract.
- **Sharing:** 16 downloadable images, exact captions, alt text, native share support, and replay links.

Reduced motion, stronger contrast, larger text, and reading view are supported. Progress and preferences stay in local browser storage; users can clear them or export validated replay inputs. No login or AI service is required.

## Run and verify

```sh
python -m http.server 8000 --directory website
node website/interfaces/observatory/engine.test.mjs
node website/interfaces/observatory/qgnn.test.mjs
python scripts/qa_observatory.py
```

Open `/interfaces/observatory/`. Browser QA uses an existing Chromium executable and Playwright. It exercises desktop/mobile navigation, numerical changes, training, replay validation, accessibility preferences, sharing, and the additive iframe bridge.

## Mathematical scope

The spectral model uses the attached E47 QGNN's Casimir sectors and the canonical repository workbench's filter, Gamma = I - K²/99144. The main filter view simulates sector populations. The additional exact QGNN playground executes four phase-sensitive compressed eigengates from the attached source on a fixed normalized retained input, with a Python-generated fixture. The neural trainer is a conventional small MLP on synthetic data, separate from the existing ENTRAIN encoding/projection monitor. No quantum advantage or Einstein-equation derivation is claimed by this app.

## Embedding and platform use

The additive `bridge.mjs` doorway embeds the app inside existing same-origin City surfaces. Notion can embed the hosted URL; Notion does not execute this JavaScript itself. External Grok and ChatGPT-hosted apps remain direct destinations unless an authorized editable source and verified embedding policy are available.

The catalog is a public source snapshot, not an unrestricted connector session. Private Drive records, workspace-scoped Supabase objects, and credential-bearing material are excluded. `machine.json` documents stable operations for browser agents and ES-module consumers. The application does not grant agents authority to perform remote actions.

## Social assets

See `share/manifest.json` for sizes, captions, alt text, and platform use. Rebuild with `python scripts/build_observatory_share.py`. Posts are composed by the user; creating the kit does not post to social accounts.

## Provenance

Uses user-supplied E47_QGNN.zip and e47_qgnn Python as mathematical references; canonical `website/interfaces/e47-research-workbench/engine.mjs`; existing instrument portal and route packets; explicitly public Supabase evidence; the supplied hosted-surface list. The threshold Ring-LWE bundle is linked as a future collaboration instrument, not silently relabelled as deployed cryptographic infrastructure.
