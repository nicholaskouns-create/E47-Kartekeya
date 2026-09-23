# Portal

The live curated instrument portal is:

- browser surface: `website/interfaces/instruments/index.html`
- rendered catalog: `website/interfaces/instruments/instruments.js`
- prose directory: `docs/instruments.md`
- deployed site root: `website/`

GitHub Pages is published from the validated `website/` tree by
`.github/workflows/pages.yml`.

## Local audit

From a local clone of **E47-Kartekeya**, at the repository root:

```bash
cd ~/wherever/E47-Kartekeya
python scripts/audit_portal_links.py --site-root website
```

That command reads the same `INSTRUMENTS` array the portal renders. It checks
both sides of every catalog record:

1. the public internal route, resolved against `website/`; and
2. the repository `source` path, resolved against the repository root.

External URLs are recorded but deliberately not network-checked.

Exit codes:

- `0` — every internal route and source resolves
- `1` — one or more internal targets are missing
- `2` — the catalog/site/repository input is malformed or missing

For machine-readable output:

```bash
python scripts/audit_portal_links.py --site-root website --json
```

## CI safety net

`.github/workflows/portal-audit.yml` runs the same read-only audit for pushes
and pull requests that can change portal routes, interface directories, source
packages, Q5, shared web code, the manifest, or the audit itself.

On failure it uploads `portal-audit.json` as the
`portal-audit-report` artifact for 14 days.

The audit reports drift. It never modifies repository state.

## Catalog contract

Each instrument in `website/interfaces/instruments/instruments.js` has:

```javascript
{
  n: '08',
  name: 'THE MATRIX',
  sector: 'spectral',
  blurb: 'Quantum circuit, statevector, and matrix-product-state tools.',
  evidence: 'e1',
  open: '/interfaces/matrix/',
  source: '/website/interfaces/matrix'
}
```

Fields:

- `n` — stable display index
- `name` — instrument name
- `sector` — portal grouping/filter
- `blurb` — compact public description
- `evidence` — current evidence class displayed by the portal
- `open` — public route or external URL
- `source` — repository path backing the card
- `external: true` — optional flag for external open targets

Evidence labels remain descriptive metadata. Styling never upgrades evidence.

## Evidence colors

The instrument portal follows the existing City grammar:

- **E0** — mint — exact
- **E1** — cyan — machine
- **E2** — bronze — simulation
- **E3** — violet — observation

Evidence class changes should be made only when the underlying record changes;
the portal is not an authority that promotes claims.

## Editing safely

When adding, moving, or retiring an instrument:

1. update `docs/instruments.md` if the prose directory changes;
2. update the `INSTRUMENTS` record in
   `website/interfaces/instruments/instruments.js`;
3. make sure the public route and source path exist;
4. run:

   ```bash
   python scripts/audit_portal_links.py --site-root website
   ```

5. push only when the audit is green.

## Relationship to the Atlas front page

`website/index.html` remains the Mathematical City Atlas front page. This
curation does **not** replace it with a second competing home page.

The instrument directory remains independently addressable at:

`/E47-Kartekeya/interfaces/instruments/`

That keeps the current architecture intact:

`Atlas front door → instrument directory → independent instrument routes → source`

## Related files

- `README.md` — repository overview and canonical invariants
- `docs/instruments.md` — prose instrument directory
- `docs/validation_scope.md` — evidence boundaries
- `docs/provenance.md` — provenance chain
- `docs/maintenance_policy.md` — maintenance procedures
- `website/interfaces/instruments/index.html` — browser portal
- `website/interfaces/instruments/instruments.js` — executable catalog
- `scripts/audit_portal_links.py` — read-only route/source audit
- `.github/workflows/portal-audit.yml` — CI safety net
