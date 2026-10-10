# E47 Research WorkBench delivery

Instrument: `website/interfaces/e47-research-workbench/`, version 1.0.0, research maturity, E1/E2.

## Validation

- Full Python suite: 199 passed, 1 expected failure.
- Workbench Python regression subset after final numerical/package edits: 22 passed.
- Workbench browser numerical engine: 6 tests passed.
- Saved matrix/geometry reconstruction ledger: 13/13 passed.
- Lab and instrument contracts: 8 declared instruments passed.
- Autonomous smoke suite: all 8 instruments passed.
- Required website, E47 bridge, and EIDOLON receipt checks passed.
- Playwright Chromium QA: desktop/mobile, discrete/continuous, seeded/custom runs, JSON replay with tampered result recomputation, arbitrary stable imported steps, CSV/Markdown/OBJ exports, facet selection, keyboard rotation, browser parity verification, workspace destinations, and invalid import rejection. No unexpected JavaScript or CSP errors.

The optional browser QA runner is `scripts/qa_e47_workbench_browser.py`; Playwright is a separate development dependency. Browser binaries and screenshots are not committed.

## Repairs

The new adapter delegates operator construction to the existing E47 core. It replaces the supplied geometry script's hardcoded `/mnt/data` output with an explicit output path, constructs ordered polygon facets, checks supporting planes/edge incidence/topology/connectivity, and exposes clear zero-target and underflow outcomes. Continuous time and discrete step bookkeeping have distinct semantics. Receipt imports validate inputs, recompute outputs, and preserve custom stable epsilon values.

Supplied originals are retained byte-identically and SHA-256 identified. The comparison CSV's differing radius is labeled unresolved because generator/step provenance is missing. Inferred epsilon is not silently promoted to a verified parameter. No new hardware or empirical claim is introduced.

## Workspace records

- [Google Workspace build guide](https://docs.google.com/document/d/1QSEoFN19Gu3e8bAEfhoYJESQiA2YhBe5Y2SNdbYxNpU/edit?usp=drivesdk)
- [Private Notion delivery draft](https://app.notion.com/p/3f546094fd30814fb37ad856bb52a967?pvs=204)
- [Linear REC-16](https://linear.app/4521/issue/REC-16/build-e47-research-workbench-with-reproducible-spectral-experiments)

These records are linked by navigation. The app does not invoke live account connectors. Native Sites eligibility discovery and local publishing helpers are unavailable in this session, so that capability remains blocked rather than substituted with a fake synchronization feature. GitHub Pages remains the repository's existing deployment path after review/landing.

## Security review

No keys, credentials, account contents, external scripts, arbitrary remote fetches, eval or executable imports. Files are bounded to 2 MB; schema, weights, step range and horizon are validated. Display text uses textContent. External links are HTTPS with noopener/noreferrer. CSP restricts scripts/fetches to the app origin and disallows objects. Receipts are unsigned reproducibility records. Runs remain in memory until exported. This review is not a Codex Security service scan or a verification of program enrollment.

## Offline delivery

`scripts/package_e47_workbench.py` produces a directly openable single-file HTML app. It embeds the verified bundle and destination links, removes module fetches, and uses exact SHA-256 CSP script/style hashes with network reads disabled. The same full browser interaction QA is run against the file URL.

Remote CI exposed that pytest.ini adjusts only the parent import path. The portable-output regression now explicitly supplies src to its CLI subprocess, and displays captured stderr on failure. Validation is rerun without a pre-set PYTHONPATH to match CI.
