# E47 → Gauge-Inequivalent Einstein Geometry

**Obligation:** E47-EIN-PHYS-001  
**Decision:** Outcome 3 — conditional construction  
**Status:** CONDITIONAL PASS  
**Scope:** exact finite E47 algebra + theorem-level conditional nonlinear Einstein construction

## 1. E47 side

Let
[
V=V_2^{\otimes 3},\qquad
K=(C-6I)(C-30I),\qquad
E_{47}=\ker K=\operatorname{Ran}P_{47}.
]

The canonical finite construction gives
[
\dim V=125,\qquad \dim E_{47}=47,
]
and therefore
[
K^2|_{E_{47}}=0.
]

## 2. Declared Einstein-side structure

Let (g_0) be a vacuum Einstein background for which the gauge-reduced Einstein solution space is locally a smooth manifold at ([g_0]). A standard sufficient setting is a linearization-stable globally hyperbolic vacuum spacetime with compact CMC Cauchy surface and no Killing fields.

Assume its physical tangent space contains a 47-dimensional subspace
[
W_{47}\subset
T_{[g_0]}(\mathcal M_{\rm Einstein}/\mathrm{Diff})
]
such that the gauge-invariant linearized curvature map is injective on (W_{47}):
[
R^{(1)}|_{W_{47}}\text{ is injective}.
]

These are explicit additional geometric hypotheses. They are not inferred from E47 and are not numerically certified by the finite Python validator.

## 3. Conditional nonlinear construction

Choose a linear isomorphism
[
A:E_{47}\xrightarrow{\sim}W_{47}.
]

Because the gauge-reduced exact Einstein solution space is, by hypothesis, locally a smooth manifold at ([g_0]), choose a chart
[
\chi:U_0\subset
T_{[g_0]}(\mathcal M_{\rm Einstein}/\mathrm{Diff})
\to
\mathcal M_{\rm Einstein}/\mathrm{Diff}
]
with
[
\chi(0)=[g_0],\qquad D\chi_0=I.
]

For sufficiently small (U\subset E_{47}) with (A(U)\subset U_0), define
[
\boxed{
F_{\rm phys}(u)=\chi(Au).
}
]

Since (A) is injective and (\chi) is a local chart,
[
\boxed{
F_{\rm phys}:U\hookrightarrow
\mathcal M_{\rm Einstein}/\mathrm{Diff}
}
]
is locally injective. Every point in its image is an equivalence class of an exact nonlinear Einstein geometry.

Its derivative at the base point is
[
\Phi_{\rm phys}:=DF_{\rm phys}|_0=A,
]
so
[
\operatorname{rank}\Phi_{\rm phys}=47.
]

## 4. Projector and operator intertwining

Let (\Pi_{\rm phys}) denote the projection to the declared physical gauge slice. Since the image of (A) lies in (W_{47}),
[
\Pi_{\rm phys}\Phi_{\rm phys}=\Phi_{\rm phys}.
]
Because (P_{47}) is the identity on (E_{47}),
[
\boxed{
\Phi_{\rm phys}P_{47}
=
\Pi_{\rm phys}\Phi_{\rm phys}.
}
]

Let
[
\mathcal L_E=D\mathcal E_{g_0}
]
be the gauge-fixed linearized Einstein operator. Tangent vectors to the exact Einstein solution manifold satisfy
[
\mathcal L_E A u=0.
]
On the E47 side,
[
K^2u=0\qquad(u\in E_{47}).
]
Hence
[
\boxed{
\mathcal L_E\Phi_{\rm phys}
=
\Phi_{\rm phys}K^2
=
0
\quad\text{on }E_{47}.
}
]

## 5. Gauge-inequivalent nontriviality

For every nonzero (u\in E_{47}),
[
Au\neq0.
]
By the declared curvature-injectivity hypothesis,
[
\boxed{
R^{(1)}[\Phi_{\rm phys}u]\neq0
\qquad(u\neq0).
}
]
Thus no nonzero E47 direction maps to a pure-gauge tangent direction.

## 6. Decision

This is **Outcome 3: Conditional construction**.

The construction is exact once the following additional structure is supplied:

1. an exact vacuum Einstein background (g_0);
2. local smoothness / linearization stability of the gauge-reduced Einstein solution space at ([g_0]);
3. a 47-dimensional physical tangent subspace (W_{47});
4. injectivity of a gauge-invariant curvature observable on (W_{47}).

The finite E47 side and the algebraic intertwining consequences are machine-checkable. The geometric hypotheses remain explicit theorem gates until an explicit background and 47-mode basis are supplied.

## 7. Retained failed predecessor

The earlier pure-gauge construction remains part of the record:

- algebraic intertwiner residual: 0;
- linearized Einstein residual: 0;
- curvature nontriviality: FAIL;
- rank after gauge quotient: 0/47;
- obstruction: image lies in the pure-gauge orbit.

That failure is not erased by this conditional construction.

## 8. Machine paths

Primary reconstruction:
`research/e47/validation/e47_einstein_conditional_validation.py`

Independent City parity reconstruction:
`city/parity/e47_einstein_parity.py`

The two implementations use different SU(2) counting routes and compare only at the resulting invariants.
