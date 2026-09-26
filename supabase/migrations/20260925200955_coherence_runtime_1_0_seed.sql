insert into public.coherence_contracts
(contract_id, version, title, contract_digest, contract_body, status)
values (
  'CIRP-COHERENCE-RUNTIME-1.0',
  '1.0.0',
  'Coherence, Runtime 1.0',
  '3804f50da447b6abb9fc9c4bfc60aecd43f6467842e65b0db953afc6e0f59b76',
  '{"canonical_source":"github:E47-Kartekeya/contracts/coherence-runtime-1.0.contract.json"}'::jsonb,
  'active'
)
on conflict (contract_id) do update set
  version=excluded.version,
  title=excluded.title,
  contract_digest=excluded.contract_digest,
  contract_body=excluded.contract_body,
  status=excluded.status;
