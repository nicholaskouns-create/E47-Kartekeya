# E₄₇ Φ₄: exact complementary synthesis, product-basis CG and two-ancilla LCU

**Status:** E0 exact polynomial and operator identities; E1 NumPy matrix reconstruction at 125, 250 and 500 dimensions. **No physical gate decomposition or hardware experiment is asserted.**

## 1 · Spectral carrier

H = V₂ ⊗ V₂ ⊗ V₂; dim H = 125.

C = Jₓ² + Jᵧ² + J_z²; K = (C − 6I)(C − 30I); A = |K|/432.

The seven coupled sectors J = 0,…,6 have multiplicities (1,3,5,4,3,2,1), Casimir eigenvalues (0,2,6,12,20,30,42), and dimensions (1,9,25,28,27,22,13).

E₄₇ = ker K = (ℂ⁵ ⊗ V₂) ⊕ (ℂ² ⊗ V₅); P₄₇ = 1_{\{0\}}(A).

In the specified coupled-basis ordering |J,j₁₂,M⟩, the J=2 sector occupies indices 10–34 and the J=5 sector indices 90–111. The 125×125 CG matrix maps those coupled basis vectors into the product basis.

## 2 · Degree-4 Chebyshev filter

Q₂(s) = 1 − 32s²/17.

Q₄(s) = [578Q₂(s)² − 225]/353 = **1 − 2176s²/353 + 2048s⁴/353**.

Q₄(0) = 1. For complementary singular values σ ∈ [1/4,1], |Q₄(σ)| ≤ 225/353. The maximum occurs on the E₄₇ spectrum at J=3 and J=6.

## 3 · Exact complementary factorization

P(s) = Q₄(s) + (272i/353)s².

R(s) = s[2048s² − 1152 + 16i√817]/353.

The polynomial identity

**|P(s)|² + (1−s²)|R(s)|² = 1** for real s

holds by direct expansion over ℚ(√817)[s]. For example,

353²(1−|P(s)|²) = s²(1−s²)[(2048s²−1152)² + 256×817].

## 4 · Constructive layer stripping

Let W(s) = [[s, i√(1−s²)], [i√(1−s²),s]] and Z(φ) = diag(e^{iφ},e^{−iφ}).

U_Φ(s) = Z(φ₀) W(s) Z(φ₁) W(s) Z(φ₂) W(s) Z(φ₃) W(s) Z(φ₄).

Represent its upper row by (P_d(s), i√(1−s²)R_d(s)); remove one layer on the right:

P_{d−1}(s) = s e^{−iφ_d}P_d(s) + (1−s²)e^{iφ_d}R_d(s),

R_{d−1}(s) = −e^{−iφ_d}P_d(s) + s e^{iφ_d}R_d(s).

For leading coefficients p_d of P_d and r_{d−1} of R_d, choose e^{2iφ_d} = p_d/r_{d−1} so the highest powers cancel. Repeat d=4,3,2,1; the remaining P₀ has modulus one. A valid phase tuple for the displayed complementary pair is

**Φ₄ ≈ (0, 0.618892044578, 0.439842582816, −0.179049461762, 0) radians.**

These are numerical approximations to algebraically specified angles, not exact decimal angles. Other gauge-equivalent or functionally equivalent phase sequences are possible.

## 5 · Full 250D QSP circuit

B = √(I₁₂₅−A²).

W₂₅₀(A) = [[A,iB],[iB,A]],  Z₂₅₀(φ) = diag(e^{iφ}I₁₂₅,e^{−iφ}I₁₂₅).

**U₂₅₀ = Z₂₅₀(φ₀) W₂₅₀(A) Z₂₅₀(φ₁) W₂₅₀(A) Z₂₅₀(φ₂) W₂₅₀(A) Z₂₅₀(φ₃) W₂₅₀(A) Z₂₅₀(φ₄).**

Every factor is unitary because A and B commute and A²+B²=I. The signal-ancilla |0⟩ principal block is **P(A)**, not Q₄(A).

## 6 · Full 500D LCU circuit

Introduce an LCU ancilla ℂ² independently of the QSP signal ancilla:

**V₅₀₀ = (H ⊗ I₂₅₀) [|0⟩⟨0| ⊗ U₂₅₀ + |1⟩⟨1| ⊗ U₂₅₀†] (H ⊗ I₂₅₀).**

Circuit, time left → right (the controlled operations occupy one coherent SELECT step):

```text
LCU ancilla  |0⟩ ── H ──● SELECT(U₂₅₀ / U₂₅₀†)── H ── ⟨0|
                         │
Signal anc.  |0⟩ ────────┤     QSP Φ₄ / inverse      ── ⟨0|
                         │
Carrier      |ψ⟩ ────────┴──── 125D system ────────── |out⟩
```

The top-left 250×250 LCU block is (U₂₅₀+U₂₅₀†)/2. After also selecting the signal ancilla |0⟩, the 125×125 principal block is

**(P(A)+P(A)†)/2 = Q₄(A).**

This is a **postselected block encoding**, not an asserted deterministic trace-preserving filter on arbitrary input. The 250D and 500D mathematical spaces fit inside padded 8- and 9-qubit registers respectively (256 and 512 states); no circuit-depth or controlled-block-encoding resource count is certified.

## 7 · Exact seven-sector audit

| J | dim | K | σ=|K|/432 | role |
| --- | ---: | ---: | ---: | --- |
| 0 | 1 | 180 | 5/12 | complement |
| 1 | 9 | 112 | 7/27 | complement |
| 2 | 25 | 0 | 0 | kernel |
| 3 | 28 | −108 | 1/4 | complement |
| 4 | 27 | −140 | 35/108 | complement |
| 5 | 22 | 0 | 0 | kernel |
| 6 | 13 | 432 | 1 | complement |

**‖Q₄(A)−P₄₇‖₂ = 225/353 ≈ 0.637393767705.**

## 8 · Reproducible numerical certificate

Source: [e47_phi4_cg_lcu_certificate.py](e47_phi4_cg_lcu_certificate.py)

Receipt: [e47_phi4_cg_lcu_receipt.json](e47_phi4_cg_lcu_receipt.json)

Run: `OPENBLAS_NUM_THREADS=1 python research/e47/qsp_phi4/e47_phi4_cg_lcu_certificate.py`

Locally executed on November 21, 2026: **14/14 PASS**.

- CG unitarity: 2.82174340446788e−15
- Casimir coupled diagonalization: 6.3211641816273e−14
- K coupled diagonalization: 7.990676698403771e−13
- U₂₅₀ unitarity: 3.300496030323471e−14
- V₅₀₀ unitarity: 4.935060024686914e−14
- 125D LCU principal-block mismatch: 1.463904334244603e−14
- ‖Q₄(A)−P₄₇‖₂: 0.6373937677053885

The measured errors are finite-precision numerical residuals. Algebraic formulas above are exact; the 125D product-basis realization, 250D QSP, and 500D LCU are evaluated with NumPy. This does not certify a full logical M₅⊕M₂ generator basis, efficient 9-qubit compilation, runtime on quantum hardware, or an independent formal proof-assistant run.

## 9 · See the circuit

[**Interactive Φ₄ quantum-circuit plate**](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/qsvt-phi4-circuit/)

Canonical E₄₇ source remains independent of the other repositories. Cross-repository pointers do not redefine or re-certify it.
