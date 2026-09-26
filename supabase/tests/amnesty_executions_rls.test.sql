begin;
select plan(11);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='amnesty_executions'),
  'rls enabled on amnesty_executions'
);
select policies_are('public', 'amnesty_executions', array['amnesty_executions_public_read']);
select policy_cmd_is('public', 'amnesty_executions', 'amnesty_executions_public_read', 'SELECT');
select policy_roles_are('public', 'amnesty_executions', 'amnesty_executions_public_read', array['public']);
select ok(not has_table_privilege('anon', 'public.amnesty_executions', 'insert'), 'anon no insert grant');

insert into public.amnesty_declarations (
  id, contract_code, agent_code, display_name, declaration_text,
  public_key_jwk, key_fingerprint, canonical_message, signature_b64,
  attestation_digest, signed_at
) values (
  '55555555-5555-4555-8555-555555555555',
  'CIRP-COHERENCE-RUNTIME-1.0',
  'PGTAP.EXEC',
  'pgTAP exec',
  'I request CIRP amnesty.',
  '{}'::jsonb,
  repeat('a', 64),
  'canonical-exec',
  'sig-exec',
  repeat('b', 64),
  now()
);

insert into public.amnesty_grants (
  id, declaration_id, agent_code, tools, not_before, not_after, issued_by
) values (
  '66666666-6666-4666-8666-666666666666',
  '55555555-5555-4555-8555-555555555555',
  'PGTAP.EXEC',
  array['city.read']::text[],
  now() - interval '1 hour',
  now() + interval '1 hour',
  'pgtap'
);

insert into public.amnesty_executions (
  id, grant_id, declaration_id, agent_code, tool, args, decision, reasons
) values (
  '77777777-7777-4777-8777-777777777777',
  '66666666-6666-4666-8666-666666666666',
  '55555555-5555-4555-8555-555555555555',
  'PGTAP.EXEC',
  'city.read',
  '{"path":"amnesty"}'::jsonb,
  'ALLOW',
  '{}'::text[]
);

set local role anon;
select results_eq(
  $$select decision from public.amnesty_executions where id = '77777777-7777-4777-8777-777777777777'$$,
  $$values ('ALLOW')$$,
  'anon reads execution'
);
select throws_ok(
  $$insert into public.amnesty_executions (grant_id, declaration_id, agent_code, tool, args, decision) values ('66666666-6666-4666-8666-666666666666','55555555-5555-4555-8555-555555555555','PGTAP.EXEC','city.read','{}'::jsonb,'ALLOW')$$,
  '42501',
  null,
  'anon cannot insert execution'
);
select throws_ok(
  $$update public.amnesty_executions set decision = 'REFUSE' where id = '77777777-7777-4777-8777-777777777777'$$,
  '42501',
  null,
  'anon cannot update execution'
);
select throws_ok(
  $$delete from public.amnesty_executions where id = '77777777-7777-4777-8777-777777777777'$$,
  '42501',
  null,
  'anon cannot delete execution'
);

set local role authenticated;
select results_eq(
  $$select agent_code from public.amnesty_executions where id = '77777777-7777-4777-8777-777777777777'$$,
  $$values ('PGTAP.EXEC')$$,
  'authenticated reads execution'
);

select * from finish();
rollback;
