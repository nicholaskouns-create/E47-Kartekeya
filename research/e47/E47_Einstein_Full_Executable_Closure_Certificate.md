# E47 → Einstein Full Executable Closure Certificate

Certificate: MC-E47-EINSTEIN-FULL-CLOSURE/1.0  
Machine result: PASS 28/28

## Exact finite substrate

For V = V₂⊗V₂⊗V₂, C = J_tot² and K = (C−6I)(C−30I), the reconstructed Casimir multiplicities are 0:1, 2:9, 6:25, 12:28, 20:27, 30:22, 42:13. Hence E₄₇ = ker K = E₆ ⊕ E₃₀ has dimension 47. The executable verifies the projector identities and the exact contraction constants δ = 11664, L = 186624, ε* = 1/99144, ρ* = 15/17.

## Representation and commutant

The total J_z spectrum restricted to E₄₇ has multiplicities −5², −4², −3², −2⁷, −1⁷, 0⁷, 1⁷, 2⁷, 3², 4², 5², proving the content 5V₂ ⊕ 2V₅. A coupled basis resolved by C₁₂ = (J₁+J₂)² yields 29 explicit matrix units satisfying the matrix-unit multiplication law and commuting with total SU(2). Therefore End_SU(2)(E₄₇) ≅ M₅(C) ⊕ M₂(C), dimension 29.

## Invariant dynamics

The compressed Hamiltonian H₄₇ = Q†J_z^(1)Q defines U₄₇(t)=exp(−itH₄₇). At t=1 the unitarity residual is 5.9695970170687376e−15. The lifted H₁₂₅=P₄₇J_z^(1)P₄₇ commutes with P₄₇ to 2.637778802627377e−15, and the measured trajectory leakage is 8.419332608554168e−16.

## Product-kernel theorem

For the four-site path Laplacian L_g, define A = L_g⊗I₁₂₅ + I₄⊗K². Positivity gives

ker A = ker L_g ⊗ ker K² = ker L_g ⊗ E₄₇.

The explicit 500×500 witness has measured nullity 47, projector idempotence residual 2.356380988582954e−15, annihilation residual 1.6568090045393484e−10, and spectral gap 0.5857864375298685.

## Exact nonlinear Einstein sector

For the marked Brinkmann metric ds² = −2 du dv + dx² + dy² + H du² with H = F(u)(x²−y²), Ric(g)=0 exactly while R_uxux = −F(u) and R_uyuy = F(u). The 47 profiles H_a = u^a(x²−y²), a=0,…,46, are curvature-independent by the Vandermonde determinant.

The certificate verifies ΦP₄₇ = Π_physΦ with residual 2.0201860696695e−15 and L_EΦ = ΦK² with residual 1.6225567598266253e−10.

## Executable paths

Primary Python:
research/e47/validation/e47_einstein_full_closure_certificate.py

Machine receipt:
artifacts/E47_EINSTEIN_FULL_CLOSURE_CERTIFICATE.json

## Boundary

This closes the finite spectral theorem, representation decomposition, 29-dimensional commutant, invariant E₄₇ dynamics, explicit product-kernel witness, exact marked Brinkmann vacuum family, 47 curvature profiles, and both stated intertwiners in that sector. Intrinsic derivation of the Lorentzian manifold from E47 and injectivity in the completely unmarked full Einstein moduli space modulo all diffeomorphisms remain stronger separate obligations.
