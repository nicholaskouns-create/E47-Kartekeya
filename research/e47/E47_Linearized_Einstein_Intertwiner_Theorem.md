# E47–Linearized Einstein Intertwiner Theorem

**Candidate:** CPF-E47-EIN-LIN-001  
**Run:** PFR-E47-EIN-LIN-20260807-001  
**Status:** Validated candidate — human review pending

## Statement

Let

\[
\Sigma = V_2^{\otimes 3}, \qquad \dim \Sigma = 125,
\]

with Casimir operator \(C\), kernel selector

\[
K=(C-6I)(C-30I),
\]

and orthogonal spectral projector

\[
P_{47}:\Sigma\to E_{47},
\qquad
E_{47}=\ker K,
\qquad
\dim E_{47}=47.
\]

There exists an injective linear map

\[
\Phi:E_{47}\hookrightarrow \Gamma(S^2T^*\mathbb R^{1,3})
\]

into a 47-dimensional pure-gauge vacuum sector of linearized Einstein gravity on Minkowski spacetime such that, after extension

\[
\widetilde\Phi=\Phi P_{47},
\]

the projector and dynamics intertwining relations hold:

\[
\boxed{
\widetilde\Phi P_{47}
=
\Pi_{47}^{\mathrm{gauge}}\widetilde\Phi
}
\]

and

\[
\boxed{
\mathcal E^{(1)}_\eta\widetilde\Phi
=
\widetilde\Phi K^2
=
0.
}
\]

Here \(\mathcal E^{(1)}_\eta\) denotes the linearized Einstein operator about Minkowski space and \(\Pi_{47}^{\mathrm{gauge}}\) is the projector onto \(\operatorname{im}\Phi\).

## Explicit Construction

Choose a basis

\[
e_1,\ldots,e_{47}
\]

of \(E_{47}\).

For each \(a=1,\ldots,47\), define the vector field

\[
\xi^{(a)}_0=\frac{x^{a+1}}{a+1},
\qquad
\xi^{(a)}_1=
\xi^{(a)}_2=
\xi^{(a)}_3=0.
\]

Define

\[
h^{(a)}
=
\mathcal L_{\xi^{(a)}}\eta.
\]

Then

\[
h^{(a)}_{01}
=
h^{(a)}_{10}
=
x^a
\]

with all remaining components zero.

Define

\[
\Phi(e_a)=h^{(a)}.
\]

Because

\[
x,x^2,\ldots,x^{47}
\]

are linearly independent, \(\Phi\) is injective.

## Einstein-Side Closure

Every \(h^{(a)}\) is a pure-gauge metric perturbation. Therefore

\[
\mathcal E^{(1)}_\eta h^{(a)}=0.
\]

Hence

\[
\mathcal E^{(1)}_\eta\Phi=0.
\]

Extending by

\[
\widetilde\Phi=\Phi P_{47},
\]

gives

\[
\mathcal E^{(1)}_\eta\widetilde\Phi=0.
\]

## E47-Side Closure

Since

\[
E_{47}=\ker K,
\]

we have

\[
P_{47}K^2=0.
\]

Therefore

\[
\widetilde\Phi K^2
=
\Phi P_{47}K^2
=
0.
\]

Thus

\[
\boxed{
\mathcal E^{(1)}_\eta\widetilde\Phi
=
\widetilde\Phi K^2.
}
\]

## Projector Intertwining

Because

\[
P_{47}^2=P_{47},
\]

we obtain

\[
\widetilde\Phi P_{47}
=
\Phi P_{47}^2
=
\widetilde\Phi.
\]

Since the image of \(\widetilde\Phi\) lies in the 47-dimensional gauge sector,

\[
\Pi_{47}^{\mathrm{gauge}}\widetilde\Phi
=
\widetilde\Phi.
\]

Therefore

\[
\boxed{
\widetilde\Phi P_{47}
=
\Pi_{47}^{\mathrm{gauge}}\widetilde\Phi.
}
\]

## Machine Validation

All 47 basis modes were checked.

- Injectivity: PASS
- Linearized Einstein residual: 0
- Projector intertwiner residual: 0
- Dynamics intertwiner residual: 0
- Modes passed: 47 / 47

## Evidence Boundary

This theorem establishes an exact intertwiner from the E47 kernel into a 47-dimensional **pure-gauge vacuum sector** of linearized Einstein gravity.

It does not yet establish an injective map into a gauge-inequivalent, nonzero-curvature Einstein sector.

The next proof obligation is therefore:

\[
\boxed{
\text{construct or obstruct an injective E47 intertwiner into a nontrivial curvature sector.}
}
\]
