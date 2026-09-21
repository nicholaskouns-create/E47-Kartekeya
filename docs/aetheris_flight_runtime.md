# AETHERIS Flight Boundary and E47 Witness

This Python module is the offline/CI companion to the browser **SKYRMION Runtime 2**. It does not duplicate the browser's 120 Hz 6DOF engine. It makes the shared model boundary and spectral witness inspectable from Python.

## Architecture

```text
one State6DOF contract
        |
VehicleRegistry
        |
+-------+-----------------------+
|                               |
CONVENTIONAL                    EXPLICIT_EXPERIMENTAL_SIMULATION
F-16 / SR-71 / X-15             EIDOLON / MANTA / SKYRMION / Syntax Jacob
|                               |
existing aero model             shared E47Witness
|                               |
+---------------+---------------+
                |
        state transition
                |
      deterministic receipt
```

The switch changes the **vehicle model**, not the state universe.

## Canonical E47 witness

The witness compiles the existing repository authority once:

```python
from aetheris.flight_runtime import E47Witness

e47 = E47Witness.compile()
projection = e47.inspect(psi_125)

assert projection.receipt.projector_rank == 47
assert projection.receipt.kp_zero
```

The projector has shape (125\times125) and rank 47. Therefore

[
P_{47}\psi\in\mathbb C^{125}
]

is still a 125-component carrier state lying in a rank-47 subspace. The module also exposes coordinates in an orthonormal kernel basis:

[
a_{47}=Q^\dagger\psi\in\mathbb C^{47},\qquad P_{47}\psi=Qa_{47}.
]

## Capture versus the rank fraction

For a particular state,

[
\Omega(\psi)=\frac{\|P_{47}\psi\|^2}{\|\psi\|^2}.
]

This is a live state-dependent capture value. It is not generally (47/125).

The fixed object-level fraction is

[
\Omega_c=\frac{\operatorname{rank}P_{47}}{125}=\frac{47}{125}.
]

The receipt records both values separately.

## Semigroup

The canonical continuous filter is

[
S(t)=e^{-tK^2}.
]

It acts on the **unprojected** state and suppresses the complementary 78-dimensional component:

[
S(t)\psi\to P_{47}\psi.
]

Once a state is already projected, (K^2P_{47}\psi=0), so using (-K^2P_{47}\psi) as a propulsion flow would yield zero to numerical tolerance. The Python runtime therefore treats that quantity as an invariant check, not a force law.

## Evidence boundary

The E47 witness checks are **E1 machine evidence**:

- rank (P_{47}=47);
- (P_{47}^2=P_{47});
- (KP_{47}=0);
- (K^2P_{47}=0);
- basis reconstruction;
- spectral gap (11664).

Any mapping from the projected state to forces, moments, control authority, or trajectory is a separate **E2 simulation model**. Passing the E47 witness does not establish physical propulsion validity.

## Fleet contract

The Python defaults mirror the browser vehicle registry:

| Boundary | Vehicles |
|---|---|
| CONVENTIONAL | F-16 · SR-71 · X-15 |
| EXPLICIT_EXPERIMENTAL_SIMULATION | EIDOLON · MANTA · SKYRMION · SYNTAX JACOB |

The browser remains the authoritative interactive 6DOF implementation. This module exists so CI, offline experiments, and provenance records can use the same boundary vocabulary and the same canonical E47 witness.
