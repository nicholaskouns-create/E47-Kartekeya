# Observatory integration contract

The catalog contains owner-supplied public destinations only. External titles, availability, iframe permissions, and state compatibility remain unverified. Domain labels are used where no title is known. ENTRAIN was described in the conversation but its original hosted URL is not identified; its catalog link explicitly leads to the new local Neural Lab. No private workspace metadata or credentials are included.

## Navigation and embedding

External instruments open in a separate tab with `noopener noreferrer`. Do not infer embed permission from a successful HTTP response. Verify Content-Security-Policy `frame-ancestors`, X-Frame-Options, and actual frame loading before marking a route verified. Notion can present a link or embed to the public GitHub Pages URL where permitted; it cannot host this application runtime itself.

The local bridge accepts only `CITY-OBSERVATORY-BRIDGE-1` messages from `https://nicholaskouns-create.github.io` and the actual parent window. Allowed actions are `open-view` and `request-state`; view names are validated. State responses use an exact target origin. Adding another trusted parent requires an explicit allowlist change and verification. Never accept wildcard origins, executable message content, credentials, or arbitrary redirect URLs.

## Shared state

A replay carries versioned public experiment inputs and deterministic outputs where supported. Keep provenance, assumptions, and numerical scope attached to the experiment. Predictive accuracy is distinct from projection capture. A browser simulation is not a hardware execution receipt. Reading preferences and saved progress can remain local; synchronize through Supabase only after explicit authentication, RLS policies, and a reviewed public/private data contract.

## Platform boundaries

GitHub Pages serves the static app. Supabase can provide authorized persistence and server operations; no privileged key belongs in browser code. Drive, Calendar, Notion, and Linear require deliberate connector or backend workflows, rather than browser access to account credentials. No connector data is automatically public. Links and public exports preserve provenance. Existing hosted instruments should be integrated incrementally through small adapters with versioned schemas and origin checks.

## Verification queue

Confirm original ENTRAIN route; fetch live titles and frame policies; inspect permitted embedding; define accepted replay fields per instrument; verify keyboard, reduced-motion, text, and phone behavior; confirm public publication scope before adding any connected workspace data.

## Public endpoint audit

All 24 supplied Grok endpoints returned HTTP 200 on 2026-10-13; their observed titles now identify the Atlas cards. No restrictive frame headers were observed, but the build browser could not validate external frames, so these remain direct launch destinations with embedding marked unknown. `surface-audit.json` records the bounded public reads.
