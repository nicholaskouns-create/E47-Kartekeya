# Arrival Mathematics: Continuity, Variational Closure, and Spectral Convergence

## First-principles conditional proof and executable E47 realization

### 1. Continuity and conserved norm
For sufficiently smooth \(\rho_I(x,t)\ge 0\) and \(S_I(x,t)\), define
\[
J_I=\rho_I\nabla S_I,\qquad \partial_t\rho_I+\nabla\cdot J_I=0.
\]
With periodic boundaries or \(J_I\cdot n=0\) on \(\partial M\),
\[
\frac{d}{dt}\int_M\rho_I\,dV=0.
\]
Hence \(\mathcal N=\int_M\rho_I\,dV\) is invariant. For \(\Psi=\sqrt{\rho_I}e^{iS_I/\hbar}\), the same law preserves \(\|\Psi\|_{L^2}^2\).

### 2. Closure field
Given
\[
\psi_C=f_{\mathrm{fractal}}+\nabla\cdot(\rho_I\nabla S_I),
\]
continuity implies
\[
\psi_C=f_{\mathrm{fractal}}-\partial_t\rho_I.
\]
If \(\psi_C=0\), then \(f_{\mathrm{fractal}}=\partial_t\rho_I\), and under the same boundary conditions \(\int_M f_{\mathrm{fractal}}\,dV=0\).

### 3. Arrival as a joint zero-residual set
Let \(\Phi=(\rho_I,S_I,U,C,\psi_C,D)\) and collect all model constraints into a residual map \(R(\Phi)\). The arrival set is
\[
\mathcal A=R^{-1}(0).
\]
Define
\[
\mathcal E(\Phi)=\frac12\sum_a w_a\|R_a(\Phi)\|^2,\qquad w_a>0.
\]
Then
\[
\mathcal E(\Phi)=0\iff \Phi\in\mathcal A.
\]
For differentiable residuals, gradient relaxation \(\dot\Phi=-\nabla\mathcal E\) obeys
\[
\frac{d\mathcal E}{d\tau}=-\|\nabla\mathcal E\|^2\le0.
\]

### 4. Exact spectral convergence theorem
For a linear residual \(R(x)=Ax\), let
\[
B=A^\dagger W A\ge0.
\]
Then \(\ker B=\ker A\). If the positive spectrum of \(B\) lies in \([\Delta,M]\), then for
\[
x_{n+1}=(I-\varepsilon B)x_n,\qquad 0<\varepsilon<2/M,
\]
we have
\[
x_n\to P_{\ker A}x_0.
\]
The optimal constant step is
\[
\varepsilon_*=\frac{2}{\Delta+M},\qquad q_*=\frac{M-\Delta}{M+\Delta},
\]
and
\[
\|x_n-P_{\ker A}x_0\|\le q_*^n\|(I-P_{\ker A})x_0\|.
\]

### 5. E47 finite realization
For the supplied spin-2 carrier
\[
V=V_2^{\otimes3},\qquad \dim V=125,
\]
and
\[
K_E=(C-6I)(C-30I),
\]
the supplied Casimir multiplicities give
\[
E_{47}=\ker K_E=E_6\oplus E_{30},\qquad \dim E_{47}=25+22=47.
\]
Set \(A=K_E\), \(W=I\), \(B=K_E^2\). Then
\[
\Delta=11664,\qquad M=186624,
\]
so
\[
\Gamma_*=I-\frac{K_E^2}{99144},\qquad q_*=\frac{15}{17}.
\]
Therefore
\[
\Gamma_*^n\to P_{47},\qquad
\|\Gamma_*^n-P_{47}\|_2=\left(\frac{15}{17}\right)^n.
\]
At \(n=220\), the exact operator error is approximately
\[
1.0998014528\times10^{-12}.
\]
The invariant rank fraction is
\[
\Omega_c=\frac{\operatorname{Tr}P_{47}}{125}=\frac{47}{125}=0.376.
\]

### 6. Dimensional flow
For
\[
\frac{dD}{ds}=\sigma(10-D),\qquad \sigma>0,
\]
we obtain
\[
D(s)=10+[D(s_0)-10]e^{-\sigma(s-s_0)},
\]
so \(D\to10\). The equation \(\lambda_D^D-\lambda_D-1=0\) has a unique root above 1 for \(D>1\). At \(D=10\),
\[
\lambda_{10}=1.075766066086837,
\]
and
\[
\lambda_{10}^{20}=(\lambda_{10}+1)^2\approx4.30880476111762.
\]

### 7. Executable validation
The companion Python validator reconstructs the 125-dimensional spectrum, verifies the 47-dimensional kernel, computes the exact optimal contraction, checks an explicit compatible zero-residual witness, verifies the dimension-10 root identity, and evolves 256 normalized complex random states for 220 iterations.

Observed validation:
- 15/15 checks PASS.
- \(\operatorname{rank}P_{47}=47\).
- \(\Omega_c=0.376\).
- \(\|\Gamma_*^{220}-P_{47}\|_2=1.0998014528\times10^{-12}\).
- Maximum 256-state projection error \(\approx7.40\times10^{-13}\).
- Kernel drift: 0 to numerical precision.
- 20,000-state Haar Monte Carlo mean: 0.376150597, consistent with the exact expectation 0.376.

### 8. Evidence boundary
The spectral algebra, kernel dimension, contraction theorem, and executable checks are mathematical results conditional on the stated carrier and operator definitions. The physical identifications of residuals such as \(Q\), \(\Omega\), \(m_{\mathrm{eff}}\), \(D\), \(\mathcal H_\perp\), and \(\mathcal H_i\), and any claimed equivalences among them, require additional coupling laws and/or independent empirical validation.

## Core statement
\[
\boxed{\text{Arrival is projection onto the jointly invariant zero-residual manifold.}}
\]

Within the linear E47 realization, admissible components are invariant, violating components decay geometrically, and the limiting state is the orthogonal projection onto \(E_{47}\).
