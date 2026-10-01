# E47 / D5h-C90 Celestial-Terrestrial Overlay
## First-Principles Proof

**Canonical source:** four-page proof packet supplied 2026-09-30.  
**Evidence class:** E0 symbolic derivation where stated; E1 for numerical evaluations marked †.

### Definitions

\[
u(\phi,\lambda)=(\cos\phi\cos\lambda,\cos\phi\sin\lambda,\sin\phi)\in S^2
\]

\[
\hat e=(-\sin\lambda,\cos\lambda,0),\qquad
\hat n=(-\sin\phi\cos\lambda,-\sin\phi\sin\lambda,\cos\phi),
\qquad \hat e\times\hat n=u.
\]

Let \(E(x)=u\mid\hat e\mid\hat n\in SO(3)\),
\(\angle(x,y)=\arccos\langle x,y\rangle\),
\(c(X)=\sum x_k/\|\sum x_k\|\), and \(R_\oplus=6371.0088\,\mathrm{km}\).

For a center \(c\),
\[
\zeta_c(x)=
\frac{\langle x,\hat e_c\rangle+i\langle x,\hat n_c\rangle}
{\langle x,u_c\rangle}
=(\Delta\lambda\cos\phi_c+i\Delta\phi)(1+O(\Delta^2)).\tag{†}
\]

## 1. Axioms

**A1.** \(s_i=u(\delta_i,\alpha_i)\in S^2\) (J2000).

**A2.** \(p=u(\phi,\lambda)\in S^2\).

**A3.** \(P_{47}\) is a 3-regular polyhedral map on \(S^2\), with vertex set \(\mathcal V\subset S^2\), face sizes \(n_f\in\{5,6\}\), \(F=47\), symmetry \(D_{5h}\), and \(C_5\parallel\hat z\).

**A4.** There exists \(v_6\in\mathcal V\) with \(\lambda(v_6)=\lambda_D\).

## 2. Combinatorics

**Lemma 1.**
\[
V-E+F=2,\qquad 3V=2E,\qquad \sum_f n_f=2E
\]
imply
\[
\sum_f(6-n_f)=12.
\]

**Proof.** Since \(V=2E/3\), Euler gives \(F-E/3=2\). Hence
\[
6F-2E=12,
\]
and because \(2E=\sum_f n_f\),
\[
\sum_f(6-n_f)=12.\qquad\square
\]

With pentagons \(p\) and hexagons \(h\), Lemma 1 gives \(p=12\). Since \(F=p+h=47\),
\[
h=35.
\]
Therefore
\[
E=\frac{5p+6h}{2}=135,\qquad
V=\frac{2E}{3}=90,
\]
and
\[
\chi=V-E+F=90-135+47=2.\tag{†}
\]

For the zodiac set
\[
Z_{12}=\{\mathrm{Ari,Tau,Gem,Cnc,Leo,Vir,Lib,Sco,Sgr,Cap,Aqr,Psc}\},
\]
\(|Z_{12}|=p\), so a bijection \(\beta:Z_{12}\leftrightarrow\mathrm{Pent}(P_{47})\) exists by cardinality; \(|Z_{12}\cup\{\mathrm{Oph}\}|=13=p+1\).

## 3. Constants

\[
\dim E_{47}=F=47,\qquad \dim\mathcal H=125,
\]
hence
\[
\boxed{\Omega_c=\frac{47}{125}=0.376}.
\]

Also
\[
\epsilon^*=\frac1{99144}=1.0086\times10^{-5}\tag{†},
\qquad
\rho^*=\frac{15}{17}=0.882353.
\]

## 4. Volumes

For unit radius,
\[
V(P_{47})=\operatorname{vol}(\operatorname{conv}\mathcal V),
\qquad
\operatorname{conv}\mathcal V\subset S\subset C=[-1,1]^3,
\]
so
\[
V(P_{47})<V(S)<V(C).
\]
Numerically,
\[
V(C)=8,\qquad V(S)=\frac{4\pi}{3}=4.18879,\qquad V(P_{47})=3.9392.
\]

