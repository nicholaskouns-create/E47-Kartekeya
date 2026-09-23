# E47 lexical spine checksum

Runtime spine:

```text
Σ → K → Ψ → Γ → Λ → Ω → I → M → Σ′
```

Canonical parse:

```text
grammar.ambient
→ grammar.selector
→ grammar.survivor
→ grammar.contraction
→ grammar.projector
→ grammar.coherence
→ grammar.interpretation
→ grammar.memory
→ grammar.next
```

Lexicon schema: `E47-LEXICAL-ATTRACTOR-1.0`.

## Locked bindings

- `K=(C-6I)(C-30I)` is not modified.
- `Λ=P47` is one cached full `125×125` matrix exposed as both the tomographic P47 gate and the Eidolon lock projector.
- Existing 7-sector and field-level visualizer views remain derived representations.
- `base5.carrier` is a typed `5×5×5` register with `index=25*x+5*y+z`; it does not alter `K`.
- QuTiP wraps `C`, `K`, and `Λ` on the same 125-dimensional carrier.
- Runtime recursion binds `I=Ψ†` and `M=Ψ`.
- `Σ′` is exported only through `next_state_record`; the lexical term table is not mutated.

## Checksum record

Deterministic seed: `470125`.

- kernel dimension: `47`
- projector rank: `47`
- kernel residual after lock: `2.8671498588897305e-12`
- machine-zero backward-error bound: `1.2129774839217246e-10`
- machine-zero reached: `PASS` on recursive round `1`
- `K` digest, rounded 12: `17ef4787e2d43769fdda7054e726b8730cfba012b23938815bcdd6fe1e0cdc9b`
- `Λ` digest, rounded 12: `5cfcc6e25f2e4ff70b5b1e3706452e9a6819dbc0c5dc8dbc3e014d45e8245121`

Executable: `spine_checksum.py`.

Portable record: `results/next_state_record.json`.

City mirror: `website/data/E47-NEXT-STATE-RECORD-20260923.json`.

External mirrors are recorded in the City source-artifact registry and the corresponding Notion/Drive exports.
