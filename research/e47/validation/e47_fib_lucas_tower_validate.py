#!/usr/bin/env python3
"""E47 Fibonacci-Lucas tower validator (stdlib only, exact arithmetic where possible).

Exit code 0 and a final line "PASS" mean every assertion below held.

EXACT FACTS checked here (integer / Fraction arithmetic unless noted):
 (a) For odd n in {5, 7, 11, 13}, with integer j = (F_n - 1)/2 and J = (L_n - 1)/2,
     the multiplicities of spin j and spin J in V_j^{(x)3}, computed directly from
     the weight census, are n(j) = F_n and n(J) = F_{n-2}; and J(J+1) = 5 j(j+1).
 (b) The kept dimension D = n(j)(2j+1) + n(J)(2J+1) = F_n^2 + F_{n-2} L_n.
     At n = 5 (j = 2, J = 5) this is 5*5 + 2*11 = 47 = dim ker K = dim(E_6 (+) E_30).
 (c) D / (2j+1)^2 -> 3/phi along the tower: |D/(2j+1)^2 - 3/phi| strictly decreases
     over the odd n in 5..19 for which j and J are integers (n = 5, 7, 11, 13, 17, 19),
     and is below 1e-6 at n = 19. The identity 1 + sqrt5/phi^2 = 3/phi is checked
     numerically to 1e-12 (it is exact: phi^2 = phi + 1 and sqrt5 = 2 phi - 1).
 (d) Quantum tetrahedron: dim Inv(V_j^{(x)4}) equals the multiplicity of j in
     V_j^{(x)3}, for j = 2 (both 5) and j = 6 (both 13).
 (e) Selector identity: with S_a^2 = j(j+1), the Casimir values
     mu +/- sigma = 3j(j+1) +/- 2j(j+1) equal J(J+1) for J = j and for the J with
     J(J+1) = 5 j(j+1); equivalently sum_{a<b} S_a.S_b = +/- j(j+1) on those sectors.
     For j = 2 the 125x125 Casimir C = sum_a S_a^2 + 2 sum_{a<b} S_a.S_b is built
     with integer entries (a diagonal similarity of the standard spin matrices, so
     the spectrum is unchanged) and checked exactly: its eigenvalues are J(J+1) with
     multiplicity n(J)(2J+1) for every J present; dim E_6 = 25, dim E_30 = 22, and
     rank K = rank (C - 6I)(C - 30I) = 78, so dim ker K = 47 and Omega_c = 47/125.

OPEN INTERPRETATION (not checked, not claimed): the statements above are finite
representation-theory and Fibonacci-Lucas identities. Whether the tower limit
3/phi, or the tetrahedral reading in (d), corresponds to physical geometry stays
an open question; this script neither asserts nor refutes it.
"""
from __future__ import annotations

import math
import sys
from collections import Counter
from fractions import Fraction

PHI = (1 + math.sqrt(5)) / 2
checks: list[tuple[str, bool, object]] = []


def check(name: str, ok: bool, value: object = "") -> None:
    checks.append((name, bool(ok), value))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {value}")


