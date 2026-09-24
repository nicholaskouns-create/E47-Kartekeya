# E47 Casimir-Spectral Lorentzian Signature

**Citizen:** `E47-LOR-SIG-C01`  
**Machine certificate:** `MC-E47-CASIMIR-LOR-SIGNATURE-20260924`  
**Validator:** `research/e47/validation/e47_casimir_lorentzian_signature.py`  
**Result:** **12/12 PASS**

Let (C=J_{\rm tot}^2) on (V_2^{\otimes3}), and let (P_0,P_6) be the spectral projectors of (C) onto eigenvalues (0) and (6). Define

[
\eta=P_6-P_0.
]

For the unique unit (u\in E_0) and the three orbit tangent vectors (s_i\in W\subset E_6),

[
P_0u=u,qquad P_6u=0,qquad P_6s_i=s_i,qquad P_0s_i=0.
]

The explicit (125\times125) restriction gives

[
[g]_{\{u,s_1,s_2,s_3\}}
=
\operatorname{diag}(-1,2,8,2),
]

with eigenvalues ((-1,2,2,8)), hence

[
\operatorname{sig}(g)=(-,+,+,+).
]

The projectors are polynomials in the original Casimir:

[
P_0=
\frac{(C-2I)(C-6I)(C-12I)(C-20I)(C-30I)(C-42I)}
{3628800},
]

[
P_6=
\frac{C(C-2I)(C-12I)(C-20I)(C-30I)(C-42I)}
{1741824}.
]

The Python witness reconstructs the full carrier, both projectors, the selected (E_6) copy, the (SO(3))-orbit tangent frame, and the four-dimensional pullback directly.
