# Ω spectral correction

Let (d=(1,9,25,28,27,22,13)), (U_n) be second-kind Chebyshev polynomials,
(N=25U_4^2+22U_{10}^2), (D=\sum_{j=0}^6d_jU_{2j}^2).

[
\eta=N/D,quad \Omega_c=47/125,quad
\Omega=\frac{47}{125}-\frac2\pi\int_{-1}^1\eta(x)\sqrt{1-x^2}\,dx.
]

Exact factorization:
[
47D-125N=16x^2(2x^2-1)Q(x)
]
where
[
Q(x)=320339968x^{20}-1601699840x^{18}+3367403520x^{16}-3859415040x^{14}+2613002240x^{12}-1058193408x^{10}+247566720x^8-30728960x^6+1775800x^4-51000x^2+1125.
]

(\eta(0)=\eta(\pm1/\sqrt 2)=47/125) exactly.

For simple roots (D(r)=0) with the branch (\sqrt{r^2-1}\sim r) at infinity,
[
\Omega=47/125-2\sum_{D(r)=0}\frac{N(r)}{D'(r)}(\sqrt{r^2-1}-r).
]
This is an algebraic root-sum description; it is **not** proof of a low-degree radical.

Python 40-digit quadrature gives (\Omega\approx0.00074236226339603274234263737580108237).

A₅: (P_{26}=P_1+P_5), (\mathrm{rank}(P_{26})=26), (T^n=P_{26}+2^{-n}(I-P_{26})). Lean/Coq drafts **uncompiled**.
