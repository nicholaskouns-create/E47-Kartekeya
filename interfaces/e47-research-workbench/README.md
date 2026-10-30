# E47 Research WorkBench

An independently addressable research instrument, version 1.0.0, evidence E1/E2.

Run from the repository root:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
PYTHONPATH=src .venv/bin/python -m e47.workbench
python -m http.server 8000 --directory website --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/interfaces/e47-research-workbench/`.
For a directly openable offline app:

```bash
python scripts/package_e47_workbench.py --output artifacts/E47-Research-WorkBench.html
```

Open that generated HTML file directly. It embeds the numerical bundle and workspace
links, uses exact inline-script/style CSP hashes, and makes no network reads.

The static app has no CDN dependencies, build step, API key, or account credential.
Its generated `data.json` is committed for direct Pages hosting.

## Experiments

Choose discrete filtering or continuous flow, initial sector weights, a random seed,
iteration count, and step/horizon. Run is an explicit action. Export JSON for replay,
CSV for spreadsheet analysis, Markdown for research notes, or OBJ for geometry.
Import JSON to validate its inputs and recompute results; supplied result fields
are not trusted. An imported custom epsilon is preserved when rerun.

The browser models seven sector norms. It does not reconstruct the 125 complex
state coefficients or their phases. For this spectral filter the displayed norm,
energy, selected occupancy and conditional projection fidelity are exactly
computable from those weights. The independent Python adapter checks them against
full 125×125 matrix evolution from `src/e47/`.

The browser seeded state uses Mulberry32 and exponential squared magnitudes in a
Casimir eigenbasis. Its seed is not equivalent to the supplied NumPy product-basis
seed. Isotropic weights are a deterministic sector distribution, not a claim
that every pure state's selected occupancy equals the rank fraction 47/125.

Selected weight zero makes target fidelity undefined; complete norm underflow
makes normalized occupancy undefined. These values serialize as `null`. Charts
clip positive errors below 1e-16 at the plotting floor; inspect receipts for exact
floating-point values. Continuous tau equals `gap * physical_model_time` in the
chosen mathematical units. For discrete filtering, tau = n * epsilon * gap is step bookkeeping, not an exact continuous-time equivalence. Neither is calibrated to laboratory time.

## Repairs and source scope

Original uploaded Python/JSON/CSV files remain byte-identical under
`research/e47/workbench-inputs/`, with SHA-256 provenance. They are archival inputs,
not the app runtime. The new `e47.workbench` adapter replaces the supplied
`measure_e47.py` hardcoded `/mnt/data` write with an explicit portable output:

```bash
PYTHONPATH=src python -m e47.workbench --geometry-only --output artifacts/geometry.npz
```

Geometry rebuilds the same 90 vertices, 135 edges and 47 faces, sorts vertices
around each supporting plane, and checks planar faces, edge incidence and graph
connectivity. It does not render the cube/pyramid certificate's potentially curved
patches as flat facets. Spin labels remain a chosen correspondence.

The supplied comparison CSV has no epsilon or generator provenance. Its radius
0.9946643266360042 differs from the optimal step's 15/17. A smaller epsilon could
explain the value but is only inferred. The original CSV is retained unchanged;
its material rows are described as reduced models rather than measurements.

## Workspaces and privacy

`workspace.json` holds observed navigation destinations. It contains no document
contents, tokens, or account metadata. JSON/CSV/Markdown exports can be transferred
to Google Workspace and Notion; Linear tracks delivery and GitHub hosts source.
These links are not automatic synchronization. Live hosted connectors remain
blocked until Sites provides eligibility discovery and publishing helpers.

No imports execute code. JSON is bounded to 2 MB, inputs and schema are validated,
results are recomputed, and text is rendered with `textContent`. External links
use HTTPS and `noopener noreferrer`. CSP disallows external scripts, inline
scripts, object embeds, and external fetches. Receipts are reproducibility records,
not signed cryptographic attestations. An experiment exists in browser memory
until exported; refreshing discards it.

## Validation

```bash
PYTHONPATH=src python -m pytest tests/test_e47_workbench.py -v
node --test website/interfaces/e47-research-workbench/engine.test.mjs
node website/interfaces/e47-research-workbench/smoke.mjs
python scripts/check_lab_contract.py
python scripts/check_instrument_contracts.py
```

Python matrix checks are performed when regenerating the bundle. The validation
screen displays their stored results; its browser verification separately checks
Python/JS reference parity, bounds and occupancy monotonicity.

The public HTML includes Open Graph and Twitter large-image metadata pointing to
`share-cover.jpg` (1200 × 630 JPEG). This cover was generated with OpenAI image
generation on 2026-10-10 and depicts illustrative crystal artwork, rather than
the measured mesh. Share services fetch the public HTML and image; existing
previews may need their cache refreshed after publication.
