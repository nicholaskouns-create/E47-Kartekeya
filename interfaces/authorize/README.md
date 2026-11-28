# Authorize — anesthesia coding & prior authorization workbench

A minimal, touch-friendly standalone static browser app for Luis. Hosted under `interfaces/authorize/`; no npm, backend, or database required. This app is a code reference and preparation worksheet, **not** a payer authorization/coverage determination system.

## Run

Open `interfaces/authorize/index.html` in a browser, or deploy on GitHub Pages. Search ICD-10-CM, imported HCPCS/CPT codes, or build a de-identified authorization worksheet. The app loads code packs from `data/manifest.json` only on demand when a catalog is present; records are rendered 35 per page. No browser storage or network submission of worksheet content. You may import local JSON catalogs and search them in memory.

## Import FY2027 ICD-10-CM

```bash
python interfaces/authorize/tools/build_catalog.py
# Alternative when the official download URL has moved:
python interfaces/authorize/tools/build_catalog.py --source ~/Downloads/icd10cm-order-2027.zip
```

The importer validates more than 50,000 records and emits `data/icd10cm-2027.json` and a manifest. Review the source, effective year and counts; commit the generated files to deploy a searchable complete diagnosis catalog. The official data links are maintained by [CDC](https://www.cdc.gov/nchs/icd/icd-10-cm/files.html) and [CMS](https://www.cms.gov/medicare/coding-billing/icd-10-codes).

Other public code packs can be added to the manifest in the same schema:
```json
{"metadata":{"system":"HCPCS-II","version":"2026-Q4","effectiveDate":"2026-10-01","source":"CMS HCPCS official release"},"codes":[{"code":"G0008","description":"Example public descriptor","system":"HCPCS-II"}]}
```
Do not treat the example as verified clinical billing data. Any generated data must come from its declared official source and effective release.

## Additional official datasets to incorporate

- [Quarterly HCPCS Level II](https://www.cms.gov/medicare/coding-billing/healthcare-common-procedure-system/quarterly-update): CMS alpha-numeric level II codes, modifiers and coverage/pricing indicators.
- [PFS relative value files](https://www.cms.gov/medicare/payment/fee-schedules/physician/pfs-relative-value-files): physician fee schedule RVUs, status and policy indicators. Dollar figures require locality, year, modifier and all payment adjustments.
- [NCCI edits](https://www.cms.gov/medicare/coding-billing/national-correct-coding-initiative-ncci-edits): PTP and MUE edits, quarterly dates and update handling.
- [NCD/LCD coverage database](https://www.cms.gov/medicare-coverage-database/search.aspx): national/local medical necessity criteria; payer and policy-specific review still required.
- ICD-10-PCS: hospital inpatient procedure classification; **not** a substitute for CPT/HCPCS professional billing codes.
- Anesthesia: ASA base units, exact anesthesia code/descriptors, modifiers, anesthesia time, physical status and qualifying circumstances. Validate separately against relevant AMA/ASA licensing and payer policies.

**Licensing:** CPT is AMA copyrighted. Do not commit or redistribute licensed CPT descriptor text or ASA base-unit tables without permission. Public federal payment fields are distinct from licensed descriptions. Import licensed content privately only under applicable terms.

**Clinical safety:** Code presence or diagnosis/procedure juxtaposition does not imply authorization or medical necessity. Date of service, site, provider, plan, network, medical policy, prior treatment, modifiers, documentation and current fee-schedule methodology matter.

**PHI:** GitHub Pages is a public static site, not a HIPAA workflow. This workbench does not collect or transmit patient input; do not put PHI into code, URLs, issues or public repos. Use an appropriately contracted, authenticated clinical system if patient records or payer submission are added.
