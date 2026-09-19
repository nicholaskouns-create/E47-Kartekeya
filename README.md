# E47-Kartekeya

**The Mathematical City · independent computational research software**

[![CI](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml)
[![Pages](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml)

E47-Kartekeya is a research codebase for finite-dimensional spectral computation, reproducible validation, interactive simulation, and provenance-preserving scientific interfaces.

The repository deliberately separates **validated mathematical core**, **research runtimes**, and **experimental simulation**. Public interfaces may compose these systems, but presentation does not upgrade evidence class and no console becomes authority over the independent instruments.

**Live laboratory:** https://nicholaskouns-create.github.io/E47-Kartekeya/

## Research map

| Layer | Path | Status | Role |
|---|---|---|---|
| E47 mathematical core | src/e47/ | validated core | SU(2) kernel, projector, contraction, semigroup, certificates |
| AETHERIS | src/aetheris/ | research runtime | receipt-oriented state transitions |
| MANTA | src/manta/ | experimental | vehicle / programmable-matter simulation |
| SKYRMION | website/interfaces/skyrmion/ | research simulator | conventional + explicitly separated experimental craft models |
| Syntax Jacob | website/interfaces/syntax-jacob/ | research simulator | 3I/ATLAS trajectory and coherence interface |
| CITY CORE | website/interfaces/kouns-core/ | research console | cross-interface launch and inspection surface |
| Visualizers | website/interfaces/visualizers/ | research instruments | independent scientific visualizers |

The machine-readable version of this map is [lab-manifest.json](lab-manifest.json).

## Canonical E47 object

The validated finite-dimensional construction uses

~~~text
V = V₂ ⊗ V₂ ⊗ V₂
dim(V) = 125

K = (C - 6I)(C - 30I)
E₄₇ = ker(K)
dim(E₄₇) = 47
~~~

Canonical invariants:

| Invariant | Value |
|---|---:|
| dim(V) | 125 |
| dim(E₄₇) | 47 |
| Coherence fraction | 47 / 125 |
| K² spectral gap | 11664 |
| K² max eigenvalue | 186624 |

The package currently supports E0/E1 claims for the finite mathematical core where backed by exact construction and deterministic machine validation. Simulation surfaces remain separately typed.

## Install

Published package:

~~~bash
pip install e47-kartekeya
~~~

Local research checkout:

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
pip install -e .
~~~

## Reproduce

Run the Python suite:

~~~bash
python -m pytest tests/ -v
~~~

Validate the repository architecture contract:

~~~bash
python scripts/check_lab_contract.py
~~~

Regenerate the E47 validation certificate:

~~~bash
python scripts/generate_validation_certificate.py
~~~

Compile a spectral-kernel certificate and passport:

~~~bash
python scripts/compile_spectral_kernel.py --spin 2 --copies 3 --select 2 5
~~~

Run browser/runtime checks with Node.js 22+:

~~~bash
node --test scripts/check_website.cjs scripts/check_e47_bridge.cjs scripts/check_eidolon_receipt_binding.mjs
~~~

See [docs/reproducibility.md](docs/reproducibility.md) for the complete path.

## Repository architecture

~~~text
src/e47/                 finite mathematical core
src/aetheris/            research runtime
src/manta/               experimental simulation

tests/                   executable invariants
certificates/            committed machine certificates
artifacts/               generated outputs
scripts/                 validation and compilation tools

website/                 canonical GitHub Pages root
website/interfaces/      independent interactive instruments
web/                     shared browser runtime library, not a second site

docs/                    architecture, scope, provenance, reproducibility
research/                open research lines
lab-manifest.json        machine-readable component/evidence map
~~~

The canonical Pages source is **only** website/. The root-level web/ directory contains shared browser runtime code and is intentionally not deployable as a second homepage.

## Evidence classes

| Class | Meaning |
|---|---|
| **E0** | exact mathematics |
| **E1** | deterministic machine reconstruction |
| **E2** | numerical experiment / simulation |
| **E3** | independent external replication |
| **E4** | empirical / experimental evidence |
| **H0** | hardware design or protocol |

See [docs/validation_scope.md](docs/validation_scope.md) for claim boundaries.

## Documentation

- [docs/lab_architecture.md](docs/lab_architecture.md) — component and interface architecture
- [docs/reproducibility.md](docs/reproducibility.md) — clean-checkout reproduction path
- [docs/validation_scope.md](docs/validation_scope.md) — validated and open claim classes
- [docs/provenance.md](docs/provenance.md) — implementation lineage and certificates
- [docs/aetheris_runtime.md](docs/aetheris_runtime.md) — AETHERIS runtime
- [docs/city_125_runtime.md](docs/city_125_runtime.md) — City-125 runtime
- [CONTRIBUTING.md](CONTRIBUTING.md) — local-component contribution pattern

## Public interfaces

Serve the canonical public surface locally:

~~~bash
python -m http.server 8000 --directory website
~~~

Then open http://127.0.0.1:8000/.

GitHub Pages deployment is performed by [.github/workflows/pages.yml](.github/workflows/pages.yml) after website validation succeeds.

## Development principle

The repository favors **additive, typed, independently testable instruments**.

A component may be surfaced through the Mathematical City without surrendering its local contract. Contradictions, open questions, experimental branches, and failed tests remain visible rather than being collapsed into a single narrative.

That separation is part of the research architecture.
