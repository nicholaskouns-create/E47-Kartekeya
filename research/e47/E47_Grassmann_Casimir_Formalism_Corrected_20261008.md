# E47 Grassmann–Casimir Formalism (corrected)

Exact statement of what the spin-2 triple construction certifies. A PASS is a theorem of this formalism. A witness clause is not implied by dimension count alone. Standard gravitational and thermodynamic identities are not theorems of this formalism.

## 1. Factor representation

Let \(V_2=\mathbb{C}^5\) with weight basis \(\lvert m\rangle\), \(m\in\{-2,-1,0,1,2\}\).

\[
J_z=\operatorname{diag}(-2,-1,0,1,2),
\]
\[
J_+\lvert m\rangle=(2-m)\lvert m+1\rangle,
\qquad
J_-\lvert m\rangle=(2+m)\lvert m-1\rangle.
\]

These ladder operators are unnormalized. The positive definite metric that restores the unitary structure is

\[
G_5=\operatorname{diag}\!\left(1,\frac14,\frac16,\frac14,1\right).
\]

The \(G_5\)-adjoint is \(X^{*_5}:=G_5^{-1}X^{\mathsf T}G_5\). In this adjoint,

\[
J_z^{*_5}=J_z,\qquad J_+^{*_5}=J_-,\qquad J_+^{\mathsf T}G_5=G_5 J_-.
\]

The factor Casimir is

\[
C_5=J_z^2+\frac12(J_+J_-+J_-J_+)=6I_5.
\]

Certified factor relations: \([J_z,J_\pm]=\pm J_\pm\), \([J_+,J_-]=2J_z\).

## 2. Carrier

\[
\mathcal H=V_2^{\otimes 3},\qquad \dim\mathcal H=5^3=125.
\]

\[
G=G_5^{\otimes 3}\succ 0,
\qquad X^{*_G}:=G^{-1}X^{\mathsf T}G.
\]

With total-spin operators summed over the three tensor legs,

\[
C=T_z^2+\frac12(T_+T_-+T_-T_+).
\]

Certified: \([C,T_z]=0\) and \(C^{*_G}=C\).

## 3. Spectrum

\[
\sigma(C)=\{j(j+1):j=0,\ldots,6\}=\{0,2,6,12,20,30,42\}.
\]

Irrep multiplicities and isotypic dimensions are

\[
n_j=(1,3,5,4,3,2,1),
\qquad
d_j=(2j+1)n_j=(1,9,25,28,27,22,13),
\]
\[
\sum_{j=0}^{6}d_j=125.
\]

Corrected \(T_z\) weight census for \(m=-6,\ldots,6\):

\[
\mu(m)=(1,3,6,10,15,18,19,18,15,10,6,3,1).
\]

The earlier plate labels \((19,21,19)\) at the center are a figure error.

## 4. Selector and kernel

\[
K=(C-6I)(C-30I).
\]

\[
\ker K=E_6\oplus E_{30},
\qquad
\dim\ker K=d_2+d_5=25+22=47.
\]

Excluded: \(\dim\ker K=82\). The integer 82 belongs to the constraint map \(A\) in the Grassmann construction.

On the complement, the nonzero \(K^2\)-eigenvalues are

\[
32400,\ 12544,\ 11664,\ 19600,\ 186624.
\]

\[
K^{*_G}=K,\qquad K^2\succeq_G0,\qquad \ker K^2=\ker K.
\]

## 5. Projector

Let \(P=P_6+P_{30}\) be the \(G\)-orthogonal projector onto \(\ker K\). Then

\[
P^2=P,\qquad \operatorname{tr}P=47,\qquad KP=0,
\]
\[
P^{*_G}=P\quad\Longleftrightarrow\quad P^{\mathsf T}G=GP.
\]

Coordinate dagger \(P=P^\dagger\) is not the certified statement in the unnormalized weight basis.

The carrier fraction is

\[
\Omega_c=\frac{\operatorname{rank}P}{\dim\mathcal H}=\frac{47}{125}.
\]

For \(\lVert x\rVert_G=1\), the state overlap \(\lVert Px\rVert_G^2=\langle x,Px\rangle_G\) depends on \(x\), and is not generally \(47/125\).

## 6. Contraction

