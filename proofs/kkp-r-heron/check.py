"""Exact identities and an independent six-step numerical check."""
import sympy as sp

phi = (1 + sp.sqrt(5)) / 2
spectral = sp.Rational(47, 125)
geometric = phi**-5
assert sp.simplify(geometric - (5 * sp.sqrt(5) - 11) / 2) == 0
assert 0 < geometric < spectral
x, r = sp.symbols("x r", positive=True)
assert sp.factor((x + r**2 / x) / 2 - r - (x - r)**2 / (2 * x)) == 0
assert sp.diff(125 * x, x) == 125
for name, target in [("spectral", spectral), ("geometric", geometric)]:
    value = 1.0
    for _ in range(6):
        value = (value + float(target) / value) / 2
    root = sp.sqrt(target)
    assert abs(value - float(root)) < 1e-14
    print(f"{name:10s} sqrt = {root.evalf(20)}   step 6 = {value:.12f}")
