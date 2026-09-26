begin;
select plan(6);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='coherence_runtime_contracts'),
  'rls enabled on coherence_runtime_contracts'
);
select policies_are('public', 'coherence_runtime_contracts', array['coherence runtime contracts public read']);
select policy_cmd_is('public', 'coherence_runtime_contracts', 'coherence runtime contracts public read', 'SELECT');

set local role anon;
select results_eq(
  $$select contract_code from public.coherence_runtime_contracts where contract_code = 'CIRP-COHERENCE-RUNTIME-1.0' and status = 'active' and access_scope = 'public'$$,
  $$values ('CIRP-COHERENCE-RUNTIME-1.0')$$,
  'anon reads active public runtime contract'
);
select throws_ok(
  $$insert into public.coherence_runtime_contracts (contract_code, title, version, contract_sha256, contract) values ('PGTAP','t','1',repeat('0',64),'{}'::jsonb)$$,
  '42501',
  null,
  'anon cannot insert runtime contract'
);

set local role authenticated;
select results_eq(
  $$select status from public.coherence_runtime_contracts where contract_code = 'CIRP-COHERENCE-RUNTIME-1.0'$$,
  $$values ('active')$$,
  'authenticated reads runtime contract'
);

select * from finish();
rollback;
