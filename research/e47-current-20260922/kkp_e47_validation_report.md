# KKP / E47 Python Validation Report

## Summary
- **PASS**: 34
- **FAIL**: 2
- **INFO**: 1
- **CONDITIONAL**: 1
- **NEEDS_INPUT_OR_EXPERIMENT**: 9

## Results
1. **PASS** — dim V = 5^3 = 125
   - computed: `125`
   - target: `125`
2. **PASS** — spec(C) = {0,2,6,12,20,30,42}
   - computed: `[0, 2, 6, 12, 20, 30, 42]`
   - target: `[0, 2, 6, 12, 20, 30, 42]`
3. **PASS** — Casimir eigenspace dimensions = [1,9,25,28,27,22,13]
   - computed: `[1, 9, 25, 28, 27, 22, 13]`
   - target: `[1, 9, 25, 28, 27, 22, 13]`
4. **PASS** — SU(2) irrep multiplicities J=0..6 = [1,3,5,4,3,2,1]
   - computed: `[1, 3, 5, 4, 3, 2, 1]`
   - target: `[1, 3, 5, 4, 3, 2, 1]`
5. **PASS** — K=(C-6I)(C-30I) is self-adjoint
   - computed: `0.0`
   - target: `0.0`
6. **PASS** — dim ker K = 47
   - computed: `47`
   - target: `47`
7. **PASS** — rank K = dim im K = 78
   - computed: `78`
   - target: `78`
8. **PASS** — Omega_c = 47/125 = 0.376
   - computed: `47/125 = 0.376000000000000`
   - target: `47/125 = 0.376`
9. **PASS** — ker K ≅ 5 V_2 ⊕ 2 V_5
   - computed: `5 V_2 + 2 V_5`
   - target: `5 V_2 + 2 V_5`
10. **PASS** — P_47 is an orthogonal projector
   - computed: `3.517770542025983e-14`
   - target: `<1e-10`
11. **PASS** — K P_47 = 0
   - computed: `1.5084648494913136e-11`
   - target: `<1e-9`
12. **PASS** — tr(P_47)=rank(P_47)=47
   - computed: `{'trace': np.float64(46.99999999999987), 'rank': 47}`
   - target: `47`
13. **PASS** — positive spectrum(K^2) = {11664,12544,19600,32400,186624}
   - computed: `[11664, 12544, 19600, 32400, 186624]`
   - target: `[11664, 12544, 19600, 32400, 186624]`
14. **PASS** — spectral gap Δ = 11664
   - computed: `11664`
   - target: `11664`
15. **PASS** — ||K^2|| = 186624
   - computed: `186624`
   - target: `186624`
16. **PASS** — stability interval 0<ε<2/||K^2|| = 1/93312
   - computed: `1/93312`
   - target: `1/93312`
17. **PASS** — optimal ε* = 1/99144
   - computed: `1/99144`
   - target: `1/99144`
18. **PASS** — optimal transverse contraction ρ*=15/17
   - computed: `15/17`
   - target: `15/17`
19. **PASS** — Γ^220 ≈ P_47 for Γ=I-ε*K^2, ε*=1/99144
   - computed: `1.1344513014760442e-12`
   - target: `<1e-10`
20. **PASS** — A5 character of ker K on [e,5A,5B,3A,2A] = [47,2,2,-7,3]
   - computed: `[47, 2, 2, -7, 3]`
   - target: `[47, 2, 2, -7, 3]`
21. **PASS** — A5 decomposition ker K = 2T1 ⊕ 2T2 ⊕ 7H
   - computed: `{'1': '0', 'T1': '2', 'T2': '2', 'G': '0', 'H': '7'}`
   - target: `{'1': '0', 'T1': '2', 'T2': '2', 'G': '0', 'H': '7'}`
22. **PASS** — 1 + 2 cos(2π/5) = φ
   - computed: `1/2 + sqrt(5)/2`
   - target: `1/2 + sqrt(5)/2`
23. **PASS** — Γ_P=(1-Ωc)I+ΩcP has eigenvalues {78/125,1}
   - computed: `[np.float64(0.624), np.float64(1.0)]`
   - target: `[0.624, 1.0]`
24. **PASS** — scalar overlap recursion p_n=1-(1-p0)(1-Ωc)^n exceeds 99% by n=10 for p0=Ωc
   - computed: `0.9944149060052163`
   - target: `>0.99`
25. **PASS** — Babylonian map R(x)=1/2(x+τ/x) fixes x*=sqrt(τ)
   - computed: `sqrt(tau)`
   - target: `sqrt(tau)`
26. **PASS** — Babylonian map has quadratic local convergence: R'(sqrt τ)=0
   - computed: `0`
   - target: `0`
