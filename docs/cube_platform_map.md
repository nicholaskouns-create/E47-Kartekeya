# Cube Platform Map + MATRIX MPS validation

The City can be viewed as one typed cube rather than a directory. Faces are public/runtime domains; edges are adapters; the interior is the invariant/provenance spine.

## Cube faces
- Front: Eidolon / City World / CITY CORE
- Back: AETHERIS packets, receipts, persistence
- Right: THE MATRIX, dense reference and two-site MPS
- Left: WaveForge and field/dynamics labs
- Top: SEE / Proof Forge / certificates
- Bottom: GitHub / Drive / Notion / data provenance
- Interior: Kartekeya / E47, 125 → K → 47

## MATRIX compute spine
dense reference → two-site MPS Web Worker → accelerator contract → explicit 125 feature bridge → E47 → Cube → AETHERIS

The MPS engine contracts adjacent site tensors, applies a two-site gate, computes a Schmidt factorization via the Hermitian Gram matrix, truncates to χ, reconstructs the two sites, and records discarded Schmidt weight. Small registers are independently checked against exact dense evolution.

The 125 feature bridge is explicitly a feature map, not an isomorphism between a qubit Hilbert space and V2^⊗3. E47 evidence begins only after the typed 125-vector is formed.

## Backend status
Current accelerated isolation is a Web Worker using complex Float64. WASM/WebGPU/JAX remains a replaceable backend target under the same contract. This branch does not claim those backends are implemented.

Run:
`node scripts/check_matrix_mps_worker.mjs`
