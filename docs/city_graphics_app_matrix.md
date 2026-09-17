# App Graphics Migration Matrix

| Surface | Profile | Primary acceleration work | Current host state |
|---|---|---|---|
| SPECTRA | spectral-2d | batching, adaptive DPR, worker precompute | external host migration |
| Fold | protein-geometry | instancing, LOD, worker geometry | external host migration |
| Murmuration | instanced-agents | GPU instancing, spatial binning, worker simulation | external host migration |
| Mnemosyne | ui-low-motion | visibility throttling, cached layers | external host migration |
| Density | volume-field | field textures, adaptive resolution, compute-ready path | external host migration |
| Horizon | timeseries | decimation, offscreen rendering | external host migration |
| Wave | field-solver | fixed-step solver, ping-pong textures, worker separation | external host migration |
| Identity | transport | batched vectors, worker metrics | external host migration |
| BUILD | instanced-construction | instancing, culling, LOD | external host migration |
| SOAR | trajectory | trajectory batching, fixed-step rendering | external host migration |
| SCALAR | scalar-field | field texture / compute-ready path | external host migration |
| EIDOLON | flight-simulator | WebGPU path, terrain LOD, KTX2/Basis, worker flight dynamics | source migration required |
| InvariFold | protein-cinema | instanced residues, LOD, worker geometry | Fold payload migration |
| The Cube | canvas-scientific | adaptive DPR, visibility throttling, fixed-step animation | Supabase direct patch candidate |
| THE MATRIX | quantum-circuit | worker statevector, batched visualization | source migration required |
| City OS | control-plane | layer caching, worker layout, visibility throttling | source migration required |

A row moves to `integrated` only after its source is changed and all proof gates pass.
