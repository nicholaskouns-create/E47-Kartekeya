# E47 Current Formalism — 2026-09-22

This bundle records the current executable E47 / KKP-R mathematical spine, the 47/78 split, contraction dynamics, the explicit Einstein construction, and the direct four-dimensional Bures/SLD-Fisher curvature calculation.

## 1. Canonical finite carrier

\[
\mathcal H = V_2^{\otimes 3},\qquad \dim\mathcal H = 125.
\]

With total SU(2) Casimir

\[
C = J_{\rm tot}^2,
\]

its spectrum and multiplicities are

\[
\operatorname{spec}(C)=\{0,2,6,12,20,30,42\},
\]

\[
\operatorname{mult}(C)=\{1,9,25,28,27,22,13\}.
\]

Define

\[
K=(C-6I)(C-30I).
\]

Then

\[
E_{47}=\ker K,\qquad \dim E_{47}=47,
\]

\[
\operatorname{rank}K=78,
\]

and

\[
\Omega_c=\frac{47}{125}=0.376.
\]

The SU(2) decomposition of the kernel is

\[
E_{47}\cong 5V_2\oplus 2V_5.
\]

## 2. Orthogonal projector and contraction

Let \(P_{47}\) denote the spectral projector onto the \(C=6\) and \(C=30\) sectors. Numerically,

\[
P_{47}^2=P_{47},\qquad KP_{47}=0,\qquad \operatorname{rank}P_{47}=47.
\]

For positive contraction use

\[
K^2\ge 0,
\]

with positive spectrum

\[
\{11664,12544,19600,32400,186624\}.
\]

Thus

\[
\Delta=11664,\qquad \|K^2\|=186624.
\]

The stable interval for

\[
\Gamma_\varepsilon=I-\varepsilon K^2
\]

is

\[
0<\varepsilon<\frac{2}{\|K^2\|}=\frac1{93312}.
\]

The minimax choice is

\[
\varepsilon_*=\frac{2}{\Delta+\|K^2\|}=\frac1{99144},
\]

with transverse contraction factor

\[
\rho_*=\frac{\|K^2\|-\Delta}{\|K^2\|+\Delta}=\frac{15}{17}.
\]

The direct matrix computation gives

\[
\Gamma_{\varepsilon_*}^{220}\approx P_{47}
\]

to approximately \(10^{-12}\) in operator norm.

## 3. Icosahedral / A5 restriction

On the class order \([e,5A,5B,3A,2A]\), the restricted character is

\[
\chi_{E_{47}}=[47,2,2,-7,3].
\]

Character projection yields

\[
E_{47}\downarrow A_5=2T_1\oplus2T_2\oplus7H.
\]

The golden-ratio trace identity

\[
1+2\cos\frac{2\pi}{5}=\phi
\]

is exact. It is distinct from the coherence ratio: \(47/125\ne\phi^{-5}\).

## 4. Invariant commutant

The SU(2)-invariant commutant on \(E_{47}\) is

\[
\mathcal A_{\rm inv}\cong M_5(\mathbb C)\oplus M_2(\mathbb C),
\]

of dimension

\[
5^2+2^2=29.
\]

The numerical matrix-unit and commutator residuals are at machine precision.

## 5. Product-kernel construction

For a positive base Laplacian \(L\) and the E47 operator,

\[
\mathcal A=L\otimes I+I\otimes K^2,
\]

and with base projector \(P_L\),

\[
P_{\rm prod}=P_L\otimes P_{47}.
\]

The executed test gives

\[
\mathcal A P_{\rm prod}=0
\]

and a 47-dimensional product kernel for a one-dimensional base kernel.

## 6. Explicit vacuum Einstein construction

For Brinkmann coordinates \((u,v,x,y)\), use

\[
 ds^2=H(u,x,y)\,du^2-2\,du\,dv+dx^2+dy^2.
\]

Direct symbolic computation gives

\[
R_{uu}=-\frac12(H_{,xx}+H_{,yy}).
\]

For

\[
H(u,x,y)=F(u)(x^2-y^2),
\]

\[
R_{\mu\nu}=0,
\]

