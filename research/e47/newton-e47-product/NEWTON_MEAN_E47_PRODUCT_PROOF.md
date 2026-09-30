# Newton–Mean × E47 Product-Kernel Invariant

Certificate: `MC-E47-NEWTON-MEAN-PRODUCT-20260930-001` · **24/24 PASS**

For `F_NM(z,psi)=(T(z),Gamma* psi)`, with `Gamma*=I-K^2/99144`,
the fixed manifold is `A47={z*} x E47`. At a Newton–Mean fixed point,

`D F_NM ~ 0 ⊕ tau ⊕ I_47 ⊕ Gamma*|_78`.

Therefore the transverse asymptotic rate is

`r_joint=max(|tau|,15/17)`,

and the rate-resonance surface is `|tau(a,b,kappa)|=15/17`.

Deterministic witness `(a,b,kappa)=(4,9,0.5)`: `tau=0.509893953950370 < 15/17`, so the E47 complement controls the asymptotic rate.

The finite-dimensional quantum simulation validates the CPTP block-dephasing completion `D_P(rho)=P rho P+Q rho Q`, including Kraus completeness, trace preservation, positivity, cross-block removal, and E47-state invariance. It does not claim that the nonlinear Newton map is itself a physical quantum channel or that quantum hardware was executed.

Numeric highlights: rank P=47, rank Q=78; rho(Gamma*|Q)=0.882352941176472; scalar quadratic residual 1.110e-16; product fixed-map residual 3.508e-16; product-kernel residual 1.635e-13.
