# E₄₇ Casimir-derived quartic filter — seven-sector certificate (2026-11-21)

**Instrument:** [Live seven-sector interactive observatory](https://nicholaskouns-create.github.io/e47-casimir-filter/) · [QSVT Φ₄ circuit](https://nicholaskouns-create.github.io/qsvt-phi4/) · [THE MATRIX](https://nicholaskouns-create.github.io/matrix-quantum-simulator/)

## Representation and normalization
Let (H=V_2^{\otimes3}=\mathbb C^{125}), where each factor is a spin-2 representation. Define total generators (J_a=J_a^{(1)}+J_a^{(2)}+J_a^{(3)}), (C=J_x^2+J_y^2+J_z^2), (K=(C-6I)(C-30I)), and (A=K/432). Then (mathrm{spec}(C)=\{0,2,6,12,20,30,42\}) with multiplicities (1,9,25,28,27,22,13), and (|A|_2=1).

## Real sector data

| Spin J | Multiplicity | C | K | s=K/432 | Q₄(s) |
|---:|---:|---:|---:|---:|---:|
|0|1|0|180|0.416666667|0.104675970|
|1|9|2|112|0.259259259|0.611875464|
|2|25|6|0|0|1|
|3|28|12|-108|-0.25|0.637393768|
|4|27|20|-140|-0.324074074|0.416592888|
|5|22|30|0|0|1|
|6|13|42|432|1|0.637393768|

The quartic is (Q_4(A)=I-\frac{2176}{353}A^2+\frac{2048}{353}A^4), and its complex completion (P(A)=Q_4(A)+i\frac{272}{353}A^2) is contractive on this specific normalized Casimir spectrum. Its Hermitian average equals (Q_4(A)).

**Theorem (exact operator norm contraction).** With (P_{47}) the orthogonal spectral projector onto (E_{47}=\ker K=5V_2\oplus2V_5) (dimension 47), for all nonnegative integers (n),
[
\|Q_4(A)^n-P_{47}\|_2=(225/353)^n.
]
The (n=0) case is (\|I-P_{47}\|_2=1). Therefore (Q_4(A)) is NOT itself the exact projector; it is one strict contraction stage on its 78D complement. The unique largest complement response occurs in J=3 and J=6.

**Independent exact finite polynomial:**
[
P_{47}=\prod_{\lambda\in\{11664,12544,19600,32400,186624\}}\left(I-K^2/\lambda\right).
]

**Nine-qubit reference block encoding:** pad 125 data dimensions to 128 (7 qubits); signal (1) and LCU (1) yield a 512-dimensional unitary. A standard defect-operator unitary dilation of (P(A)), followed by SELECT of (U) and (U^\dagger) and LCU Hadamards, yields (langle00|V|00\rangle=Q_4(A)) on the physical carrier. This is a **dense numerical reference architecture**, not a fault-tolerant elementary gate compilation. Repeated postselected stages implement the *unnormalized* operator (Q_4(A)^n); cumulative probabilities must be accounted for before making deterministic-channel claims.

**Evidence boundaries:** the 125×125 full Casimir numerical constructor was executed in NumPy with (|Q-P_{47}|_2=0.6373937677054193), (|QP_{47}-P_{47}|_2=1.7981858770009357\times10^{-14}), and a unitary-dilation contractivity check (lambda_{\min}(I-P^\dagger P)\approx-1.33\times10^{-15}) (numerical zero). Qiskit and QuTiP full 512×512 gates were not rerun for this record.

**2×2 Eigen Explorer bridge:** independent educational visualizer (A_2v=\lambda v) with four matrix-entry sliders, draggable input and output, real eigendirections and grid vector field. This 2×2 input is NOT the 125×125 Casimir operator; the cross-link compares eigenanalysis without replacing either model.
