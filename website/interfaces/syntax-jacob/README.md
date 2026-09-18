# Syntax Jacob

Standalone Mathematical City instrument for live 3I/ATLAS navigation.

- Original work / concept lineage: Nick Kouns.
- Astronomy truth layer: JPL Horizons Cartesian state vectors and JPL SBDB orbital metadata, refreshed at runtime.
- Earth: 3D sphere using NASA Earth Observatory Blue Marble: Next Generation imagery.
- 3I rendering: generated irregular nucleus + coma + dust/ion tails; morphology is explicitly a reconstruction, not an observed shape model.
- Scalar copilot: the existing 125-state E47 engine with `K=(C-6I)(C-30I)`, `Gamma=I-K^2/99144`, `Omega_c=47/125`.
- Independent coherence witness: existing Supabase `matrix-cube-adapter`.
- Rendering capability contract: existing Supabase `city-graphics-accelerator`.

The live astronomy layer and the scalar/coherence model layer remain typed separately in the UI.
