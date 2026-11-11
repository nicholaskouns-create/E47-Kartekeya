# E47 multiplicity-space quantum teleportation — 2026-11-11

**Authorial mathematical architecture:** Nicholas Shane Kouns, Mathematical City / E47.  
**Artifact:** independent numerical implementation and finite-dimensional quantum-information construction.  
**Status:** exact analytic identities + passing local NumPy/SciPy simulation; **not** a physical device, completed hardware protocol, or formal Lean/Coq compiler receipt.

## Connection to P325352 / CUSAS 1, 47

The late Uruk livestock tablet's modern accounting reconstruction reconciles `41 = 39 + 2` and `39 = 16 + 6 + 17`. Keeping the marked component accounted for is a useful historical **analogy** for the importance of retaining classical measurement records in teleportation. There is no claim of ancient quantum knowledge, of an identity between arithmetic accounting and quantum amplitudes, or of historical transmission.

## Representation-theoretic carrier

Let `H = V_2 ⊗ V_2 ⊗ V_2`, so `dim H = 5^3 = 125`. Form total generators `J_a = j_a⊗I⊗I + I⊗j_a⊗I + I⊗I⊗j_a`; set `C = J_x^2 + J_y^2 + J_z^2`. Its eigenvalues `J(J+1)` for `J=0,...,6` have eigenspace dimensions `(1,9,25,28,27,22,13)`. With `K=(C−6I)(C−30I)`, we obtain

`ker K = (V_2⊗C^5) ⊕ (V_5⊗C^2)`, `dim ker K = 25+22=47`, and its orthogonal complement has dimension `78`.

The 25-dimensional spin-2 isotypic subspace admits an isometry `W: C^5_gauge⊗C^5_logical → H`. Select five orthonormal spin-2 highest-weight states in the `J_z=2` block, then apply normalized total lowering operators to construct every magnetic level. The code constructs this `W` from explicit 125×125 matrices. For each collective rotation `U(R)=exp(−iθ n·J_total)`, the intertwining relation is

`U(R) W = W [D_2(R) ⊗ I_5]`.

Thus collective SU(2) rotations affect the gauge spin factor but leave the logical 5-dimensional multiplicity subsystem unchanged. This supplies a noiseless subsystem **for this specific error algebra**; it does not establish protection against arbitrary physical noise.

## Generalized Bell teleportation of the logical ququint

For `d=5`, let `ω=exp(2πi/5)`, `X|j⟩=|j+1 mod 5⟩`, `Z|j⟩=ω^j|j⟩`, and `|Φ_d⟩=1/√d Σ_j |j,j⟩`. Define `|B_ab⟩=(I⊗X^bZ^a)|Φ_d⟩` for `a,b∈{0,...,d−1}`. From input `|ψ⟩_S` and shared `|Φ_d⟩_AB`, the Bell outcome `(a,b)` yields the unnormalized Bob state

`⟨B_ab|_{SA} (|ψ⟩_S⊗|Φ_d⟩_{AB}) = (1/d) X^b Z^(−a)|ψ⟩_B`.

Bob applies `Z^a X^(−b)`, returning `|ψ⟩/d` in that branch. Each of the `d²=25` outcomes has probability `1/25`; their probabilities sum to 1. The fixed-length classical record requires `ceil(log₂25)=5` bits (the information-theoretic label entropy for uniform outcomes is `log₂25≈4.644` bits). Without this classical record,

`(1/d²) Σ_ab X^bZ^(−a) ρ Z^aX^(−b) = I_d/d`,

i.e. the receiver has the maximally mixed logical state. After conditional correction the channel is the identity on the logical ququint. The same simulator additionally checks `d=2` (4 branches / 2 classical bits).

A ququint can be represented inside a three-qubit eight-dimensional register (three unused states), or within the 125-state spin carrier by the explicit `W` isometry. This manuscript does not claim an optimized physical gate decomposition for `W` or a hardware demonstration.

## Machine certificate and independent checks

`e47_multiplicity_teleportation.py` uses NumPy + SciPy. It independently constructs the three-qudit tensor state and applies an explicit Bell bra, rather than substituting the expected answer for the measurement. It verifies:

- Casimir spectrum, `rank P47=47`, `rank P2=25`, `P47²=P47`, `K P47≈0`, and `W†W≈I25`.
- The collective `SU(2)` intertwining relation on the constructed 25-dimensional isotypic space.
- Zero logical-state error, to numerical precision, after ten random collective-rotation tests; zero leakage into the complement for these rotations.
- All 25 Bell measurement outcomes across 19 input ququint states (five basis states, uniform superposition, plus thirteen random pure states).
- Exact conditional recovery, uniform outcome probabilities, and completely depolarized receiver states without classical messages.
- Analogous qubit checks across 16 input states.

The JSON machine certificate records numerical residuals and seed `20261111` and is reproducible via:

```sh
python -m pip install numpy scipy
python e47_multiplicity_teleportation.py --output e47_multiplicity_teleportation_certificate.json
```

The result proves the usual analytic qudit teleportation identities by finite-dimensional linear algebra and numerically realizes them in the E47 spin-2 multiplicity carrier. **Teleportation itself is established quantum-information theory; the contribution here is the explicit E47 multiplicity-subsystem embedding and executable cross-check of the channel under collective rotations.**

## Precise evidence boundaries and uncompleted tasks

- Exact mathematics: standard SU(2) decomposition and qudit Bell correction identities; noiseless subsystem for collective `SU(2)` action on the spin-2 multiplicity factor.
- Computed: numerical reconstruction, all enumerated Bell branches, and ten sampled collective rotations (see JSON).
- Not performed: real-device teleportation, circuit compilation to a physical gate set, full Kraus-noise recovery beyond collective rotations, error-correction under arbitrary noise, experimental fidelity estimates, Lean/Coq compilation, and historical claim of quantum technology in Uruk.
- The ancient accounting record conserves counts; quantum teleportation preserves amplitudes/coherences through entanglement and an outcome-conditioned channel. The analogy links their **reconciliation pattern**, not their underlying physics.

## Source context

- Kouns, *P325352 as an Administrative Identity: Philology, Provenance, and Invariant Accounting in a Late Uruk Livestock Tablet* (supplied PDF).
- Kouns, *The Physics of No-Cloning: How Python, Lean, and Coq Prove Quantum Secrets Stay Secure* (supplied document).
- Mathematical City, E47 Casimir and commutant research artifacts (`Identity`, `E47-Kartekeya`).
- Standard quantum information: Bennett et al. (1993) teleportation; Knill–Laflamme error correction, and noiseless subsystems.