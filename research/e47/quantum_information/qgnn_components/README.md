# E47: corrected encoding, measurement, and trace-preserving dynamics

Implemented and validated 18 October 2026. Author of E47/KKP-R framework: Nicholas Shane Kouns. This package implements the corrections requested in this conversation. Numerical checks use double precision; algebraic channel identities below are exact.

## Run

```bash
python -m pip install -r requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python e47_corrected.py
```

The script regenerates operators, every packed label, an eight-qubit circuit in QPY and synthesized OpenQASM 3, and the validation ledger. It exits on the first failed check. See validation.json and run.log for actual execution results and package versions. Qiskit Statevector and DensityMatrix circuit simulations are classical quantum simulations, not hardware executions. This package implements encoding, projection, relaxation and a two-node update demonstration; training is outside this package.

## 1. Encoding and actual coupled-basis transformation

The physical product basis is |m1,m2,m3>, mi=2,1,0,-1,-2, in NumPy Kronecker order. Product index =25(2-m1)+5(2-m2)+(2-m3). Encode those indices 0..124 on seven qubits; indices 125..127 are unused.

The coupled labels are |j,j12,m>, with j12=0..4 and |j12-2| <= j <= j12+2, -j<=m<=j. Sort lexicographically by (j,j12,m), and assign consecutive binary integers. There is no fixed sector-header register. Spin-sector dimensions in ascending j order are 1,9,25,28,27,22,13. All 47 target states are exactly indices 10..34 and 90..111. encoding.json is the exhaustive 128-entry map.

Build C=J_total^2 and C12=(J1+J2)^2 directly from spin-2 matrices. Their joint eigenvectors with Jz define the coupled basis V. Each eigenvector's largest product-basis component is made real positive; this is a valid coupled-basis phase convention, and need not equal the Condon–Shortley convention. The implementation numerically diagonalizes C+sqrt(2)C12+sqrt(3)Jz and independently verifies each separate eigenvalue equation and distinct label. V maps coupled coordinates to product coordinates. The actual seven-qubit encoding transform is W=V† ⊕ I3. W is implemented as a Qiskit UnitaryGate and then synthesized into u/cx gates. The exported QASM contains those gates, not a placeholder transform.

For each spin sector j the Casimir is j(j+1). K=(C-6I)(C-30I) selects j=2,5. P_packed is diagonal on the selected indices. P_product=W† P_packed W. The three unused computational states are excluded explicitly: extending K with zeros alone would incorrectly admit them.

## 2. Projector measurement

One syndrome ancilla starts in |0>. The membership circuit implements

U_P = P_packed ⊗ X_anc + (I-P_packed) ⊗ I_anc,

with the tensor factors ordered physically according to Qiskit's little-endian convention: q0..q6 are data and q7 is the most significant ancilla. The displayed expression specifies the data/ancilla action, not the array Kronecker order.

An equality-controlled ancilla flip is applied once for each selected integer. Negative controls are implemented by temporary X gates. After W and U_P, measuring the ancilla gives outcome 1 with probability Tr(P_product rho). The normalized successful state is P rho P / Tr(P rho); if this probability is zero, no successful branch exists. Conditional normalization is not a deterministic linear channel.

To return to the original product basis apply W† to the data after tagging. Ignoring the syndrome gives the trace-preserving measurement channel rho -> P rho P + Q rho Q. That measurement removes coherence between the two sectors but leaves their populations unchanged.

basis_and_measurement.qasm operates on an input already supplied in product encoding. With no preceding preparation, the default input is computational |0>, corresponding to physical |2,2,2>, entirely spin 6, so it correctly returns syndrome 0. State preparation is intentionally left to the caller.

## 3. Trace-preserving relaxation

Define A on the 128-dimensional packed space by

A|k> = [1-((j(j+1)-6)(j(j+1)-30))²/99144]|k> for k<125,
A|k> = 0 for k=125,126,127.

A=P+QAQ, A†A<=I, and ||AQ||2=15/17. Choose alpha as the first selected packed basis state, with label (j=2,j12=0,m=-2), and tau=|alpha><alpha|. This choice is explicit and replaceable by any density matrix supported in E47. The pure reset target does not preserve full SU(2) covariance; tau=P/47 is the covariant reset option, implementable with the corresponding mixed-state Kraus family.

The implemented channel is

