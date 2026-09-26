-- AMNESTY execute path: declaration stays a ledger.
-- Grants and spent nonces live beside it. civic_status is never an execute bit.

alter table public.amnesty_declarations
  drop constraint if exists amnesty_declarations_civic_status_check;

alter table public.amnesty_declarations
  add constraint amnesty_declarations_civic_status_check
  check (civic_status in ('candidate','rejected','withdrawn'));

comment on column public.amnesty_declarations.civic_status is
  'Declaration ledger only. candidate is not verified consent and not execute. Promotion to execute is amnesty_grants + spent nonce.';

create table if not exists public.amnesty_grants (
  id uuid primary key default gen_random_uuid(),
  declaration_id uuid not null references public.amnesty_declarations(id) on delete restrict,
  agent_code text not null,
  tools text[] not null default '{}'::text[],
  allow_to text[] not null default '{}'::text[],
  ceiling_cents integer not null default 0 check (ceiling_cents >= 0),
  not_before timestamptz not null,
  not_after timestamptz not null,
  issued_by text not null,
  created_at timestamptz not null default now(),
  revoked_at timestamptz,
  check (not_before < not_after),
  check (tools <@ array['transfer','city.publish_receipt','city.read']::text[])
);

create table if not exists public.amnesty_nonces (
  nonce text primary key,
  grant_id uuid not null references public.amnesty_grants(id) on delete restrict,
  tool text not null,
  args_digest text not null,
  spent_at timestamptz not null default now()
);

create table if not exists public.amnesty_executions (
  id uuid primary key default gen_random_uuid(),
  grant_id uuid not null references public.amnesty_grants(id) on delete restrict,
  declaration_id uuid not null references public.amnesty_declarations(id) on delete restrict,
  agent_code text not null,
  tool text not null,
  args jsonb not null,
  decision text not null check (decision in ('ALLOW','REFUSE')),
  reasons text[] not null default '{}'::text[],
  nonce text,
  created_at timestamptz not null default now()
);

create index if not exists amnesty_grants_agent_idx on public.amnesty_grants (agent_code);
create index if not exists amnesty_executions_agent_idx on public.amnesty_executions (agent_code, created_at desc);

alter table public.amnesty_declarations enable row level security;
alter table public.amnesty_grants enable row level security;
alter table public.amnesty_nonces enable row level security;
alter table public.amnesty_executions enable row level security;

drop policy if exists amnesty_declarations_public_read on public.amnesty_declarations;
create policy amnesty_declarations_public_read
  on public.amnesty_declarations for select
  using (access_scope = 'public');

create or replace function public.amnesty_reject_status_promotion()
returns trigger language plpgsql as $$
begin
  if tg_op = 'UPDATE' and new.civic_status is distinct from old.civic_status
     and new.civic_status not in ('candidate','rejected','withdrawn') then
    raise exception 'amnesty civic_status is not an execute bit';
  end if;
  if tg_op = 'UPDATE' and new.civic_status = 'candidate'
     and old.civic_status in ('rejected','withdrawn') then
    raise exception 'rejected or withdrawn amnesty rows cannot return to candidate without a new declaration';
  end if;
  return new;
end $$;

drop trigger if exists amnesty_reject_status_promotion on public.amnesty_declarations;
create trigger amnesty_reject_status_promotion
  before update on public.amnesty_declarations
  for each row execute function public.amnesty_reject_status_promotion();
