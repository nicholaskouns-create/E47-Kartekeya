# SKYRMION Licensed Aircraft Asset Register

This register covers third-party 3D aircraft assets admitted to SKYRMION. A visually similar model is never allowed to replace a named craft. Runtime replacement requires an exact identity match, a runtime-authorized asset URL or vendored file, and preserved attribution in `licensed-aircraft-assets.js`.

## Runtime-ready reference assets

| Asset ID | Model | Source / author | License or usage basis | SKYRMION status |
|---|---|---|---|---|
| `f15-polyducky` | McDonnell Douglas F-15 Eagle | PolyDucky; redistributed by srcejon/sdrangel-3d-models | CC BY 4.0 | Fighter GLB reference only; **never presented as F-16** |
| `nasa-global-hawk` | NASA Global Hawk | NASA/Michael D. Carbajal | NASA Media Usage Guidelines | Official NASA GLB; loader, material, shadow and normalization reference |
| `amvlab-a320` | Airbus A320 | amvlab aircraft-models contributors | CC BY 4.0 | Airliner loader / normalization reference |
| `amvlab-b737-nologo` | B737 logo-free | amvlab aircraft-models contributors | CC BY 4.0 | Logo-free airliner reference |
| `amvlab-evtol` | eVTOL | amvlab aircraft-models contributors | CC BY 4.0 | Experimental-aircraft reference |
| `amvlab-drone` | Drone | amvlab aircraft-models contributors | CC BY 4.0 | Small-aircraft reference |

## Exact fleet candidates

These records have a verified public license statement on the provider page, but SKYRMION does **not** bypass provider-controlled downloads. Their `runtimeUrl` remains null until an authorized GLB is materialized and provenance/checksum capture is complete.

| Asset ID | Intended slot | Author / provider | License shown by provider | Current status |
|---|---|---|---|---|
| `f16-cdesrocher` | F-16 | cdesrocher / Sketchfab | CC Attribution | License verified; authorized GLB materialization still required |
| `sr71-manilov` | SR-71 | manilov.ap / Sketchfab | CC Attribution | License verified; authorized GLB materialization still required |
| `x15-cmoreau` | X-15 | cmoreau / Sketchfab | CC Attribution | License verified; authorized GLB materialization still required |

## Source and license links

- NASA Global Hawk 3D resource: https://science.nasa.gov/3d-resources/global-hawk/
- NASA Images and Media Usage Guidelines: https://www.nasa.gov/nasa-brand-center/images-and-media/
- Creative Commons Attribution 4.0 International: https://creativecommons.org/licenses/by/4.0/
- srcejon/sdrangel-3d-models license register: https://github.com/srcejon/sdrangel-3d-models/blob/main/LICENSE
- amvlab/aircraft-models: https://github.com/amvlab/aircraft-models
- F-16 candidate: https://sketchfab.com/3d-models/f-16-fighting-falcon-031debe8efad46dd9ba362604707ebb1
- SR-71 candidate: https://sketchfab.com/3d-models/sr71-908985d8ec544638bcd661bc315597ad
- X-15 candidate: https://sketchfab.com/3d-models/north-american-x-15-plane-bf491206ba844282949734b48b938c53

## Admission and rendering rules

1. Verify a model-level license or NASA usage basis, not merely the surrounding application license.
2. Preserve author, source, license, and modification/provenance metadata.
3. Do not map a different aircraft to a named slot. The F-15 and Global Hawk validate the pipeline but must not become F-16, SR-71, or X-15.
4. Prefer CC0, U.S.-government/NASA material under applicable usage guidance, or CC BY assets. Noncommercial/share-alike assets require separate compatibility review.
5. Imported presentation geometry does not alter the authoritative flight-state, E47, MANTA, GPS, terrain, or propulsion-simulation contracts.
6. Named bones/nodes may drive ailerons, elevators, stabilators, rudders, flaps, spoilers, gear, canopy materials, exhaust, contrails, and shadows. If those nodes do not exist, SKYRMION does not claim that the GLB is rigged.
7. Skinned GLBs are cloned with Three.js SkeletonUtils rather than naive scene cloning.
8. Material tuning clones materials per imported scene so runtime glass/roughness changes do not mutate the cached source.
9. Runtime models are normalized by measured bounds and inspected for mesh, triangle, bone, texture, animation, and control-binding counts.
10. Exact production replacements should ultimately be vendored with a checksum and this register updated to the vendored path. External CDN delivery is a staging mechanism.
