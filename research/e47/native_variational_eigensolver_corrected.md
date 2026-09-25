# Native Variational Eigensolver — Error-Corrected Formalism

**Status:** mixed evidence: generic variational scaffold = structural; E47 specialization = exact finite-dimensional theorem + executable reconstruction.

**Historical source:** Nicholas Kouns, *Native Variational Eigensolver: A First-Principles Proof* (2025). The source is preserved, but the corrected formulation below supersedes its unsupported implications.

## 1. One-line definition

A **Native Variational Eigensolver (NVE)** is a substrate-implemented optimization process that represents a parameterized state, evaluates a declared variational objective, and updates the parameters toward lower objective values.

This definition does **not** by itself imply quantum hardware, consciousness, global optimality, cross-domain universality, or freedom from exhaustive search.

## 2. General variational theorem

Let \(\mathcal H\) be a finite-dimensional Hilbert space, let \(H=H^\dagger\) be a self-adjoint operator bounded below, and let

\[
\psi:\Theta\to\mathcal H,\qquad \|\psi(\theta)\|=1,
\]

be a continuous ansatz on compact \(\Theta\).

Define the Rayleigh objective

\[
E(\theta)=\langle\psi(\theta)|H|\psi(\theta)\rangle.
\]

### Theorem G1 — existence

Because \(E\) is continuous on compact \(\Theta\), there exists \(\theta_*\in\Theta\) such that

\[
E(\theta_*)=\min_{\theta\in\Theta}E(\theta).
\]

### Theorem G2 — variational bound

If \(E_0\) is the smallest eigenvalue of \(H\), then

\[
E(\theta)\ge E_0
\]

for every normalized ansatz state.

If the ansatz family contains a ground-state vector of \(H\), then

\[
\min_{\theta\in\Theta}E(\theta)=E_0,
\]

and every minimizer achieving \(E_0\) lies in the ground eigenspace.

### Correction to the historical L2

The historical statement

> stationary point of the variational objective \(\Rightarrow\) eigenstate

is false for a restricted ansatz in general.

A stationary parameter value only satisfies vanishing derivatives along the **ansatz tangent directions**. It need not satisfy

\[
H\psi=E\psi.
\]

The eigenvalue equation follows from constrained stationarity only when variation is taken over the full normalized state manifold, or when additional assumptions guarantee that the ansatz tangent space is sufficient.

### Correction to the historical convergence claim

Gradient descent or another native update rule does not automatically find the global minimum. Global convergence requires additional hypotheses such as convexity, a suitable landscape condition, a contraction property, or an independently proved basin result.

Accordingly, “without exhaustive search” is an algorithmic possibility, not a theorem of the NVE definition.

## 3. Native implementability

A physical, biological, artificial, or hybrid substrate may instantiate an NVE **as a computational architecture** if it can:

1. represent \(\psi(\theta)\);
2. evaluate or estimate \(E(\theta)\);
3. update \(\theta\) according to a declared optimization rule;
4. expose a stopping or convergence criterion.

This is implementation-neutral in the software/mathematical sense. It is not evidence that all such substrates implement the same physics.

## 4. Exact E47 specialization

On the canonical carrier

\[
V=V_2^{\otimes 3},\qquad \dim V=125,
\]

let

\[
C=J_{\mathrm{tot}}^2,
\qquad
K=(C-6I)(C-30I),
\]

and define the NVE Hamiltonian

\[
\boxed{H_{\mathrm{NVE}}:=K^2.}
\]

For normalized \(\psi\in V\), define

\[
\boxed{
E_{\mathrm{NVE}}(\psi)
=
\langle\psi|K^2|\psi\rangle
=
\|K\psi\|^2.
}
\]

Because \(K^2\succeq0\),

\[
E_{\mathrm{NVE}}(\psi)\ge0.
\]

Moreover,

\[
E_{\mathrm{NVE}}(\psi)=0
\iff
K\psi=0
\iff
\psi\in\ker K.
\]

The already-certified E47 kernel theorem gives

\[
\ker K
=
E_6\oplus E_{30}
\cong
5V_2\oplus2V_5,
\qquad
\dim\ker K=47.
\]