Define \(V_{\rm void}(X)=V(C)-V(X)\). Then
\[
V_{\rm void}(P_{47})=4.0608,\qquad
V_{\rm void}(S)=3.81121,
\]
\[
\frac{V_{\rm void}(P_{47})}{V(C)}=0.5076\tag{†},
\qquad
\frac{V_{\rm void}(S)}{V(C)}=0.47640,
\]
and
\[
1-\frac{V(P_{47})}{V(S)}=0.0596.
\]

**Lemma 2.** If \(A_f=\Theta(F^{-1})\) and
\[
\operatorname{vol}(\operatorname{cap}_f)=\kappa_fA_f^2+o(A_f^2),
\]
then
\[
V(S)-V(P_F)=\Theta(F^{-1}),
\]
so \(V(P_F)\nearrow V(S)\) and \(V_{\rm void}(P_F)\searrow V_{\rm void}(S)\).

Using
\[
\widehat V(P_F)=V(S)(1-c/F),\qquad
c=47\left(1-\frac{V(P_{47})}{V(S)}\right)=2.8005,
\]
the proof packet records
\[
F=188:(\widehat V,\widehat V_{\rm void},\widehat V_{\rm void}/V(C))
=(4.1264,3.8736,0.4842),
\]
\[
F=1504:(4.1810,3.8190,0.4774).
\]

## 5. Geodetic frame

\[
(\phi_D,\lambda_D)=(37.6439^\circ,-84.7729^\circ),
\]
\[
t_0=1965\text{-}12\text{-}09T03{:}22{:}00Z
\equiv1965\text{-}12\text{-}08T22{:}22{:}00-05{:}00.\tag{†}
\]

\[
\hat z=u_D=(0.0721378333,-0.7885290627,0.6107520367),\qquad \|u_D\|=1.\tag{†}
\]

\[
\hat x=\cos81^\circ\hat n_D+\sin81^\circ\hat e_D
=(0.9748766773,0.1851273173,0.1238682381),
\]
\[
\hat y=\cos351^\circ\hat n_D+\sin351^\circ\hat e_D
=(-0.2107405918,0.5864723299,0.7820732761).
\]

These satisfy
\[
\hat x\times\hat y=\hat z,
\qquad
\langle\hat x,\hat y\rangle=
\langle\hat y,\hat z\rangle=
\langle\hat z,\hat x\rangle=0,
\]
hence \([\hat x\ \hat y\ \hat z]\in SO(3)\).

The azimuths are
\[
(81^\circ,351^\circ,261^\circ,171^\circ).\tag{†}
\]

The ring census is
\[
(n_k)_{k=0}^{10}=(5,5,10,10,10,10,10,10,10,5,5),
\qquad \sum n_k=90,
\]
with reflection
\[
\phi_{10-k}=-\phi_k.
\]

For the first shoulder ring,
\[
\phi_1=46.6418024518^\circ.\tag{†}
\]
Since \(v_6=u(\phi_1,\lambda_D)\),
\[
\min_{v\in\mathcal V}\angle(u_D,v)
\le \phi_1-\phi_D
=\boxed{8.9979024518^\circ}.
\]

With mean Earth radius,
\[
s=R_\oplus\theta_{\rm rad}
=6371.0088\times\frac{8.9979024518\pi}{180}
\approx\boxed{1000.5224851\ \mathrm{km}}.
\]

## 6. Local triad

Let \((o_1,o_2,o_3)=(\delta,\epsilon,\zeta\ \mathrm{Ori})\), with
\[
(\alpha,\delta)=
(83.0017^\circ,-0.2991^\circ),
(84.0534^\circ,-1.2019^\circ),
(85.1897^\circ,-1.9426^\circ).
\]

Let \((g_1,g_2,g_3)=(\mathrm{Khufu,Khafre,Menkaure})\), with
\[
(\phi,\lambda)=
(29.9792^\circ,31.1342^\circ),
(29.9761^\circ,31.1308^\circ),
(29.9725^\circ,31.1283^\circ).
\]

