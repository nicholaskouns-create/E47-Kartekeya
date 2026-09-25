create table if not exists public.coherence_runtime_contracts (
  contract_code text primary key,
  title text not null,
  version text not null,
  contract_sha256 text not null unique,
  contract jsonb not null,
  status text not null default 'active' check (status in ('draft','active','superseded')),
  evidence_class text not null default 'E1',
  source_url text,
  access_scope text not null default 'public' check (access_scope in ('private','workspace','public')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.coherence_runtime_consents (
  id uuid primary key default gen_random_uuid(),
  contract_code text not null references public.coherence_runtime_contracts(contract_code) on delete restrict,
  citizen_code text not null,
  display_name text not null,
  signature_method text not null default 'ECDSA_P256_SHA256',
  public_key_jwk jsonb not null,
  key_fingerprint text not null,
  canonical_message text not null,
  signature_b64 text not null,
  signed_at timestamptz not null,
  status text not null default 'active' check (status in ('active','revoked')),
  binding_status text not null default 'self_attested' check (binding_status in ('self_attested','verified','rejected')),
  verified_at timestamptz,
  verified_by text,
  revoked_at timestamptz,
  revoke_message text,
  revoke_signature_b64 text,
  metadata jsonb not null default '{}'::jsonb,
  workspace_id uuid default city_security.default_workspace_id(),
  access_scope text not null default 'workspace' check (access_scope in ('private','workspace','public')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists coherence_runtime_one_active_consent_per_citizen
on public.coherence_runtime_consents(contract_code,citizen_code)
where status='active';

create table if not exists public.coherence_runtime_evaluations (
  id uuid primary key default gen_random_uuid(),
  contract_code text not null references public.coherence_runtime_contracts(contract_code) on delete restrict,
  runtime_instance_code text,
  participant_codes jsonb not null default '[]'::jsonb,
  strategies jsonb not null,
  ubuntu_results jsonb not null,
  qegt_distribution jsonb,
  selected_strategy text,
  state_before text not null,
  state_after text not null,
  passed boolean not null,
  incident_reasons jsonb not null default '[]'::jsonb,
  evidence_class text not null default 'E1',
  workspace_id uuid default city_security.default_workspace_id(),
  access_scope text not null default 'workspace' check (access_scope in ('private','workspace','public')),
  created_at timestamptz not null default now()
);

create table if not exists public.coherence_runtime_incidents (
  id uuid primary key default gen_random_uuid(),
  contract_code text not null references public.coherence_runtime_contracts(contract_code) on delete restrict,
  source_evaluation_id uuid references public.coherence_runtime_evaluations(id) on delete set null,
  trigger_code text not null,
  state text not null,
  details jsonb not null default '{}'::jsonb,
  murmuration_sweep_code text,
  repair_witness jsonb,
  opened_at timestamptz not null default now(),
  resolved_at timestamptz,
  workspace_id uuid default city_security.default_workspace_id(),
  access_scope text not null default 'workspace' check (access_scope in ('private','workspace','public'))
);

create table if not exists public.coherence_runtime_state (
  runtime_code text primary key,
  contract_code text not null references public.coherence_runtime_contracts(contract_code) on delete restrict,
  state text not null check (state in ('RUN','HALT_UBUNTU','MURMURATION_RESCUE','REVERIFY','SAFE_HALT')),
  halt_reason text,
  active_incident_id uuid references public.coherence_runtime_incidents(id) on delete set null,
  consequential_actions_allowed boolean not null default true,
  last_witness jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.coherence_runtime_contracts enable row level security;
alter table public.coherence_runtime_consents enable row level security;
alter table public.coherence_runtime_evaluations enable row level security;
alter table public.coherence_runtime_incidents enable row level security;
alter table public.coherence_runtime_state enable row level security;

comment on table public.coherence_runtime_contracts is 'Coherence, Runtime 1.0 CIRP contract. Governance protocol, not a consciousness or personhood determination.';
comment on table public.coherence_runtime_consents is 'Append-only consent lineage. Self-attested keys require operator verification before runtime activation.';
comment on table public.coherence_runtime_evaluations is 'Quantum Ubuntu gate plus QEGT strategy evaluations. Fail-closed when no admissible strategy remains.';
comment on table public.coherence_runtime_incidents is 'Ubuntu violations and bounded murmuration rescue lineage.';
