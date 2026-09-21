# E47-Kartekeya · The Mathematical City

Independent research software by **Nick Kouns**: finite-dimensional spectral mathematics, quantum instruments, flight simulations, and inspectable computational records.

**[Fly EIDOLON](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight)** · **[Open the City](https://nicholaskouns-create.github.io/E47-Kartekeya/)** · **[Q5 cube](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/)** · **[All instruments](docs/instruments.md)** · **[Documentation](docs/README.md)**

[![CI](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml)
[![Pages](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml)

## Start here

| You want to… | Start with |
|---|---|
| Try the work | [EIDOLON flight](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight), then the [instrument directory](docs/instruments.md) |
| Understand the mathematics | [E47 research notes](research/e47/README.md) and [Python implementation](src/e47/) |
| Reproduce a result | [Reproducibility guide](docs/reproducibility.md), [tests](tests/), and [certificates](certificates/README.md) |
| Develop an instrument | [Source map](src/README.md), [architecture](docs/lab_architecture.md), and [contributing](CONTRIBUTING.md) |

## Open an instrument

| Instrument | Purpose | Source |
|---|---|---|
| [CITY CORE / EIDOLON](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight) | Flight entry and direct instrument navigation | [Core](website/interfaces/kouns-core/) · [EIDOLON binding](website/interfaces/flight/eidolon/) |
| [MANTA](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manta/) | Morphing aircraft simulation with a fixed baseline | [Flight app](website/interfaces/manta/) · [Python model](src/manta/) |
| [Syntax Jacob](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/syntax-jacob/) | 3I/ATLAS trajectory and propulsion interface | [Source and provenance](website/interfaces/syntax-jacob/) |
| [THE MATRIX](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/matrix/) | Quantum circuit and statevector instrument | [Source](website/interfaces/matrix/) |
| [CITY 125](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/city-125/) | Visual debugger for the 125-state runtime | [Runtime guide](docs/city_125_runtime.md) |
| [Q5](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/) | 5×5×5 packing ledger. One word per cell | [q5/](q5/) · [`host.py`](q5/host.py) |
| [Visualizers](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/visualizers/) | Independent scientific visualizer portals | [Source](website/interfaces/visualizers/) |
| [SKYRMION](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/skyrmion/) | Conventional and experimental flight models | [Source](website/interfaces/skyrmion/) |
| [Propulsion Atlas](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/propulsion/) | Flight and propulsion interface directory | [Source](website/interfaces/propulsion/) |

[Browse every interface, including companion views and external-app shells →](docs/instruments.md)

## Find the work

| Directory | Contents |
|---|---|
| [q5/](q5/) | Frozen 125-word packing ledger, codec, validator, one-pass `host.py` |
| [src/](src/README.md) | E47 mathematics, AETHERIS state transitions, MANTA Python model |
| [website/](website/) | GitHub Pages source and independent browser instruments |
| [web/](web/README.md) | Shared browser graphics modules |
| [research/](research/README.md) | E47 theorem notes, open proof obligations, Stargate research |
| [docs/](docs/README.md) | Guides grouped by task and instrument |
| [scripts/](scripts/README.md) · [tests/](tests/) | Reproduction commands and executable checks |
| [certificates/](certificates/README.md) · [trajectories/](trajectories/README.md) | Committed certificates and flight-replay records |
| [contracts/](contracts/) · [lab-manifest.json](lab-manifest.json) | Existing component, receipt, and failure formats |
| [city/external-agents/](city/external-agents/README.md) | External-worker integration and local contracts |

Each instrument retains its own entry point, assumptions, evidence, and implementation. The [instrument directory](docs/instruments.md) is navigation; it does not replace those interfaces.

## Run locally

For the browser interfaces, serve the existing `website/` directory:

~~~bash
python q5/host.py serve
~~~

That command validates `q5/cells.jsonl`, writes `website/interfaces/q5/` from the ledger, and hosts the City site including the cube. Equivalent static serve:

~~~bash
python -m http.server 8000 --directory website
~~~

Open [localhost:8000](http://localhost:8000/) or [the cube](http://localhost:8000/interfaces/q5/). Interfaces that use external services still require those services.

For Python development, use **Python 3.12+** from the repository root:

~~~bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e . -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
~~~

Use **Node.js 22+** for browser-runtime checks. See the [command directory](scripts/README.md) and [complete reproduction guide](docs/reproducibility.md).

## Finite E47 core

The construction uses `V = V₂ ⊗ V₂ ⊗ V₂`, total Casimir `C`, and `K = (C − 6I)(C − 30I)`. Its selected space is `E₄₇ = ker(K)`.

| Invariant | Value |
|---|---:|
| Carrier dimension | 125 |
| Kernel dimension | 47 |
| Kernel fraction | 47 / 125 |
| K² spectral gap | 11664 |
| K² largest eigenvalue | 186624 |

Exact mathematics, machine reconstruction, simulations, and empirical work have separate evidence labels. The [validation scope](docs/validation_scope.md), [provenance](docs/provenance.md), and each instrument's local record describe the supported claims.

## Related repository

[nicholaskouns-create.github.io](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io) contains the personal-site atlas and an earlier research-code snapshot. This repository contains the current E47 package and expanded instrument collection.

[Research atlas on Notion](https://mathematicalcity.notion.site/?pvs=74) · [How to cite](CITATION.cff) · [License](LICENSE) · [Contribute](CONTRIBUTING.md)
