# Executable Formalism Atlas

The Atlas is a compiled view of the live Mathematical City across Notion, Supabase, GitHub, Google Drive, public-surface records, and relevant Gmail provenance.

## Public interface

`website/interfaces/formalism-atlas/index.html`

The interface is zero-dependency HTML/JavaScript. It loads four machine-readable snapshots:

- `website/data/formalism-registry.json` — 94 live Notion Formalism Registry rows.
- `website/data/formalism-graph.json` — 241 Mathematical City identity nodes and 206 typed theorem edges.
- `website/data/formalism-provenance.json` — certificates, source artifacts, corrections, failures, discrepancies, stranded math, Python corpus, and public surfaces.
- `website/data/formalism-source-snapshot.json` — GitHub workflow snapshot, Drive ledger row counts, and relevant Gmail metadata.

## Registry invariant

The live registry spans IDs 1–97 with IDs 54–56 absent. The Atlas preserves that gap rather than synthesizing rows.

The registry's `Claim Status` field remains authoritative at registry level. Exact E-classes remain attached to Mathematical City identities and machine certificates:

- E0 — exact proof
- E1 — executable reconstruction
- E2 — simulation
- E3 — external benchmark
- E4 — experiment
- H0 — hardware

The interface's `evidence_band` is only a display aid. It does not promote evidence.

## Core lock

`dim V = 125` · `K=(C-6I)(C-30I)` · `dim E47=47` · `Ωc=47/125` · `gap(K²)=11664` · `||K²||=186624` · `ε*=1/99144` · `ρ*=15/17`.

## Validate

```bash
python scripts/validate_formalism_atlas.py
```

A PASS certifies the Atlas structure and locked registry invariants. It does not convert open claims into proofs or simulations into experiments.

## Preserved discrepancies

The Atlas intentionally preserves failed certificates, cross-platform discrepancies, and stranded-math candidates. The current source ledger shows 345 Supabase source artifacts while the Drive primary-source spreadsheet contains 341 data rows; the interface marks that as drift rather than silently normalizing it.
