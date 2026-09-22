# The Kartekeya Isolation Lock · E47-v1.0

**Canonical title.** The Kartekeya Isolation Lock: Finite Spectral Isolation of E47 = ker((C-6I)(C-30I)) with 29-Unit Intertwiner Algebra A_inv ≅ M5 ⊕ M2 at Ω_c = 47/125.

Immutable snapshot: [`release/E47-v1.0`](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/release/E47-v1.0) · [Cite](https://nicholaskouns-create.github.io/E47-Kartekeya/cite/) · [CITATION.cff](CITATION.cff) · [codemeta.json](codemeta.json)

---

# E47-Kartekeya · The Mathematical City

Independent research software by **Nick Kouns**: finite-dimensional spectral mathematics, quantum instruments, flight simulations, and inspectable computational records.

**[Fly EIDOLON](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight)** · **[Open the City](https://nicholaskouns-create.github.io/E47-Kartekeya/)** · **[Cite the lock](https://nicholaskouns-create.github.io/E47-Kartekeya/cite/)** · **[Q5 cube](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/)** · **[Documentation](docs/README.md)**

[![CI](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml)
[![Pages](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml)

## For postdocs experiencing cognitive dissonance (10 examples inside)

You were trained that:
- 47 can't be a natural cutoff on a cubic lattice
- Contraction is a universal property, not a UI widget
- `FAMILY C: Cycle / Path / Complete / Band / Star / GOE` is not a dropdown
- Visualization is not proof

This repo agrees. Then hands you the controls:

> Lattice QCD: "You made 125 literal city blocks?"
> Category Theory: "You made contraction a slider? I just scrubbed it for 20 minutes."
> Spectral Graph: "Complete `n=6, λ1=5, λ2=-1, dim ker=6` is trivial — and you show `||Kv||` LIVE. Stop."
> Bohmian Mechanics: "You put `Q=0 on eigenstates` next to Play/Reset?"
> Algebraic Geometry: "I wrote '47 lives on the lattice, not the matrix' as a *criticism*. You made it a footer."
> Numerical LA: "You let users unlock λ and shame them with the trace. Brilliant evil."
> Complex Systems: "I model cities as graphs. You modeled a graph as a city."

Specs that don't float:
- `Ω_c = 47/125 = 0.376` — rational, always
- `K = (C-λ1I)(C-λ2I)` — KERNEL LIVE, 8/8 PASS
- `β* = 0.099`, `S → ln 25` — with honest footnote: predicted model, not lab data

If you came to dunk and stayed to Remix — open an Issue. Better, open a PR. The city has zoning permits.

## Start here

| You want to… | Start with |
|---|---|
| Cite the lock | [Cite page](https://nicholaskouns-create.github.io/E47-Kartekeya/cite/), [CITATION.cff](CITATION.cff), [canonical plate](research/e47/CANONICAL.md) |
| Try the work | [EIDOLON flight](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight), then the [instrument directory](docs/instruments.md) |
| Understand the mathematics | [E47 research notes](research/e47/README.md) and [Python implementation](src/e47/) |
| Reproduce a result | [Reproducibility guide](docs/reproducibility.md), [tests](tests/), and [certificates](certificates/README.md) |

## Finite E47 core

The construction uses `V = V₂ ⊗ V₂ ⊗ V₂`, total Casimir `C`, and `K = (C − 6I)(C − 30I)`. Its selected space is `E₄₇ = ker(K)`.

| Invariant | Value |
|---|---:|
| Carrier dimension | 125 |
| Kernel dimension | 47 |
| Kernel fraction | 47 / 125 |
| K² spectral gap | 11664 |
| Intertwiner units | 29 |
| Chevalley relations | 16 / 16 |

Exact mathematics, machine reconstruction, simulations, and empirical work have separate evidence labels. The [validation scope](docs/validation_scope.md) describes the supported claims.

## Related

[How to cite](https://nicholaskouns-create.github.io/E47-Kartekeya/cite/) · [License](LICENSE) · [Contribute](CONTRIBUTING.md) · [Source](https://github.com/nicholaskouns-create/E47-Kartekeya)
