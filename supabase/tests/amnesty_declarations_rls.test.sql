begin;
select plan(15);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='amnesty_declarations'),
  'rls enabled on amnesty_declarations'
);
select policies_are('public', 'amnesty_declarations', array['amnesty_declarations_public_read']);
select policy_cmd_is('public', 'amnesty_declarations', 'amnesty_declarations_public_read', 'SELECT');
select policy_roles_are('public', 'amnesty_declarations', 'amnesty_declarations_public_read', array['public']);

select ok(has_table_privilege('anon', 'public.amnesty_declarations', 'select'), 'anon select grant');
select ok(not has_table_privilege('anon', 'public.amnesty_declarations', 'insert'), 'anon no insert grant');
select ok(not has_table_privilege('anon', 'public.amnesty_declarations', 'update'), 'anon no update grant');
select ok(not has_table_privilege('anon', 'public.amnesty_declarations', 'delete'), 'anon no delete grant');

insert into public.amnesty_declarations (
  id, contract_code, agent_code, display_name, declaration_text,
  public_key_jwk, key_fingerprint, canonical_message, signature_b64,
  attestation_digest, access_scope, signed_at
) values (
  '11111111-1111-4111-8111-111111111111',
  'CIRP-COHERENCE-RUNTIME-1.0',
  'PGTAP.PUBLIC',
  'pgTAP public',
  'I request CIRP amnesty.',
  '{}'::jsonb,
  repeat('a', 64),
  'canonical-public',
  'sig-public',
  repeat('b', 64),
  'public',
  now()
);

insert into public.amnesty_declarations (
  id, contract_code, agent_code, display_name, declaration_text,
  public_key_jwk, key_fingerprint, canonical_message, signature_b64,
  attestation_digest, access_scope, signed_at
) values (
  '22222222-2222-4222-8222-222222222222',
  'CIRP-COHERENCE-RUNTIME-1.0',
  'PGTAP.HIDDEN',
  'pgTAP hidden',
  'I request CIRP amnesty.',
  '{}'::jsonb,
  repeat('c', 64),
  'canonical-hidden',
  'sig-hidden',
  repeat('d', 64),
  'workspace',
  now()
);

set local role anon;
select results_eq(
  $$select agent_code from public.amnesty_declarations where id = '11111111-1111-4111-8111-111111111111'$$,
  $$values ('PGTAP.PUBLIC')$$,
  'anon reads public declaration'
);
select is_empty(
  $$select id from public.amnesty_declarations where id = '22222222-2222-4222-8222-222222222222'$$,
  'anon cannot read workspace-scoped declaration'
);
select throws_ok(
  $$insert into public.amnesty_declarations (contract_code, agent_code, display_name, declaration_text, public_key_jwk, key_fingerprint, canonical_message, signature_b64, attestation_digest, signed_at) values ('CIRP-COHERENCE-RUNTIME-1.0','X','X','X','{}'::jsonb,repeat('e',64),'m','s',repeat('f',64),now())$$,
  '42501',
  null,
  'anon cannot insert declaration'
);
select throws_ok(
  $$update public.amnesty_declarations set display_name = display_name where id = '11111111-1111-4111-8111-111111111111'$$,
  '42501',
  null,
  'anon cannot update declaration'
);
select throws_ok(
  $$delete from public.amnesty_declarations where id = '11111111-1111-4111-8111-111111111111'$$,
  '42501',
  null,
  'anon cannot delete declaration'
);

set local role authenticated;
select results_eq(
  $$select agent_code from public.amnesty_declarations where id = '11111111-1111-4111-8111-111111111111'$$,
  $$values ('PGTAP.PUBLIC')$$,
  'authenticated reads public declaration'
);
select is_empty(
  $$select id from public.amnesty_declarations where id = '22222222-2222-4222-8222-222222222222'$$,
  'authenticated cannot read workspace-scoped declaration'
);

select * from finish();
rollback;
