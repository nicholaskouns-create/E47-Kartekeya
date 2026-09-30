# E47 Canonical 47-Face Dual Crystal

Certificate: `MC-E47-CANONICAL-47FACE-CRYSTAL-20260930-001`  
Status: **PASS · 21/21 checks**

## Construction

The carrier is \(\mathcal H=V_2^{\otimes 3}\), with total Casimir \(C=\mathbf J^2\) and selector

\[
K=(C-6I)(C-30I),\qquad E_{47}=\ker K.
\]

Fix the coupling tree

\[
((V_2\otimes V_2)\to j_{12})\otimes V_2\to J
\]

and the standard Condon–Shortley Clebsch–Gordan phase convention. The simultaneous labels \((J,j_{12},m)\) resolve all 47 basis states:

\[
\mathcal B_{47}=
\{|2,j_{12},m\rangle:j_{12}=0,1,2,3,4;\ m=-2,\ldots,2\}
\cup
\{|5,j_{12},m\rangle:j_{12}=3,4;\ m=-5,\ldots,5\}.
\]

Thus \(25+22=47\).

A deterministic label-derived map sends each coupled state to a unique unit normal \(n_a\in S^2\). The polar dual is

\[
\mathcal C_{47}=\{x\in\mathbb R^3:n_a\cdot x\le 1,\ a=1,\ldots,47\}.
\]

Because all 47 spherical points are exposed vertices and the origin lies strictly inside their convex hull, the polar dual has exactly 47 facets, with exact correspondence

\[
F_a\longleftrightarrow |J_a,j_{12,a},m_a\rangle.
\]

## Validation

- coupled-basis orthonormality residual: `9.024e-16`
- total-Casimir eigenlabel residual: `1.526e-14`
- intermediate-Casimir eigenlabel residual: `1.184e-14`
- selector annihilation residual: `2.036e-13`
- facet-plane residual: `3.331e-16`
- primal hull vertices: `47`
- dual topology: `V=90, E=135, F=47`, so `V-E+F=2`
- face-size histogram: `3×4-gon, 14×5-gon, 23×6-gon, 6×7-gon, 1×8-gon`

## Evidence boundary

The coupled basis is canonical after fixing the coupling tree, phase convention, product-basis ordering, and facet ordering. The 3D spherical embedding is a deterministic canonicalization convention and is **not** claimed to be the unique Euclidean embedding forced by SU(2). The exact invariant content is the one-to-one mapping between the 47 resolved E47 channels and the 47 dual facets.

Evidence class: **E0 exact finite representation labels + E1 deterministic Python reconstruction**. No physical crystal, optical device, materials realization, or empirical hardware performance claim is promoted by this certificate.