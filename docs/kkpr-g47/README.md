# KKP-R · G47 · Algebraic Core — exact basis and dynamics

Published: 2026-11-23. Attribution: Nicholas Shane Kouns / AIMS Research Institute.

## Evidence status

- **Exactly checked in Python/SymPy (local execution):** 125×47 integer matrix built from seven corrected highest-weight seeds; five spin-2 chains and two spin-5 chains; \(CU=U\operatorname{diag}(6I_{25},30I_{22})\), \(KU=0\); full rank 47 over \(\mathbb Q\) certified by modular rank 47 over \(\mathbb F_{101}\).
- **Symbolically derived:** 5-cycle Laplacian eigenvalues and ratio; fixed-source exact contraction solution and error formula.
- **Conditional:** variable-source perturbation bound and Bianchi defect estimate under specified bounded-coefficient and derivative hypotheses.
- **Not certified in this publication:** compilation of the user-supplied Lean 4 or Coq extensions; a full tensorial Bianchi limit derived solely from scalar fixed-point convergence; and a machine-checked 47×47 Gram determinant. The Gram determinant is nonzero as a mathematical consequence of the verified modular rank, not because a determinant was directly evaluated.

## Carrier and kernel

\(H=V_2^{\otimes3},\;\dim H=125,\;C=J_+J_-+J_z^2-J_z,\;K=(C-6I)(C-30I).\)

\(V_2^{\otimes3}\cong V_0\oplus3V_1\oplus5V_2\oplus4V_3\oplus3V_4\oplus2V_5\oplus V_6.\)

\(E_{47}=\ker K=5V_2\oplus2V_5,\quad\Omega_c=47/125.\)

A 0-based tensor index is \(i=25a+5b+c\), where \((a,b,c)\in\{0,1,2,3,4\}^3\) and \(m_z=6-a-b-c\). The attached Python source gives an exact **integer, nonorthonormal** basis \(U\in\mathbb Z^{125\times47}\). For each highest weight \(v\), columns are \(v,J_-v,\dots,J_-^{2j}v\).

### Corrected highest-weight seeds

Each pair below is `(zero_based_flat_index, integer_coefficient)`:

```json
{
  "j2": [
    [
      [
        4,
        1
      ],
      [
        8,
        -4
      ],
      [
        12,
        24
      ],
      [
        16,
        -4
      ],
      [
        20,
        1
      ]
    ],
    [
      [
        4,
        1
      ],
      [
        8,
        -3
      ],
      [
        12,
        12
      ],
      [
        16,
        -1
      ],
      [
        28,
        -1
      ],
      [
        32,
        6
      ],
      [
        36,
        -6
      ],
      [
        40,
        1
      ]
    ],
    [
      [
        4,
        1
      ],
      [
        8,
        -2
      ],
      [
        12,
        4
      ],
      [
        28,
        -2
      ],
      [
        32,
        8
      ],
      [
        36,
        -4
      ],
      [
        52,
        4
      ],
      [
        56,
        -4
      ],
      [
        60,
        4
      ]
    ],
    [
      [
        4,
        1
      ],
      [
        8,
        -1
      ],
      [
        28,
        -3
      ],
      [
        32,
        6
      ],
      [
        52,
        12
      ],
      [
        56,
        -6
      ],
      [
        76,
        -1
      ],
      [
        80,
        1
      ]
    ],
    [
      [
        4,
        1
      ],
      [
        28,
        -4
      ],
      [
        52,
        24
      ],
      [
        76,
        -4
      ],
      [
        100,
        1
      ]
    ]
  ],
  "j5": [
    [
      [
        1,
        -1
      ],
      [
        5,
        1
      ]
    ],
    [
      [
        1,
        -1
      ],
      [
        25,
        1
      ]
    ]
  ]
}
```

These replace the originally supplied seeds, several of which had the wrong \(J_z\) weight and failed the claimed eigenvalue identities.