def F(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def L(n: int) -> int:
    return F(n - 1) + F(n + 1)


def weights(j: int, k: int) -> Counter:
    """Weight census of V_j^{(x)k}: number of states with total S_z = M."""
    m = Counter({0: 1})
    for _ in range(k):
        m2 = Counter()
        for M, c in m.items():
            for a in range(-j, j + 1):
                m2[M + a] += c
        m = m2
    return m


def multiplicity(j: int, k: int, J: int) -> int:
    """Multiplicity of spin J in V_j^{(x)k} (= #weights J minus #weights J+1)."""
    m = weights(j, k)
    return m[J] - m[J + 1]


# (a) + (b): tower census, exact integers ---------------------------------------
print("(a)/(b) census along the tower")
for n in (5, 7, 11, 13):
    assert (F(n) - 1) % 2 == 0 and (L(n) - 1) % 2 == 0
    j, J = (F(n) - 1) // 2, (L(n) - 1) // 2
    nj, nJ = multiplicity(j, 3, j), multiplicity(j, 3, J)
    check(f"n={n} j={j} J={J}: n(j)=F_n={F(n)}", nj == F(n), nj)
    check(f"n={n}: n(J)=F_(n-2)={F(n - 2)}", nJ == F(n - 2), nJ)
    check(f"n={n}: J(J+1)=5j(j+1)", J * (J + 1) == 5 * j * (j + 1), (J * (J + 1), 5 * j * (j + 1)))
    D = nj * (2 * j + 1) + nJ * (2 * J + 1)
    check(f"n={n}: D=F_n^2+F_(n-2)L_n", D == F(n) ** 2 + F(n - 2) * L(n), D)
check("E47: D(n=5) = 5*5 + 2*11 = 47", F(5) ** 2 + F(3) * L(5) == 47, F(5) ** 2 + F(3) * L(5))

# (c): tower ratio -> 3/phi ---------------------------------------------------
print("(c) D/(2j+1)^2 -> 3/phi")
target = 3 / PHI
errs = []
for n in range(5, 20, 2):
    if (F(n) - 1) % 2 or (L(n) - 1) % 2:
        print(f"    n={n}: j or J not an integer (F_n={F(n)}, L_n={L(n)}), not on the tower")
        continue
    j = (F(n) - 1) // 2
    ratio = Fraction(F(n) ** 2 + F(n - 2) * L(n), (2 * j + 1) ** 2)  # exact
    err = abs(float(ratio) - target)
    errs.append((n, err))
    print(f"    n={n:<2} j={j:<5} D/(2j+1)^2={str(ratio):<22} |err|={err:.3e}")
check("|D/(2j+1)^2 - 3/phi| strictly decreasing over n=5,7,11,13,17,19",
      [n for n, _ in errs] == [5, 7, 11, 13, 17, 19] and all(b < a for (_, a), (_, b) in zip(errs, errs[1:])),
      [n for n, _ in errs])
check("|D/(2j+1)^2 - 3/phi| < 1e-6 at n=19", errs[-1][0] == 19 and errs[-1][1] < 1e-6, f"{errs[-1][1]:.3e}")
check("1 + sqrt5/phi^2 = 3/phi (to 1e-12)", abs(1 + math.sqrt(5) / PHI ** 2 - 3 / PHI) < 1e-12,
      f"{abs(1 + math.sqrt(5) / PHI ** 2 - 3 / PHI):.1e}")

# (d): quantum tetrahedron ----------------------------------------------------
print("(d) dim Inv(V_j^4) = multiplicity of j in V_j^3")
for j, expected in ((2, 5), (6, 13)):
    inv4, m3 = multiplicity(j, 4, 0), multiplicity(j, 3, j)
    check(f"j={j}: dim Inv(V_j^4)={inv4}, n(j) in V_j^3={m3}, both {expected}",
          inv4 == m3 == expected, (inv4, m3))

# (e): selector identity -----------------------------------------------------
print("(e) selector identity mu +/- sigma")
for n in (5, 7, 11, 13, 17, 19):
    j, J = (F(n) - 1) // 2, (L(n) - 1) // 2
    s2 = j * (j + 1)
    mu, sigma = 3 * s2, 2 * s2
    ok = (mu - sigma == j * (j + 1)) and (mu + sigma == J * (J + 1))
    dots = {Jx: Fraction(Jx * (Jx + 1) - mu, 2) for Jx in (j, J)}  # sum_{a<b} S_a.S_b
    ok = ok and dots[j] == -s2 and dots[J] == s2
    check(f"n={n} j={j}: mu-sigma=j(j+1), mu+sigma=J(J+1)={J * (J + 1)}, sum S_a.S_b = -/+ j(j+1)", ok,
          (mu - sigma, mu + sigma))

# Exact 125x125 Casimir for j = 2 -------------------------------------------
j, k = 2, 3
d = 2 * j + 1
ms = list(range(j, -j - 1, -1))  # basis order m = j..-j
N = d ** k
# Integer spin matrices (diagonal similarity of the standard ones):
#   S+ e_m = e_{m+1},  S- e_{m+1} = (j-m)(j+m+1) e_m,  Sz e_m = m e_m.
# Then S-S+ and S+S- match the standard matrices, so C has the true spectrum.
def idx(t):
    r = 0
    for m in t:
        r = r * d + ms.index(m)
    return r

states = [(a, b, c) for a in ms for b in ms for c in ms]
C = [[0] * N for _ in range(N)]
for t in states:
    col = idx(t)
    # sum_a S_a^2 = 3 j(j+1) on every state
    C[col][col] += k * j * (j + 1)
    for a in range(k):
        for b in range(a + 1, k):
            ma, mb = t[a], t[b]
            C[col][col] += 2 * ma * mb  # 2 Sz_a Sz_b
            # 2 * (S+_a S-_b + S-_a S+_b)/2 = S+_a S-_b + S-_a S+_b
            if ma < j and mb > -j:  # S+_a S-_b
                u = list(t); u[a] = ma + 1; u[b] = mb - 1
                C[idx(u)][col] += (j - (mb - 1)) * (j + (mb - 1) + 1)
            if ma > -j and mb < j:  # S-_a S+_b
                u = list(t); u[a] = ma - 1; u[b] = mb + 1
                C[idx(u)][col] += (j - (ma - 1)) * (j + (ma - 1) + 1)


def matmul(A, B):
    Bt = list(zip(*B))
    return [[sum(x * y for x, y in zip(r, c)) for c in Bt] for r in A]


def shift(A, lam):
    return [[A[r][c] - (lam if r == c else 0) for c in range(N)] for r in range(N)]


def rank(A) -> int:
    M = [[Fraction(x) for x in row] for row in A]
    rk, rows, cols = 0, len(M), len(M[0])
    for c in range(cols):
        p = next((r for r in range(rk, rows) if M[r][c] != 0), None)
        if p is None:
            continue
        M[rk], M[p] = M[p], M[rk]
        piv = M[rk][c]
        for r in range(rows):
            if r != rk and M[r][c] != 0:
                f = M[r][c] / piv
                M[r] = [x - f * y for x, y in zip(M[r], M[rk])]
        rk += 1
    return rk


census = {J: multiplicity(j, k, J) for J in range(0, k * j + 1)}
present = {J: n for J, n in census.items() if n}
check("j=2 census n(J) = 1,3,5,4,3,2,1 (J=0..6)", [census[J] for J in range(7)] == [1, 3, 5, 4, 3, 2, 1],
      [census[J] for J in range(7)])
check("tr C = sum_J n(J)(2J+1) J(J+1)", sum(C[i][i] for i in range(N)) ==
      sum(n * (2 * J + 1) * J * (J + 1) for J, n in present.items()), sum(C[i][i] for i in range(N)))
# minimal polynomial: prod_J (C - J(J+1) I) = 0  (C is diagonalizable: similar to Hermitian)
P = None
for J in present:
    P = shift(C, J * (J + 1)) if P is None else matmul(P, shift(C, J * (J + 1)))
check("prod over J present of (C - J(J+1)I) = 0", all(x == 0 for row in P for x in row))
dims = {J: N - rank(shift(C, J * (J + 1))) for J in present}
check("eigenspace dim of J(J+1) = n(J)(2J+1) for every J present",
      all(dims[J] == n * (2 * J + 1) for J, n in present.items()), dims)
check("E_6 (J=2): eigenvalue 6 = mu - sigma, dim 25", dims[2] == 25 and 3 * 6 - 2 * 6 == 6, dims[2])
check("E_30 (J=5): eigenvalue 30 = mu + sigma, dim 22", dims[5] == 22 and 3 * 6 + 2 * 6 == 30, dims[5])
K = matmul(shift(C, 6), shift(C, 30))
rK = rank(K)
check("rank K = 78, dim ker K = 47, Omega_c = 47/125", rK == 78 and Fraction(N - rK, N) == Fraction(47, 125),
      (rK, N - rK, str(Fraction(N - rK, N))))

failed = [name for name, ok, _ in checks if not ok]
print(f"RESULT: {len(checks) - len(failed)} / {len(checks)} checks")
if failed:
    print("FAIL:", "; ".join(failed))
    sys.exit(1)
print("PASS")
