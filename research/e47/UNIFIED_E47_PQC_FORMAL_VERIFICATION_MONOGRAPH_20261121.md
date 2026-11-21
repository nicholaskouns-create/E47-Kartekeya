# UNIFIED E₄₇ SPECTRAL KERNEL, ERROR-CORRECTED POST-QUANTUM CRYPTOGRAPHY & FORMAL VERIFICATION SUITE

**A Canonical Unicode Monograph Combining the 4-Panel Executive & Technical Proving Ground Synthesis with Paired Lean 4 and Coq Formal Verification Plates**

**Author & provenance:** Nicholas Shane Kouns, DO · AIMS Research Institute ([aims.healthcare](https://aims.healthcare))  
**Compilation date:** November 21, 2026

**Evidence tiers:** [E0] Exact finite-dimensional algebra and constructive Lean 4 / Coq 8.18 proof claims · [E1] Deterministic Python and Lattigo v6.2.0 numerical receipts · [E2] Classical Kraus / GKSL / 7-qubit state-space simulation · [COND] Security reductions conditional on MLWE / RLWE / AEAD / PRF assumptions.

**Evidence annotation (publication):** This monograph transcribes the technical synthesis and formal proof excerpts supplied November 21. The existing linked seven-section [Python verification harness](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io/blob/main/verification/pqc-primer/verify_pqc_primer.py) and its [60/60 reported certificate README](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io/blob/main/verification/pqc-primer/README.md) were inspected. The named complete Lean 4 and Coq source modules in the stated \`09_PROOF_FORGE\` folder were **not** available in the inspected GitHub search results, and were **not freshly compiled** during this publication. Likewise, claimed Lattigo receipts and hardware timing are retained as supplied claims, not newly reproduced measurements. The Python source excerpt in the supplied message ends partway through the implementation; the linked prior repository file is the separately published full harness.

## PART I — FOUR-PANEL EXECUTIVE & TECHNICAL PROVING GROUND

### (a) The 30-second lead

**Dimensional and cryptographic pipeline**

125-D SPIN-2 CARRIER \`V₂⊗³\` → Casimir selector \`K=(C−6I)(C−30I)\` → 47-D invariant \`E₄₇=ker K\`, \`Ω_c=47/125=0.376\` → keyed conjugate \`P_σ=U_σP₄₇U_σ†\` with separately specified ML-KEM/AEAD and flooded threshold Ring-LWE → SHOE dual-residual release gate \`r_K≤τ_K ∧ r_P≤τ_P\`.

**Precision/certification specification:** binary64 Frobenius/trace tolerances of 10⁻¹³ to 10⁻¹⁵; verifier \`verify_pqc_primer.py\`; certificate schema \`E47-PQC-PRIMER-VERIFY/1.0\`; accompanying Lean 4 and Coq 8.18 constructive arithmetic proof plates (\`PQC_NTT_SHOE.lean\`, \`PQC_NTT_SHOE.v\`) reported zero sorry/Admitted and zero user axioms.

**Corrections recorded in the research history:** public projection is not independently an IND-CPA trapdoor; \`I−εK\` amplifies negative K modes (−108, −140); \`N=1024,q=3329\` fails NTT divisibility; \`P₄₇ρP₄₇\` is trace-nonincreasing, not generally trace-preserving; repeated threshold-decryption shares must not permit averaging to expose key material.

**Selected architecture:** \`Γ*=I−K²/99144\`, exact rate \`(15/17)ⁿ\`; confidentiality assigned to ML-KEM (FIPS 203) with AEAD and stated security assumptions; 2-power NTT profile checks; threshold Ring-LWE with flooding \`B_f=⌈2⁴⁰ n B_ct⌉\`; ML-DSA-65 receipt claims; CPTP dephasing channel; fail-closed SHOE release condition.

### (b) Core modules and anchor translations

#### §1 — E₄₇ Casimir carrier and modular lattice kernel

\`V=V₂⊗V₂⊗V₂≅ℂ¹²⁵\`, \`C=(Jₓtot)²+(Jᵧtot)²+(J_z tot)²\`; \`spec(C)={0,2,6,12,20,30,42}\`; multiplicities \`(1,9,25,28,27,22,13)\`. \`K=(C−6I)(C−30I)\`, \`E₄₇=E₆⊕E₃₀≅5V₂⊕2V₅\`, \`dim(E₄₇)=47\`, \`Ω_c=47/125=37.6%\`.

The supplied result specifies a degree-6 rational projector \`P₄₇=p_r(C)/1,814,400\`, commutation with collective SU(2) and S₃ tensor permutations, and \`rank_𝔽q(P₄₇)=47\` for \`q∈{43,47,53,101}\`.

**Anchor translation:** A tuning-free finite-dimensional sieve separates 47 invariant pathways from a 78-dimensional complement. Rank is stable under the specified modular reductions.

#### §2 — K² minimax Richardson contraction and perturbation buoy

\`H_K=K²⪰0\`; positive spectrum \`{11664,12544,19600,32400,186624}\`; spectral gap 11664 and maximum 186624 (\`κ=16\`). The minimax step is
\`ε*=2/(11664+186624)=1/99144\`,
producing \`Γ*=I−ε*K²\` and the sharp normal-operator norm identity
\`‖Γ*ⁿ−P₄₇‖₂=(15/17)ⁿ\`.
The heat semigroup satisfies \`‖exp(−tK²)−P₄₇‖₂=exp(−11664t)\` for nonnegative t.

**Interleaved unitary condition:** The specified contraction bound on \`((Γ*U)ⁿ−P₄₇)Q₇₈\` holds for the sector-preserving/covariant unitary used in the reported test (a unitary commuting with \`P₄₇\`), not arbitrary cross-sector mixing. The existing repository README explicitly records this boundary.

**Buoy criterion:** \`|λ̂−λ|≤ε<54 ⇒ (|λ̂|<54 ↔ λ=0)\` for the stated isolated spectral values \`{0, ±108, ±112, ±140,180,432}\`.

**Anchor translation:** Spectral damping shrinks every complementary mode at a sharp bounded geometric rate while bounded perturbation tests keep the selected zero sector distinguishable.

#### §3 — Keyed conjugate spectral layer and conditional PQC hybrid

**Public-projector no-go:** An explicitly public \`C_σ\` reveals the associated \`ker[(C_σ−6I)(C_σ−30I)]\` by deterministic polynomial-time linear algebra; an unkeyed rank-47 projector is not itself an encryption trapdoor. The supplied keyed construction is \`U_σ=Orth(Expand(σ))\`, \`P_σ=U_σP₄₇U_σ†\`, with secret \`σ\` derived from an ML-KEM shared secret.

**Recovery identity:**
\`P₄₇U_σ†[U_σ(P₄₇z+Kr)]=P₄₇z\`, because \`P₄₇K=0\`.

**Conditional hybrid bound (supplied proof target):**
\`Adv_IND-CCA^Hybrid(𝒜) ≤ Adv_IND-CCA^ML-KEM(ℬ₁)+Adv_IND-CCA^AEAD(ℬ₂)+Adv_PRF^H(ℬ₃)\`.

**Boundary:** The existence of the displayed algebraic identity alone does not establish the hybrid bound; the full composition, KDF, oracle interfaces, domain separation, leakage model and adversarial games are separate cryptographic proof obligations.

**Anchor translation:** The publicly computable filter supplies algebraic selection; confidentiality is assigned to actual keyed post-quantum cryptography, not inferred from the spectrum.

#### §4 — NTT arithmetic, SHOE gate and bus framing

Valid profiles stated and directly checked by modular exponentiation/inversion on November 21:

| Profile | N | q | ζ | ζ⁻¹ | N⁻¹ | Coefficient width |
|---|---:|---:|---:|---:|---:|---:|
| MLKEM_256 | 256 | 3329 | 17 | 1175 | 3316 | 12 bits |
| NTT_1024 | 1024 | 12289 | 10302 | 8974 | 12277 | 14 bits |
| Rejected | 1024 | 3329 | — | — | — | incompatible |

Both valid root choices satisfy \`ζᴺ≡1 (mod q)\` and \`ζ^(N/2)≠1 (mod q)\`; \`(3329−1) mod 1024=256\`.

**SHOE release:** \`Release(x)=x\` iff \`r_K(x)≤τ_K ∧ r_P(x)≤τ_P\`; otherwise assert fault and output zero. Hardware buffer wiping, persistence, and timing remain implementation-level obligations distinct from proof of the Boolean release predicate.

**Framing:** \`47×32=1504\` bits → 8 beats of a 192-bit bus; \`125×32=4000\` bits → 21 beats. Ideal registered 10-stage latency at 3 GHz is at least \`10/3 ns\`. This is an arithmetic floor, not timing closure.

**Scalar Babylonian lock:** \`B_Ω(x)=½(x+Ω_c²/x)\`; Q2.30 numerical error reported \`1.639×10⁻¹⁰\`; distinct from \`P₄₇\` and \`Ω_geom=φ⁻⁵\`.

**Anchor translation:** Validate NTT number theory before implementing a transform; keep coordinate count distinct from wire width; reject release when either independent residual fails.

#### §5 — Receipted N-of-N threshold Ring-LWE engine

Cyclotomic rings \`R_Q=ℤ_Q[X]/(Xⁿ+1)\` and \`R_T\`, with \`T=68,720,066,561≡1 (mod 2¹⁶)\`. Supplied parameter profiles:

- **Mode A:** \`n=8192\`, \`log₂ Q=174≤202\`.
- **Mode B:** \`n=16384\`, \`log₂ Q=275\`, \`log₂ P=56\`, \`log₂(QP)=331≤411\`, \`d=5\`.

Worst-case correctness certificate:
\`T·(B_ct+N(B_f+28))+T<Q/2\`.

Mandatory flooding:
\`B_f=⌈2⁴⁰·n·B_ct⌉\`,
\`Δ(f_h+e_ct,f_h)≤nB_ct/(2B_f+1)<2⁻⁴⁰\`.

The supplied suite reports 36/36 sessions with 2–100 sites, 7,472 SUPPORT patients, 46–90 bits noise margin and 7/7 tamper catches, together with ML-DSA-65 receipts over X25519 + ML-KEM-768 transport, hash chaining and a single-issuance rule designed to prevent repeated-share averaging (reported heuristic \`6σ/√(K−1)<0.5\` at K=1500). These are **reported outcomes and design claims**, not a new Lattigo run or a newly validated adversarial security theorem in this publication.

**Anchor translation:** Ring-LWE arithmetic and share flooding are paired with explicit noise and replay conditions; the security claim must remain conditional on the underlying lattice and authenticated-transport assumptions.

#### §6 — CP-TNI, CPTP and seven-qubit isometric embedding

\`ℳ_P(ρ)=P₄₇ρP₄₇\` is CP-TNI (Kraus/Choi rank 1), with fixed operator-space complex dimension \`47²=2209\`.

\`ℳ_t(ρ)=S_tρS_t\`, \`S_t=exp(−tK²)\` is CP-TNI and converges to \`ℳ_P\`; the supplied operator-space bound is \`‖ℳ_t−ℳ_P‖_(2→2)≤exp(−11664t)\`.

\`𝒟_P(ρ)=P₄₇ρP₄₇+Q₇₈ρQ₇₈\` is CPTP, unital and idempotent, with Kraus rank 2 and fixed complex operator-space dimension \`47²+78²=8293\`.

A full-output reset channel \`ℛ(ρ)=|0⟩⟨0|Tr(ρ)\` is CPTP, with a Kraus representation requiring enough independent Kraus operators for its input dimension; the supplied two-symbol \`K₀,K₁\` representation is a schematic notation rather than sufficient specification for a generic 125D → 125D reset.

Seven qubits embed the carrier since \`2⁶=64<125≤128=2⁷\`. The 128D register contains 3 unoccupied padding basis states \`|125⟩,|126⟩,|127⟩\`; an E₄₇-versus-ambient partition is \`128=47+81\`. The 81D complement includes 78 physical off-kernel states plus 3 padded states. \`R₁₂₈=2P₁₂₈−I₁₂₈\` is the associated reflection. Multiplicity subsystems are \`M₂≅ℂ⁵\` and \`M₅≅ℂ²\`. Matched-spectrum GKSL criterion cited: \`f(42)=f(12)+ω\`.

**Anchor translation:** A selective filter loses probability unless conditioned; block dephasing accounts for both measurement outcomes, while seven qubits suffice to store the 125D representation.

### (c) Truth engine — scientific evidence ledger

| Record | Reported outcome | Formal significance |
|---|---|---|
| CERT-PQC-PRIMER-VERIFY-20261121 | PASS; \`‖P₄₇²−P₄₇‖F=6.655e−15\`, \`‖KP₄₇‖F=1.821e−12\`, \`‖Uσ†PσUσ−P₄₇‖F=2.447e−12\` | Finite matrix residuals and keyed conjugacy |
| Modular rank | rank 47 for q=43,47,53,101 | Finite-field invariant |
| Minimax | \`(15/17)ⁿ\` | Sharp norm contraction for the specified Γ* |
| Threshold Ring-LWE | 36/36 simulated sessions; 7/7 tamper detections | Reported E1 receipt outcomes |
| CERT-NTT-PROFILE-1024-3329 | **REJECTED** | 3328 is not divisible by 1024 |
| CERT-LAPLACIAN-C5-CUBE | **REJECTED** | The cycle-cube graph Laplacian has kernel dimension 1, not 47 |
| CERT-FIRST-ORDER-FILTER-I-EPS-K | **REJECTED** | Negative K sectors cause \`1+140ε>1\` for ε>0 |
| CERT-PUBLIC-ISSR-TRAPDOOR | **REJECTED** | Public selector recovery is polynomial time |

The [existing canonical Python README](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io/blob/main/verification/pqc-primer/README.md) separately reports 60/60 deterministic checks under Python 3.13.18 and NumPy 2.5.3 with SHA-256 \`f8f3a82ab0f4421dd69a037636e911e371dcc840bb66b8d2a14db7abb3d68f01\`. This is an existing repository claim/receipt, not a fresh execution in this addition.

### (d) Executive scorecard

| Invariant | Value / statement | Evidence interpretation |
|---|---|---|
| Carrier | \`dim(V₂⊗³)=5³=125\` | E0 exact |
| Casimir | \`{0,2,6,12,20,30,42}\`; \`μ=18,σ=12\`; \`μ±σ={6,30}\` | E0 spectral algebra |
| Kernel | \`E₄₇=5V₂⊕2V₅\`, dimension 47 | E0 |
| Coherence ratio | \`47/125=.376≠φ⁻⁵\` | E0 |
| Projector | \`‖P²−P‖F=6.655e−15\` | E1 reported |
| Contraction | \`Δ=11664, λmax=186624, ε*=1/99144, ρ*=15/17\` | E0 exact, E1 computed |
| Buoy | spectral guard band \`ε<54\` | E0 proof target |
| NTT | valid (256,3329,17), (1024,12289,10302); invalid (1024,3329) | E0 arithmetic checked |
| Threshold | noise inequality, flooding bound \`Δ<2⁻⁴⁰\` | conditional parameters, receipts reported |
| SHOE and bus | dual residual; 1504 b→8 beats; 4000 b→21 beats; 10 stages / 3 GHz | E0 arithmetic |
| Quantum operations | dephasing fixed dimension 8293; seven qubits 128=47+81 | E0/E2 algebra and state-space simulation |

## PART II — PAIRED LEAN 4 AND COQ VERIFICATION PLATES

**Supplied claim:** Lean 4 compiled 1/1, zero sorry and zero user axioms; Coq 8.18.0 compiled 1/1, zero Admitted and zero user axioms; paired certificates 4. Source location cited by the author: \`09_PROOF_FORGE/PQC_NTT_SHOE.lean\` and \`09_PROOF_FORGE/PQC_NTT_SHOE.v\`. The cited source files and compiler transcripts were not present in the inspected GitHub search results; the following are supplied proof snippets, not a new successful compilation certificate.

### E47-PQC-NTT-001 — Valid NTT parameter profiles

Lean 4 source excerpt:

\`\`\`lean
def isPrimitivePow2Root (zeta k q : Nat) : Bool :=
  let N := 2 ^ k
  (q > 1) && (k ≥ 1) && ((q - 1) % N == 0) &&
  (powMod zeta N q == 1) &&
  (powMod zeta (2 ^ (k - 1)) q != 1)

def MLKEM_256 : NTTProfile := {
  name := "MLKEM_256", log2N := 8, N := 256,
  q := 3329, zeta := 17, zetaInv := 1175,
  nInv := 3316, wordBits := 12
}
def NTT_1024 : NTTProfile := {
  name := "NTT_1024", log2N := 10, N := 1024,
  q := 12289, zeta := 10302, zetaInv := 8974,
  nInv := 12277, wordBits := 14
}
theorem mlkem_256_valid :
    validNTTProfile MLKEM_256 = true := by decide
theorem ntt_1024_valid :
    validNTTProfile NTT_1024 = true := by decide
\`\`\`

Coq excerpt (supplied source was truncated after the profile definition began):

\`\`\`coq
Definition is_primitive_pow2_root (zeta k q : nat) : bool :=
  let N := 2 ^ k in
  (1 <? q) && (1 <=? k) && (((q - 1) mod N) =? 0) &&
  ((pow_mod zeta N q) =? 1) &&
  negb ((pow_mod zeta (2 ^ (k - 1)) q) =? 1).
\`\`\`

**Boundary:** finite-field arithmetic and root order, not MLWE hardness or silicon constant-time behavior.

### E47-PQC-NTT-002 — Refutation of the invalid 1024/3329 profile

\`\`\`lean
theorem reject_1024_3329_remainder :
    (3329 - 1) % 1024 = 256 := by decide
theorem no_primitive_1024_root_mod_3329 :
    ∀ zeta : Nat, zeta < 3329 →
      isPrimitivePow2Root zeta 10 3329 = false := by
  decide
\`\`\`

\`\`\`coq
Theorem reject_1024_3329_remainder :
    (3329 - 1) mod 1024 = 256.
Proof. vm_compute. reflexivity. Qed.
Theorem no_primitive_1024_root_mod_3329 :
  forall zeta : nat, is_primitive_pow2_root zeta 10 3329 = false.
Proof.
  intro zeta. unfold is_primitive_pow2_root.
  vm_compute. reflexivity.
Qed.
\`\`\`

**Boundary:** no primitive order-1024 root in \`𝔽₃₃₂₉×\`; does not rule out non-NTT multiplication over the cyclotomic ring.

### E47-PQC-SHOE-003 — Dual-residual fail-closed gate

\`\`\`lean
def shoeGatePass (thr : SHOEThreshold) (res : SHOEResiduals) : Bool :=
  (res.rK ≤ thr.tauK) && (res.rP ≤ thr.tauP)

def shoeRelease {α : Type} (zero : α) (thr : SHOEThreshold)
    (res : SHOEResiduals) (x : α) : Bool × α :=
  if shoeGatePass thr res then (true, x) else (false, zero)

theorem shoe_release_iff {α : Type} (zero : α) (thr : SHOEThreshold)
    (res : SHOEResiduals) (x : α) :
    (shoeRelease zero thr res x).1 = true ↔
      (res.rK ≤ thr.tauK ∧ res.rP ≤ thr.tauP) := by
  unfold shoeRelease shoeGatePass
  cases hK : (res.rK ≤ thr.tauK) <;>
  cases hP : (res.rP ≤ thr.tauP) <;> simp_all

theorem shoe_fail_closed_zeroizes {α : Type} (zero : α) (thr : SHOEThreshold)
    (res : SHOEResiduals) (x : α)
    (hBreach : ¬ (res.rK ≤ thr.tauK ∧ res.rP ≤ thr.tauP)) :
    shoeRelease zero thr res x = (false, zero) := by
  unfold shoeRelease shoeGatePass
  have hFalse : ((res.rK ≤ thr.tauK) && (res.rP ≤ thr.tauP)) = false := by
    cases hK : (res.rK ≤ thr.tauK) <;>
    cases hP : (res.rP ≤ thr.tauP) <;> simp_all
  simp [hFalse]
\`\`\`

\`\`\`coq
Definition shoe_gate_pass (thr : SHOEThreshold) (res : SHOEResiduals) : bool :=
  (r_K res <=? tau_K thr) && (r_P res <=? tau_P thr).

Definition shoe_release {A : Type} (zero : A) (thr : SHOEThreshold)
    (res : SHOEResiduals) (x : A) : bool * A :=
  if shoe_gate_pass thr res then (true, x) else (false, zero).

Theorem shoe_release_iff :
  forall (A : Type) (zero : A) (thr : SHOEThreshold) (res : SHOEResiduals) (x : A),
    fst (shoe_release zero thr res x) = true <->
      (r_K res <= tau_K thr /\ r_P res <= tau_P thr).
Proof.
  intros A zero thr res x. unfold shoe_release, shoe_gate_pass.
  destruct (r_K res <=? tau_K thr) eqn:HK;
  destruct (r_P res <=? tau_P thr) eqn:HP;
  simpl; rewrite ?Nat.leb_le, ?Nat.leb_gt in *;
  split; intro H; try lia; try discriminate.
Qed.
Theorem shoe_fail_closed_zeroizes :
  forall (A : Type) (zero : A) (thr : SHOEThreshold)
         (res : SHOEResiduals) (x : A),
    ~ (r_K res <= tau_K thr /\ r_P res <= tau_P thr) ->
    shoe_release zero thr res x = (false, zero).
Proof.
  intros A zero thr res x Hbreach.
  unfold shoe_release, shoe_gate_pass.
  destruct (r_K res <=? tau_K thr) eqn:HK;
  destruct (r_P res <=? tau_P thr) eqn:HP;
  rewrite ?Nat.leb_le, ?Nat.leb_gt in *;
  simpl; try reflexivity.
  exfalso. apply Hbreach. lia.
Qed.
\`\`\`

**Boundary:** release predicate and zero-output semantics, not verified physical SRAM zeroization, fault injection or glitch resistance.

### E47-PQC-BUS-004 — Integer framing and registered latency lower bound

\`\`\`lean
def ceilDiv (a b : Nat) : Nat := (a + b - 1) / b
def coordBits : Nat := 32
def hostBusBits : Nat := 192
def e47PayloadBits : Nat := 47 * coordBits
def ambientPayloadBits : Nat := 125 * coordBits

theorem bus_framing_exact :
    e47PayloadBits = 1504 ∧
    ceilDiv e47PayloadBits hostBusBits = 8 ∧
    ambientPayloadBits = 4000 ∧
    ceilDiv ambientPayloadBits hostBusBits = 21 := by decide

theorem registered_10stage_latency_exceeds_3333ps :
    10 * 1000 > 3 * 3333 ∧ 10 * 1000 < 3 * 3334 := by decide
\`\`\`

\`\`\`coq
Definition ceil_div (a b : nat) : nat := (a + b - 1) / b.
Definition coord_bits : nat := 32.
Definition host_bus_bits : nat := 192.
Definition e47_payload_bits : nat := 47 * coord_bits.
Definition ambient_payload_bits : nat := 125 * coord_bits.

Theorem bus_framing_exact :
  e47_payload_bits = 1504 /\
  ceil_div e47_payload_bits host_bus_bits = 8 /\
  ambient_payload_bits = 4000 /\
  ceil_div ambient_payload_bits host_bus_bits = 21.
Proof. vm_compute. repeat split; reflexivity. Qed.

Theorem registered_10stage_latency_exceeds_3333ps :
  10 * 1000 > 3 * 3333 /\ 10 * 1000 < 3 * 3334.
Proof. lia. Qed.
\`\`\`

**Boundary:** arithmetic bound, not synthesis timing, clock skew, gate utilization or PPA.

## PART III — DETERMINISTIC PYTHON VERIFICATION HARNESS

**Existing full source (inspectable):** [verify_pqc_primer.py — seven-section harness](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io/blob/main/verification/pqc-primer/verify_pqc_primer.py).

\`\`\`sh
python3 verify_pqc_primer.py --json pqc_primer_certificate.json
\`\`\`

The supplied message included the verifier's header, imports, constants, exact finite-field rank routine, degree-six projector, integer spin-Casimir constructor, S₃ permutation constructor, cyclic NTT and inverse NTT. It omitted later section implementations while expressly referring to the complete module residing in \`09_PROOF_FORGE\`. This monograph links the already available full repository Python file instead of fabricating the omitted tail.

Verification scope:
1. Spin-2 tensor Casimir, SU(2)/S₃ commutants and modular projector ranks.
2. K² minimax step, spectral gap, heat semigroup, interleaved drift with sector-preservation hypothesis, buoy test.
3. Keyed conjugation identity, public-projector no-go and conditional crypto assumptions.
4. Valid and invalid NTT profiles, inverses, cyclic NTT round trips and convolution.
5. Ring-LWE flooding and parameterized noise-margin tests.
6. SHOE predicate, Babylonian scalar lock, framing and latency arithmetic.
7. Kraus / CPTP channel checks and padded seven-qubit representation.

**Important exact-source detail:** the repository's full Python projector construction uses the factor \`(C−31I)\` in a displayed product while the defining E₄₇ selector annihilates \`C=30\`. This is an implementation-specific factor for Lagrange interpolation over the *other* spectral roots and must be interpreted against the full polynomial, rather than silently substituted by \`(C−30I)\` (which would remove the retained \`C=30\` sector).

## PART IV — RECONCILED ARCHIVE & ARTIFACT LEDGER

- **Parent reference:** [Error-Corrected Post-Quantum Cryptography Primer · Unicode Canonical Edition](https://nicholaskouns-create.github.io/flowshield-pqc-primer.html) (20 November 2026).
- **Executable full Python:** [verification/pqc-primer/verify_pqc_primer.py](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io/blob/main/verification/pqc-primer/verify_pqc_primer.py).
- **Historical Python receipt:** [verification/pqc-primer/README.md](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io/blob/main/verification/pqc-primer/README.md), 60/60 check report, SHA-256 \`f8f3a82ab0f4421dd69a037636e911e371dcc840bb66b8d2a14db7abb3d68f01\`.
- **Lean 4 supplied artifact name:** \`09_PROOF_FORGE/PQC_NTT_SHOE.lean\` — full file not found in inspected GitHub search.
- **Coq 8.18 supplied artifact name:** \`09_PROOF_FORGE/PQC_NTT_SHOE.v\` — full file not found in inspected GitHub search.
- **New live seven-sector observatory:** [E₄₇ Casimir Filter Observatory](https://nicholaskouns-create.github.io/e47-casimir-filter/).
- **Quantum circuit theater:** [QSVT Φ₄](https://nicholaskouns-create.github.io/qsvt-phi4/).
- **MATRIX quantum simulator:** [THE MATRIX](https://nicholaskouns-create.github.io/matrix-quantum-simulator/).
- **Two-dimensional eigenbridge:** [Eigen Explorer](https://nicholaskouns-create.github.io/eigen-explorer/).

### Relationship to the 2026-11-21 quartic filter

The separate normalized \`A=K/432\` quartic \`Q₄(A)=I−(2176/353)A²+(2048/353)A⁴\` preserves \`E₄₇\` and contracts its complement with **sharp rate \`(225/353)ⁿ\`**, whereas the minimax Richardson \`I−K²/99144\` contracts at **sharp rate \`(15/17)ⁿ\`**. These are two independently parameterized convergent spectral filters sharing the same rank-47 attractor. The quartic is the subject of the [dedicated seven-sector certificate](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/casimir_quartic_filter_20261121.md); the cryptography suite retains the original minimax flow and surrounding security/verification modules.
