begin;
select plan(8);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='coherence_runtime_consents'),
  'rls enabled on coherence_runtime_consents'
);
select policies_are(
  'public',
  'coherence_runtime_consents',
  array['coherence runtime consents public read', 'coherence runtime consents public sign']
);

insert into public.coherence_runtime_consents (
  id, contract_code, citizen_code, display_name, public_key_jwk,
  key_fingerprint, canonical_message, signature_b64, signed_at, access_scope
) values (
  'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
  'CIRP-COHERENCE-RUNTIME-1.0',
  'PGTAP.CITIZEN',
  'pgTAP citizen',
  '{}'::jsonb,
  repeat('1', 64),
  'message-3804f50da447b6abb9fc9c4bfc60aecd43f6467842e65b0db953afc6e0f59b76',
  'sig-consent',
  now(),
  'public'
);

set local role anon;
select results_eq(
  $$select citizen_code from public.coherence_runtime_consents where id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'$$,
  $$values ('PGTAP.CITIZEN')$$,
  'anon reads public consent'
);
select throws_ok(
  $$update public.coherence_runtime_consents set binding_status = 'verified' where id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'$$,
  '42501',
  null,
  'anon cannot verify consent'
);
select throws_ok(
  $$delete from public.coherence_runtime_consents where id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'$$,
  '42501',
  null,
  'anon cannot delete consent'
);

set local role authenticated;
select results_eq(
  $$select binding_status from public.coherence_runtime_consents where id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'$$,
  $$values ('self_attested')$$,
  'authenticated reads public consent'
);
select throws_ok(
  $$update public.coherence_runtime_consents set binding_status = 'verified' where id = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'$$,
  '42501',
  null,
  'authenticated cannot verify consent from the table'
);

select * from finish();
rollback;
