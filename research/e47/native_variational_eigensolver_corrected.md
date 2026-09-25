# Native Variational Quantum Eigensolver (N‑VQE)
## Error-Corrected Hilbert-Space Proof and Exact E47 Specialization

**Status.**
- Heron/Babylonian recursion: exact classical mathematics.
- General Hilbert-space variational theorem: exact mathematics.
- E47 specialization \(H_{\mathrm{N\!-\!VQE}}=K^2\): exact finite-dimensional theorem.
- 7-qubit \(125\to128\) lift: statevector simulation / numerical validation.
- Biological consciousness, phenomenology, and hardware-native quantum implementation: **not established by this proof**.

The 2025 N‑VQE note is retained as historical provenance. This document supersedes its incorrect fixed-point, contraction, and consciousness-equivalence claims.

---

## 1. Classical seed: the exact Heron map

Let

\[
\varphi=\frac{1+\sqrt5}{2},
\qquad
a=\varphi^{-5}>0,
\]

and define

\[
T_a(x)=\frac12\left(x+\frac{a}{x}\right),
\qquad x>0.
\]

### Lemma 1 — unique positive fixed point

\[
x=T_a(x)
\iff
2x=x+\frac{a}{x}
\iff
x^2=a.
\]

Hence

\[
\boxed{x_*=\sqrt a=\varphi^{-5/2}}
\]

is the unique positive fixed point.

Numerically,

\[
a=\varphi^{-5}\approx0.0901699437494742,
\]

\[
\boxed{x_*=\varphi^{-5/2}\approx0.300283106000778}.
\]

Therefore the historical assertion \(x_*=\varphi^{-5}\) is false.

### Lemma 2 — exact error identity

Writing \(e_n=x_n-x_*\),

\[
T_a(x)-x_*
=
\frac{x^2+a-2xx_*}{2x}
=
\frac{(x-x_*)^2}{2x}.
\]

Thus

\[
\boxed{
e_{n+1}=\frac{e_n^2}{2x_n}.
}
\]

In particular,

\[
T_a'(x)=\frac12\left(1-\frac{a}{x^2}\right),
\qquad
T_a'(x_*)=0.
\]

