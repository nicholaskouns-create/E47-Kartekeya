# City Graphics Acceleration Rollout

Record: `CITY-GRAPHICS-ACCELERATOR-1.0`

The graphics layer is a performance/runtime contract. It does not change the mathematics, solver semantics, evidence class, provenance, or scientific claims of any app.

## Shared runtime

`web/city_graphics_accelerator.js` provides:

- WebGPU capability detection with WebGL2/WebGL1/Canvas2D fallback
- adaptive device-pixel-ratio control
- fixed-timestep simulation/render decoupling
- visibility throttling
- OffscreenCanvas worker transfer support
- Wasm/SIMD-ready capability reporting

## Proof gates

Every host migration must pass all three gates before its profile is marked integrated:

1. accelerated vs reference state equivalence
2. frame-rate independence
3. backend fallback equivalence

## App profiles

The canonical migration ledger is `web/city_graphics_profiles.json`. It currently covers the 13 public surfaces plus The Cube, THE MATRIX and City OS.

External Grok/ChatGPT-hosted applications remain `source-migration-required` or `external-host-migration` until their writable source is patched. This is deliberate: a profile is a target, not a claim that a remote host changed.

## High-impact priorities

- **EIDOLON:** WebGPU render path, GPU instancing, terrain LOD, KTX2/Basis textures, fixed-step flight dynamics, worker separation, temporal-upscale-ready render pipeline.
- **Wave:** GPU field textures / ping-pong buffers, fixed-step solver, worker separation.
- **Murmuration:** GPU instancing, spatial binning and worker simulation.
- **Fold / InvariFold:** instanced residue geometry, LOD and worker geometry generation.
- **Density / SCALAR:** field-texture and compute-oriented paths with adaptive resolution.
- **The Cube:** adaptive DPR, visibility throttling and fixed-step animation.

## Evidence boundary

Acceleration success means the application renders or responds faster while preserving the typed computational result. It is not evidence for the physical interpretation of the modeled system.