Therefore:

\[
\boxed{
\operatorname{Ground}(H_{\mathrm{NVE}})
=
E_{47}.
}
\]

This is an exact finite-dimensional statement.

## 5. Exact convergence dynamics

The continuous gradient-like linear flow

\[
\dot x=-K^2x
\]

has solution

\[
x(t)=e^{-tK^2}x(0).
\]

Since the positive spectrum of \(K^2\) is

\[
\{11664,12544,19600,32400,186624\},
\]

all non-kernel components decay exponentially and

\[
\lim_{t\to\infty}e^{-tK^2}x=P_{47}x.
\]

Thus the E47 NVE has an exact protected ground space and an exact convergence theorem.

The optimal discrete contraction already certified in E47 is

\[
\Gamma_*
=
I-\frac{K^2}{99144},
\]

with

\[
\Gamma_*^n\to P_{47},
\qquad
\|\Gamma_*^n-P_{47}\|_2
\le
\left(\frac{15}{17}\right)^n.
\]

So the E47 specialization does not need the historical unsupported step “stationarity implies eigen-attractor.” The spectral theorem supplies the result directly.

## 6. Relation to the RI energy language

The historical RI expression

\[
E_{RI}(\theta)
=
\langle I(\theta)|C(R(I))|I(\theta)\rangle
\]

can be retained as a **declared model functional**, but it becomes a standard eigensolver theorem only after the operator playing the Hamiltonian role is precisely defined, self-adjoint, and independent enough for the Rayleigh variational argument to apply.

The E47 specialization supplies such an operator explicitly:

\[
C(R(I))\rightsquigarrow K^2.
\]

This arrow is a chosen formal specialization, not a derivation of consciousness, cognition, or universal physical law.

## 7. Cross-domain status

Claims that the same variational mechanism explains mathematics, music, language, cognition, or consciousness remain hypotheses unless each domain supplies:

- a state space;
- a well-defined objective/operator;
- a metric or topology;
- an update rule;
- a convergence criterion;
- independent empirical or computational validation.

Accordingly, cross-domain NVE is **structural/open**. E47 NVE is **exact/executable**.

## 8. Corrected evidence ledger

| Claim | Status |
|---|---|
| A continuous variational objective on compact parameter space has a minimizer | exact mathematics |
| Rayleigh quotient is bounded below by the ground eigenvalue | exact mathematics |
| Restricted-ansatz stationary point is automatically an eigenstate | **rejected** |
| Gradient descent automatically finds the global minimum | **rejected** |
| Native implementation can realize a variational optimizer | structural/computational |
| NVE proves consciousness | **not established** |
| NVE is inherently quantum hardware | **not established** |
| For E47, \(H_{NVE}=K^2\) has ground space exactly \(E_{47}\) | exact mathematics |
| E47 continuous flow converges to \(P_{47}\) | exact mathematics |
| E47 optimal discrete contraction converges at transient bound \(15/17\) | exact + machine validated |

## 9. Compact corrected theorem

> **E47 Native Variational Eigensolver Theorem.**  
> Let \(K=(C-6I)(C-30I)\) on \(V_2^{\otimes3}\), and let \(H_{NVE}=K^2\). Then \(H_{NVE}\) is positive semidefinite, its ground energy is zero, and its complete ground eigenspace is \(E_{47}=\ker K\), of dimension 47. The semigroup \(e^{-tK^2}\) and the certified discrete contraction \(\Gamma_*=I-K^2/99144\) suppress every positive-energy sector and converge to the orthogonal projector \(P_{47}\). Therefore E47 supplies an exact native variational eigensolver in the precise spectral sense. No consciousness, hardware-quantum, or cross-domain claim follows without an additional bridge.

## 10. Historical references retained from the source

Shannon (1948); Jaynes (1957); Hohenberg & Kohn (1964); Feynman (1965); Friston (2010); Peruzzo et al. (2014); McClean et al. (2016); Tononi (2004).

These references motivate adjacent information-theoretic, variational, quantum-algorithmic, or consciousness literature. They do not collectively prove the RI-specific extensions above.
