alter table public.amnesty_grants enable row level security;
alter table public.amnesty_executions enable row level security;
alter table public.amnesty_nonces enable row level security;
alter table public.coherence_runtime_state enable row level security;
alter table public.coherence_runtime_evaluations enable row level security;

drop policy if exists amnesty_grants_public_read on public.amnesty_grants;
create policy amnesty_grants_public_read
  on public.amnesty_grants
  for select
  to public
  using (true);

drop policy if exists amnesty_executions_public_read on public.amnesty_executions;
create policy amnesty_executions_public_read
  on public.amnesty_executions
  for select
  to public
  using (true);

comment on policy amnesty_grants_public_read on public.amnesty_grants is
  'Public SELECT only. Insert/update/delete stay service_role via coherence-runtime.';
comment on policy amnesty_executions_public_read on public.amnesty_executions is
  'Public SELECT only. Insert/update/delete stay service_role via coherence-runtime.';
