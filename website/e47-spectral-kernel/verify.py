"""Recompute the finite E47 arithmetic with Python standard-library integers."""
from fractions import Fraction
from math import isqrt

spins = range(7)
copies = [sum(abs(k - 2) <= j <= k + 2 for k in range(5)) for j in spins]
weights = [(2*j + 1)*copies[j] for j in spins]
values = [j*(j + 1) for j in spins]
total = sum(weights)
mean = Fraction(sum(w*c for w, c in zip(weights, values)), total)
variance = sum(w*(c - mean)**2 for w, c in zip(weights, values)) / total
assert copies == [1, 3, 5, 4, 3, 2, 1]
assert weights == [1, 9, 25, 28, 27, 22, 13]
assert (total, mean, variance) == (125, 18, 144)
roots = (mean.numerator - isqrt(variance.numerator), mean.numerator + isqrt(variance.numerator))
squares = [((c - roots[0])*(c - roots[1]))**2 for c in values]
assert squares == [32400, 12544, 0, 11664, 19600, 0, 186624]
rank = sum(w for w, a in zip(weights, squares) if a == 0)
assert (rank, total-rank) == (47, 78)
positive = [a for a in squares if a]
lo, hi = min(positive), max(positive)
step = Fraction(2, hi + lo)
gains = [1 - step*a for a in squares]
rate = max(abs(g) for g, a in zip(gains, squares) if a)
assert (Fraction(hi, lo), isqrt(hi), step, step*hi) == (16, 432, Fraction(1, 99144), Fraction(32, 17))
assert gains[3] == rate == -gains[6] == Fraction(15, 17)
alpha = Fraction(total, rank)**2
assert Fraction(7073, 1000) < alpha < Fraction(7074, 1000)
assert alpha != Fraction(70617, 10000)
pairs = []
for j in range(117):
    d = 1 + 20*j*(j + 1)
    if isqrt(d)**2 == d:
        pairs.append((j, (isqrt(d) - 1)//2))
assert pairs == [(0, 0), (2, 5), (6, 14), (44, 99), (116, 260)]
assert [n for n in range(2, 26) if 3*isqrt(2*n*(n-1)//3)**2 == 2*n*(n-1)] == [3, 25]
print("PASS: sector counts, moments, shells, kernel, endpoints, alpha and finite ladders")
