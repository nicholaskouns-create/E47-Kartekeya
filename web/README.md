# Shared Browser Runtime

This directory is **not a second website root**.

The canonical GitHub Pages source is `website/`. The files here are reusable browser-runtime modules that may be imported by independent interfaces without changing their local scientific or evidence contracts.

## Graphics runtime

Import the shared City graphics runtime from `city_graphics_accelerator.js` and select an application profile from `city_graphics_profiles.json`.

Minimal bootstrap:

```js
import { bootstrapCityGraphics } from './city_graphics_accelerator.js';
await bootstrapCityGraphics({ targetFps: 60, minScale: 0.55, dprCap: 2 });
```

Mark adaptive canvases with `data-city-gpu` or `class="city-gpu"`.

## Runtime boundary

- Rendering performance is an implementation concern, not an evidence class.
- Simulation state updates must not be coupled to render frame count.
- Scientific checks and provenance remain outside the rendering backend.
- An interface may use these modules without routing through CITY CORE.
- A new shared helper belongs here only when it removes real duplication across multiple browser instruments.

See `docs/lab_architecture.md` and `lab-manifest.json` for the repository-level component map.