27. **PASS** — R''(sqrt τ)=1/sqrt(τ)
   - computed: `1/sqrt(tau)`
   - target: `1/sqrt(tau)`
28. **FAIL** — Claim Ωc = φ^-5
   - computed: `{'47/125': 0.376, 'phi^-5': 0.09016994374947422}`
   - target: `equality`
29. **INFO** — Exponent n solving φ^-n = 47/125
   - computed: `2.0327142531692477`
   - target: `not an integer; ≈2.0323`
30. **PASS** — Fibonacci recurrence has dominant eigenvalue φ
   - computed: `['1/2 - sqrt(5)/2', '1/2 + sqrt(5)/2']`
   - target: `1/2 + sqrt(5)/2`
31. **PASS** — x^2-x-1 roots are {φ,-1/φ}
   - computed: `['1/2 - sqrt(5)/2', '1/2 + sqrt(5)/2']`
   - target: `['1/2 + sqrt(5)/2', '-1/(1/2 + sqrt(5)/2)']`
32. **PASS** — V(Ω)=Λ/4(Ω^2-Ωc^2)^2 gives dV/dΩ=ΛΩ(Ω^2-Ωc^2)
   - computed: `Lambda*Omega*(Omega - Omega_c)*(Omega + Omega_c)`
   - target: `Lambda*Omega*(Omega^2-Omega_c^2)`
33. **PASS** — Displayed recursive mass term has ∂M/∂Ω = 0 if N,χ are Ω-independent
   - computed: `0`
   - target: `0`
34. **FAIL** — Displayed Ω field equation from the shown Lagrangian has no mass-source RHS unless N(Ω) or χ(Ω) is supplied
   - computed: `RHS = ∂M/∂Ω = 0 with the displayed definitions`
   - target: `nonzero mass-source requires additional Ω dependence`
   - note: This is a structural test of the formula as printed, not of a modified model with N(Ω) or χ(Ω).
35. **CONDITIONAL** — m_eff = m_static(1-Ω)
   - computed: `internally consistent as a constitutive definition`
   - target: `derivation from displayed Lagrangian`
   - note: The displayed Lagrangian does not contain this coupling explicitly.
36. **PASS** — For PSD K_A,K_B,K_C: ker(K_A+K_B+K_C)=ker K_A ∩ ker K_B ∩ ker K_C
   - computed: `{'common_nullity': np.int64(2), 'individual_nullities': [np.int64(2), np.int64(2), np.int64(2)]}`
   - target: `2`
   - note: General proof: x*(ΣK_i)x=Σ x*K_i x=0; PSD makes each term ≥0, hence each K_i^{1/2}x=0.
37. **PASS** — 1+3+12+20+42 = 78
   - computed: `78`
   - target: `78`
   - note: Arithmetic match only; it is not by itself a representation-theoretic derivation.
38. **PASS** — 1/φ ≈ 0.618
   - computed: `0.6180339887498948`
   - target: `0.6180339887498948`
39. **NEEDS_INPUT_OR_EXPERIMENT** — Collider resonance signatures / exact TeV targets
   - note: Requires a fully specified interaction Hamiltonian/cross section and collider data.
40. **NEEDS_INPUT_OR_EXPERIMENT** — Vacuum interferometer phase shift
   - note: The formula can be simulated, but physical truth requires measured phase data and calibrated apparatus parameters.
41. **NEEDS_INPUT_OR_EXPERIMENT** — PCO resonator inertial-mass variation
   - note: Requires measured mass/inertia response; no computation alone establishes the effect.
42. **NEEDS_INPUT_OR_EXPERIMENT** — Metric-propulsion thrust
   - note: Requires a covariant stress-energy/metric solution and thrust data; the displayed proportionality is a prediction, not a proof.
43. **NEEDS_INPUT_OR_EXPERIMENT** — Exact particle mass spectrum
   - note: Requires the complete (N,chi) assignments and comparison dataset; the plate alone is insufficient.
44. **NEEDS_INPUT_OR_EXPERIMENT** — Pyramid tangency K_p=phi
   - note: Exact tangency equations/coordinates are not included in the supplied plate.
45. **NEEDS_INPUT_OR_EXPERIMENT** — Lindblad fidelity 0.9997 for four initial states
   - note: Needs the explicit Hamiltonian, collapse operators, rates, time grid, and four initial states.
46. **NEEDS_INPUT_OR_EXPERIMENT** — 13-pillar post-quantum security
   - note: Functional code can be tested, but cryptographic security needs a precise adversary model and a reduction/proof or empirical cryptanalysis.
47. **NEEDS_INPUT_OR_EXPERIMENT** — E47 implies Einstein geometry / propulsion
   - note: Needs an explicit map from E47 states to a spacetime metric/stress tensor, then curvature and Einstein-residual computation.