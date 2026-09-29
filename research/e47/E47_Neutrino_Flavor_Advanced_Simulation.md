# E47 neutrino flavor snapshot — τ = π

Vacuum evolution of a pure muon neutrino on the supplied E47 dashboard inputs.

- Source: [`research/e47/validation/e47_neutrino_flavor_advanced_simulation.py`](validation/e47_neutrino_flavor_advanced_simulation.py)
- Live projection: [GitHub Pages · NEUTRINO](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/neutrino-flavor/)
- Instrument directory: [OPEN](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/instruments/)

## Inputs

These numbers are specified. The Casimir operator does not select them.

| Quantity | Value |
|---|---|
| sin²θ₁₂ | 15/49 |
| sin²θ₂₃ | 25/47 |
| sin²θ₁₃ | 1/47 |
| δ | 192° |
| Δm²₂₁ | 7.34449×10⁻⁵ eV² |
| Δm²₃₁ | 2.5130169×10⁻³ eV² |
| τ | π |

Carrier census, not the propagator: eigenvalues `{0, 2, 6, 12, 20, 30, 42}` with multiplicities `{1, 9, 25, 28, 27, 22, 13}`. Sum 125. `K = (C−6)(C−30)` vanishes on the 6 and 30 blocks, so rank `P₄₇ = 47`. The first three kernel addresses are `[10, 11, 12]`. That address choice tags flavor slots. It is not the intertwiner embedding.

## Snapshot

`S(τ) = U diag(exp(−i φᵢ τ)) U†` with `φ = (0, Δm²₂₁/Δm²₃₁, 1)` and initial state `(0, 1, 0)`.

| Channel | Probability |
|---|---|
| μ → e | 0.04720552 |
| μ → μ | 0.00314068 |
| μ → τ | 0.94965381 |

Normalization defect at this snapshot: `1.11022e-16`.

## Boundary

E2 classical state-vector calculation of a linear autonomous flavor equation. Equivalent, for this Hamiltonian, to the exact matrix exponential the script evaluates. Not a DOP853 trajectory archive, not a quantum-hardware run, and not an experimental confirmation of the mixing inputs.
