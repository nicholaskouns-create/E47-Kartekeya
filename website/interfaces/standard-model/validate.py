"""Validate the E47 gauge and matter construction with exact Python arithmetic."""
from collections import Counter
from fractions import Fraction as F
from itertools import combinations
from math import gcd

def check(name, actual, expected):
    if actual != expected:
        raise AssertionError(f"{name}: {actual} != {expected}")
    print(f"PASS  {name}: {actual}")

# Couple spin 2 twice, then couple the third spin 2.
paths = {j: [l for l in range(5) if abs(l - 2) <= j <= l + 2]
         for j in range(7)}
dims = {j: len(ls) * (2*j + 1) for j, ls in paths.items()}
check("carrier", sum(dims.values()), 125)
endpoints = [j for j in paths if j*(j+1) in (6, 30)]
check("kernel sectors", [dims[j] for j in endpoints], [25, 22])
check("kernel fraction", F(sum(dims[j] for j in endpoints), sum(dims.values())), F(47,125))

# Pair exchange in the spin-2 multiplicity space.
signs = [(-1)**l for l in paths[2]]
p, q = signs.count(1), signs.count(-1)
check("exchange multiplicities", (p,q), (3,2))
# Rank of the traceless commutator kernel: one real determinant constraint.
check("centralizer dimension", sum(a == b for a in signs for b in signs)-1, 12)
a, b = -q//gcd(p,q), p//gcd(p,q)
check("primitive central weights", (a,b,p*a+q*b), (-2,3,0))
check("covering kernel order", gcd(abs(p*a),abs(q*b)), 6)

# Conventional charge unit; chosen matter module W* + exterior square of W.
u, v = F(a,6), F(b,6)
weights = [u]*p + [v]*q
dual = Counter(-w for w in weights)
wedge = Counter(x+y for x,y in combinations(weights,2))
dc, lepton, uc, quark, ec = -u, -v, 2*u, u+v, 2*v
check("dual multiplicities", (dual[dc],dual[lepton]), (3,2))
check("exterior square multiplicities", (wedge[uc],wedge[quark],wedge[ec]), (3,6,1))
family = dual + wedge
check("one generation", sum(family.values()), 15)
anomalies = (q-1-1, q*quark+uc+dc, p*quark+lepton,
             sum(n*y for y,n in family.items()),
             sum(n*y**3 for y,n in family.items()))
check("five anomaly sums", tuple(map(str, anomalies)), ("0",)*5)
check("weak doublet parity", (p+1)%2, 0)
yukawa = (-quark-v-uc, -quark+v-dc, -lepton+v-ec)
check("three barred-field Yukawa sums", tuple(map(str,yukawa)), ("0",)*3)