E(rho)=A rho A† + Tr[(I-A†A)rho] tau.

Its Kraus operators are A and B_k=sqrt(1-gamma_k²)|alpha><k| for every complement or unused basis state. Thus

A†A + sum_k B_k†B_k = I.

This proves complete positivity and trace preservation. Every density matrix supported in E47 is fixed. On a normalized input,

Tr[Q E^n(rho)] <= (15/17)^(2n) Tr(Q rho),
lim E^n(rho)=P rho P + Tr(Q rho) tau.

This retains all originally selected information and transfers rejected population into the selected reset state. It differs from conditional projection: reset information is added, and the rejected input is not recovered. E47/complement coherences decay at most (15/17)^n. In the physical product encoding conjugate the input and output by W and W†.

The explicit formula is checked against an eight-qubit flagged attenuation circuit with unitary blocks [[A,-D],[D,A]], D=sqrt(I-A†A). Measuring the flag, retaining branch 0 and resetting branch 1 to alpha implements the channel deterministically when outcomes are averaged. The reset branch is simulated using actual Qiskit reset and X instructions. attenuation_and_reset.qpy stores both component circuits. No device execution or hardware-native compilation of this reset instrument is claimed. The eight-qubit QASM implements the basis transformation and projector instrument.

## 4. Correct graph update

For a global graph density matrix R, let rho_v=Tr_except_v R. For each neighboring u form

sigma_vu = Tr_u[U_vu R_vu U_vu†],

using the actual joint reduced state R_vu when correlations exist. Using rho_v ⊗ rho_u is an explicitly factorized approximation and defines a nonlinear rule if both factors are updated from the input.

Choose weights a_v,b_vu >=0 with a_v+sum_u b_vu=1. Then use

sigma_v=a_v rho_v+sum_u b_vu sigma_vu,
rho'_v=E_v(U_v sigma_v U_v†).

All terms have trace 1 and are positive; the normalized nonnegative mixture, unitary, and relaxation each preserve trace. This local marginal update does not on its own specify a consistent correlated global state. A global implementation can instead schedule edge unitaries (for example in disjoint matchings), then apply local E_v channels. The composition is a global CPTP graph layer and retains correlations explicitly.

The executable demonstration uses a two-node product input, a diagonal entangling unitary and normalized self/neighbor weights 0.6 and 0.4, followed by E. It checks trace and positivity. General graph training, task performance and gradient behavior are not measured here.

## Files

- e47_corrected.py: executable construction, quantum simulations, assertions and export.
- encoding.json: all coupled-state labels and unused indices.
- e47_operators.npz: spin Casimirs, V, W, projectors and contraction eigenvalues.
- basis_and_measurement.qpy: Qiskit circuit retaining the matrix unitary.
- basis_and_measurement.qasm: actual synthesized OpenQASM 3 circuit and ancilla measurement.
- attenuation_and_reset.qpy: flagged attenuation and conditional reset component circuits.
- validation.json: check names, numeric residuals, tolerances, software versions and circuit counts.
- run.log: captured execution output.

## Executed results

All 36 checks passed. Exhaustive membership error: 1.66e-14; synthesized circuit state error: 2.64e-13; flagged relaxation/reset versus channel formula: 8.55e-17; 220-step density limit error: 5.63e-13. Kraus completeness and arbitrary E47-state preservation residuals were zero in this run.

The generic synthesized circuit uses 20,824 u gates and 15,309 cx gates, depth 21,828, plus one measurement. This is an executable reference compilation; no gate-count or hardware noise optimization is claimed. The circuit was tested on an arbitrary complex superposition; its membership component was tested exhaustively. Numerical state differences use Euclidean norm; matrix differences use Frobenius norm unless an explicit scalar spectral bound is checked.

Versions: NumPy 2.3.5, SciPy 1.17.0, Qiskit 2.6.0.

## Tensor and RTL extension

See Tensor_and_RTL_Validation.md for the complete tensor-to-hardware description. All 21 independent PyTorch checks passed, and all 768 complex-coordinate comparisons across six simulated RTL frames matched the integer reference exactly. RTL outputs are in packed coupled coordinates.

Run `python torch_validation.py` for tensor validation and `python build_rtl_validation.py` with Icarus Verilog installed for RTL simulation. The existing 36-check quantum ledger remains included.
