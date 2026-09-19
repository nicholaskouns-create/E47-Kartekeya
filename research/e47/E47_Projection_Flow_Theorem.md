# E47 Projection Flow

Let

\[
E=\ker K
\]

and let

\[
P:\mathcal H\to E
\]

be the orthogonal projector.

Define

\[
H=I-P.
\]

Then

\[
P^2=P=P^\*,
\]

\[
H^2=H,
\]

and

\[
PH=HP=0.
\]

Every state decomposes uniquely as

\[
x=Px+Hx.
\]

Define the functional

\[
F[x]
=
\frac12\|Hx\|^2.
\]

Then

\[
\nabla F=Hx.
\]

The gradient flow

\[
\dot x=-Hx
\]

has exact solution

\[
x(t)
=
e^{-tH}x_0
=
Px_0+e^{-t}Hx_0.
\]

Therefore

\[
\boxed{
\lim_{t\to\infty}x(t)=Px_0.
}
\]

The invariant component is preserved exactly:

\[
Px(t)=Px_0.
\]

The transverse component decays exponentially:

\[
Hx(t)=e^{-t}Hx_0.
\]

Thus projection is not merely an endpoint operation. It is the asymptotic state of an exact contraction flow.
