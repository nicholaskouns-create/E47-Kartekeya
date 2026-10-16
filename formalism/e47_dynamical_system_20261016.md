# E47 Dynamical System

## Fixed-point theorem · Lyapunov stability · perturbations · continuous-time semigroup

Let

\[
H=V_2^{\otimes 3}\cong \mathbb C^{125},\qquad C=J_x^2+J_y^2+J_z^2,
\]

\[
K=(C-6I)(C-30I),\qquad P=P_{47}=\operatorname{proj}_{\ker K},
\]

\[
R=I-\frac{K^2}{99144}.
\]

The E47 kernel is

\[
\mathcal K_{47}=\ker K=E_6\oplus E_{30},\qquad \dim \mathcal K_{47}=25+22=47,
\]

with

\[
\Omega_c=\frac{47}{125}=0.376.
\]

## Discrete fixed-point theorem

\[
Rx=x\iff K^2x=0\iff Kx=0,
\]

hence

\[
\operatorname{Fix}(R)=\mathcal K_{47}.
\]

Moreover

\[
\|R^n-P_{47}\|_2=\left(\frac{15}{17}\right)^n,
\]

so for every \(x\in H\),

\[
\lim_{n\to\infty}R^n x=P_{47}x.
\]

Thus \(\mathcal K_{47}\) is a globally exponentially attractive 47-dimensional fixed-point subspace.

## Lyapunov theorem

Define

\[
V(x)=\|(I-P_{47})x\|^2.
\]

Then

\[
V(Rx)\le \left(\frac{15}{17}\right)^2V(x)
\]

and

\[
V(R^n x)\le \left(\frac{15}{17}\right)^{2n}V(x).
\]

Hence \(V\) is a strict Lyapunov function transverse to the kernel.

## Additive perturbations

For

\[
x_{n+1}=Rx_n+u_n,
\]

with transverse error \(e_n=(I-P_{47})x_n\),

\[
\|e_n\|\le \left(\frac{15}{17}\right)^n\|e_0\|+
\sum_{j=0}^{n-1}\left(\frac{15}{17}\right)^{n-1-j}\|(I-P_{47})u_j\|.
\]

If \(\|u_j\|\le\delta\), then

\[
\limsup_{n\to\infty}\|e_n\|\le \frac{17}{2}\delta.
\]

## Continuous-time semigroup

Set

\[
A=\frac{K^2}{99144},\qquad T(t)=e^{-tA}.
\]

Then

\[
T(t+s)=T(t)T(s),\qquad T(0)=I,
\]

and the positive spectral gap is

\[
\lambda_{\min}(A)=\frac{11664}{99144}=\frac{2}{17}.
\]

Therefore

\[
\|T(t)-P_{47}\|_2=e^{-2t/17},
\]

and

\[
\lim_{t\to\infty}T(t)=P_{47}.
\]

## Quantum relaxation channel

Choose a normalized logical state \(|0_L\rangle\in E_{47}\) and complementary eigenstates \(|i\rangle\) with decay rates \(a_i>0\). Define

\[
M_0(t)=P_{47}+\sum_i e^{-a_i t}|i\rangle\langle i|,
\]

\[
M_i(t)=\sqrt{1-e^{-2a_i t}}\,|0_L\rangle\langle i|.
\]

Then

\[
M_0^\dagger M_0+\sum_i M_i^\dagger M_i=I,
\]

so the map is CPTP and leaves E47 invariant as a decoherence-free subspace while relaxing complementary modes into the kernel.

## Principal result

The E47 recursion is an exact globally convergent linear dynamical system with a 47-dimensional fixed-point attractor, exact discrete and continuous convergence rates, a strict transverse Lyapunov function, and an exact bounded-disturbance stability estimate.

Evidence boundary: finite-dimensional algebraic and numerical statements are E0/E1. The Kraus construction is a compatible quantum channel construction, not a hardware-executed quantum experiment.
