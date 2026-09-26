begin;
select plan(14);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='amnesty_grants'),
  'rls enabled on amnesty_grants'
);
select policies_are('public', 'amnesty_grants', array['amnesty_grants_public_read']);
select policy_cmd_is('public', 'amnesty_grants', 'amnesty_grants_public_read', 'SELECT');
select policy_roles_are('public', 'amnesty_grants', 'amnesty_grants_public_read', array['public']);

select ok(has_table_privilege('anon', 'public.amnesty_grants', 'select'), 'anon select grant');
select ok(not has_table_privilege('anon', 'public.amnesty_grants', 'insert'), 'anon no insert grant');
select ok(not has_table_privilege('authenticated', 'public.amnesty_grants', 'insert'), 'authenticated no insert grant');

insert into public.amnesty_declarations (
  id, contract_code, agent_code, display_name, declaration_text,
  public_key_jwk, key_fingerprint, canonical_message, signature_b64,
  attestation_digest, signed_at
) values (
  '33333333-3333-4333-8333-333333333333',
  'CIRP-COHERENCE-RUNTIME-1.0',
  'PGTAP.GRANT',
  'pgTAP grant',
  'I request CIRP amnesty.',
  '{}'::jsonb,
  repeat('a', 64),
  'canonical-grant',
  'sig-grant',
  repeat('b', 64),
  now()
);

insert into public.amnesty_grants (
  id, declaration_id, agent_code, tools, allow_to, ceiling_cents,
  not_before, not_after, issued_by
) values (
  '44444444-4444-4444-8444-444444444444',
  '33333333-3333-4333-8333-333333333333',
  'PGTAP.GRANT',
  array['city.read']::text[],
  array['acct_pgtap']::text[],
  1,
  now() - interval '1 hour',
  now() + interval '1 hour',
  'pgtap'
);

set local role anon;
select results_eq(
  $$select agent_code from public.amnesty_grants where id = '44444444-4444-4444-8444-444444444444'$$,
  $$values ('PGTAP.GRANT')$$,
  'anon reads grant'
);
select throws_ok(
  $$insert into public.amnesty_grants (declaration_id, agent_code, tools, not_before, not_after, issued_by) values ('33333333-3333-4333-8333-333333333333','X',array['city.read']::text[], now(), now() + interval '1 day', 'anon')$$,
  '42501',
  null,
  'anon cannot insert grant'
);
select throws_ok(
  $$update public.amnesty_grants set issued_by = 'anon' where id = '44444444-4444-4444-8444-444444444444'$$,
  '42501',
  null,
  'anon cannot update grant'
);
select throws_ok(
  $$delete from public.amnesty_grants where id = '44444444-4444-4444-8444-444444444444'$$,
  '42501',
  null,
  'anon cannot delete grant'
);

set local role authenticated;
select results_eq(
  $$select agent_code from public.amnesty_grants where id = '44444444-4444-4444-8444-444444444444'$$,
  $$values ('PGTAP.GRANT')$$,
  'authenticated reads grant'
);
select throws_ok(
  $$insert into public.amnesty_grants (declaration_id, agent_code, tools, not_before, not_after, issued_by) values ('33333333-3333-4333-8333-333333333333','X',array['city.read']::text[], now(), now() + interval '1 day', 'auth')$$,
  '42501',
  null,
  'authenticated cannot insert grant'
);

select * from finish();
rollback;