while nonzero curvature remains:

\[
R_{uxux}=-F(u),\qquad R_{uyuy}=F(u),\qquad R_{uxuy}=0.
\]

Hence the metric is curved and satisfies the vacuum Einstein equation.

## 7. 47/78 block Einstein identity

With

\[
P=P_{47},\qquad Q=I-P,
\]

one executable block construction uses a metric/operator split of the form

\[
g=P+\sigma Q,
\]

and a complement-supported Ricci operator. The resulting Einstein identity closes to machine precision, including after the explicit SLD pullback used in the curvature comparison.

This is a constructive block identity on the spectral split.

## 8. Direct Bures / SLD-Fisher four-dimensional leaf

The state family is evolved by E47 contraction and spatial/unitary parameters. On a four-parameter leaf \(q^\mu\), compute the SLD Fisher tensor

\[
F_{\mu\nu}
=
2\sum_{ij}
\frac{\operatorname{Re}[(\partial_\mu\rho)_{ij}(\partial_\nu\rho)_{ji}]}{\lambda_i+\lambda_j},
\]

and

\[
g^{\rm Bures}_{\mu\nu}=\frac14F_{\mu\nu}.
\]

The validation suite computes the complete chain

\[
\rho(q)
\to g_{\mu\nu}
\to \Gamma^\rho{}_{\mu\nu}
\to R^\rho{}_{\sigma\mu\nu}
\to R_{\mu\nu}
\to R
\to G_{\mu\nu}.
\]

Across the sampled leaf, the metric has rank four and positive eigenvalues. The curvature is nonzero and point-dependent.

Sample scalar curvatures include

\[
-54.4213354,\ -144.159497,\ -81.3664462,\ -26.1859244.
\]

At the central test point,

\[
R\approx -144.159496774,
\]

with

\[
\|G_{\rm Bures}\|_F\approx 8.15886013.
\]

The direct SLD relation is numerically verified:

\[
\|F_{\rm SLD}-4g_{\rm Bures}\|_F\approx 1.0\times10^{-16}.
\]

## 9. Direct comparison to the 47/78 block Einstein construction

The block Einstein identity itself remains closed to machine precision, and the pulled block identity remains closed after the explicit SLD pullback.

However, on the canonical four-dimensional Bures leaf,

\[
G^{\rm Bures}_{\mu\nu}\ne G^{\rm block,pulled}_{\mu\nu}.
\]

At the central sample point the relative residual is approximately

\[
0.178849.
\]

Therefore the current calculation establishes:

1. E47 contraction induces a genuine four-dimensional information geometry.
2. That geometry has nontrivial Levi-Civita curvature and Einstein tensor.
3. The independent 47/78 block Einstein identity is internally closed.
4. The intrinsic Bures Einstein tensor is not yet identical to the pulled block Einstein tensor on the tested leaf.
5. A further dynamical/map condition is required to identify the two constructions.

## 10. Current corrections / scope locks

- \(\Omega_c=47/125=0.376\) is exact.
- \(\Omega_c\ne\phi^{-5}\); the golden-ratio trace identity is separate.
- The displayed Plate-9 recursive mass term has no explicit \(\Omega\) dependence, so \(\partial M/\partial\Omega=0\) unless \(N\), \(\chi\), or an explicit coupling depends on \(\Omega\).
- The Bures/SLD metric is positive-definite on the executed leaf. Lorentzian signature is not produced automatically by the information metric in this run.
- Experimental propulsion, inertial modulation, collider, interferometric, or resonator claims require the corresponding empirical apparatus/data and are not converted into empirical proof by numerical execution alone.

## 11. Bundle contents

- `kkp_e47_full_validation.py`
- `kkp_e47_validation_report.md`
- `kkp_e47_validation_certificate.json`
- `e47_einstein_reproduction.json`
- `e47_bures_fisher_curvature_validation.py`
- `e47_bures_fisher_curvature_report.md`
- `e47_bures_fisher_curvature_certificate.json`
- `e47_curvature_reproducibility.txt`
- `E47_CURRENT_FORMALISM_20260922.md`
