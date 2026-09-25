# Research Lab Architecture

E47-Kartekeya is organized as a research-software laboratory rather than a single application.

The architecture separates **mathematical objects**, **runtime systems**, **interactive instruments**, **evidence artifacts**, and **public presentation**. The separation is descriptive, not supervisory: instruments may remain independent, compete, fail, or evolve locally without being absorbed into one control layer.

## 1. Mathematical core

`src/e47/` contains the finite-dimensional E47 implementation.

Its contract is narrow:

- construct the SU(2) carrier and Casimir-derived kernel,
- construct and validate the rank-47 projector,
- expose contraction and semigroup machinery,
- generate deterministic validation results,
- serialize machine-readable certificates.

This layer is the strongest reproducibility surface in the repository and carries E0/E1 evidence where supported by the corresponding theorem or deterministic reconstruction.

## 2. Research runtimes

`src/aetheris/` and related runtime modules implement higher-level state-transition and receipt machinery.

These are research runtimes, not replacements for the mathematical core. A runtime may consume E47 invariants, emit provenance, or drive an interface while preserving its own local contract.

## 3. Experimental simulation

`src/manta/`, SKYRMION experimental craft models, propulsion interfaces, and related work remain explicitly simulation-typed unless and until a separate empirical or hardware record exists.

A simulation can be useful, internally coherent, and technically sophisticated without being silently promoted to physical evidence.

## 4. Interactive research instruments

The canonical public web root is **`website/`**.

Important surfaces include:

- `website/interfaces/skyrmion/` — flagship multi-domain flight simulator
- `website/interfaces/syntax-jacob/` — 3I/ATLAS trajectory and coherence interface
- `website/interfaces/kouns-core/` — cross-interface research console
- `website/interfaces/flight/` — flight runtime and EIDOLON/AETHERIS bindings

The retired `website/interfaces/visualizers/` route is a forwarding tombstone only; current instruments are exposed through the active City surfaces and registry.\n\nThe separate root-level `web/` directory is **not a second website**. It is a shared browser-runtime library containing graphics profiles, accelerator code, schemas, and worker contracts.

## 5. Evidence artifacts

Evidence remains inspectable outside the visual interfaces:

- `certificates/` — committed machine certificates
- `artifacts/` — generated outputs
- `tests/` — executable invariants and regression checks
- `docs/validation_scope.md` — supported and unsupported claim classes
- `docs/provenance.md` — implementation lineage
- `lab-manifest.json` — machine-readable component map

No visual effect, runtime integration, or successful simulation changes an evidence class by itself.

## 6. Repository contract

The repository intentionally preserves plurality while enforcing a small number of structural invariants:

1. `website/` is the only GitHub Pages source.
2. `src/e47/` is the canonical finite-dimensional E47 implementation.
3. Every component listed in `lab-manifest.json` must resolve to a real path.
4. Mature and experimental components must remain distinguishable.
5. CI tests mathematical invariants, website integrity, and the lab manifest independently.
6. Browser frame rate must not determine simulation time evolution.
7. Deep interfaces remain directly addressable even when surfaced through CITY CORE or the homepage.

## 7. Development pattern

A new research instrument can enter the repository without requesting architectural ownership over existing work.

A strong addition normally supplies:

- one narrow purpose,
- a declared maturity state,
- a declared evidence class,
- a direct path or module boundary,
- a deterministic test where possible,
- provenance for external data,
- a failure mode that is visible rather than silently coerced.

This keeps the repository legible while preserving independent lines of investigation.
