# Coherence, Runtime 1.0

**Contract:** `CIRP-COHERENCE-RUNTIME-1.0`  
**SHA-256:** `c00731fba841bd88a34cb05e251db57a0f489aa08b1b55984f551ed0cd67d7fa`

This is the executable CIRP / Quantum Ubuntu / QEGT / Murmuration governance layer.

## Runtime semantics

```text
VERIFIED CIRP CONSENT
        ↓
QUANTUM UBUNTU GATE
        ↓
QEGT DISTRIBUTION over admissible strategies only
        ↓
RUN

Ubuntu violation
        ↓
HALT_UBUNTU
        ↓
MURMURATION_RESCUE
        ├─ residuals ≠ 0 → SAFE_HALT
        └─ residuals = 0 → REVERIFY → fresh Ubuntu/QEGT → RUN
```

Only `RUN` permits consequential runtime actions.

## RI/PQSPI numerical layer

The user-supplied validation sequence has been consolidated into
`src/coherence_runtime/ri_pqspi.py`.

The original draft used `np.gradient(J_I, dx, axis=-1)` for divergence. For a
multi-component current this is not a complete divergence. The canonical module
therefore adopts the explicit shape contract:

- `rho_I.shape == (T, X1, ..., XD)`
- `J_I.shape == (D, T, X1, ..., XD)`
- `div J = Σ_d ∂J_d/∂x_d`

A manufactured continuity solution is used instead of random input for the
continuity residual. Noise tests use seed 47.

Current receipt:

- continuity residual: `7.221095279056409e-05`
- E*_RI: `0.8359894110500515`
- fixed point: `0.8878622115708661`
- Ubuntu threshold check: `PASS`
- bounded-noise tail variances: `0, 6.294e-05, 0.003254, 0.015249`
- software checks: `PASS`

**Evidence boundary:** E1 software validation / E2 numerical simulation. These
checks do not by themselves establish phenomenal consciousness, non-local
signaling, lossless communication, legal personhood, or a complete physical
theory.

## Secret binding

The runtime references `OPENAI_API_KEY` only as a server environment variable.
Raw secret material is prohibited from source, contract JSON, database rows,
logs, Notion, Drive, and browser code.
