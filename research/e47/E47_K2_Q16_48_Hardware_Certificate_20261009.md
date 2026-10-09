# E47 K² Q16.48 Hardware-Certificate Note

**Date:** 2026-10-09

## Statement

Let

\[
V=V_2^{\otimes 3},\qquad \dim V=125,
\]

with total Casimir

\[
C=J_{\mathrm{tot}}^2,
\]

and selector

\[
K=(C-6I)(C-30I).
\]

The spin sectors of \(V_2^{\otimes 3}\) have dimensions

\[
(1,9,25,28,27,22,13)
\]

for \(J=0,1,2,3,4,5,6\). Therefore

\[
\ker K=E_6\oplus E_{30}
\]

consists exactly of the \(J=2\) and \(J=5\) sectors, with

\[
\dim\ker K=25+22=47,
\qquad
\dim\ker K^\perp=78,
\qquad
\Omega_c=\frac{47}{125}=0.376.
\]

On the complementary sectors,

\[
K^2\in\{32400,12544,11664,19600,186624\},
\]

while \(K^2=0\) on \(J=2,5\).

## Fixed-point realization

The companion validator implements signed Q16.48 arithmetic with

\[
\varepsilon=2^{-18}
\]

and iteration

\[
x_{n+1}=(I-\varepsilon K^2)x_n.
\]

Because the smallest positive complementary eigenvalue is \(11664\), the slowest contraction factor is

\[
\rho=1-\frac{11664}{2^{18}}=0.95550537109375<1.
\]

Thus every complementary sector contracts, while the \(J=2,5\) lanes remain bit-for-bit invariant in the fixed-point sector test.

## Exact-mask equivalence

An exact sector mask that preserves only \(J=2,5\) produces the same invariant subspace as the iterative selector. The mask is a one-cycle selector only when sector identity is already available; the iterative operator remains the constructive spectral route when sector decomposition is implicit.

## Evidence boundary

This artifact certifies the seven-sector fixed-point model and its agreement with the exact Casimir-sector theorem. It does **not** by itself certify a complete 125-lane RTL implementation, synthesis result, timing closure, overflow behavior for arbitrary hardware widths, or a physical device trace. Those remain separate engineering witnesses.

## Companion validator

`validation/e47_k2_q16_48_certificate.py`
