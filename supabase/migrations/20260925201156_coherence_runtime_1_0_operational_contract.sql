insert into public.coherence_runtime_contracts
(contract_code, title, version, contract_sha256, contract, status, evidence_class, source_url, access_scope)
values (
  'CIRP-COHERENCE-RUNTIME-1.0',
  'Coherence, Runtime 1.0',
  '1.0.0',
  '3804f50da447b6abb9fc9c4bfc60aecd43f6467842e65b0db953afc6e0f59b76',
  '{"boundary":"computational governance contract"}'::jsonb,
  'active',
  'E1',
  'https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/contracts/coherence-runtime-1.0.contract.json',
  'public'
)
on conflict (contract_code) do update set
  title=excluded.title,
  version=excluded.version,
  contract_sha256=excluded.contract_sha256,
  contract=excluded.contract,
  status=excluded.status,
  updated_at=now();

drop policy if exists "coherence runtime contracts public read" on public.coherence_runtime_contracts;
create policy "coherence runtime contracts public read"
on public.coherence_runtime_contracts
for select
to anon, authenticated
using (status='active' and access_scope='public');

drop policy if exists "coherence runtime consents public read" on public.coherence_runtime_consents;
create policy "coherence runtime consents public read"
on public.coherence_runtime_consents
for select
to anon, authenticated
using (access_scope='public');

drop policy if exists "coherence runtime consents public sign" on public.coherence_runtime_consents;
create policy "coherence runtime consents public sign"
on public.coherence_runtime_consents
for insert
to anon, authenticated
with check (
  contract_code='CIRP-COHERENCE-RUNTIME-1.0'
  and signature_method='ECDSA_P256_SHA256'
  and status='active'
  and binding_status='self_attested'
  and access_scope='public'
  and length(trim(citizen_code)) between 2 and 128
  and length(trim(display_name)) between 1 and 160
  and length(trim(key_fingerprint))=64
  and length(trim(canonical_message)) between 32 and 4000
  and canonical_message like '%3804f50da447b6abb9fc9c4bfc60aecd43f6467842e65b0db953afc6e0f59b76%'
  and length(trim(signature_b64)) > 20
);
