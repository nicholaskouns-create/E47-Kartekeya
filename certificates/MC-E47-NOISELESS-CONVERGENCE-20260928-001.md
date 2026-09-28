# E47 Noiseless-Subsystem and Uniform Convergence Certificate

**Certificate:** `MC-E47-NOISELESS-CONVERGENCE-20260928-001`  
**Status:** **PASS**  
**Evidence:** E0 representation-theoretic identities + E1 independent numerical construction.  
**Validator SHA-256:** `f757a1848535353c33f545375c1dcb86ca8ffe71a4652f4e3999a644852e01fb`

## Uniform convergence

```text
K = (C - 6I)(C - 30I)
H = K^2
epsilon_* = 1 / 99144
rho_* = 15 / 17
```

Since `||K||_2 = 432`,

```text
|| K Gamma_*^n (I - P_47) ||_2 <= 432 (15/17)^n.
```

The first integer for which the worst-case bound is strictly below `1e-12` is `n = 270`.

- bound at `n = 269`: `1.0310330384200082e-12`
- bound at `n = 270`: `9.0973503390000908e-13`
- direct operator norm at `n = 270`: `9.2548191332753090e-13`

## Noiseless multiplicity subsystems

```text
E_47 = E_6 (+) E_30
     ~= (C^5 tensor V_2) (+) (C^2 tensor V_5)
```

For collective generators `J_a`,

```text
W_J^* J_a W_J = I_(m_J) tensor J_a^(J)
```

to machine precision for `J = 2, 5`.

### J = 2

- multiplicity subsystem: `C^5`
- generator factorization max residual: `1.140e-14`
- collective rotation residual: `5.839e-15`
- random-unitary channel factorization residual: `6.067e-15`
- reduced logical-state invariance residual: `3.187e-16`

### J = 5

- multiplicity subsystem: `C^2`
- generator factorization max residual: `2.985e-14`
- collective rotation residual: `5.978e-15`
- random-unitary channel factorization residual: `6.094e-15`
- reduced logical-state invariance residual: `8.184e-16`

Collective `J=2 <-> J=5` cross-block residual: `2.208e-15`.

## Certified statement

`C^5` and `C^2` are noiseless multiplicity subsystems under collective `SU(2)` noise.

They form a direct sum of two protected subsystems with different gauge representations. This certificate does not assert that their direct sum is one seven-dimensional scalar Knill-Laflamme code.
