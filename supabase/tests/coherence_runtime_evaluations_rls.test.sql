begin;
select plan(6);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='coherence_runtime_evaluations'),
  'rls enabled on coherence_runtime_evaluations'
);
select policies_are('public', 'coherence_runtime_evaluations', '{}');

insert into public.coherence_runtime_evaluations (
  id, contract_code, strategies, ubuntu_results, state_before, state_after, passed
) values (
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
  'CIRP-COHERENCE-RUNTIME-1.0',
  '[]'::jsonb,
  '{}'::jsonb,
  'COHERENT',
  'COHERENT',
  true
);

set local role anon;
select is_empty(
  $$select id from public.coherence_runtime_evaluations where id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'$$,
  'anon cannot read evaluations'
);
select throws_ok(
  $$insert into public.coherence_runtime_evaluations (contract_code, strategies, ubuntu_results, state_before, state_after, passed) values ('CIRP-COHERENCE-RUNTIME-1.0','[]'::jsonb,'{}'::jsonb,'COHERENT','COHERENT',true)$$,
  '42501',
  null,
  'anon cannot insert evaluation'
);

set local role authenticated;
select is_empty(
  $$select id from public.coherence_runtime_evaluations where id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'$$,
  'authenticated cannot read evaluations'
);

select * from finish();
rollback;
