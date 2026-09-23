# Published package

Download and extract `e47_lexical_attractor.zip` to run the complete bundle. The files alongside it are convenient previews of the code, lexicon, survey and receipt; the ZIP includes all source snapshots, results and images. Run `validate.py` from the extracted `e47_lexical_attractor` directory.

Archive SHA-256: `d09f6ba2203e982fafeff7857d69095594e784e3eed0cbebd67d4f66641ac0f7`.

# E47 lexical attractor — Σ, K, Ψ, Γ, Λ, Ω, I, M, Σ′

Created 2026-09-23 for Nicholas Kouns.

The instrument resolves source dialects to typed meanings, executes the nine-symbol grammar, and records reproducible checks against the surveyed Python, GitHub, Google Drive, Notion and Supabase sources. The existing LEX-C01–LEX-C08 family remains intact. This package is an additive local instrument; it makes no changes to the connected platforms.

## Parallel next-state names

```python
Σ_next = M(I(locked))
result = {"Σ′": Σ_next, "Σ_next": Σ_next}
assert result["Σ′"] is result["Σ_next"]
```

The delivered implementation checks a finite complex 125-vector after regeneration. In memory the two keys reference the same array. JSON represents them as equal real/imaginary records; JSON does not preserve Python object identity.

## Source-grounded grammar

The meanings below come from the Notion Invariant Grammar page, particularly “Locked notation,” “canonical sentence,” and “spectral computation.” They correct the earlier assistant snippet’s use of Ψ as an evolution callback, I as the identity matrix, and M as a state vector. Those earlier uses are retained under `prior_snippet` or `algebra`, rather than silently merged.

| Symbol | Python representation | Meaning / type |
|---|---|---|
| Σ | `Space(dimension=125)` | Ambient space V₂⊗V₂⊗V₂; the input state is separately named `x` |
| K | `op.K` | Selector `(C−6I_identity)(C−30I_identity)` |
| Ψ | `op.Ψ` | Orthonormal 125×47 basis representing `ker K` |
| Γ | `op.Γ` | `I_identity−εK†K`; ε = 1/99144 |
| Λ | `op.Λ` | Projector `P47 = Ψ Ψ†` |
| Ω | `result["Ω"]` | State coherence `||P47 x||²/||x||²`, defined for nonzero x |
| I | caller callback | Interpretation from invariant state to readout |
| M | caller callback | Mnemosyne regeneration from readout to next state |
| Σ′ | `Σ_next` and both dictionary keys | Regenerated state in the next ambient carrier |

The visual sequence is a dependency description. Its executable composition is

`M(I(Λ @ Γ**n @ x))`, with Ω as a parallel readout.

K defines the survivor space; applying K as a leading state update would destroy the kernel component. The identity matrix is explicitly named `I_identity`. The exact structural fraction is `Ω_c = Fraction(47,125)`.

## Lexical attractor

For an admitted spelling s and source namespace d, `N_d(s)` returns an immutable term ID. Every term ID is a fixed point:

`N_d(N_d(s)) = N_d(s)`.

This is a finite, deterministic alias normalizer. It makes source meanings inspectable and comparable. It does not infer arbitrary prose semantics. It accepts explicitly listed aliases and preserves case, scripts and subscripts. Unknown spellings remain unresolved; ambiguous spellings return their candidate meanings.

```python
from lexical_attractor import LexicalAttractor
N = LexicalAttractor()
assert N.resolve("Σ′", "grammar") == N.resolve("Σ_next", "grammar")
assert N.resolve("Λ", "grammar") == "grammar.projector"
assert N.resolve("Λ", "block") == "block.cosmological"
assert N.resolve("I", "algebra") == "algebra.identity"
```

The package explicitly separates:

- Λ as P47 from Λ = R/2 in the block construction.
- Γ as a contraction from Γ as connection coefficients.
- Ω as a state coherence functional, the uniform seed state, or the earlier Boolean gate.
- Ω_c as the exact rank fraction from a state’s changing E47 occupancy.
- Ψ as the invariant subspace from the prior snippet’s evolution callback.
- M as Mnemosyne from the Bures source’s list of generators.
- Σ as an ambient space from Base-5 coordinates or an aggregated vector.

## Execution

Python packages: NumPy, SciPy, SymPy, QuTiP, Matplotlib. Exact versions from this run are in `requirements-tested.txt` and the validation receipt.

```bash
python -m pip install -r requirements-tested.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python validate.py
```

