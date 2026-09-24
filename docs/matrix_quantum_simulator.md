# THE MATRIX Quantum Simulator

![THE MATRIX Quantum Simulator](../website/assets/matrix/matrix-cover.jpg)

[Open MATRIX](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/matrix/) · [Parity certificate](../website/data/MC-MATRIX-PARITY-20260921-001.json) · [E47 prism certificate](../website/data/MC-MATRIX-E47-PRISM-20260922-001.json) · [E47 constants certificate](../website/data/MC-E47-CONSTANTS-20260923.json) · [Prism formalism](../research/e47/E47_Prism_Spectral_Formalism.md) · [Parity validator](../scripts/validate_matrix_quantum_parity.py) · [E47 constant validator](../scripts/e47_constant_validation.py)

## Status

**E1 software/numerical quantum-simulation parity: PASS.**

Canonical certificate: `MC-MATRIX-PARITY-20260921-001`.

Certified run: **8 qubits, 24 layers, maximum bond χ = 16, phase φ = 0.7**. The browser MPS worker also passes exact-equivalence smoke tests for untruncated registers `n=2..8`.

| Check | Result |
|---|---:|
| Python MPS ↔ dense phase-aligned relative L2 | `6.9797841682435854e-15` |
| State fidelity | `1.0` |
| Observable maximum error | `4.163336342344337e-15` |
| Schmidt-spectrum maximum error | `1.6653345369377348e-15` |
| Discarded weight | `5.241335934017881e-32` |
| Qiskit Aer phase-aligned relative L2 | `1.5030029036919424e-14` |
| Qiskit Aer fidelity | `1.0000000000000004` |

Independent quantum oracle: **Qiskit 2.5.0 + qiskit-aer 0.17.2**.

## Engine v2

The browser backend is a two-site complex-Float64 Matrix Product State engine running in a Web Worker. Each nearest-neighbor CNOT contracts two site tensors, reshapes the merged tensor into a matrix, performs a stable SVD/Jacobi factorization, truncates to the configured bond dimension χ when needed, and reconstructs the two MPS sites.

The worker also carries:
- an exact dense statevector reference for small registers;
- deterministic seeded amplitude-damping + phase-flip trajectories;
- explicit discarded-Schmidt-weight telemetry;
- materialization of amplitudes for the downstream typed feature lift.

## Representation contract

The simulator intentionally separates three arrows:

1. **MPS ↔ dense / Qiskit Aer** is state-representation parity up to global phase.
2. **256 → 125** is an explicit normalized sampled-amplitude **feature map**, not a Hilbert-space isomorphism.
3. **125 → 128** is an isometric embedding with invalid padding states 125, 126, 127.

## E47 downstream witness

After the typed 125-state lift, the independent Python reconstruction verifies:

- rank P47 = 47
- Ωc = 47/125 = 0.376
- Frobenius residual P47² − P47 = `5.541372953883602e-15`
- Frobenius residual K P47 = `4.996015056480395e-12`
- spec(K²) = `{0, 11664, 12544, 19600, 32400, 186624}`
- spectral gap = `11664`
- maximum K² eigenvalue = `186624`

For the 125 → 128 embedding, both the isometry residual and the R47 intertwiner residual are exactly zero at the reported numerical precision, with zero population in padding states 125..127.

## E47 finite-core constant certificate

The standalone validator `scripts/e47_constant_validation.py` reconstructs the spin-2 tensor cube independently of the MATRIX browser runtime and records **19/19 PASS** for the finite E47 fingerprint:

`125 · 47 · 78 · 47/125 · 18 · 12 · 6 · 30 · 108 · 432 · 11664 · 186624 · 1/99144 · 15/17`

It verifies the Casimir spectrum and multiplicities, `rank(K)=78`, `nullity(K)=47`, projector rank/trace 47, `P²≈P`, `KP≈0`, the `K²` gap/norm, and the minimax contraction constants. At 252 iterations the direct floating-point operator error is `4.7049900678789936e-14`; the exact spectral worst-case factor is `(15/17)^252 = 2.0038679292982893e-14`.

Authority: [machine certificate](../website/data/MC-E47-CONSTANTS-20260923.json) · [Python source](../scripts/e47_constant_validation.py) · [public Notion certificate](https://mathematicalcity.notion.site/E47-Invariant-Kernel-Verification-252-Step-Spectral-Projector-Certificate-3e546094fd3081738c01e36b7b75e3af?pvs=149).

This certificate belongs to the typed **125-state E47 layer**. It does not alter the separate MATRIX qubit-parity certificate and does not identify the 256-dimensional qubit register with the 125-dimensional E47 carrier.


## E47 prism experiment

MATRIX 2.1 exposes the Casimir decomposition of the typed 125-feature vector as a seven-band spectral witness. The certified configuration is the same one used by the parity certificate: **8 qubits, 24 layers, χ = 16, φ = 0.7**, ideal brickwork evolution.

Independent Python reconstruction gives:

| Casimir λ | Multiplicity | State weight |
|---:|---:|---:|
| 0 | 1 | 0.003873208953955917 |
| 2 | 9 | 0.06049575013782006 |
| **6** | **25** | **0.12153223655298497** |
| 12 | 28 | 0.17853315216187027 |
| 20 | 27 | 0.17702406495212444 |
| **30** | **22** | **0.25351593478374257** |
| 42 | 13 | 0.2050256524575022 |

The weights sum to (1) to floating-point precision. The two selected bands give

[
w_{E47}=w_6+w_{30}=0.3750481713367275,
]

or **37.50481713367275%** for this state. The rank fraction is (47/125=0.376), so this particular circuit state lies **0.095182866327248 percentage points below** the isotropic rank fraction.

That near numerical agreement is an observed property of this circuit/lift, not an identity for arbitrary states. The individual band weights are strongly non-uniform, so the result is not a flat dimension-proportional spectrum.

The **E47 PRISM TEST** button runs the certified configuration, performs the documented 256→125 typed lift, requests the seven projectors from the live `matrix-cube-adapter@3`, and checks their sum and (P_6+P_{30}) parity.

Reproduce locally:

```bash
python scripts/validate_e47_prism_matrix.py
python scripts/validate_e47_prism_matrix.py --live-adapter
```

Cross-platform authority: [GitHub formalism](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/E47_Prism_Spectral_Formalism.md) · [Notion FRM-96](https://app.notion.com/p/3e346094fd30818e99c1d04635983c62?pvs=204) · [Drive mirror](https://docs.google.com/document/d/1wCmn5J4Tjo0qVV5AOoHUxD1tXComhPf7lU1ntzKtaMs/edit) · [live Supabase adapter](https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter).


## Scientific boundary

- THE MATRIX is a **software quantum simulator**, not a quantum computer.
- The E1 certificate covers numerical/software parity, not hardware or experimental physics.
- Bond truncation is approximation and must be read together with discarded Schmidt weight.
- The 125-feature lift does not identify qubit Hilbert space with the E47 carrier.
- E47 analysis starts only after the typed lift.
- The E47 witness does not promote downstream E2 simulations into E1 physical claims.

## Reproduce

```bash
node scripts/check_matrix_mps_worker.mjs
python scripts/validate_matrix_quantum_parity.py --require-qiskit
python scripts/e47_constant_validation.py --csv E47_constant_validation.csv
```

The GitHub Actions workflow `.github/workflows/matrix-mps-validation.yml` runs both the browser worker smoke and the independent Python/Qiskit Aer parity gate.

## Pipeline

`circuit → two-site MPS → dense/Aer parity → feature-125 → P47,K → embedding-128 → CITY-125 / AETHERIS`