\[
CU=U\begin{pmatrix}6I_{25}&0\\0&30I_{22}\end{pmatrix},\quad KU=0,\quad\operatorname{rank}_{\mathbb F_{101}}(U\bmod101)=47.
\]

Since a nonzero minor mod 101 remains nonzero over \(\mathbb Q\), \(\operatorname{rank}_{\mathbb Q}U=47\); consequently \(U^TU\) is invertible and \(P_{47}=U(U^TU)^{-1}U^T\) is the orthogonal projector onto \(E_{47}\).

## Golden-ratio and Laplacian layer

\(L_5=2I-S-S^{-1}\), and
\[
\operatorname{spec}(L_5)=\{0^{(1)},[(5-\sqrt5)/2]^{(2)},[(5+\sqrt5)/2]^{(2)}\}.
\]
\(\lambda_-/\lambda_+=\varphi^{-2}=(3-\sqrt5)/2\),
\(a_{\rm KKP}=\Omega_c\varphi^{-2}=(141-47\sqrt5)/250\).

## Recursive stabilization

For \(0<\alpha=\varphi^{-1}<2/3\) and stationary source \(\delta_*\):
\[
\psi_{n+1}=\alpha\psi_n+\Omega_c\delta_*,\quad
\psi_*=\Omega_c\varphi^2\delta_*,\quad
\psi_n-\psi_*=\alpha^n(\psi_0-\psi_*).
\]
Hence \(|\psi_n-\psi_*|=\varphi^{-n}|\psi_0-\psi_*|\le(2/3)^n|\psi_0-\psi_*|\).

For nonstationary \(\delta_k\):
\[
|e_n|\le\alpha^n|e_0|+\Omega_c\sum_{k=0}^{n-1}\alpha^{n-1-k}|\delta_k-\delta_*|.
\]
In particular, bounded source perturbations that converge to zero imply \(e_n\to0\) by geometric-kernel convolution.

## Field equation and Bianchi identity

If \(F_0\ne0\) and \(F_0G_{\mu\nu}=\kappa_0T_{\mu\nu}-\kappa_0V_0g_{\mu\nu}\), define
\(\kappa_{\rm eff}=\kappa_0/F_0\), \(\Lambda_{\rm eff}=\kappa_0V_0/F_0\).
Then \(G_{\mu\nu}+\Lambda_{\rm eff}g_{\mu\nu}=\kappa_{\rm eff}T_{\mu\nu}\).
Metric compatibility and contracted Bianchi give
\[
\nabla^\mu(\kappa_{\rm eff}T_{\mu\nu})=\partial_\nu\Lambda_{\rm eff}.
\]
When both coefficients are constant and \(\kappa_{\rm eff}\ne0\), \(\nabla^\mu T_{\mu\nu}=0\).

The **scalar surrogate** \(D=(F'G_{\rm norm}+\kappa_0V'+h)\nabla\psi\) obeys \(|D|\le\epsilon\) whenever \(|\nabla\psi|\le\epsilon\) and the absolute value of its parenthesized coefficient is at most 1. To prove a **tensorial** \(D^{\rm KKP}_\mu\to0\), also establish gradient/Hessian convergence and the relevant field equations, not only the scalar recurrence.

## Formal modules: proof obligations

Lean 4 / Coq proof obligations (not presently compiler-attested here):
1. Concrete indexed construction of \(J_\pm,J_z,C,U\); exact 47 column eigenvalue identities.
2. Modular rank witness 47 over \(\mathbb F_{101}\), then full rank over \(\mathbb Q\).
3. Orthogonal projector identity and matrix-kernel equivalence.
4. Stationary affine recurrence; nonstationary geometric convolution; convergence.
5. Covariant Bianchi conservation with stated regularity and coefficient hypotheses.

Source verifier: [`kkpr_g47_exact_basis.py`](./kkpr_g47_exact_basis.py). Public live [GitHub Pages explainer](https://nicholaskouns-create.github.io/Identity/kkpr-g47/).
