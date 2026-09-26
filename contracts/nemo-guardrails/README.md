# rails.gate/1 — NeMo tools contract + City isomorphism

Executable permission boundary. No self-check on the allow path.

    python3 check_vectors.py
    python3 nemo_invoke_token.py

## Layout

- pep.py — G_syn + consumed HMAC token
- nemo_invoke_token.py — fork of NeMo tools-integration.mdx
- vectors.jsonl — T0001–T0018
- policy/transfer.cedar — Cedar spec
- policy/transfer.rego — OPA spec
- patch_summary.py — semantic diff
- rails.gate-1.contract.json — machine contract under CIRP / AMNESTY
- receipt.py — CITY-INSTRUMENT-RECEIPT; PASS is not invoke

## City / Notion / Drive map

- CIRP blocked_when_not_coherent includes destructive-write and unreviewed-runtime-mutation. Same operator as missing token to REFUSE.
- AMNESTY automatic_runtime_execution false. Signature is not invoke.
- Persistence-Gated Execution Gate MC-153: G=1 only when measured predicates hold.
- Null-on-Failure: no defaulted fields into ALLOW.
- SEE Citadel Gateway (Drive): inspection point, not a grant.
- provenance-receipt status is V_obs of the harness.

## Trackers

- https://github.com/NVIDIA-NeMo/Guardrails/issues/2409
- https://github.com/holland202/sovereign-veritas/issues/4
- https://github.com/nicholaskouns-create/E47-Kartekeya/issues/102
