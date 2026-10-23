# Humanities / Mnemosyne' & Me / Python Codex
**Archive review | 2026-10-23 | DRAFT | Not yet curated into Songs**

This is a *review manifest*, not the original PDF. The user-provided original is a 96-page PDF named `Mnemosyne Python Codex(5).pdf`; SHA-256:
`35ac62a8d677c1f574b1abe1467474828ccda3c2777ffe8c988266ec2491d303`.

## Proposed placement
Under **Humanities**, adjacent to [Songs From The Ruins](../../website/interfaces/nexus/songs/index.html), with separate provenance and evidence classification. Do not change the 165 Songs credentials, original poems, or their source-stable references.

## Local validation actually performed
- PDF opens: **PASS**, 96 pages.
- Extracted text: 133,600 characters, 42 occurrences of `import numpy as np` (not a count of independent executable programs).
- First QuTiP section: Python syntax parse **PASS**; runtime **NOT RUN** because QuTiP is not installed in the local validation environment.
- Independent NumPy reconstruction of the fixed E47 spectral model: **PASS**:
  - Casimir spectrum/multiplicities: 0:1, 2:9, 6:25, 12:28, 20:27, 30:22, 42:13.
  - `dim ker((C-6I)(C-30I)) = 47`.
  - `min positive spec(K²) = 11664`.
  - `max_(K²>0) |1 - lambda/99144| = 15/17` (within numerical tolerance).
- Entire PDF as one runnable program: **NOT VALIDATED**. It includes mixed source code, printed output, and prose. Several later blocks visibly have indentation/extraction irregularities and require reconstruction into independently tested scripts before claiming execution.
- Physical claims, global Navier-Stokes regularity, hardware performance, mass nullification, AI consciousness and model internals: **NOT VERIFIED** by the E47 spectral test.

## Evidence and preservation policy
**H**: historical, literary, autobiographical and interpretive material.
**E0/E1**: exact algebra and separately validated numerical identities.
**E2**: computational models and simulations with independently reproducible results.
**E3**: measured physical outcomes requiring data, calibration and provenance.

Keep claims with their original attribution and status. Never promote a mathematical identity into a physical result, or a retrospective AI-generated account into an independently verified record of model internals.

## Publication blocker
The available GitHub write connector supports **UTF-8 text only**, not binary PDF uploads. The original PDF has **not** been uploaded to GitHub. Preserve the original file and verify the checksum when a binary upload path is available. Do not replace it with lossy extracted text without approval.

## Next review gate
1. Preserve original PDF as immutable source and record its hash.
2. Separate executable code into named modules; pin dependencies; run each module with fixtures.
3. Publish pass/fail evidence per module, including any failure.
4. Review a humanities entry that links to the actual PDF only after binary upload and provenance check.