\[
\varepsilon=\frac1{99144}=\frac{32}{17\cdot186624},
\qquad
\Gamma=I-\varepsilon K^2.
\]

\[
\Gamma P=P\Gamma=P.
\]

The complement spectral radius is exactly \(15/17\), saturated by the \(j=3\) and \(j=6\) sectors:

\[
1-\varepsilon\cdot11664=\frac{15}{17},
\qquad
\left|1-\varepsilon\cdot186624\right|=\frac{15}{17}.
\]

Hence

\[
\rho\!\left(\Gamma\big|_{(\ker K)^\perp}\right)=\frac{15}{17},
\]
\[
\lim_{n\to\infty}\Gamma^n=P,
\qquad
\lVert\Gamma^n-P\rVert_{G,2}=\left(\frac{15}{17}\right)^n.
\]

At \(n=220\), the exact spectral bound is approximately \(1.10\times10^{-12}\).

## 7. Grassmann witness

For any finite-dimensional subspaces,

\[
\dim(E+F)=\dim E+\dim F-\dim(E\cap F).
\]

The explicit witness has

\[
\dim E=90,\qquad A:\mathcal H\to\mathbb C^{43},\qquad \operatorname{rank}A=43,\qquad \dim\ker A=82,
\]
\[
E+\ker A=\mathcal H,\qquad \operatorname{rank}(A|_E)=43.
\]

Therefore

\[
\dim(E\cap\ker A)=90+82-125=47.
\]

The set equality

\[
E\cap\ker A=\ker K
\]

is not implied by the dimension count. It is a witness-dependent statement. The explicit deterministic witness constructs a basis decomposition \(\mathcal H=S\oplus U\oplus W\) with \(S=\ker K\), \(\dim U=43\), \(\dim W=35\), sets \(E=S\oplus U\), and defines \(\ker A=S\oplus W\), thereby proving the equality for that constructed witness.

The two kernels remain distinct:

\[
\dim\ker K=47,\qquad \dim\ker A=82,
\]

so \(\ker K\neq\ker A\).

## 8. Explicit non-identifications

The formalism rejects the following three conflations:

1. **Coordinate-adjoint conflation:** replace unsupported \(P=P^\dagger\) by the certified metric-adjoint identity \(P^{\mathsf T}G=GP\).
2. **Kernel-nullity conflation:** \(\dim\ker K=47\); \(82\) is \(\dim\ker A\).
3. **Dimension-to-set conflation:** \(\dim(E\cap\ker A)=\dim\ker K=47\) does not imply \(E\cap\ker A=\ker K\) without an explicit witness.

## 9. Non-theorems of this formalism

The following do not follow from Sections 1–8 without additional operators, actions, maps, or hypotheses: linear seismic balance; vacuum Einstein equations and Brinkmann harmonicity; diffeomorphism inequivalence of polynomial profiles; helicity reduction to \(\{\pm2\}\); Einstein–Hilbert variation; soft-graviton universality; Planck scales; Hawking temperature; Bekenstein–Hawking entropy.

## 10. Certified chain

\[
V_2^{\otimes3}\longrightarrow C\longrightarrow K=(C-6I)(C-30I)\longrightarrow\ker K\longrightarrow P,
\]
\[
P^{*_G}=P,\qquad \Gamma P=P,\qquad \Gamma^n\to P,\qquad \dim\ker K=47,\qquad \Omega_c=\frac{47}{125}.
\]

## Executable verification

Fresh execution on 2026-10-08:

- exact SymPy witness: PASS;
- full 125-dimensional complex-state numerical simulation: 6/6 PASS;
- witness set equality: PASS for the explicit construction;
- Born identity in the \(G\)-metric: PASS;
- complement radius: \(15/17\) PASS;
- \(n=220\) state convergence: PASS;
- state-dependent projection probability in seeded run: 0.365797038206;
- exact bound at \(n=220\): 1.099801452788e-12;
- simulated state error: 6.424269749978e-13.

Validator SHA-256:

- `witness.py`: `ec7032afa5c1df714ad767747186b1cee9fa8cc4c2922da17ec52c4747f58158`
- `quantum_sim.py`: `01ad52220f8fdbb26997c6437c799ed84c5689efca9289aa03dbe6753bf9130c`

Evidence boundary: exact finite-dimensional algebra plus executable reconstruction/simulation. No external physical realization is asserted.
