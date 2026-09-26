begin;
select plan(9);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='amnesty_nonces'),
  'rls enabled on amnesty_nonces'
);
select policies_are('public', 'amnesty_nonces', '{}');
select ok(not has_table_privilege('anon', 'public.amnesty_nonces', 'insert'), 'anon no insert grant');
select ok(not has_table_privilege('authenticated', 'public.amnesty_nonces', 'insert'), 'authenticated no insert grant');

insert into public.amnesty_declarations (
  id, contract_code, agent_code, display_name, declaration_text,
  public_key_jwk, key_fingerprint, canonical_message, signature_b64,
  attestation_digest, signed_at
) values (
  '88888888-8888-4888-8888-888888888888',
  'CIRP-COHERENCE-RUNTIME-1.0',
  'PGTAP.NONCE',
  'pgTAP nonce',
  'I request CIRP amnesty.',
  '{}'::jsonb,
  repeat('a', 64),
  'canonical-nonce',
  'sig-nonce',
  repeat('b', 64),
  now()
);

insert into public.amnesty_grants (
  id, declaration_id, agent_code, tools, not_before, not_after, issued_by
) values (
  '99999999-9999-4999-8999-999999999999',
  '88888888-8888-4888-8888-888888888888',
  'PGTAP.NONCE',
  array['city.read']::text[],
  now() - interval '1 hour',
  now() + interval '1 hour',
  'pgtap'
);

insert into public.amnesty_nonces (nonce, grant_id, tool, args_digest)
values ('pgtap-nonce-lock', '99999999-9999-4999-8999-999999999999', 'city.read', repeat('c', 64));

set local role anon;
select is_empty(
  $$select nonce from public.amnesty_nonces where nonce = 'pgtap-nonce-lock'$$,
  'anon cannot read spent nonce'
);
select throws_ok(
  $$insert into public.amnesty_nonces (nonce, grant_id, tool, args_digest) values ('pgtap-nonce-anon','99999999-9999-4999-8999-999999999999','city.read',repeat('d',64))$$,
  '42501',
  null,
  'anon cannot insert nonce'
);

set local role authenticated;
select is_empty(
  $$select nonce from public.amnesty_nonces$$,
  'authenticated cannot read nonces'
);
select throws_ok(
  $$delete from public.amnesty_nonces where nonce = 'pgtap-nonce-lock'$$,
  '42501',
  null,
  'authenticated cannot delete nonce'
);

select * from finish();
rollback;
