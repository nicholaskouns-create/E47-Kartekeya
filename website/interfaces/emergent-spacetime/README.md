# 31 EMERGE · Half-Occupancy

Browser engine and explainer for the Half-Occupancy Theorem:
**g₀₀ = p̈ ⁄ 4**, so the metric signature turns Lorentzian exactly at p = ½.

Live: <https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/emergent-spacetime/>

| file | role |
|------|------|
| `flow.mjs` | The occupancy flow and the signature, in exact BigInt rationals — the same integers `HalfOccupancy.lean` and `HalfOccupancy.v` decide. No browser dependencies. |
| `flow.test.mjs` | 21 tests, run by `pages.yml` on every push. Checks the engine against the proved integers and against the canonical kernel contract. |
| `app.mjs` | Visualizer and the five-stage instrument chain. |
| `index.html`, `spacetime.css` | The page. The proof and the scope statements are static and complete without JavaScript. |

## The chain

The page holds no private copy of the kernel, the quantum simulator or the
learner. It calls the instruments already on the site, and fails closed — a
stage runs only if the one above it passed.

1. **Bind** — `shared/e47-kernel-binding.js`. Refuses to continue unless the
   constants this page derived (ε∗, ρ∗, 47/125, roots [6,30], 11664, 186624)
   match `src/e47` on all seven fields.
2. **Flow** — exact rational steps and the first Lorentzian step.
3. **Quantum** — `observatory/qgnn.mjs`. Drives the four compressed eigengates
   of the 47-dimensional carrier with angles set by the occupancy, and measures
   that the state stays normalized. That invariance is the theorem's premise, so
   it is measured rather than assumed (observed deviation ~5×10⁻¹⁶).
4. **Learn** — `observatory/engine.mjs`. The flow generates labelled samples of
   (centred occupancy, flow speed); the trainer is never given ½, and the page
   bisects its decision surface to see what it settled on. Across ten sample
   seeds the median miss is 1.8×10⁻³ and the worst 4.3×10⁻³ — sample-limited,
   not a training artefact.
5. **Receipt** — one record in the seed shape SEE ingests, so a run can be
   mirrored as source-bound evidence rather than a screenshot.

Proofs and certificates: [`docs/emergent-spacetime`](../../../docs/emergent-spacetime).
