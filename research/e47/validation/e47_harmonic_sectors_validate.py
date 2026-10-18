#!/usr/bin/env python3
"""E47 harmonic-sector validator.

Harmonic polynomials of degree k in x, y, z (homogeneous f with
Laplacian(f) = 0) form a space of dimension 2k+1. Under rotations this
space is the spin-k irreducible representation V_k, the same as the
spherical harmonics Y_{k,m}.

Degree 2 (dim 5) and degree 5 (dim 11) therefore give concrete
realizations of V_2 and V_5, the two sectors kept by the E47 selector
K = (C - 6I)(C - 30I). So

    E47 = 5 V_2 (+) 2 V_5,   dim = 5*5 + 2*11 = 47.

This script builds a basis of harmonic polynomials for k = 2 and k = 5 by
solving Laplacian(f) = 0 on a general degree-k polynomial, then asserts:
  * the basis has exactly 2k+1 elements and is linearly independent,
  * every basis polynomial has Laplacian identically 0,
  * 5*dim(H_2) + 2*dim(H_5) == 47.
It prints PASS and exits 0 on success; any failed check raises.

Requires: sympy (pip install sympy).

Note: free coefficients are substituted simultaneously into the solved
coefficients. Substituting one variable at a time leaves unsolved
coefficients in the degree-5 basis, which makes it non-harmonic.
"""
import sys

import sympy as sp

x, y, z = sp.symbols('x y z', real=True)


def lap(f):
    return sp.diff(f, x, 2) + sp.diff(f, y, 2) + sp.diff(f, z, 2)


def harmonics(k):
    monos = [x**i * y**j * z**(k - i - j)
             for i in range(k + 1) for j in range(k + 1 - i)]
    cs = sp.symbols(f'c0:{len(monos)}')
    f = sum(c * m for c, m in zip(cs, monos))
    eqs = sp.Poly(sp.expand(lap(f)), x, y, z).coeffs()
    sol = sp.solve(eqs, cs, dict=True)[0]
    free = [c for c in cs if c not in sol]
    basis = []
    for fc in free:
        fv = {c: (1 if c == fc else 0) for c in free}
        sub = {**{c: v.subs(fv) for c, v in sol.items()}, **fv}
        basis.append(sp.expand(f.subs(sub, simultaneous=True)))
    return basis, monos


def rank(basis, monos):
    rows = [[sp.Poly(b, x, y, z).coeff_monomial(m) for m in monos] for b in basis]
    return sp.Matrix(rows).rank()


def main():
    dims = {}
    for k in (2, 5):
        B, monos = harmonics(k)
        laps = [sp.simplify(lap(b)) for b in B]
        print(f"deg {k}: dim = {len(B)}, Laplace = {laps}")
        if k == 2:
            print("  basis:", B)
        assert len(B) == 2 * k + 1, f"deg {k}: expected dim {2*k+1}, got {len(B)}"
        assert all(l == 0 for l in laps), f"deg {k}: non-harmonic basis element"
        assert rank(B, monos) == 2 * k + 1, f"deg {k}: basis not linearly independent"
        dims[k] = len(B)
    total = 5 * dims[2] + 2 * dims[5]
    print("E47 = 5*dim(H2) + 2*dim(H5) =", total)
    assert total == 47, f"expected 47, got {total}"
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
