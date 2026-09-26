begin;
select plan(5);

select ok(
  (select relrowsecurity from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname='public' and c.relname='coherence_runtime_state'),
  'rls enabled on coherence_runtime_state'
);
select policies_are('public', 'coherence_runtime_state', array[]::name[]);

insert into public.coherence_runtime_state (
  runtime_code, state, contract_id, contract_digest, last_reason
) values (
  'PGTAP-RUNTIME-1',
  'COHERENT',
  'CIRP-COHERENCE-RUNTIME-1.0',
  repeat('e', 64),
  'pgtap'
)
on conflict (runtime_code) do nothing;

set local role anon;
select is_empty(
  $$select runtime_code from public.coherence_runtime_state where runtime_code = 'PGTAP-RUNTIME-1'$$,
  'anon cannot read runtime state'
);
select throws_ok(
  $$update public.coherence_runtime_state set last_reason = 'anon' where runtime_code = 'PGTAP-RUNTIME-1'$$,
  '42501',
  null,
  'anon cannot update runtime state'
);

set local role authenticated;
select is_empty(
  $$select state from public.coherence_runtime_state where runtime_code = 'PGTAP-RUNTIME-1'$$,
  'authenticated cannot read runtime state'
);

select * from finish();
rollback;