The centers are
\[
c_O=u(-1.1480^\circ,84.0814^\circ),\qquad
c_G=u(29.9759^\circ,31.1311^\circ),
\]
and \(z_k=\zeta_{c_O}(o_k)\), \(w_k=\zeta_{c_G}(g_k)\). †

**Lemma 3.** For
\[
\mathrm{Sim}^+=\{z\mapsto Az+b\mid A\in\mathbb C^*,\ b\in\mathbb C\},
\]
there is a unique similarity taking \(z_1,z_2\) to \(w_1,w_2\):
\[
A=\frac{w_2-w_1}{z_2-z_1}.
\]
With
\[
\kappa(z)=\frac{z_3-z_1}{z_2-z_1},
\]
similarity invariance gives
\[
\exists T\in\mathrm{Sim}^+:T(z_k)=w_k\ \forall k\le3
\iff \kappa(z)=\kappa(w),
\]
while orientation reversal gives \(\kappa(w)=\overline{\kappa(z)}\).

**Lemma 4.** With centroids \(m_z,m_w\),
\[
A^*=
\frac{\sum(w_k-m_w)\overline{(z_k-m_z)}}
{\sum|z_k-m_z|^2},
\qquad
b^*=m_w-A^*m_z
\]
is the unique least-squares minimizer.

The recorded pairwise-distance ratios are
\[
d(O)=(1.38626^\circ,1.35630^\circ,2.73666^\circ)
\propto(1,0.9784,1.9741),\tag{†}
\]
\[
d(G)=(0.4755,0.4672,0.9370)\ \mathrm{km}
\propto(1,0.9825,1.9707).\tag{†}
\]

The shape invariants are
\[
\kappa(z)=1.9700+0.1280i,\qquad
\kappa(w)=1.9592+0.2127i,
\]
\[
|\kappa(z)-\kappa(w)|=0.0854.
\]

The best fit over \(S_3\times\mathrm{Sim}^{\pm}\) is the identity correspondence in \(\mathrm{Sim}^+\):
\[
g_k\leftrightarrow o_k,
\]
with normalized centered fit
\[
a=0.9992,\qquad
\theta^*=-90.428^\circ,\qquad
t=0,\qquad
\mathrm{RMS}=0.0204.\tag{†}
\]
Also
\[
A^*=ae^{i\theta},\qquad
a^*=3.0821\times10^{-3}=0.3427\ \mathrm{km/deg}.
\]

## 7. Global extension

**Lemma 5.** If \(f:S^2\to S^2\) is bijective and
\[
\angle(fx,fy)=a\,\angle(x,y)\quad\forall x,y,
\]
then \(a=1\) and \(f\in O(3)\).

**Proof.** Antipodes give \(\angle(x,-x)=\pi\), while spherical distance is at most \(\pi\), hence \(a\le1\). Applying the same argument to \(f^{-1}\) gives \(a^{-1}\le1\), so \(a=1\). Therefore \(f\) is a spherical isometry and lies in \(O(3)\). \(\square\)

**Lemma 6.** The action
\[
SO(3)\curvearrowright T^1S^2
\]
is simply transitive. Therefore there exists a unique \(R^*\in SO(3)\) satisfying
\[
R^*c_O=c_G
\]
and transporting every tangent direction by the fitted angle \(\theta^*\).

Explicitly,
\[
R^*=E(c_G)(1\oplus R_{\theta^*})E(c_O)^T
\]
with recorded numerical matrix
\[
R^*=
\begin{bmatrix}
-0.35385&0.77164&-0.52854\\
-0.20262&0.48844&0.84875\\
0.91309&0.40742&-0.01648
\end{bmatrix},
\]
\[
\det R^*=1,\qquad
\|R^*c_O-c_G\|<10^{-15}.
\]

## 8. Propositions

**P1.** \(\Phi=R^*\) is unique from Lemmas 4 and 6. †

