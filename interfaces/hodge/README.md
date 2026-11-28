# Temporal Hodge Observatory · first-principles instrument

A local-first, responsive HTML/JavaScript instrument for the specified chain:

`Xₜ → Rε(Xₜ) → Δ₁ → ker(Δ₁) → Pₜ → Fₜ₊Δₜ → C_seal → (Fₜ₊Δₜ, r)`

## Run

Open `index.html` in a modern browser; SHA-256 operations require a secure context (HTTPS or localhost). No external libraries, API requests, servers, account permissions or data uploads are required.

**Live pages:** [Identity Hodge instrument](https://nicholaskouns-create.github.io/Identity/site/hodge/) · [E47-Kartekeya instrument](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/hodge/)

Choose a geometry, set epsilon and time, watch the VR complex, compute its B₁, B₂, Δ₁ spectrum and harmonic projector, adjust contraction iterations, and commit/reveal a time-horizon Betti forecast. The instrument exports its locally computed state and receipt as JSON.

## Theorems

- `Δ₁ = B₁ᵀ B₁ + B₂ B₂ᵀ`, `ker Δ₁ ≅ H₁(Rε(Xₜ); ℝ)`.
- `P = UUᵀ` is the orthogonal harmonic projector, with `P²=P=Pᵀ`, `Δ₁P=0`.
- `β₀−β₁+β₂=V−E+T`; when `(V,E,T)=(20,20,0)`, `β₁=β₀`. A variable ε or actual topological transition changes simplex counts, so the full formula is used.
- For `λmin⁺>0`, `η=2/(λmin⁺+λmax)` yields `||(I−ηΔ₁)ⁿ−P||₂=ρⁿ`, `ρ=max_{λ>0}|1−ηλ|`. Empty/zero cases handled separately.
- In a fixed edge basis, `Q(s)=exp(−isΔ₁)` satisfies `Q(s)P Q(s)†=P`. This is an algebraic unitary model, not quantum-hardware data.
- Temporal subspace comparison embeds all edges in the canonical 190-dimensional edge space. Whole-subspace retention uses minimum principal cosine; the maximum cosine is reported separately.
- Forecast seal: `C=SHA256(JSON(F) || "\\n" || r)`, with a fresh 256-bit nonce. State commitments chain as `Mₜ=SHA256(Mₜ₋₁ || "\\n" || JSON(Sₜ))`; serialization is implementation-defined and reproducible within this app, not a universal cross-language protocol.

## Independently recomputed reference cases

Validated in this session with Python/NumPy/SciPy as well as the browser JavaScript numerical core (Node VM).

| Quantity | 20-cycle | Two 10-cycles |
|---|---:|---:|
| V, E, T | 20,20,0 | 20,20,0 |
| β₀, β₁ | 1,1 | 2,2 |
| Positive spectral gap | 0.09788696740969231 | 0.38196601125010404 |
| ‖P²−P‖F | 3.98e−16 | 5.80e−16 |
| ‖Δ₁P‖F | 1.44e−15 | 1.50e−15 |
| ‖Q†Q−I‖F (s=0.7) | 1.76e−15 | 1.59e−15 |
| ‖QPQ†−P‖F | 1.23e−15 | 1.29e−15 |

A third JavaScript test at the end of the transition (`ε=0.35,t=1`) yielded `V=20,E=30,T=10,β₀=1,β₁=2` and satisfied the full Euler identity and numerical projector tests.

The forecast uses a **persistence baseline** (predicts the current β₁) and may fail when topology changes. Cryptographic binding and forecast accuracy are separate checks. No quantum hardware was used.

This app is additive to existing E₄₇ instruments and does not replace other research methods or independent proof systems.
