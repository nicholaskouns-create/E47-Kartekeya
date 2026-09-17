# Web Runtime Layer

Import the shared City graphics runtime from `city_graphics_accelerator.js` and select the app profile from `city_graphics_profiles.json`.

Minimal browser bootstrap:

```js
import { bootstrapCityGraphics } from './city_graphics_accelerator.js';
await bootstrapCityGraphics({ targetFps: 60, minScale: 0.55, dprCap: 2 });
```

Mark adaptive canvases with `data-city-gpu` or `class="city-gpu"`.

Do not couple simulation state updates to render frame count. Use the fixed-step loop for time evolution and keep scientific checks/provenance outside the render backend.