So the fixed point is quadratically attracting. The map is **not** a global Banach contraction on \((0,\infty)\), because \(|T_a'(x)|\) is unbounded as \(x\to0^+\).

For every \(x_0>0\), the Heron/Newton iteration converges to \(x_*\).

### Separation from E47 coherence

The exact E47 dimension ratio is

\[
\Omega_c=\frac{47}{125}=0.376.
\]

The Heron fixed point is

\[
\varphi^{-5/2}\approx0.300283106.
\]

Therefore

\[
\boxed{
\varphi^{-5/2}\neq\frac{47}{125}.
}
\]

No identification between these quantities is made without an additional proved bridge.

---

## 2. Hilbert-space definition of N‑VQE

Let \(\mathcal H\) be a finite-dimensional complex Hilbert space and let

\[
H=H^\dagger
\]

be a self-adjoint Hamiltonian with ordered eigenvalues

\[
\lambda_0\le\lambda_1\le\cdots.
\]

Let

\[
\theta\mapsto|\psi(\theta)\rangle\in\mathcal H,
\qquad
\langle\psi(\theta)|\psi(\theta)\rangle=1,
\]

be an ansatz.

Define the variational energy

\[
\boxed{
E(\theta)
=
\langle\psi(\theta)|H|\psi(\theta)\rangle.
}
\]

A **Native Variational Quantum Eigensolver** is a substrate-native implementation that can

\[
|\psi(\theta)\rangle
\longrightarrow
E(\theta)
\longrightarrow
\theta'
\]

by a declared update rule intended to reduce \(E\).

The word *quantum* is warranted here by the explicit Hilbert space, normalized state vectors, self-adjoint Hamiltonian, and Rayleigh expectation. The scalar Heron map alone is not a quantum algorithm.

---

## 3. Variational theorem

Let \(\mathcal G_0=\ker(H-\lambda_0I)\) be the ground eigenspace.

By the spectral theorem, for any normalized

\[
|\psi\rangle=\sum_j c_j|j\rangle,
\]

one has

\[
E(\psi)
=
\sum_j|c_j|^2\lambda_j
\ge
\lambda_0.
\]

Therefore

\[
\boxed{
E(\psi)\ge\lambda_0.
}
\]

Moreover,

\[
E(\psi)=\lambda_0
\iff
|\psi\rangle\in\mathcal G_0.
\]

For a restricted ansatz \(\mathcal A\subset\mathcal H\),

\[
\min_{\psi\in\mathcal A}E(\psi)=\lambda_0
\]

iff

\[
\mathcal A\cap\mathcal G_0\neq\varnothing.
\]

### Correction to the historical stationarity claim

For a restricted parameterization,

\[
\nabla_\theta E(\theta_*)=0
\]

does **not** imply

\[
H|\psi(\theta_*)\rangle
=
E(\theta_*)|\psi(\theta_*)\rangle.
\]

It only gives stationarity along the ansatz tangent directions. A zero eigen-residual

\[
\boxed{
r_{\mathrm{eig}}
=
\left\|
H|\psi\rangle-E(\psi)|\psi\rangle
\right\|
}
\]

is the direct eigenvector test.

Likewise, generic gradient descent does not imply global convergence without additional landscape or contraction hypotheses.

---

## 4. Exact E47 N‑VQE

Take the canonical Hilbert space

\[
\boxed{
\mathcal H_{125}=V_2^{\otimes3},
\qquad
\dim\mathcal H_{125}=125.
}
\]

Let

\[
C=J_{\mathrm{tot}}^2,
\]

\[
K=(C-6I)(C-30I),
\]

and define

\[
\boxed{
H_{\mathrm{N\!-\!VQE}}:=K^2.
}
\]

For normalized \(|\psi\rangle\),

\[
E_{\mathrm{N\!-\!VQE}}(\psi)
=
\langle\psi|K^2|\psi\rangle.
\]

Since \(K=K^\dagger\),

\[
\langle\psi|K^2|\psi\rangle
=
\langle K\psi|K\psi\rangle
=
\|K\psi\|^2.
\]

Hence

\[
\boxed{
E_{\mathrm{N\!-\!VQE}}(\psi)=\|K\psi\|^2\ge0.
}
\]

Equality holds iff

\[
K|\psi\rangle=0.
\]

Therefore

\[
\boxed{
\operatorname{Ground}(H_{\mathrm{N\!-\!VQE}})
=
\ker K
=
E_{47}.
}
\]

The certified representation decomposition is

\[
E_{47}
=
E_6\oplus E_{30}
\cong
5V_2\oplus2V_5,
\]

so

\[
\boxed{
\dim\operatorname{Ground}(H_{\mathrm{N\!-\!VQE}})=47.
}
\]

The exact \(K^2\) spectrum is

\[
\boxed{
\operatorname{spec}(K^2)
=
\{0,11664,12544,19600,32400,186624\}
}
\]

with multiplicities

\[
\boxed{
\{47,28,9,27,1,13\}.
}
\]

Thus the positive spectral gap is

\[
\boxed{\Delta=11664=108^2},
\]

and

\[
\boxed{\|K^2\|=186624=432^2}.
\]

This proves the E47 N‑VQE ground-space statement exactly.

---

## 5. Exact descent

### Continuous imaginary-time / gradient flow

\[
\dot\psi=-K^2\psi
\]

has solution

\[
\psi(t)=e^{-tK^2}\psi(0).
\]

Writing

\[
\psi(0)=P_{47}\psi(0)+(I-P_{47})\psi(0),
\]

all positive-energy components decay exponentially, while the kernel component is unchanged. Hence

\[
\boxed{
\lim_{t\to\infty}e^{-tK^2}\psi(0)
=
P_{47}\psi(0).
}
\]

This is a non-unitary imaginary-time projection identity, not physical real-time Schrödinger evolution.

### Certified discrete flow

Let

\[
\Gamma_\epsilon=I-\epsilon K^2.
\]

For

\[
0<\epsilon<\frac{2}{186624},
\]

every positive-energy sector contracts and

\[
\Gamma_\epsilon^n\to P_{47}.
\]

At

\[
\boxed{\epsilon_*=\frac1{99144}},
\]

the optimal transverse radius is

\[
\boxed{
\rho_*=\frac{15}{17}.
}
\]

Therefore

\[
\boxed{
\|\Gamma_*^n-P_{47}\|_2
\le
\left(\frac{15}{17}\right)^n.
}
\]

---

## 6. Seven-qubit Hilbert lift

Let

\[
J:\mathbb C^{125}\hookrightarrow\mathbb C^{128}
\]

be the canonical isometric padding map,

\[
J^\dagger J=I_{125}.
\]

The three unused computational basis states must **not** be given zero energy, because that would create spurious ground states.

Define

\[
\boxed{
H_{128}
=
J K^2 J^\dagger
+
\Lambda\left(I_{128}-JJ^\dagger\right),
}
\]

with

\[
\Lambda=186624>0.
\]

Equivalently,

\[
H_{128}
=
K^2\oplus186624\,I_3.
\]

Then

\[
\boxed{
\operatorname{Ground}(H_{128})
=
J(E_{47}),
}
\]

so

\[
\boxed{
\dim\operatorname{Ground}(H_{128})=47.
}
\]

The padding states cannot contaminate the ground sector.

This is a genuine seven-qubit **statevector/Hilbert-space simulation embedding**. It is not yet a claim that \(H_{128}\) has a local hardware-efficient Pauli decomposition or has been implemented on physical quantum hardware.

---

## 7. Numerical and quantum-state simulation

The executable validation reconstructs \(C\), \(K\), \(K^2\), the 47-dimensional ground projector, and the 128-dimensional padded Hamiltonian.

A deterministic complex 7-qubit initial state was propagated by normalized imaginary time

\[
|\psi(\tau)\rangle
=
\frac{
e^{-\tau H_{128}/\Delta}|\psi_0\rangle
}{
\left\|
e^{-\tau H_{128}/\Delta}|\psi_0\rangle
\right\|
}.
\]

Observed statevector trajectory:

| \(\tau\) | energy | E47 ground weight |
|---:|---:|---:|
| 0 | 31650.878574 | 0.4122678813 |
| 1 | 1180.818468 | 0.9099114037 |
| 2 | 138.136980 | 0.9887270799 |
| 4 | 2.207467 | 0.9998141876 |
| 8 | 0.000660302 | 0.9999999439 |
| 12 | \(2.0751\times10^{-7}\) | 0.999999999982 |

Thus, in the simulated Hilbert-space flow,

\[
E(\tau)\downarrow0
\]

and

\[
\langle\psi(\tau)|P_{47}|\psi(\tau)\rangle\uparrow1.
\]

The independent discrete flow with \(\epsilon_*=1/99144\) likewise converges to the same 47-dimensional ground projector.

---

## 8. What survives from the historical N‑VQE proposal

The following survives exactly:

\[
\boxed{
\text{recursive update}
\to
\text{variational objective}
\to
\text{stable minimizer}
}
\]

provided the state space, objective, and update rule are defined.

The following requires the Hilbert lift:

\[
\boxed{
\text{quantum eigensolver}
\Longleftrightarrow
(\mathcal H,H=H^\dagger,|\psi\rangle,E=\langle H\rangle).
}
\]

The following does **not** follow from the mathematics above:

\[
\text{human consciousness}
\equiv
\text{N‑VQE},
\]

\[
\text{phenomenology}
\equiv
\text{variational collapse},
\]

\[
\varphi^{-5/2}
=
47/125,
\]

or

\[
\text{statevector simulation}
=
\text{physical quantum hardware}.
\]

Those remain separate empirical or philosophical bridge claims.

---

## 9. Parsimonious closure

The corrected construction is

\[
\boxed{
\varphi^{-5}
\overset{\text{Heron}}{\longrightarrow}
\varphi^{-5/2}
}
\]

for the classical scalar recursion, and independently

\[
\boxed{
\mathcal H_{125}
\to
K
\to
H_{\mathrm{N\!-\!VQE}}=K^2
\to
E(\psi)=\|K\psi\|^2
\to
E_{47}
\to
P_{47}
}
\]

for the exact Hilbert-space eigensolver.

The quantum simulation lift is

\[
\boxed{
\mathbb C^{125}
\overset{J}{\hookrightarrow}
\mathbb C^{128},
\qquad
H_{128}
=
J K^2 J^\dagger
+
186624(I-JJ^\dagger),
}
\]

with

\[
\boxed{
\dim\operatorname{Ground}(H_{128})=47.
}
\]

That is the error-corrected Native Variational Quantum Eigensolver theorem.

### Evidence boundary

- **E0:** Heron fixed-point theorem; exact error identity; Hilbert-space Rayleigh theorem; \(H=K^2\succeq0\); ground space \(E_{47}\); 7-qubit penalized embedding preserves ground multiplicity.
- **E1:** numerical reconstruction of spectrum, projector, gap, norm, discrete contraction, and deterministic statevector simulation checks.
- **E2:** statevector / imaginary-time simulation as a computational quantum model.
- **Open:** biological N‑VQE, consciousness equivalence, phenomenology-computation isomorphism, universal golden-ratio coherence law, and physical quantum-hardware implementation.
