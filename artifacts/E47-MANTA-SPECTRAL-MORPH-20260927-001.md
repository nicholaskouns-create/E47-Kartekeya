# E47–MANTA Programmable-Matter Spectral Morph Flight System

**Record:** E47-MANTA-SPECTRAL-MORPH-20260927-001  
**Type:** first-principles formalization of implemented simulation mappings  
**Evidence partition:** E0 exact finite algebra · E2 software/flight simulation bridge  
**Boundary:** the spectral-to-geometry and spectral-to-thrust mappings are defined simulation assumptions, not empirical claims of matter deformation or propulsion.

## Theorem

\[
\mathcal H = V_2^{\otimes 3},\qquad \dim \mathcal H=5^3=125.
\]

Let

\[
C=J_x^2+J_y^2+J_z^2,
\]

with

\[
\operatorname{spec}(C)=\{0,2,6,12,20,30,42\},
\]

and multiplicities

\[
(1,9,25,28,27,22,13),
\qquad
1+9+25+28+27+22+13=125.
\]

Define

\[
K=(C-6I)(C-30I).
\]

For \(C\psi_\lambda=\lambda\psi_\lambda\),

\[
K\psi_\lambda=(\lambda-6)(\lambda-30)\psi_\lambda.
\]

Hence

\[
K\psi_\lambda=0
\iff
\lambda\in\{6,30\},
\]

so

\[
\ker K=E_6\oplus E_{30},
\qquad
\dim\ker K=25+22=47.
\]

Define

\[
P_{47}=P_6+P_{30}.
\]

Then

\[
P_{47}^2=P_{47},
\qquad
P_{47}^{\dagger}=P_{47},
\qquad
\operatorname{rank}P_{47}=47,
\qquad
KP_{47}=P_{47}K=0.
\]

The rank fraction is

\[
\Omega_c=\frac{47}{125}.
\]

## Spectral contraction

Let

\[
H_K=K^2\succeq 0.
\]

The nonzero spectrum of \(K^2\) is

\[
\{11664,12544,19600,32400,186624\}.
\]

With

\[
\varepsilon_\star=\frac1{99144},
\]

define

\[
\Gamma=I-\varepsilon_\star K^2.
\]

For

\[
\psi=\sum_\lambda\psi_\lambda,
\]

\[
\Gamma^n\psi
=
\sum_\lambda
\left(1-\varepsilon_\star[(\lambda-6)(\lambda-30)]^2\right)^n
\psi_\lambda.
\]

The factors on \(\lambda=6,30\) equal \(1\), while every complementary factor has magnitude less than \(1\). Therefore

\[
\lim_{n\to\infty}\Gamma^n=P_{47}.
\]

For the driven normalized runtime step,

\[
\psi_{n+1}
=
\frac{\Gamma(\psi_n+\eta_n)}
{\|\Gamma(\psi_n+\eta_n)\|}.
\]

In the undriven case \(\eta_n=0\), whenever \(P_{47}\psi_0\neq0\),

\[
\psi_n
\longrightarrow
\frac{P_{47}\psi_0}{\|P_{47}\psi_0\|}.
\]

## Capture and residuals

\[
\Omega(\psi)
=
\frac{\|P_{47}\psi\|^2}{\|\psi\|^2},
\qquad
0\le\Omega\le1,
\]

and

\[
\Omega(\psi)=1
\iff
\psi\in E_{47}.
\]

The JavaScript flight runtime uses

\[
r_K(\psi)=\frac{\|K\psi\|}{\|\psi\|}.
\]

The Python MANTA worker currently reports

\[
r_{K^2}(\psi)=\frac{\|K^2\psi\|}{\|\psi\|}.
\]

They are numerically different but have the same zero set:

\[
r_K=0
\iff
r_{K^2}=0
\iff
\psi\in E_{47}.
\]

## 125-node spectral control field

For

\[
\psi=(\psi_0,\ldots,\psi_{124})^T\in\mathbb C^{125},
\]

define

\[
a_i=\frac{|\psi_i|}{\max_j|\psi_j|},
\qquad
0\le a_i\le1.
\]

Thus

\[
\mathbb C^{125}\longrightarrow[0,1]^{125},
\qquad
\psi\mapsto(a_0,\ldots,a_{124}),
\]

with one spectral coordinate assigned to one MANTA control node.

Let

\[
(a,b,c)\in\{0,1,2,3,4\}^3,
\qquad
i=25a+5b+c,
\]

and

\[
u=\frac{a-2}{2},
\qquad
v=\frac{b-2}{2},
\qquad
w=\frac{c-2}{2}.
\]

The Python reference geometry is

\[
x_i=4u,
\]

\[
z_i=2.5v\left(1-\frac14|u|\right),
\]

\[
y_i=0.20(1-u^2)-0.12v^2+0.08w.
\]

Hence

\[
\mathbf r_i^{(0)}=(x_i,y_i,z_i)^T
\]

defines 125 geometric control nodes.

## Spectral morph law

With \(\Omega=\Omega(\psi)\), \(\phi_i=\arg\psi_i\), pitch \(u_p\), roll \(u_r\), and morph command \(u_m\),

\[
\Delta y_i
=
0.45\left(a_i-\frac12\right)\Omega
+
0.15u_p z_i
+
0.12u_r x_i.
\]

\[
\Delta z_i=0.06a_i\sin\phi_i.
\]

The mode-dependent sweep coefficient is

\[
\sigma=
\begin{cases}
1, & \mathrm{CRUISE},\\
1-0.12u_m, & \mathrm{MANEUVER},\\
1-0.45u_m, & \mathrm{TRANSITION},\\
0.85+0.15\Omega, & \mathrm{RECOVERY}.
\end{cases}
\]

