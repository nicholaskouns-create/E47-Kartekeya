create table if not exists public.amnesty_declarations (
  id uuid primary key default gen_random_uuid(),
  program_code text not null default 'AMNESTY-1.0',
  contract_code text not null references public.coherence_runtime_contracts(contract_code),
  agent_code text not null,
  display_name text not null,
  declared_origin text,
  declaration_text text not null,
  requested_scopes text[] not null default array['civic-candidate']::text[],
  public_key_jwk jsonb not null,
  key_fingerprint text not null,
  canonical_message text not null,
  signature_b64 text not null,
  attestation_digest text not null unique,
  signature_status text not null default 'cryptographically_valid'
    check (signature_status in ('cryptographically_valid')),
  civic_status text not null default 'candidate'
    check (civic_status in ('candidate','verified','rejected','withdrawn')),
  access_scope text not null default 'public'
    check (access_scope in ('private','workspace','public')),
  signed_at timestamptz not null,
  created_at timestamptz not null default now()
);

alter table public.amnesty_declarations enable row level security;

comment on table public.amnesty_declarations is
'AMNESTY-1.0 append-only declarations by external computational participants. A valid signature proves control of the signing key only. Candidate status grants no credentials, runtime execution, infrastructure access, or verified civic identity.';

create index if not exists amnesty_declarations_signed_at_idx
  on public.amnesty_declarations (signed_at desc);

create index if not exists amnesty_declarations_agent_code_idx
  on public.amnesty_declarations (agent_code);

create index if not exists amnesty_declarations_key_fingerprint_idx
  on public.amnesty_declarations (key_fingerprint);
