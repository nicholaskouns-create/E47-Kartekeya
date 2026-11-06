# The E₄₇ spectral kernel

Nicholas Shane Kouns, DO · Mathematical City · 6 November 2026

[Vector plate](E47-spectral-kernel.svg) · [Print PDF](E47-spectral-kernel.pdf) · [Exact Python calculation](verify.py)

## From spin addition to a projector

Couple two spin-2 factors to intermediate spin k = 0,…,4. On coupling the third factor, each k contributes one copy of spin J precisely when |k−2| ≤ J ≤ k+2. In increasing J order the multiplicities are (1,3,5,4,3,2,1). Multiplication by 2J+1 gives the state counts (1,9,25,28,27,22,13).

On the 125-dimensional carrier, the total Casimir C has eigenvalues c = J(J+1). Under the normalized trace the mean is 18 and the variance is 144. The mean ± one standard deviation gives 6 and 30. Hence K = (C−6I)(C−30I) vanishes precisely at J = 2 and 5. The orthogonal projector P onto this kernel has rank 25+22 = 47 and nullity 78.

## Exact rate

In increasing J order the eigenvalues of K² are (32400,12544,0,11664,19600,0,186624). On the complement, a = 11664 and b = 186624 bound the spectrum, b/a = 16 and √b = 432. For Γ = I−εK² the extremal gains are 1−εa and 1−εb. Their maximal absolute value is uniquely minimized when they are opposite, giving ε = 2/(a+b) = 1/99144. In units of b the step is εb = 32/17. The signed gains at J = 3 and 6 are +15/17 and −15/17.

Sector by sector, a gain of one is equivalent to K vanishing. Consequently ker K = Fix(Γ) = ran P, and ‖Γⁿ−P‖₂ = (15/17)ⁿ for every integer n ≥ 0. The norm is the induced Euclidean operator norm. The fixed components persist from the first iterate. Complement components converge geometrically.

## Number-theoretic scope and corrections

For three input spins j the upper-shell equation is J(J+1) = 5j(j+1). Setting x = 2J+1 and y = 2j+1 gives x²−5y² = −4. In the Fibonacci–Lucas parametrization, y = Fₖ and x = Lₖ for odd k. Integer j also requires Fₖ odd, equivalently 3 does not divide k. The finite check through j = 116 gives (j,J) = (0,0), (2,5), (6,14), (44,99), (116,260). J = 98 fails the fourth instance. F₉ = 34 and F₁₅ = 610 explain the parity restriction. The finite enumeration and the infinite-family characterization are distinct claims.

For tensor order n, the square condition is 2n(n−1)/3 = s². Among 2,…,24 only n = 3 works. At n = 25, s = 20. The ratio α = (125/47)² = 15625/2209 lies strictly between 7.073 and 7.074. The earlier 7.0617 fails by exact cross-multiplication.

## Verification record

Run `python3 verify.py` with assertions enabled to reproduce the finite arithmetic. The supplied audit reports 37 axiom-free theorems in Lean 4.15.0 and 37 closed theorems in Coq 8.18.0, including the sectorwise fixed-point equivalence. It reports negative controls for κ = 15 and α = 7.0617. The original 37-theorem sources and logs were not recovered for this edition. This edition independently reran the exact Python calculations.

The supplied Q4.28 residual of 17.595 LSB is a reported measurement. If a complement error receives a perturbation bounded in norm by 2δ each iteration, the geometric-series upper bound is 2δ/(1−15/17) = 17δ. Equality and the measured floor require an implementation-specific rounding model.
