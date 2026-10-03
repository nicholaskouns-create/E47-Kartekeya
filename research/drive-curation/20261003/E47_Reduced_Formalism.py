from __future__ import annotations
import sympy as sp

lam = sp.symbols("lambda")
spectrum = (0, 2, 6, 12, 20, 30, 42)
multiplicity = {0: 1, 2: 9, 6: 25, 12: 28, 20: 27, 30: 22, 42: 13}
selected = (6, 30)

def lagrange_basis(mu: int) -> sp.Expr:
    return sp.prod(
        (lam - nu) / sp.Integer(mu - nu)
        for nu in spectrum
        if nu != mu
    )

p = sp.factor(sum(lagrange_basis(mu) for mu in selected))
K = (lam - 6) * (lam - 30)

assert sum(multiplicity.values()) == 125
assert sum(multiplicity[mu] for mu in selected) == 47
assert all(sp.simplify(p.subs(lam, mu)) == (1 if mu in selected else 0)
           for mu in spectrum)
assert all(sp.simplify((p**2 - p).subs(lam, mu)) == 0
           for mu in spectrum)
assert all(sp.simplify((K*p).subs(lam, mu)) == 0
           for mu in spectrum)

print("E47 SPECTRAL PROJECTOR")
print("Sigma = V_2^(tensor 3), dim Sigma = 125")
print("spec(C) =", spectrum)
print("K = (C - 6I)(C - 30I)")
print("Psi = ker(K) = E_6 direct_sum E_30")
print("dim(Psi) = 47")
print("p(lambda) =", p)
print("P_47 = p(C)")
print("rank(P_47) = 47")
print("Omega_c = 47/125 =", sp.Rational(47, 125))
