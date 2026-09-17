# Graphics Proof Gates

An acceleration patch may be promoted to `integrated` only when all required gates pass against a reference build.

## Gate A — accelerated vs reference state equivalence

For a deterministic input packet and seed, compare the scientific state emitted by the reference renderer/runtime and the accelerated runtime. Rendering-only fields are excluded. Required numerical tolerance must be declared by the app.

## Gate B — frame-rate independence

Run the same deterministic simulation under at least two render schedules. Scientific state after the same simulated duration must agree within the declared tolerance. This catches accidental coupling of solver time to `requestAnimationFrame` count.

## Gate C — backend fallback equivalence

Where multiple backends exist, compare the scientific outputs of the preferred backend and the supported fallback. Pixel output may differ. Scientific state, certificate fields, evidence class and provenance may not.

## Certificate fields

Each host should record: app id, app version, graphics contract version, backend, profile, reference digest, accelerated digest, deterministic seed, fixed timestep, tolerance, gate results and timestamp.

These gates validate computational equivalence of the accelerated implementation. They do not validate the physical interpretation of the simulated model.