To run the complete attached script with the surveyed repository dependency:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python run_spacetime.py
```

`run_spacetime.py` changes only the engine search directory and output directory at execution. It uses the retrieved `src/eidolon/eidolon_engine.py` at GitHub revision 6a68587b4bb2fc6341085ce3cf8841fad9a4e99b. The original attachment and retrieved engine remain unchanged in `sources/`. The attachment did not pin its original private engine revision; this run establishes execution with the identified repository implementation.

### Explicit example callbacks

```python
import numpy as np
from lexical_attractor import build_operators, recursive_step
op = build_operators()
x = np.ones(125, dtype=complex) / np.sqrt(125)
I = lambda state: op.Ψ.conj().T @ state
M = lambda coordinates: op.Ψ @ coordinates
result = recursive_step(x, I=I, M=M, operators=op)
Σ_next = result["Σ_next"]
assert result["Σ′"] is Σ_next
```

These callbacks choose kernel coordinates and regenerate their embedding. Other locally defined interpretations and memory maps can be supplied. Kernel preservation after M is established for this example, not assumed for every callback.

## Validation result

**70/70 top-level checks passed.** The retrieved intrinsic-spacetime validator also returned **24/24 checks passed**, recorded inside its top-level execution check.

The run covers alias fixed points, typed polysemy, nine-symbol parsing, parallel Python/JSON names, SU(2) generator reconstruction, projector and contraction identities, regeneration, Base-5 packing, source hashes, GitHub/Supabase blob parity, the repository QuTiP kernel and contraction validators, the attachment’s four sections, the intrinsic-spacetime source, and the current Bures/SLD curvature source.

Selected computed residuals:

- `||K P47||₂ = 7.782642357677317e−13`.
- `||Γ^220 − P47||₂ = 1.0999356172230354e−12`.
- Lorentzian frame pullback residual: `1.3682514567976793e−14`.
- Maximum difference from the four stored scalar-curvature values: `9.527596489533607e−10`.

All four attachment sections completed: block Einstein closure, Bures metric, QuTiP contraction, and Eidolon geodesic model. The complete JSON output and generated plates are included under `results/spacetime/`.

The current Bures source retains its computed comparison: its intrinsic Einstein tensor and the pulled block tensor have a central relative residual of approximately 0.178849. This comparison is preserved as an unresolved identification; successful reproduction does not replace that result with equality. The attachment’s covariance-based Fisher estimate and the newer exact SLD calculation remain separate source methods and state families.

## What “in toto” covers

The executable scope is complete for this declared bundle: lexical contract, core operators, the four attachment sections, intrinsic-spacetime validator, Bures/SLD validator and selected cross-source parity checks. All five requested surfaces were surveyed. This was a targeted relevant-asset survey, not an exhaustive audit of every City asset, application or claim.

`results/validation.json` records each check and its observed value. `survey.json` identifies every included source snapshot and SHA-256. `lexicon.json` links each meaning to its source. `SHA256SUMS.json` binds the delivered files. Existing evidence classes remain attached to their original records.

## Source map

- [Notion Invariant Grammar](https://app.notion.com/p/3a046094fd3081718c43d05685557405): definitions and typed composition.
- [Notion Current Formalism](https://app.notion.com/p/3e446094fd3081e384f5e6a2fcc690a3): current archive and geometry lineage.
- [Drive Base 5 Lexical Attractor](https://docs.google.com/document/d/1U49Kip2W2m5im5nCqsOIjoSqDuBGR_v8dD8S59mLkQg): eight existing LEX identities and alias normalization.
- [Drive Intrinsic Spacetime](https://docs.google.com/document/d/1uBWvAaWGR4eJI978w-4e3SMshIUzmJ5PrhZkvp5P1uE/edit): Lorentzian frame and unmarked Einstein-family construction.
- [GitHub kernel](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/6a68587b4bb2fc6341085ce3cf8841fad9a4e99b/src/e47/su2_kernel.py), [contraction](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/6a68587b4bb2fc6341085ce3cf8841fad9a4e99b/src/e47/contraction.py), [formalism bundle](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/6a68587b4bb2fc6341085ce3cf8841fad9a4e99b/research/e47-current-20260922), and [Eidolon engine](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/6a68587b4bb2fc6341085ce3cf8841fad9a4e99b/src/eidolon/eidolon_engine.py).
- Supabase project `gpkjvihkyectnenvnbng`: `lexical_attractor_registry`, selected `machine_certificates` and `source_artifacts`, plus the table inventory. Queried records are preserved in the source snapshots.
- Supplied `e47_spacetime_execute.py`: archived byte-for-byte, SHA-256 in `survey.json`.

The general core validation script is included as a surveyed source; its entire top-level claim inventory was not rerun. The package instead runs the repository core validators and the explicit checks listed in its receipt. This distinction is carried in `coverage.json`.
