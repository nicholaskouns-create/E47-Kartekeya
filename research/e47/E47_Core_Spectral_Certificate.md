# E47 Exact Spectral Core

## Carrier

\[
\Sigma=V_2\otimes V_2\otimes V_2,
\qquad
\dim\Sigma=5^3=125.
\]

## Casimir Spectrum

\[
\operatorname{spec}(C)
=
\{0,2,6,12,20,30,42\}.
\]

Multiplicities:

\[
1,\ 9,\ 25,\ 28,\ 27,\ 22,\ 13.
\]

Therefore

\[
1+9+25+28+27+22+13=125.
\]

## Spectral Statistics

\[
\mu=18,
\qquad
\sigma=12,
\]

so

\[
\mu-\sigma=6,
\qquad
\mu+\sigma=30.
\]

## Kernel Selector

\[
K=(C-6I)(C-30I).
\]

Hence

\[
\ker K
=
E_6\oplus E_{30}.
\]

Because

\[
\dim E_6=25,
\qquad
\dim E_{30}=22,
\]

we obtain

\[
\boxed{
\dim\ker K=47.
}
\]

## Orthogonal Projector

Let

\[
P_{47}=P_6+P_{30}.
\]

Then

\[
P_{47}^2=P_{47},
\qquad
P_{47}^\*=P_{47},
\qquad
KP_{47}=0,
\]

and

\[
\operatorname{rank}P_{47}
=
\operatorname{Tr}P_{47}
=
47.
\]

## Invariant Occupancy

For the maximally mixed state

\[
\rho_*=\frac{I}{125},
\]

\[
\Omega_{47}(\rho_*)
=
\operatorname{Tr}(P_{47}\rho_*)
=
\boxed{\frac{47}{125}}
=
0.376.
\]

## Contraction

For

\[
\Gamma_\varepsilon
=
I-\varepsilon K^2,
\]

the optimal scalar step for the nonzero spectrum is

\[
\boxed{
\varepsilon_*=\frac1{99144}
}
\]

with worst-mode contraction

\[
\boxed{
\rho_*=\frac{15}{17}.
}
\]

Therefore

\[
\Gamma_{\varepsilon_*}^n
\longrightarrow
P_{47}.
\]

The continuous analogue is

\[
e^{-tK^2}
\longrightarrow
P_{47}.
\]

## Canonical Identity

\[
\boxed{
K
\rightarrow
\ker K
\rightarrow
P_{47}
\rightarrow
H=I-P_{47}
\rightarrow
x_\infty=P_{47}x_0.
}
\]
