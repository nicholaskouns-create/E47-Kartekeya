# Native-coordinate residuals and transfer bounds

Let $A$ act on a finite-dimensional complex Hilbert space. Partition its spectrum into nonempty clusters $S$ and $T$ separated by $g=\min_{a\in S,b\in T}|a-b|>0$. A real operator admits the same real construction for conjugation-invariant clusters. In arbitrary native coordinates, use the corresponding Gram matrix for norms and adjoints.

Factor the minimal polynomial $m=m_Sm_T$ by assigning each root with its full multiplicity to its cluster. Bézout's identity gives $u m_S+v m_T=1$. Set
$$
P=v(A)m_T(A),\qquad Q=I-P=u(A)m_S(A).
$$
On the generalized eigenspaces in $S$, $m_S(A)=0$ and $P=I$. In $T$, $m_T(A)=0$ and $P=0$. Thus $P^2=P$ and $E=\ker Q$ is the selected spectral subspace. These polynomials can be applied by Horner's rule using only native-coordinate products. For a normal operator, Lagrange interpolation also gives $P$, which is orthogonal.

More generally let $R=p(A)$ vanish on $E$ and be invertible on the complementary spectral subspace. The choice $R=Q$ always qualifies. Write $\Pi$ for the orthogonal projector onto $E$, $M=\|R\|$, and $\sigma=\sigma_{\min}(R|_{E^\perp})>0$. Injectivity on $E^\perp$ and compactness of its unit sphere give positivity. Since $Rx=R(I-\Pi)x$, for every $x$
$$
\sigma d(x,E)\le \|Rx\|\le M d(x,E).
$$
For $R=Q$ one can use $\sigma=1$, since $(I-\Pi)Q=I-\Pi$. An eigenvalue gap alone gives no upper sensitivity bound for nonnormal operators. For $A=\left(\begin{smallmatrix}0&b\\0&1\end{smallmatrix}\right)$ with $S=\{0\}$, the gap is 1 and $\|Q\|=\sqrt{1+|b|^2}$. For normal $A$, the choice $p(z)=\prod_{a\in S}(z-a)$ gives $\sigma=\min_{\lambda\in T}|p(\lambda)|\ge g^{|S|}$ and $M=\max_{\lambda\in T}|p(\lambda)|$.

## Transfer to an external implementation

Let $z$ be an external state and $x$ the corresponding target native state. Suppose a decoder has $\|Dz-x\|\le b$, the implemented residual has $\|\widehat R-R\|\le\eta$, and the reported score $s$ has absolute arithmetic or measurement error at most $\epsilon$ relative to $\|\widehat R Dz\|$. With $B=Mb+\eta\|Dz\|+\epsilon$,
$$
|s-\|Rx\||\le B,\qquad
\frac{\max(0,s-B)}{M}\le d(x,E)\le \frac{s+B}{\sigma}.
$$
The first inequality follows by expanding $\widehat R Dz-Rx=(\widehat R-R)Dz+R(Dz-x)$ and applying the reverse triangle inequality. For tolerance $\tau$, accept if $s+B\le \sigma\tau$ and reject if $s-B>M\tau$. The remaining interval is inconclusive. If the joint error assumptions hold with probability at least $1-\alpha$, unsafe acceptance has unconditional probability at most $\alpha$. Given a failure event $F$ of positive probability, the conditional bound is $\min(1,\alpha/\Pr(F))$. These implications require no independence assumption.

For $p(z)=\sum_{j=0}^m a_jz^j$, assume $\|\widetilde A-A\|\le\delta$ and both operator norms are at most $L$. Telescoping noncommuting powers gives
$$
\|p(\widetilde A)-p(A)\|\le\delta\sum_{j=1}^m j|a_j|L^{j-1}.
$$
The same bound holds for $\|Dp(\widetilde A)-p(A)D\|$ when $D$ is a rectangular decoder and $\|D\widetilde A-AD\|\le\delta$. Expand the $j$th power defect into the sum of $j$ terms $A^k(D\widetilde A-AD)\widetilde A^{j-1-k}$.

For dynamical transfer, set $G=I-hR^*R$ for $0<h<2/M^2$. The spectrum of $R^*R$ on $E^\perp$ lies in $[\sigma^2,M^2]$. Thus $G$ is the identity on $E$ and its complementary operator norm is at most $q=\max(|1-h\sigma^2|,|1-hM^2|)<1$. If $\|Dz_{n+1}-GDz_n\|\le b_n$, then
$$
d(Dz_n,E)\le q^n d(Dz_0,E)+\sum_{j=0}^{n-1}q^{n-1-j}b_j .
$$
Project each step onto $E^\perp$ and iterate the triangle inequality. For $b_j\le b_*$ the perturbation term is at most $b_*(1-q^n)/(1-q)$. For the continuous system $y'=-R^*Ry+u(t)$ with integrable forcing, variation of constants gives
$$
d(y(t),E)\le e^{-\sigma^2t}d(y(0),E)
 +\int_0^t e^{-\sigma^2(t-s)}\|(I-\Pi)u(s)\|\,ds.
$$

These are membership guarantees. A fault that substitutes another vector in $E$ has zero residual. A shared decoder fault can violate the assumed coordinate error bound. An output-correctness policy additionally needs a trusted reference tying the protected component to the requested input.
