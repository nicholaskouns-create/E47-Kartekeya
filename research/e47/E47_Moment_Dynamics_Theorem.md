# E47 Moment Dynamics — the cube contracts fastest

**Certificate:** `MC-E47-MOMENT-DYNAMICS/1.0` · 13/13 PASS
**Executable:** [`validation/e47_moment_dynamics_certificate.py`](validation/e47_moment_dynamics_certificate.py)
**Record:** [`artifacts/E47_MOMENT_DYNAMICS_CERTIFICATE.json`](../../artifacts/E47_MOMENT_DYNAMICS_CERTIFICATE.json)
**Evidence:** E0 exact rational arithmetic over every sector of each member; E1 float64 replay of the flow, the iteration, and finite termination on the 125 × 125 carrier.
**Derivation:** Nicholas Shane Kouns with Claude, 15 October 2026, continuing the [moment selector](E47_Moment_Selector_Theorem.md).

## Setting

On a Fibonacci–Lucas carrier \(V_j^{\otimes3}\) (\(2j+1=F_k\), \(k\) odd, \(k\ge5\)), put \(a=j(j+1)\). The moment selector acts on the spin-\(J\) sector as the scalar

\[
\mu_J=\bigl(J(J+1)-a\bigr)\bigl(J(J+1)-5a\bigr),
\]

which vanishes exactly on \(J=j\) and the upper root \(J_\ast\).

## The dynamics

\[
\dot x=-K^2x,\qquad x(t)=e^{-tK^2}x_0\;\longrightarrow\;Px_0,\qquad \bigl\|e^{-tK^2}-P\bigr\|=e^{-\Delta t};
\]

\[
x_{n+1}=(I-\varepsilon K^2)\,x_n,\qquad \text{stable iff } 0<\varepsilon<2/\Lambda;
\]

\[
\varepsilon_\ast=\frac{2}{\Delta+\Lambda},\qquad
\rho_\ast=\frac{\kappa-1}{\kappa+1},\qquad
\rho_{\mathrm{Cheb}}=\frac{\sqrt\kappa-1}{\sqrt\kappa+1},
\]

where \(\Delta\) and \(\Lambda\) are the smallest and largest nonzero eigenvalues of \(K^2\), and \(\kappa=\Lambda/\Delta\).

## Theorem — closed forms on every member

\[
\begin{aligned}
\text{gap at } J=j+1:&\quad |\mu_{j+1}|=4(j+1)^2(2j-1), & \Delta&=16(j+1)^4(2j-1)^2,\\
\text{top at } J=3j:&\quad |\mu_{3j}|=4j^2(4j+1)(2j-1), & \Lambda&=16j^4(4j+1)^2(2j-1)^2,
\end{aligned}
\]

\[
\sqrt\kappa=\frac{\|K\|}{\mathrm{gap}}=\frac{j^2(4j+1)}{(j+1)^2},
\qquad
\varepsilon_\ast=\frac{1}{8(2j-1)^2\bigl[(j+1)^4+j^4(4j+1)^2\bigr]} .
\]

*Proof.* Substitute \(J(J+1)=a+2(j+1)\) for \(J=j+1\), \(a-2j\) for \(J=j-1\), and \(3j(3j+1)\) for \(J=3j\) into \(\mu_J\). The two neighbours of the lower root satisfy \(|\mu_{j-1}|=|\mu_{j+1}|+4\). Since \(\mu\) is a parabola in \(J(J+1)\), the smallest nonzero \(|\mu_J|\) sits beside a root. The upper root's neighbours are larger still: \(|\mu_{J_\ast+1}|>|\mu_{J_\ast-1}|>|\mu_{j+1}|\). This uses \(2j<J_\ast<3j\) when \(j\ge3\); the cube is checked directly (140 > 108). So the gap is at \(J=j+1\). At the top, \(|\mu_{3j}|\) exceeds the bottom sector's \(5a^2\) when \((3j+1)(j-1)>0\), and the vertex's \(4a^2\). ∎

| \(k\) | \(j\) | \(\sqrt\kappa\) | \(\rho_\ast\) | \(\rho_{\mathrm{Cheb}}\) | \(\varepsilon_\ast\) | exact steps |
|---:|---:|---:|---:|---:|---:|---:|
| **5** | **2** | **4** | **15/17** | **3/5** | **1/99144** | **5** |
| 7 | 6 | 900/49 | 0.99409 | 0.89673 | 1/786404168 | 16 |
| 9 | 33/2 | 72963/1225 | 0.99944 | 0.96698 | 1/2726451196928 | 48 |
| 11 | 44 | 114224/675 | 0.99993 | 0.98825 | 1/7110512379055368 | 131 |
| 13 | 116 | 2085680/4563 | 0.99999 | 0.99563 | 1/16712979795248631048 | 346 |

"Exact steps" is the number of distinct nonzero values of \(\mu_J^2\). The product \(\prod_m(I-K^2/m)\) over those values is the exact projector, so the iteration terminates in that many steps.

## Corollary — the cube contracts fastest

\(\sqrt\kappa\) increases along the family, so the cube is the best-conditioned moment carrier. It has the optimal rate 15/17, the Chebyshev rate 3/5, and five-step termination. It is also the only carrier whose ratio \(\|K\|/\mathrm{gap}\) is an integer, 4. For integer \(j\), \(\gcd(j,j+1)=1\) forces \((j+1)^2\mid 4j+1=4(j+1)-3\), so \(j=2\). For half-integer \(j=m/2\), \((m+2)^2\mid 2m+1\) has no solution. The validator scans \(2j\le4000\).

The cube is the first proper moment carrier ([selector theorem](E47_Moment_Selector_Theorem.md)), and it is also the one that contracts fastest. On the cube these numbers reproduce the [condition lock](E47_Condition_Lock_Theorem.md): condition 4, rate 15/17, Chebyshev 3/5, five-step termination.

## Boundary

- Linear flow and iteration of the moment selector on the Fibonacci–Lucas triple products. Closed forms are proved for every member and checked exactly for \(k=5,\dots,13\).
- \(\Delta\) sets the decay rate in the operator's own units. No physical time scale or physical identification is claimed.

**First to select, fastest to settle: 125 → 47 at 15/17 per step.**
