# E47 harmonic-polynomial realization: E0–E4 validation

Nicholas Shane Kouns · 17 October 2026

The level definitions here are explicit for this validation: E0 mathematical proof; E1 exact computation; E2 numerical simulation; E3 independent implementation/replication; E4 physical experiment. E3 and E4 are reporting categories, not claims of completed validation or a redefinition of any existing project-wide taxonomy.

## E0 — Mathematical proof

Let P_l be the real homogeneous polynomials of degree l in three variables, and H_l = ker(Delta:P_l -> P_(l-2)). Equip monomials with the positive inner product <x^a,x^b> = a! delta_(ab). Differentiation is adjoint to multiplication by the corresponding variable. Thus Delta is adjoint to multiplication by r^2=x^2+y^2+z^2. Multiplication by r^2 is injective; therefore Delta is surjective in these finite-dimensional spaces. Consequently

    dim H_l = binomial(l+2,2) - binomial(l,2) = 2l+1.

In particular dim H_2=5 and dim H_5=11. The supplied five quadratics are harmonic and independent: the three mixed terms have distinct monomials, and the coefficients of y^2 and x^2 distinguish the remaining two. Hence they form a basis of H_2.

Define R_x=y*d_z-z*d_y, R_y=z*d_x-x*d_z, R_z=x*d_y-y*d_x and Euler operator D=x*d_x+y*d_y+z*d_z. Direct differentiation gives

    C = -(R_x^2+R_y^2+R_z^2) = D(D+1)-r^2 Delta.

On H_l, D=l and Delta=0, so C=l(l+1). Rotation preserves homogeneity and commutes with Delta. H_l is the real integer-spin l representation; its complexification is the usual complex spin-l representation. This specifies the field distinction in the polynomial realization.

For the complex tensor carrier V_2 tensor V_2 tensor V_2, Clebsch–Gordan decomposition gives

    V_0 + 3 V_1 + 5 V_2 + 4 V_3 + 3 V_4 + 2 V_5 + V_6.

The dimensions of its Casimir eigenspaces are respectively 1,9,25,28,27,22,13, totaling 125. For K=(C-6I)(C-30I), its kernel is exactly the spin-2 and spin-5 sectors. Thus

    E47 ≅ (C^5 tensor H_2^C) direct-sum (C^2 tensor H_5^C),
    dim_C E47 = 5*5 + 2*11 = 47.

Equivalently, the corresponding real representation uses R and real H_l throughout. The isomorphism requires a choice of basis in each multiplicity space; it is not a unique identification of individual carrier coordinates with polynomials.

On the full carrier, the nonzero eigenvalues of K^2 are 11664,12544,19600,32400,186624. For Gamma=I-K^2/99144 and orthogonal kernel projector P,

    Gamma P=P,
    ||Gamma^n-P||_2=(15/17)^n,
    lim_(n->infinity) Gamma^n=P.

Indeed the optimal constant step is 2/(11664+186624)=1/99144; the extreme complementary eigenvalues of Gamma are +15/17 and -15/17. Every other complementary eigenvalue lies between them. This proves the norm identity for integers n>=0.

The Euclidean polynomial Laplacian Delta and the angular Casimir C have distinct roles: Delta selects harmonic polynomials within a fixed degree; C distinguishes the angular sectors with eigenvalues 6 and 30.

## E1 — Exact computation: PASS, 15 checks

`validate.py` uses only the Python standard library, with rational arithmetic for polynomial algebra. It constructs the degree-2 and degree-5 Laplacian matrices, computes their nullspaces, exports all 16 basis polynomials, and checks harmonicity, angular Casimir eigenvalues, closure under the three rotation generators, and their Lie bracket relation. It separately checks the supplied quadratic basis.

It reconstructs tensor multiplicities from the exact weight character (t^-2+t^-1+1+t+t^2)^3 using m_j=w_j-w_(j+1), then checks the Casimir census, kernel dimension, K^2 spectrum, and optimal contraction factor.

The Lie bracket convention for these real vector fields is [R_x,R_y]=-R_z. The Hermitian angular momentum generators are J_i=-i R_i, with [J_x,J_y]=i J_z.

## E2 — Numerical simulation: PASS, 2 checks

A seeded normalized complex state in the 125-dimensional spectral basis was evolved for 220 steps. The computed distance to its E47 projection was 5.76847450957188e-13. The operator bound was (15/17)^220 = 1.0998014527879737e-12. Kernel coordinates were preserved exactly in this implementation.

This is a classical complex-state simulation in a known spectral basis. Gamma is a nonunitary contraction; its output is not renormalized here. A physical quantum implementation requires a specified dilation, postselection, or channel construction. No quantum circuit or hardware run is claimed. This execution does not construct the full carrier-to-polynomial intertwining matrix.

## E3 — Independent implementation/replication: NOT RUN

An independent implementation can construct the three 125-by-125 collective spin matrices directly, diagonalize their Casimir, and build an intertwiner U to the harmonic blocks. It can then check U†U=I_47 and J_i U=U J_i^(harm) for all three generators, and reproduce the contraction result. This is an available next validation, not an executed result in this package.

## E4 — Physical experiment: NOT TESTED

No physical device execution or experimental measurement was supplied or performed. A physical validation can encode the selected sectors and implement a specified channel or conditioned filter, with measured leakage and retained logical information compared with its mathematical predictions. No empirical conclusion follows merely from naming this level.

## Reproduce

    python3 validate.py

The command writes `results.json`, including the exact harmonic bases, all check statuses, the simulation seed, and numerical results. Any failed executed check raises an exception. No third-party packages are required.