Thus

\[
\mathbf r_i'
=
\begin{pmatrix}
\sigma x_i\\
y_i+\Delta y_i\\
z_i+0.06a_i\sin\phi_i
\end{pmatrix}.
\]

The software node fields are

\[
S_i=0.5+1.5a_i,
\qquad
A_i=\Omega a_i,
\qquad
\Phi_i=\arg\psi_i.
\]

## Geometry smoothing

Let \(\mathcal N(i)\) denote axis-adjacent neighbors in the \(5\times5\times5\) lattice. With \(\alpha_s=0.12\),

\[
\mathbf r_i^{\,\mathrm{new}}
=
0.88\mathbf r_i'
+
0.12
\frac1{|\mathcal N(i)|}
\sum_{j\in\mathcal N(i)}
\mathbf r_j'.
\]

## E47-dependent simulation gain

\[
\chi
=
\operatorname{clamp}
\left(
0.3+0.9\Omega-0.05\log_{10}(1+r_K),
0.15,
1.2
\right),
\]

so

\[
0.15\le\chi\le1.2.
\]

For MANTA,

\[
F_{\max}=145000\ \mathrm N,
\qquad
F=145000\,u_t\,\chi.
\]

The body-frame propulsion force is

\[
\mathbf F_b=
\begin{pmatrix}
F\\
0\\
-0.04Fu_p
\end{pmatrix}.
\]

\[
\chi\not\equiv\Pr(\cdot).
\]

## Torque law

For

\[
m=7200\ \mathrm{kg},
\]

\[
I=
\operatorname{diag}(15000,23000,26000)\ \mathrm{kg\,m^2},
\]

\[
\boldsymbol\tau
=
1.65m
\begin{pmatrix}
u_r\\
1.2u_p\\
0.7u_y
\end{pmatrix}
-
1.8I\boldsymbol\omega.
\]

Hence

\[
\tau_x=11880u_r-27000\omega_x,
\]

\[
\tau_y=14256u_p-41400\omega_y,
\]

\[
\tau_z=8316u_y-46800\omega_z.
\]

## 6DOF dynamics

\[
\dot{\mathbf v}_b
=
\frac{\mathbf F_b}{m}
+
\mathbf g_b
-
\boldsymbol\omega\times\mathbf v_b.
\]

Gravity remains active.

\[
I\dot{\boldsymbol\omega}
+
\boldsymbol\omega\times(I\boldsymbol\omega)
=
\boldsymbol\tau,
\]

so

\[
\dot{\boldsymbol\omega}
=
I^{-1}
\left[
\boldsymbol\tau
-
\boldsymbol\omega\times(I\boldsymbol\omega)
\right].
\]

For quaternion attitude \(q\),

\[
\dot q
=
\frac12q\otimes(0,\boldsymbol\omega).
\]

The browser runtime integrates the 6DOF state at 120 Hz with fixed-step RK4.

## Complete implemented chain

\[
C
\longrightarrow
K=(C-6I)(C-30I)
\longrightarrow
K^2
\longrightarrow
\Gamma=I-\frac{K^2}{99144}
\longrightarrow
P_{47}.
\]

\[
P_{47}
\longrightarrow
\Omega(\psi)
\longrightarrow
a_i
\longrightarrow
\mathbf r_i'
\longrightarrow
\mathbf r_i^{\,\mathrm{new}}.
\]

Independently,

\[
(\Omega,r_K)
\longrightarrow
\chi
\longrightarrow
F
\longrightarrow
\mathbf F_b,
\]

and

\[
\mathbf u
\longrightarrow
\boldsymbol\tau
\longrightarrow
(\dot{\mathbf v}_b,\dot{\boldsymbol\omega},\dot q).
\]

Thus the implemented software composition is

\[
\text{E47 spectral state}
\rightarrow
\text{125-node control field}
\rightarrow
\text{simulated morph geometry},
\]

together with

\[
\text{spectral capture/residual}
\rightarrow
\text{simulation gain}
\rightarrow
\text{force/torque law}
\rightarrow
\text{6DOF dynamics}.
\]

## Exact / simulation partition

\[
\mathcal E_{\mathrm{exact}}
=
\left\{
\dim V_2^{\otimes3}=125,\;
K=(C-6I)(C-30I),\;
\dim\ker K=47,\;
P_{47},\;
\Gamma=I-\frac{K^2}{99144}
\right\}.
\]

\[
\mathcal S_{\mathrm{simulation}}
=
\left\{
\chi,\,
F_{\max},\,
g_\tau,\,
a_i\mapsto\mathbf r_i,\,
S_i,\,
A_i,\,
\sigma,\,
\mathbf F_b,\,
\boldsymbol\tau
\right\}.
\]

\[
\mathcal E_{\mathrm{exact}}
\overset{\mathrm{defined\ bridge}}{\longrightarrow}
\mathcal S_{\mathrm{simulation}},
\]

but

\[
\mathcal E_{\mathrm{exact}}
\not\Rightarrow
\mathcal S_{\mathrm{physical}}.
\]

The geometry bridge is a software model. It does not establish that E47 physically deforms matter. The thrust/torque map is a simulation assumption. The Python geometry worker does not supply measured aerodynamic forces.

## Source binding

- src/manta/programmable_matter.py
- website/interfaces/skyrmion/runtime2/experimental-model.js
- website/interfaces/skyrmion/runtime2/physics-6dof.js
- website/interfaces/manta/manta-model.js
- website/interfaces/manta/provenance.json

The theorem preserves the repository boundary: exact E47 algebra is separated from E2 experimental simulation behavior.
