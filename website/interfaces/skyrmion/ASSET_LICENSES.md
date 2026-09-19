# SKYRMION Licensed Aircraft Asset Register

This register covers third-party 3D aircraft assets admitted to the SKYRMION licensed-asset pipeline. A model is not allowed to replace a named SKYRMION craft merely because it is visually similar. Runtime replacement requires an explicit identity match in `licensed-aircraft-assets.js`.

## Assets

| Asset ID | Model | Author / source | License | SKYRMION status |
|---|---|---|---|---|
| `f15-polyducky` | McDonnell Douglas F-15 Eagle | PolyDucky; redistributed by srcejon/sdrangel-3d-models | CC BY 4.0 | Reference fighter only; **not** presented as F-16 |
| `amvlab-a320` | Airbus A320 | amvlab aircraft-models contributors | CC BY 4.0 | Loader / normalization reference |
| `amvlab-evtol` | eVTOL | amvlab aircraft-models contributors | CC BY 4.0 | Experimental-aircraft reference only |
| `amvlab-drone` | Drone | amvlab aircraft-models contributors | CC BY 4.0 | Small-aircraft reference only |

### License links

- Creative Commons Attribution 4.0 International: https://creativecommons.org/licenses/by/4.0/
- srcejon/sdrangel-3d-models license register: https://github.com/srcejon/sdrangel-3d-models/blob/main/LICENSE
- amvlab/aircraft-models: https://github.com/amvlab/aircraft-models

## Admission rules

1. Verify an explicit license covering the model itself, not just surrounding code.
2. Preserve author/source/license metadata in this register and the runtime manifest.
3. Do not map a different aircraft to a named slot. An F-15 may validate the fighter GLB pipeline, but it must not become the F-16.
4. Prefer CC0, public-domain, or CC BY assets. Copyleft/noncommercial/share-alike assets require a separate compatibility review before bundling.
5. Imported assets are presentation geometry. They do not alter flight-state, E47, MANTA, evidence, or propulsion claims.
6. Control-surface binding may use named nodes/bones when present. If the GLB is static, SKYRMION keeps procedural control/effect attachments rather than inventing a false rig.
7. External CDN delivery is currently a staged runtime dependency. Exact production replacements should be vendored into the repository after file-level provenance and checksum capture.
