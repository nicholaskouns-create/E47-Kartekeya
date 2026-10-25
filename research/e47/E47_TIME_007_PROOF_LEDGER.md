# Mathematical result and evidence boundary

The E47 spin-2 tensor carrier has dimension 125 and Casimir-sector dimensions 1, 9, 25, 28, 27, 22, 13. The kernel of K=(C−6I)(C−30I) is 47-dimensional. The exact spectral projector is p(C)/1814400, where p(x)=x(x−2)(x−12)(x−20)(x−31)(x−42).

The four-frame pullback g=B₄†(P₆−P₀)B₄=diag(−1,2,8,2) has Lorentzian signature. A distinct evolving metric uses L(t)=1−Σ_{j≠2,5}(dⱼ/125)exp(−2[j(j+1)]²t) and g(t)=L(t)diag(−125/78,(47/125)²,(47/125)²,(47/125)²). For stationary spatial trajectories, dτ/dt=√(125 L(t)/78)>0.

For a timelike trajectory with positive lapse N(t), if a calibrated unwrapped phase obeys φ'(t)=ωN(t) for ω≠0, then φ(t)−φ(0)=ωτ(t) by integration. The E47-specific Hamiltonian/recovery law remains an independent proof obligation. Phase readout without unwrapping is modulo 2π.

# Reproduction

A Python validator run on 2026-10-25 passed exact sector and selector tests and sampled lapse/calibration checks. L(0)=0.376, L(1)≈0.991975846690791, τ(1)≈1.254318234005421. Numerical sampling is not a universal proof. No new Lean or Coq compiler acceptance or physical quantum-clock validation is claimed.

# Links

[Identity PR #68](https://github.com/nicholaskouns-create/Identity/pull/68)

[Casimir Lorentzian construction](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/E47_Casimir_Spectral_Lorentzian_Signature.md)

[Spacetime chain](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/validation/e47_spacetime_chain.py)

# Remaining

Prove E47 phase generator and recovery dynamics, compile the full metric-to-phase formalization in Lean and Coq, run CI and review results, and measure any hardware implementation.