# Civic assignment integration · deployment record

Canonical assignment: `website/data/city-assignment.json` (18 verified legacy ledger claims).

Compiler: `python scripts/build_city_assignment.py`. CI: `.github/workflows/city-assignment.yml`.

Public City entrypoint: `website/index.html` loads `website/js/city-assignment.js`; the four publication views use `website/interfaces/civic-assignment/?surface=citadel|citizenship_bureau|proof_forge|publication`.

Supabase project `gpkjvihkyectnenvnbng`: Edge Function `city-civic-assignment` v1 deployed with JWT verification enabled. Authenticated GET `/functions/v1/city-civic-assignment?surface=<name>` checks canonical payload SHA-256 and the requested surface's digest before returning the common claim set; rejects errors fail-closed.

## Operational boundary

The shared read-only gateway is live as a deployed function, but integration into the existing Citadel, Citizenship Bureau, and Proof Forge *application internals* is not yet established by this deployment. Their callers must use the gateway or the common static JSON record, and enforcement of mutations requires a separate server-side authorization/assignment check. GitHub Actions successful completion and external HTTP availability must be independently checked. No claim that all historical city citizens have been reassessed: this snapshot covers the 18 claims in the existing ledger. New proofs need individual ledger admission.

## Security

Do not disable JWT verification. Client UI is read-only. Do not use an unverified browser label as an authorization grant. The gateway verifies the content digest but relies on HTTPS/GitHub Pages origin for source authenticity; for stronger provenance pin a signed digest or release artifact.

## Runtime integration update (2026-10-09)
- **Citadel / SEE and Proof Forge hosted interface:** `city-app-host` v8 inserts a navigation backlink to the common evidence assignment at HTML serve time, without changing hosted artifact source.
- **Citizenship / transit orchestration:** `mathematical-city-orchestrator` v5 verifies canonical assignment digest and exact claim/evidence grade before processing a promotion or citizen enrollment. It removes the old reviewer-preference gate for E0 upgrades while preserving other safeguards.
- **Proof Forge / research runtime:** `city-research-lab` v3 verifies the same assignment before work, includes digest in snapshot output and proof-search queue provenance.
- **Shared read API:** `city-civic-assignment` v1 is JWT-protected and verifies content digest.
- **Automated integrity:** `scripts/audit_city_links.py` checks governance routes, `scripts/crawl_city_site.py` inventories every HTML file and checks reachability, local link targets and optional live URLs. `.github/workflows/city-live-crawl.yml` schedules daily live checks and supports manual dispatch.
- **Verification limitation:** Deployed versions are confirmed active, but an authenticated runtime transaction, successful Actions run and passing live full-site crawl are not yet confirmed. Hosted Citadel and Proof Forge front-end backlinks are navigational; mutation-grade evidence enforcement occurs in the orchestrator, not in a client-side banner. The full-site crawl may surface legacy orphans; no clean crawl has been established.
