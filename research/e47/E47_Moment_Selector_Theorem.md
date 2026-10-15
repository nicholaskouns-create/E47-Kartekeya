# E47 Moment Selector — the Fibonacci–Lucas carriers

**Certificate:** `MC-E47-MOMENT-SELECTOR/1.0` · 13/13 PASS
**Executable:** [`validation/e47_moment_selector_certificate.py`](validation/e47_moment_selector_certificate.py)
**Record:** [`artifacts/E47_MOMENT_SELECTOR_CERTIFICATE.json`](../../artifacts/E47_MOMENT_SELECTOR_CERTIFICATE.json)
**Evidence:** E0 exact rational arithmetic over Clebsch–Gordan decompositions; E1 float64 replay on the 125 × 125 carrier.
**Derivation:** Nicholas Shane Kouns with Claude, 15 October 2026, extending the Moment Theorem (T1).

## The moment selector

On a carrier \(H=V_j^{\otimes n}\) with total Casimir \(C\), let \(\mu\) and \(\sigma^2\) be the mean and variance of \(\operatorname{spec}(C)\) under the normalized trace. The **moment selector** is

\[
K_{\mathrm{mom}}=\bigl(C-(\mu-\sigma)I\bigr)\bigl(C-(\mu+\sigma)I\bigr).
\]

It cuts whole Casimir sectors exactly when both \(\mu\pm\sigma\) are Casimir values. On the cube, \(\mu=18\), \(\sigma=12\), and \(K_{\mathrm{mom}}=(C-6I)(C-30I)=K\): this is T1, \(\Omega_c=\Pr[(C-\mu)^2=\sigma^2]\).

## Lemma — moments of a tensor power

\[
\mu=n\,j(j+1),\qquad \sigma^2=\frac{2n(n-1)}{3}\,\bigl[j(j+1)\bigr]^2 .
\]

*Proof.* \(C=\sum_i C_i+2\sum_{i<k}J^{(i)}\!\cdot J^{(k)}\). Each \(C_i\) is the scalar \(j(j+1)\). The pair terms are traceless and pairwise uncorrelated, and each has second moment \(\sum_a\bigl(\operatorname{tr}J_a^2/d\bigr)^2=[j(j+1)]^2/3\). ∎

So \(\sigma\) is rational only when \(2n(n-1)/3\) is a rational square: \(n=3,25,243,\dots\) Three factors are the first carriers on which the selector can land on the spectrum at all.

## Theorem — the Fibonacci–Lucas carriers

On \(V_j^{\otimes3}\), \(\mu=3j(j+1)\) and \(\sigma=2j(j+1)\), so

\[
\mu-\sigma=j(j+1),\qquad \mu+\sigma=5\,j(j+1).
\]

The lower root is always the \(J=j\) sector. The upper root is a Casimir value if and only if

\[
(2J+1)^2-5(2j+1)^2=-4,
\qquad\text{i.e.}\qquad
(2J+1,\;2j+1)=(L_k,\;F_k),\quad k\ \text{odd}.
\]

| \(k\) | \(2j+1=F_k\) | \(j\) | \(2J+1=L_k\) | \(J\) | \(\dim\ker K_{\mathrm{mom}}\,/\,\dim H\) |
|---:|---:|---:|---:|---:|---:|
| 3 | 2 | 1/2 | 4 | 3/2 | 8 / 8 (whole carrier) |
| **5** | **5** | **2** | **11** | **5** | **47 / 125** |
| 7 | 13 | 6 | 29 | 14 | 314 / 2197 |
| 9 | 34 | 33/2 | 76 | 75/2 | 2144 / 39304 |
| 11 | 89 | 44 | 199 | 99 | 14687 / 704969 |
| 13 | 233 | 116 | 521 | 260 | 100658 / 12649337 |

*Proof.* \(J(J+1)=5j(j+1)\) rearranges to \((2J+1)^2-5(2j+1)^2=-4\). Its positive solutions are the units of norm \(-1\) in \(\mathbb Z[\varphi]\), namely \(\varphi^k=\tfrac12(L_k+F_k\sqrt5)\) with \(k\) odd. Since \(F_k\equiv L_k \pmod 2\), \(J-3j\) is an integer. Since \(j<J\le 3j\), the sector occurs in \(V_j^{\otimes3}\) through \(V_{2j}\otimes V_j\). The validator confirms the "only if" direction exhaustively for \(2j\le400\). ∎

## Corollary — the cube is the first proper moment carrier

Spin \(1/2\) selects the whole carrier. Spin 2, with \(5=F_5\) and \(11=L_5\), is the first triple product on which the moment selector cuts a proper kernel. There it is \(K=(C-6I)(C-30I)\), with \(\dim\ker K=47\).

With the [Casimir census](E47_Casimir_Census_Theorem.md), the selection reads in two steps. The moment rule picks the cube among carriers. Inside the cube, \(\{2,5\}\) is the unique two-sector selection of dimension 47.

## Boundary

- The statement covers triple products \(V_j^{\otimes3}\). For \(n=25,243,\dots\), \(\sigma\) is rational and the question is open.
- The moment rule is a chosen selector. The theorem shows the carrier it forces, not that it is the only natural rule.
- The golden ratio enters through which carriers admit the rule, not through the value of \(\Omega_c\).
- No physical identification is claimed.

**One rule. One family. First proper member: 125 → 47.**
