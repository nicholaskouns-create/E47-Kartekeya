# City Graphics Worker Protocol

Main thread to worker:

- `CITY_OFFSCREEN_CANVAS`: transferred canvas ownership
- `CITY_STATE_SNAPSHOT`: immutable simulation/render snapshot plus sequence id
- `CITY_RESIZE`: CSS width, CSS height and negotiated pixel ratio
- `CITY_QUALITY`: negotiated profile/tier

Worker to main thread:

- `CITY_FRAME_METRICS`: frame time, scale, backend
- `CITY_RENDER_READY`: worker initialized
- `CITY_RENDER_ERROR`: typed render failure without mutation of simulation state

The rendering worker must never become the authority for evidence class, provenance or scientific certification. Simulation state ownership stays with the app's declared computational layer.
