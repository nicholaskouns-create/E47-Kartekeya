# Newton–E47 Product-Kernel Invariant

## Theorem

Let
[
B_a(x)=\frac12\left(x+\frac ax\right),\qquad a>0,
]
and let
[
K=(C-6I)(C-30I)
]
on (V_2^{\otimes 3}), with
[
E_{47}=\ker K,qquad P=P_{47},qquad Q=I-P.
]

Define
[
\Gamma_*=I-\frac{K^2}{99144}.
]

Then the product map
[
\mathscr F_a(x,\psi)=\bigl(B_a(x),\Gamma_*\psi\bigr)
]
has fixed manifold
[
\operatorname{Fix}(\mathscr F_a)=\{\sqrt a\}\times E_{47}.
]

The scalar Newton error obeys
[
e_{n+1}=\frac{e_n^2}{2x_n},
]
while the E47 complement obeys
[
\|Q\psi_n\|\le \left(\frac{15}{17}\right)^n\|Q\psi_0\|.
]

Hence the coupled tangent dynamics decomposes as
[
\mathbb R_{\rm Newton}\oplus E_{47}\oplus E_{47}^{\perp}
]
with multipliers
[
0\oplus I_{47}\oplus \Gamma_*|_{78}.
]

For a Newton–Mean block with nonzero local eigenvalue \(\tau\), the asymptotic joint contraction rate is
[
r_{\rm joint}=\max\{|\tau|,15/17\}.
]

The switching surface is therefore
[
|\tau|=\frac{15}{17}.
]

## Machine validation

Certificate: `MC-E47-NEWTON-PRODUCT-20260930-001`.

Validated numerically:
- rank (P=47), rank (Q=78)
- (P^2=P)
- (KP=0)
- (Gamma_*P=P)
- (ho(Gamma_*|_Q)=15/17)
- (|\Gamma_*^n-P|_2=(15/17)^n) to floating-point precision
- exact Newton quadratic-error identity numerically
- product fixed-manifold witness
- CPTP dephasing completion (D_P(\rho)=P\rho P+Q\rho Q): trace, Hermiticity, positivity, block dephasing, and E47-state invariance

Scope: finite-dimensional numerical and quantum-channel validation of the stated product construction. No physical hardware or laboratory realization is claimed.