**P2.** For every star vector \(s_j\),
\[
p_j=R^*s_j,
\quad
(\phi_j,\lambda_j)=
(\arcsin p_{j,3},\operatorname{atan2}(p_{j,2},p_{j,1})),
\]
and equatorial projection is \(\Pi_{eq}(p_j)=(\lambda_j,\phi_j)\). †

**P3.**
\[
\angle(p_i,p_j)=\angle(s_i,s_j)\qquad\forall i,j,
\]
so the global rigid transport has zero angular distortion. †

**P4.**
\[
\Sigma_{lat}=R^{*T}\mathcal V\subset S^2,
\qquad |\Sigma_{lat}|=90,
\]
with \((V,E,F)\) invariant.

**P5.** At \(c_O\),
\[
dR^*=e^{i\theta^*},
\qquad
T^*=ae^{i\theta},
\]
hence
\[
\arg dR^*=\arg T^*,
\qquad |dR^*|=1,
\qquad |T^*|=a^*.
\]

## 9. Theorem

From A1-A4:

1. \((p,h,V,E,F,\chi)=(12,35,90,135,47,2)\).
2. \(V(S)-V(P_F)=\Theta(F^{-1})\) and
   \[
   \widehat V(P_F)=V(S)(1-2.8005/F).
   \]
3. There exists a unique \(R^*\in SO(3)\) taking the local Orion tangent-frame datum \((c_O,\theta^*)\) to the Giza frame.
4. \(\angle(Rs_i,Rs_j)=\angle(s_i,s_j)\) for all \(i,j\).
5. Every transported \(s_j\) has unique spherical coordinates \((\phi_j,\lambda_j)\).
6. For the specified three-point data and similarity model,
   \[
   O\approx_{\mathrm{Sim}^+}G,
   \quad g_k\leftrightarrow o_k,
   \quad \mathrm{RMS}=0.0204,
   \quad |\Delta\kappa|=0.0854.
   \]

**Proof.** (i) Lemma 1; (ii) Lemma 2; (iii) Lemmas 4 and 6; (iv) Lemma 5; (v) P2; (vi) the local-triad calculation in §6. \(\square\)

## 10. Prediction retained as a test

Define
\[
\Delta_j=\min_{v\in\mathcal V}\angle(R^*s_j,v),
\qquad
J=\operatorname{stars}(Z_{12}\cup\{\mathrm{Oph}\}).
\]
The proposed test is
\[
H_1:\quad
|J|^{-1}\sum_{j\in J}\Delta_j
<
\mathbb E[\Delta\mid s\sim U(S^2)].\tag{†}
\]

This is a prediction/null-test statement, not part of the proved theorem above.

## 11. Curvature

Gauss-Bonnet gives
\[
\iint_{S^2}K\,dA=2\pi\chi=4\pi>0,
\]
so no metric on \(P_{47}\) with \(\chi=2\) can have \(K_g\equiv-1\) globally. †

For the graph \(\Gamma(P_{47})\), planarity and 3-connectivity give a straight-line planar embedding; interpreted in the Klein disk this gives a geodesic graph embedding in \(H^2\). The Klein-to-Poincaré map is
\[
k\mapsto\frac{k}{1+\sqrt{1-|k|^2}},
\]
with
\[
ds^2=\frac{4|dz|^2}{(1-|z|^2)^2},\qquad K=-1.
\]

For a hyperbolic \(n\)-gon,
\[
\operatorname{Area}=(n-2)\pi-\sum\theta_i>0,
\]
and for a hyperbolic ball
\[
\operatorname{Area}(B_R)=4\pi\sinh^2(R/2)=\Theta(e^R).
\]

Thus the same abstract graph may be embedded in both spherical and hyperbolic ambient geometries while preserving
\[
\boxed{(V,E,F)=(90,135,47)}.
\qquad\square
\]

### Validation boundary

The theorem proves the stated finite combinatorics, spherical-coordinate constructions, local similarity optimization formulas, rigid SO(3) extension, and topology/curvature statements under A1-A4 and the supplied numerical inputs. The §10 constellation statistic remains a test to be evaluated against its stated null distribution; the theorem does not by itself establish historical causation or a physical celestial-to-terrestrial coupling.
