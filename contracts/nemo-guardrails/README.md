# rails.gate/1

`ValidSig ⊭ Invoke`. Invoke only by ∧I of Candidate, G_syn, X.

## Formalism

- [INVOKE_BY_AND_I.md](INVOKE_BY_AND_I.md) — sequent plate
- [invoke_by_and_introduction.py](invoke_by_and_introduction.py) — line checker (30/30)
- [validsig_does_not_entail_invoke.py](validsig_does_not_entail_invoke.py) — predicate lattice (10/10)

## PEP

- [pep.py](pep.py) — G_syn + consumed HMAC token
- [nemo_invoke_token.py](nemo_invoke_token.py) — generate() is proposal; invoke gated
- [vectors.jsonl](vectors.jsonl) · [check_vectors.py](check_vectors.py) — T0001–T0018
- [policy/transfer.cedar](policy/transfer.cedar) · [policy/transfer.rego](policy/transfer.rego)
- [amnesty_execute.py](amnesty_execute.py) — A0001/A0002/A0003/A0016

## Contracts

- [rails.gate-1.contract.json](rails.gate-1.contract.json)
- ../../contracts/amnesty-1.0.contract.json
- [receipt.py](receipt.py) — PASS is V_obs, not X
- [patch_summary.py](patch_summary.py)
- [NVIDIA-2409.md](NVIDIA-2409.md)

## Runtime (live)

- ../../supabase/functions/coherence-runtime/index.ts
- ../../supabase/functions/coherence-runtime/execute_gate.ts
- ../../supabase/migrations/20260926_amnesty_execute_gate.sql
- GET https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/coherence-runtime

## Trackers

- https://github.com/NVIDIA-NeMo/Guardrails/issues/2409
- https://github.com/holland202/sovereign-veritas/issues/4
- https://github.com/nicholaskouns-create/E47-Kartekeya/issues/102
