# E47 Condition Lock

**Certificate:** `MC-E47-CONDITION-LOCK/1.0` · 25/25 PASS
**Executable:** [`validation/e47_condition_lock_certificate.py`](validation/e47_condition_lock_certificate.py)
**Record:** [`artifacts/E47_CONDITION_LOCK_CERTIFICATE.json`](../../artifacts/E47_CONDITION_LOCK_CERTIFICATE.json)
**Evidence:** exact rational arithmetic, replayed in float64 on the 125 × 125 carrier.

This note sharpens the existing contraction theorem (step \(\varepsilon_*=1/99144\), rate \(\rho_*=15/17\)). It explains where those constants come from, proves they are optimal, and shows the projector is reached exactly in five steps.

## Setting

On \(V_2\otimes V_2\otimes V_2\), \(C=(J_1+J_2+J_3)^2\) has eigenvalues \(c=j(j+1)\in\{0,2,6,12,20,30,42\}\) with multiplicities \(1,9,25,28,27,22,13\). Let \(K=(C-6I)(C-30I)\), \(E_{47}=\ker K\), and let \(P\) be its orthogonal projector.

## Sector values

\(K\) acts on each Casimir sector by the integer \(k_c=(c-6)(c-30)\):

| \(c\) | 0 | 2 | 6 | 12 | 20 | 30 | 42 |
|---|---:|---:|---:|---:|---:|---:|---:|
| \(k_c\) | 180 | 112 | 0 | −108 | −140 | 0 | 432 |

Every statement below follows from this row.

## Theorem 1 — Condition-4 lock

On \(E_{47}^\perp\), \(|K|\) takes the values \(\{108,112,140,180,432\}\). Hence

\[
\kappa(K|_{E^\perp})=\frac{432}{108}=4,\qquad \kappa(K^2|_{E^\perp})=16 .
\]

## Theorem 2 — Two integers fix every constant

With \(\delta=108^2\) and \(L=16\cdot108^2\),

\[
\delta=11664,\quad L=186624,\quad \varepsilon_*=\frac{2}{\delta+L}=\frac{2}{108^2\cdot17}=\frac1{99144},\quad
\rho_*=\frac{\kappa-1}{\kappa+1}=\frac{15}{17}.
\]

The 17 is \(1+\kappa\).

## Theorem 3 — Equioscillation (optimality)

\(\Gamma_*=I-\varepsilon_*K^2\) takes the values \(1-\varepsilon_*\lambda\) on \(E^\perp\), with extremes exactly \(-15/17\) (at \(\lambda=L\)) and \(+15/17\) (at \(\lambda=\delta\)). A constant step \(\varepsilon\) has rate \(\max(|1-\varepsilon\delta|,|1-\varepsilon L|)\), and the two ends balance only at \(\varepsilon_*\). So \(15/17\) is the best rate any constant-step iteration can reach.

## Theorem 4 — Five-factor exact projector

\[
P=\prod_{\lambda\in\{108^2,\,112^2,\,140^2,\,180^2,\,432^2\}}\left(I-\frac{K^2}{\lambda}\right).
\]

Each factor is \(1\) on \(E_{47}\), and each nonzero eigenvalue of \(K^2\) is annihilated by its own factor. \(\Gamma_*\) is the constant-step relaxation of this finite product.

## Theorem 5 — Five-step termination

\(K^2|_{E^\perp}\) has exactly five distinct eigenvalues, so every Krylov space \(\operatorname{span}\{(K^2)^i(I-P)b\}\) has dimension at most 5. Constructively, five Richardson steps with steps \(1/\lambda_i\) take any \(b\) to \(Pb\) exactly: \(x_{i+1}=x_i-K^2x_i/\lambda_i\), \(x_5=Pb\).

## Theorem 6 — Chebyshev rate 3/5

If only the interval \([\delta,L]\) is used, the degree-\(n\) Chebyshev polynomial \(p_n\) with \(p_n(0)=1\) gives

\[
\|p_n(K^2)(I-P)\|\le\frac1{T_n(17/15)}=\frac{2}{(5/3)^n+(3/5)^n},
\]

which is asymptotically \((3/5)^n\), where \(3/5=(\sqrt\kappa-1)/(\sqrt\kappa+1)\). For \(n\ge2\) this is strictly below \((15/17)^n\).

## Corollaries

- **K inertia \((23,55,47)\).** \(K>0\) on \(c\in\{0,2,42\}\) (dimensions \(1+9+13\)), \(K<0\) on \(c\in\{12,20\}\) (\(28+27\)), and \(K=0\) on \(E_{47}\).
- **Krein compatibility.** \(\Gamma_*\) commutes with \(\eta=2P-I\), so it preserves \(E_{47}\) and \(E_{47}^\perp\), the positive and negative subspaces of the signature-\((47,78)\) Krein form. It is not an isometry of that form: \(\Gamma_*^\dagger\eta\Gamma_*=\eta\Gamma_*^2\neq\eta\). See [E47 signature and symmetry](E47_Signature_Symmetry_Theorem.md), Theorem 6.

## Boundary

These are finite spectral statements about the fixed 125-dimensional carrier. They add no physical claim.
