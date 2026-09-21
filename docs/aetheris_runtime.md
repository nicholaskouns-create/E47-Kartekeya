# AETHERIS Runtime v0.1

AETHERIS is the compositional execution layer above independent Mathematical City instruments. It does **not** replace or govern those instruments. Each lab remains independently executable and joins a run only through a small typed module contract.

## Core contract

```text
StatePacket
    -> RuntimeModule.execute(...)
    -> StatePacket
    -> ModuleReceipt
    -> ...
    -> ExecutionCertificate
```

A `StatePacket` carries typed payload, metadata, parent digest, and producer. Every packet has a canonical SHA-256 digest. Every module emits checks and measurements. A full pipeline emits an `ExecutionCertificate` whose digest is deterministic for the same inputs and module outputs.

## Existing City instruments

Wrap an existing solver without rewriting it:

```python
from aetheris import AetherisRuntime, FunctionModule, StatePacket

runtime = AetherisRuntime()
runtime.register(FunctionModule(name="waveforge.fdtd", function=waveforge_step))
runtime.register(FunctionModule(name="eidolon.flight", function=eidolon_step))

packet = StatePacket(
    kind="field.flight",
    payload={"field": field_state, "craft": craft_state},
)

result = runtime.execute(packet, ["waveforge.fdtd", "eidolon.flight"])
print(result.certificate.to_record())
```

The callable can return a `ModuleResult`, a `StatePacket`, or a replacement payload mapping.

## Canonical E47 adapter

AETHERIS includes a lazy E47 adapter using the repository's existing `construct_e47_projector()` implementation:

```python
from aetheris import AetherisRuntime, E47ProjectorModule, StatePacket

runtime = AetherisRuntime()
runtime.register(E47ProjectorModule())
result = runtime.execute(
    StatePacket(kind="quantum.state", payload={"state": amplitudes_125}),
    ["e47.projector"],
)
```

The adapter certificates three conditions at runtime: projector rank 47, projector idempotence within tolerance, and invariance of the projected output under a second projection.

## Proposed instrument namespace

The runtime does not reserve implementations, only stable names for adapters:

```text
kartekeya.e47          spectral/kernel services
e47.projector          canonical 125 -> E47 projection
waveforge.fdtd         spatial field evolution
vectorcliff.simd       Clifford/SIMD compute kernel
mps.evolve             tensor-network evolution
eidolon.flight         flight-state evolution/render bridge
citadel.passport       evidence/provenance packaging
city.persistence       optional persistence sink
```

## Flight boundary and E47 witness

The browser SKYRMION Runtime 2 remains the interactive 120 Hz 6DOF implementation. AETHERIS now ships a Python companion in [`src/aetheris/flight_runtime.py`](../src/aetheris/flight_runtime.py) that supplies the shared state contract, conventional ↔ experimental-simulation vehicle boundary, one compiled E47 witness, and deterministic receipts without duplicating the browser aerodynamics.

The critical separation is:

```text
E47 projector/kernel witness     E1
            |
experimental adapter mapping     E2
            |
6DOF trajectory                  E2
```

See [AETHERIS Flight Boundary and E47 Witness](aetheris_flight_runtime.md) for the exact projector/capture/semigroup semantics and fleet contract.

## Persistence

Persistence is deliberately optional. `InMemoryStore` and `JsonlStore` ship in the core. A Supabase adapter can implement the same single-method `ExecutionStore.append(result)` protocol without introducing Supabase as a runtime dependency.

## Evidence boundary

AETHERIS certificates attest to what the executed modules actually checked. A machine receipt is not automatically experimental or physical validation. Modules carry the City's evidence class (`E0`, `E1`, `E2`, `E3`, `E4`, `H0`) so composed runs preserve the provenance of each claim rather than flattening them into one status.

## v0.1 invariants

1. Same packet content produces the same packet digest.
2. Same deterministic pipeline produces the same certificate digest.
3. Every module receipt links input and output digests.
4. Failed checks remain in the certificate and stop execution by default.
5. No external service is required by the core runtime.
6. Existing labs can be wrapped without modification.
