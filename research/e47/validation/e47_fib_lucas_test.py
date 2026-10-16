#!/usr/bin/env python3
"""E47 Fibonacci-Lucas lemma check (exact arithmetic).

For odd n with 2j+1 = F_n, 2J+1 = L_n, count coupling paths in V_j^{(x)3}
and verify n(j) = F_n and n(J) = F_{n-2}. Also checks the E47 census
(j=2): 1,3,5,4,3,2,1 and 25 + 22 = 47 (Omega = 47/125).
"""
from fractions import Fraction as Fr
from collections import Counter


def fib(k):
    a, b = 0, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def lucas(k):
    a, b = 2, 1
    for _ in range(k):
        a, b = b, a + b
    return a


def couple(a, b):
    J, out = abs(a - b), []
    while J <= a + b:
        out.append(J)
        J += 1
    return out


def census(j):
    c = Counter()
    for x in couple(j, j):
        for J in couple(x, j):
            c[J] += 1
    return dict(sorted(c.items()))


def isprime(n):
    return n > 1 and all(n % p for p in range(2, int(n ** 0.5) + 1))


def main():
    # E47 census
    c2 = census(Fr(2))
    assert [c2[Fr(J)] for J in range(7)] == [1, 3, 5, 4, 3, 2, 1]
    assert sum(v * (2 * k + 1) for k, v in c2.items()) == 125
    assert 5 * 5 + 2 * 11 == 47 and c2[Fr(2)] * 5 + c2[Fr(5)] * 11 == 47
    print("E47 census j=2, n(J) J=0..6:", [c2[Fr(J)] for J in range(7)], "| 25+22=47, Omega=47/125")
    print()
    print(f"{'n':>2} {'(j, J)':>14} {'(2j+1)^3':>9} {'n(j)':>5} {'n(J)':>5} {'dim':>6} {'fraction':>14} prime")
    for n in (3, 5, 7, 9, 11):
        F, L = fib(n), lucas(n)
        assert 3 * F - L == 2 * fib(n - 2)
        j, J = Fr(F - 1, 2), Fr(L - 1, 2)
        assert J <= 3 * j
        c = census(j)
        nj, nJ = c.get(j, 0), c.get(J, 0)
        assert nj == F, (n, nj)
        assert nJ == fib(n - 2) == 3 * j - J + 1, (n, nJ)
        assert max(c.values()) == nj
        N = F ** 3
        d = int(nj * (2 * j + 1) + nJ * (2 * J + 1))
        print(f"{n:>2} {'(' + str(j) + ', ' + str(J) + ')':>14} {N:>9} {nj:>5} {nJ:>5} {d:>6} {str(Fr(d, N)):>14} {isprime(d)}")
    print("\nAll identities verified: n(j)=F_n, n(J)=F_{n-2}=3j-J+1, 3F_n-L_n=2F_{n-2}.")


if __name__ == "__main__":
    main()
