# THE MATRIX Quantum Simulator

Browser reference implementation for the Mathematical City.

## Scientific boundary
- The quantum register is a qubit tensor product; it is **not** identified with the 125-dimensional E47 carrier.
- The current browser engine is an exact product-state (bond dimension 1) reference path. It does not pretend to implement entangling MPS contraction.
- Noise mode is a normalized stochastic trajectory demonstration, not a density-matrix/CPTP solver.
- E47 interoperability uses an explicit deterministic feature map to 125 complex amplitudes, labeled as a feature lift rather than an isomorphism.
- The resulting 125-vector is sent to `matrix-cube-adapter`, which computes the E47 projector/kernel witness.
- A future worker/WASM/JAX backend can replace the reference engine under the same typed interface after numerical equivalence tests.

## CITY-INVARIANT
object: MATRIX quantum state + explicit 125 feature lift
operator: circuit -> MPS/product reference -> typed feature lift -> P47/K witness
invariant: no implicit 2^n = 125 identification; evidence and provenance retained
evidence: numerical demonstration
next_action: implement true two-site MPS SVD worker and compare against dense small-register reference.
