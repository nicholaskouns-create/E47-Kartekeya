from collections import Counter

def couple(j1, j2):
    return list(range(abs(j1 - j2), j1 + j2 + 1))

# 2 ⊗ 2
two = couple(2, 2)
assert sum(2 * j + 1 for j in two) == 25

# V2 ⊗ V2 ⊗ V2
n = Counter()
for j in two:
    for J in couple(j, 2):
        n[J] += 1

rows = []
total = 0
for J in range(0, 7):
    d = n[J] * (2 * J + 1)
    total += d
    rows.append((J, n[J], d, J * (J + 1)))

assert total == 125
assert rows == [
    (0, 1, 1, 0),
    (1, 3, 9, 2),
    (2, 5, 25, 6),
    (3, 4, 28, 12),
    (4, 3, 27, 20),
    (5, 2, 22, 30),
    (6, 1, 13, 42),
]

dim_E6 = n[2] * (2 * 2 + 1)
dim_E30 = n[5] * (2 * 5 + 1)
dim_ker = dim_E6 + dim_E30
assert dim_E6 == 25
assert dim_E30 == 22
assert dim_ker == 47
assert dim_ker / total == 47 / 125

# complement spectrum of K = (C - 6I)(C - 30I)
ksq = []
for J, copies, states, lam in rows:
    if lam in (6, 30):
        continue
    k = (lam - 6) * (lam - 30)
    ksq.append(k * k)
ksq = sorted(set(ksq))
lam_min, lam_max = ksq[0], ksq[-1]
kappa = lam_max // lam_min
eps_den = lam_min + lam_max
assert lam_min == 108 ** 2 == 11664
assert lam_max == 432 ** 2 == 186624
assert kappa == 16
assert eps_den // 2 == 99144
assert (16 - 1) / (16 + 1) == 15 / 17

print("carrier", total)
print("blocks")
for J, copies, states, lam in rows:
    mark = " KER" if lam in (6, 30) else ""
    print(f"  J={J}  n={copies}  d={states}  λ={lam}{mark}")
print("dim E6", dim_E6)
print("dim E30", dim_E30)
print("dim ker", dim_ker)
print("Ωc", f"{dim_ker}/{total}")
print("distinct K^2", ksq)
print("κ", kappa)
print("ε*", f"1/{eps_den // 2}")
print("ρ*", "15/17")
print("PASS")
