# Acceptance

A City app graphics migration is accepted only when:

- its profile is selected from `city_graphics_profiles.json`;
- its simulation step is independent of render frame rate;
- accelerated and reference scientific states agree at the declared tolerance;
- fallback backend scientific state agrees at the declared tolerance;
- provenance and evidence class are unchanged;
- host status is changed to `integrated` only after those checks pass.

Visual fidelity, FPS, memory use and load time are optimization metrics. They are not substitutes for the equivalence gates above.
