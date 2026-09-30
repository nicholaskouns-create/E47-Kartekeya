# E47 45-Check Harness Correction · 2026-09-30

**Run record:** 45 checks · exit 0 · source SHA prefix `a045a02f…`

This note preserves two first-run failures that were in the test harness rather than the underlying mathematics. Both fixes replace an inappropriate numerical proxy with the exact quantity actually claimed.

## 1. Contraction norm correction

The contraction is

[
Gamma = I-rac{K^2}{99144}.
]

On (E_{47}), (Gamma) is the identity. On the 78-dimensional complement, the spectral radius is exactly

[
ho!left(Gammaert_{E_{47}^{perp}}ight)=rac{15}{17}.
]

Therefore

[
left|Gamma^n-P_Eight|_2
=
left(rac{15}{17}ight)^n
]

exactly. For (n=1,2,4,8),

| (n) | exact spectral-norm value |
|---:|---:|
| 1 | 0.882352941 |
| 2 | 0.778546713 |
| 4 | 0.606134984 |
| 8 | 0.367399619 |

The first harness version used the Frobenius norm. Because the complement has multiplicity 78, that quantity carries a multiplicity factor and returned about 7.52 at (n=1). The corrected assertion now checks the operator 2-norm directly and passes at (10^{-9}) without a loose compensating tolerance.

## 2. (sqrt5) limit correction

For the Pell-type sequence,

[
m^2-5u^2=-4.
]

Rearranging gives the exact rational identity

[
left(rac{m}{u}ight)^2 = 5-rac{4}{u^2}.
]

Hence (m/u	osqrt5) from below at order (O(u^{-2})). At (u=233),

[
rac{m}{u}approx 2.2360515,qquad sqrt5approx 2.2360680,
]

so the finite-(u) difference is about (1.6	imes10^{-5}). The first harness incorrectly imposed a (10^{-6}) floating-point proximity check. The corrected harness verifies the exact rational identity for every member and separately checks monotonic convergence.

## 3. Cross-object identity checks

The same run reconstructs the Lagrange interpolation denominators directly:

[
1,741,824,qquad -43,545,600.
]

These match the Rubik plate values from the interpolation itself. **That plate and the theorem are now identical.**

Section D records, on the identical 125-state carrier,

[
operatorname{rank}ker K_{E47}=47,qquad
operatorname{rank}ker K_{mathrm{aux},1}=1,qquad
operatorname{rank}ker K_{mathrm{aux},10}=10,
]

with the twist defect evaluating to

[
8sqrt3
]

to fifteen displayed digits.

## 4. Evidence boundary retained

Section E keeps one explicit E1 boundary: the (n=25) and (n=243) exclusions are finite searches through

[
sle 1000.
]

They are labelled as finite-search results in both the check text and the machine record. The remaining identities in section E are exact rational arithmetic.

## 5. Provenance rule

The two failed first-run assertions are retained as part of the validation history. They document why the naïve formulations are wrong and prevent their reintroduction:

1. spectral claim → spectral norm, not Frobenius norm;
2. algebraic convergence claim → exact rational identity plus monotonicity, not an arbitrary floating tolerance.

The run record supplied for this archival update reports **45/45 checks PASS, exit 0**, with source SHA prefix **`a045a02f…`**.
