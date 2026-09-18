# THE MATRIX Quantum Simulator

## Engine v2
The browser backend is now a real two-site Matrix Product State engine running in a Web Worker. Each nearest-neighbor CNOT contracts two site tensors, reshapes the merged tensor into a matrix, obtains a Schmidt/SVD factorization from the Hermitian Gram matrix, truncates to the configured bond dimension χ, and reconstructs the two MPS sites.

For small registers (n ≤ 10), the worker independently evolves the same circuit as an exact dense statevector and reports relative L2 disagreement. For n ≤ 16 it can materialize the MPS amplitudes for downstream feature extraction.

## Scientific boundary
- Qubit Hilbert space and the 125-dimensional E47 carrier remain distinct.
- The 125-vector is an explicit sampled-amplitude feature map, not an isomorphism.
- E47/Cube analysis begins only after that typed lift.
- Bond truncation is reported as discarded Schmidt weight.
- This worker is CPU/Web Worker acceleration. WebGPU/WASM/JAX are replaceable future backends behind the same contract.
- No canonical promotion is implied by numerical agreement.

## Pipeline
dense reference → two-site MPS worker → accelerator contract → 125 feature bridge → E47 → Cube → AETHERIS
