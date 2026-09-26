create or replace function public.amnesty_reject_status_promotion()
returns trigger
language plpgsql
set search_path = public
as $function$
begin
  if tg_op = 'UPDATE' and new.civic_status is distinct from old.civic_status and new.civic_status not in ('candidate','rejected','withdrawn') then
    raise exception 'amnesty civic_status is not an execute bit';
  end if;
  if tg_op = 'UPDATE' and new.civic_status = 'candidate' and old.civic_status in ('rejected','withdrawn') then
    raise exception 'rejected or withdrawn amnesty rows cannot return to candidate without a new declaration';
  end if;
  return new;
end
$function$;

alter table public.amnesty_grants enable row level security;
alter table public.amnesty_executions enable row level security;
alter table public.amnesty_nonces enable row level security;
alter table public.coherence_runtime_state enable row level security;
alter table public.coherence_runtime_evaluations enable row level security;

drop policy if exists amnesty_grants_public_read on public.amnesty_grants;
create policy amnesty_grants_public_read on public.amnesty_grants for select to public using (true);

drop policy if exists amnesty_executions_public_read on public.amnesty_executions;
create policy amnesty_executions_public_read on public.amnesty_executions for select to public using (true);

revoke insert, update, delete on public.amnesty_grants from anon, authenticated;
revoke insert, update, delete on public.amnesty_executions from anon, authenticated;
revoke insert, update, delete on public.amnesty_declarations from anon, authenticated;
revoke insert, update, delete on public.amnesty_nonces from anon, authenticated;
grant select on public.amnesty_grants, public.amnesty_executions, public.amnesty_declarations to anon, authenticated;
