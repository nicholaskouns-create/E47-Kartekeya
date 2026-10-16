# E47 Fibonacci–Lucas Lemma

Status: verified lemma + open item. Validation: `research/e47/validation/e47_fib_lucas_test.py` (exact arithmetic, exits 0).

## Setting

E47 carrier: \(V_2^{\otimes 3}\), dim 125, Casimir \(C = J(J+1)\), kernel \(K = (C-6I)(C-30I)\),
\(\ker K = E_6 \oplus E_{30}\), dim 47 = \(5\cdot V_2 + 2\cdot V_5\), \(\Omega_c = 47/125\) (certificate \(\mathcal{K}_{47/125}\)).

## Lemma

Let \(n\) be odd, \(2j+1 = F_n\), \(2J+1 = L_n\). Then \(J \le 3j\), and in \(V_j^{\otimes 3}\):

- the spin-\(j\) sector has multiplicity \(n(j) = 2j+1 = F_n\) (the maximum multiplicity);
- the spin-\(J\) sector has multiplicity \(n(J) = F_{n-2}\).

**Proof sketch.** For \(j \le J \le 3j\), coupling-path counting gives \(n(J) = 3j - J + 1\), and \(n(j) = 2j+1\).
Substituting, \(n(J) = (3F_n - L_n)/2\), and \(3F_n - L_n = 2F_{n-2}\) (Fibonacci–Lucas identity), so \(n(J) = F_{n-2}\). ∎

## Table (computed exactly)

| n | (j, J) | (2j+1)³ | n(j) | n(J) | dim E_j⊕E_J | fraction | prime |
|---|---|---|---|---|---|---|---|
| 3 | (1/2, 3/2) | 8 | 2 | 1 | 8 | 1 | no |
| 5 | **(2, 5)** | 125 | 5 | 2 | **47** | **47/125** | **yes** |
| 7 | (6, 14) | 2197 | 13 | 5 | 314 | 314/2197 | no |
| 9 | (33/2, 75/2) | 39304 | 34 | 13 | 2144 | 268/4913 | no |
| 11 | (44, 99) | 704969 | 89 | 34 | 14687 | 14687/704969 | no |

E47 census (j = 2), n(J) for J = 0..6: 1, 3, 5, 4, 3, 2, 1; d(J) = 1, 9, 25, 28, 27, 22, 13 (sum 125); 25 + 22 = 47.

## E47 as the first integer instance

- n = 3 is half-integer and trivial (fraction 1). n = 5, (2, 5), is the first integer-spin instance.
- It is the only listed instance with prime selected dimension (47).
- It is the only instance with \(3j - J = 1\) (J is the next-to-top spin, n(J) = 2).

The structure (multiplicities \(F_n, F_{n-2}\)) is uniform across the family; E47 is its first non-trivial integer member, not a unique case.

## Open item

The lemma describes the selection; it does **not** derive \(K = (C-6I)(C-30I)\). Why the kernel selects Casimir eigenvalues 6 and 30 remains open.
