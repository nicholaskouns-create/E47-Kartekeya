# Parameter-Free Spectral Projection

**Nicholas Shane Kouns — 26 November 2026**

The operator Γ = I − K²/99144 converges to the orthogonal projector onto a
47-dimensional subspace of a 125-dimensional carrier at the exact rate (15/17)ⁿ,
and every constant in it — both roots of K and the denominator 99144 — is fixed
by the carrier's own spectrum rather than chosen.

---

## Abstract

A spectral projector is normally built by choosing a filter: one picks the
polynomial, picks the relaxation parameter, and tunes until the iteration
converges. This note exhibits a case in which nothing is picked.

On the 125-dimensional carrier formed by coupling three spin-2 systems, let C be
the total Casimir and set K = (C − 6I)(C − 30I) and Γ = I − K²/99144. Then Γⁿ
converges in operator norm to the orthogonal projector onto ker K, a subspace of
dimension 47, and the convergence is exactly geometric with ratio 15/17.

Three facts make the construction parameter-free. The two roots of K are the only
pair in the Casimir spectrum lying one standard deviation either side of its
dimension-weighted mean, which is exactly 18 with variance exactly 144. The
denominator 99144 is the arithmetic mean of the extreme nonzero eigenvalues of
K², which is the unique minimax choice. And the resulting rate 15/17 is precisely
the classical optimum (κ − 1)/(κ + 1) for a condition number κ that here equals
exactly 16.

The operator is therefore the optimally relaxed Richardson iteration for K²,
arrived at without reference to the classical theory and agreeing with it
exactly. The surviving invariant is the fraction of the carrier that the
projector retains, Ω_c = 47/125.

---

## The construction

The whole formalism is five lines.

```
K   = (C − 6I)(C − 30I)
Γ   = I − K²/99144
lim Γⁿ = P₄₇          (n → ∞)
K P₄₇ = 0
Ω_c = 47/125
```

Line 1 selects. Line 2 damps everything the selector does not annihilate. Line 3
is the limit. Line 4 says the limit lands inside the selector's kernel. Line 5
records what fraction of the carrier survives.

Everything below is a consequence of these five lines together with the spectrum
of C. No further input is used, and in particular no parameter is fitted.

---

## The carrier

Take three spin-2 systems and couple them: ℋ = V₂ ⊗ V₂ ⊗ V₂, of dimension
5³ = 125. Let J be the total angular momentum and C = J₁² + J₂² + J₃² the total
Casimir.

The Clebsch–Gordan series gives
D² ⊗ D² ⊗ D² = 1·D⁰ ⊕ 3·D¹ ⊕ 5·D² ⊕ 4·D³ ⊕ 3·D⁴ ⊕ 2·D⁵ ⊕ 1·D⁶
(Edmonds 1957, ch. 3; Varshalovich et al. 1988, ch. 8). C acts on Dʲ as j(j+1),
so its spectrum and the dimension of each eigenspace are fixed:

| j | C = j(j+1) | multiplicity | eigenspace dimension |
|---|---|---|---|
| 0 | 0 | 1 | 1 |
| 1 | 2 | 3 | 9 |
| 2 | 6 | 5 | 25 |
| 3 | 12 | 4 | 28 |
| 4 | 20 | 3 | 27 |
| 5 | 30 | 2 | 22 |
| 6 | 42 | 1 | 13 |

The dimensions sum to 1 + 9 + 25 + 28 + 27 + 22 + 13 = 125, as they must.

This table is the only input. C is self-adjoint, so K and Γ are real polynomials
in a self-adjoint operator: all three commute and share an eigenbasis, and every
statement below is a statement about the seven numbers in the second column.

---

## Deduction 1 — the fixed set is exactly ker K

Write K(c) = (c − 6)(c − 30) for the value of K on the C-eigenvalue c. On that
eigenspace Γ acts as the scalar γ(c) = 1 − K(c)²/99144, so γ(c) = 1 if and only
if K(c) = 0, which happens only at c = 6 and c = 30. Those are the j = 2 and
j = 5 blocks, of dimensions 25 and 22:

```
dim ker K = 25 + 22 = 47
```

So the fixed-point set of Γ is exactly the 47-dimensional space E₄₇ = ker K, and
line 4 of the construction, K P₄₇ = 0, is not an extra assumption: it is the
definition of P₄₇ as the projector onto that kernel.

Two consequences worth stating. First, Γ preserves E₄₇ pointwise and preserves
its orthogonal complement, because both are spanned by C-eigenvectors. Second,
P₄₇ must be built spectrally from the eigenbasis, not from a pseudo-inverse: a
pseudo-inverse construction fails idempotence at the 10⁻³ level in double
precision, which is large enough to corrupt any downstream claim about the
subspace while still looking plausible.

---

## Deduction 2 — convergence, with an exact rate

Evaluating γ on the five non-kernel eigenvalues gives the whole spectrum of Γ:

| C-eigenvalue c | K(c) | K(c)² | γ(c) = 1 − K(c)²/99144 |
|---|---|---|---|
| 0 | −180 | 32400 | 103/153 ≈ 0.6732 |
| 2 | −112 | 12544 | ≈ 0.8735 |
| 6 | 0 | 0 | 1 |
| 12 | −108 | 11664 | 15/17 ≈ 0.8824 |
| 20 | −140 | 19600 | ≈ 0.8023 |
| 30 | 0 | 0 | 1 |
| 42 | 432 | 186624 | −15/17 ≈ −0.8824 |

Every non-kernel value has modulus at most 15/17 < 1, and the bound is attained
twice, at c = 12 and c = 42, with opposite signs. Since Γ is self-adjoint and
diagonal in the C-eigenbasis,

```
‖Γⁿ − P₄₇‖ = max |γ(c)|ⁿ = (15/17)ⁿ        (c ∉ {6, 30})
```

which proves line 3 and gives the rate as an equality, not a bound. The error
falls below 10⁻¹⁰ by n = 182.

The limit is the *orthogonal* projector. This is the spectral theorem applied to
a polynomial filter: Γ is self-adjoint, γ equals 1 on the target part of the
spectrum and is bounded by q = 15/17 in modulus elsewhere, so Γⁿ → E({1}) in norm
at rate qⁿ. The limit coincides with the Riesz projection obtained by integrating
the resolvent around the isolated eigenvalue, which is self-adjoint here because
the contour is symmetric about the real axis (Kato 1966, III-§6.4 and V-§3).

This is not a named classical theorem but a corollary of the functional calculus,
and is stated here with its one-line proof rather than attributed. Its numerical
form — polynomial filters applied to project onto a chosen spectral window — is
standard practice in large-scale eigenvalue computation (Zhou, Saad, Tiago &
Chelikowsky 2006; Fang & Saad 2012).

---

## Deduction 3 — the denominator is forced, and the rate is the classical optimum

The number 99144 looks arbitrary. It is not. Consider the one-parameter family
Γ_ω = I − ωK², ω > 0, and ask which ω drives the complement to zero fastest. Off
the kernel, K² takes the five values {11664, 12544, 19600, 32400, 186624}. The
convergence factor is max |1 − ωa| over those a, which as a function of ω is the
maximum of the two endpoint lines, falling on the smallest and rising on the
largest. Its minimum is where they cross:

```
1 − ω·a_min = −(1 − ω·a_max)    ⟹    ω* = 2/(a_min + a_max)
```

With a_min = 11664 and a_max = 186624 this gives ω* = 2/198288 = 1/99144. So
**99144 is the arithmetic mean of the extreme nonzero eigenvalues of K²**, and the
denominator in line 2 is the unique minimax choice rather than a fitted constant.
The equioscillation — the error being equal in size and opposite in sign at the
two extremes — is what certifies optimality, and is visible in the table above as
±15/17 at c = 12 and c = 42 (Cheney 1966, Alternation Theorem, p. 75;
Trefethen 2013, Theorem 10.1).

The resulting rate is then forced too:

```
ρ* = (a_max − a_min)/(a_max + a_min) = (κ − 1)/(κ + 1),
κ  = a_max/a_min = 186624/11664 = 16
```

and (16 − 1)/(16 + 1) = 15/17 exactly.

This is the point of contact with the classical literature. Γ is precisely the
optimally relaxed Richardson iteration applied to the operator K²
(Richardson 1911; Saad 2003, Theorem 4.1 and Example 4.1), and 15/17 is the
textbook optimal convergence factor for condition number 16. The construction was
not derived from that theory, and agrees with it exactly.

Two features of this instance are unusual. The condition number is an exact small
integer rather than an estimate, because the spectrum is known in closed form. And
the extremes are attained at genuine eigenvalues rather than at the ends of an
enclosing interval, so the minimax bound is tight rather than conservative.

---

## Deduction 4 — the roots are forced

Deduction 3 forces the denominator once the roots are given. The roots themselves
are forced by the same table.

Treat the Casimir spectrum as a distribution, each eigenvalue weighted by the
dimension of its eigenspace:

```
μ  = (1/125) Σ dⱼ cⱼ        = 2250/125  = 18
σ² = (1/125) Σ dⱼ (cⱼ − 18)² = 18000/125 = 144
```

Both are exact integers, and 144 is a perfect square, so σ = 12 exactly.
Therefore μ − σ = 6 and μ + σ = 30.

The two roots of K are the points one standard deviation either side of the
spectral mean. No other pair in the spectrum has this property, and the pair is
symmetric about the mean by construction.

This is a statement about a seven-point distribution and nothing more. It does not
explain *why* the one-sigma points should be the right ones to select, and this
note does not claim that it does. What it establishes is narrower: the selector
was not free. Given the carrier, K is determined by a property of the carrier's
own spectrum, and Γ is then determined by K through Deduction 3. The construction
has no adjustable constants anywhere.

---

## Deduction 5 — the invariant

What survives the limit is a single number. Since P₄₇ is an orthogonal projector,
its trace is the dimension of its range, so

```
Ω_c = (1/125) tr P₄₇ = 47/125 = 0.376
```

Equivalently, and without reference to P₄₇ at all,

```
Ω_c = lim (1/125) tr Γⁿ        (n → ∞)
```

because tr Γⁿ = 47 + Σ γ(c)ⁿ over the non-kernel eigenvalues, and that sum
vanishes geometrically. Ω_c is therefore an invariant of the filter itself,
readable from its iterates without constructing the projector.

It also governs how a state is drawn in. For a state Ψ write p = ‖P₄₇Ψ‖²/‖Ψ‖² for
the fraction inside the kernel. One step of Γ fixes the kernel part and multiplies
the complement, so in the worst case — all complement weight sitting in an
equioscillation sector — p evolves by the exactly rational map

```
p ↦ p / (p + (1 − p)(15/17)²)
```

The odds p/(1−p) are multiplied by exactly 289/225 each step, so the log-odds is
linear in n. This is the logistic law in discrete form, with continuum slope
κ = ln(17/15) (Verhulst 1838).

Starting from p₀ = Ω_c = 47/125, the first four values are exact rationals:
47/125, 13583/31133, 3925487/7874237 and 1134465743/2022934493. The third is below
one half and the fourth above it, so the flow crosses half occupancy at step 3,
missing the midpoint at step 2 by 23263/15748474. Because the map is the worst
case, every other state crosses at that step or sooner.

---

## Scope

**Established.** Everything in Deductions 1 to 5 follows from the Casimir table by
finite arithmetic. The spectrum, the kernel dimension, the minimax step, the rate
15/17, the condition number 16, the mean 18 and variance 144, and the rational
trajectory are all exact. The convergence statement is an equality, not an
estimate. The arithmetic core has been checked independently in Lean 4.35.0 and
Coq 8.18, both reporting no axiom dependencies.

**Not claimed.** Four limits, stated plainly.

The one-sigma coincidence is an observation about a seven-point distribution. It
shows the roots were not free; it does not explain why the one-sigma points are
the natural ones to select, and no mechanism is offered here.

The optimality in Deduction 3 is optimality within the single-parameter family
I − ωK². Higher-degree polynomial filters converge faster, and Chebyshev
acceleration is the standard way to obtain them (Golub & Varga 1961). Nothing here
claims Γ is the best filter available, only that it is the best member of its own
family and that its constant was not fitted.

The step count in Deduction 5 is an upper bound, not the typical case. The
rational map assumes the entire complement contracts at 15/17, which happens only
when the complement weight lies in the c = 12 or c = 42 sectors. A state spread
across all five non-kernel sectors contracts faster and crosses earlier.

The quantity Ω_c is a dimension ratio of this specific carrier. Its appearance
elsewhere in the surrounding corpus is a separate matter and is not argued for
here.

**On Γ as a quantum operation.** Γ is self-adjoint with norm 1 but is not unitary,
so it is not a gate. It can be realised as the success branch of a two-outcome
channel with Kraus operators {Γ, √(I − Γ²)}, which is complete by construction,
and that channel dilates to a unitary on ℋ ⊗ ℂ² (Stinespring 1955; Kraus 1971;
Watrous 2018, Theorem 2.22). Any physical reading of the iteration must account
for the post-selection this involves.

---

## References

Every entry below was checked against a publisher, AMS, APS, IOP, Springer or
index record. Where a theorem or section number is given, that number was
confirmed in the stated edition. Section numbers that could not be confirmed have
been omitted rather than guessed, so a few entries cite a work without pinpointing
a location inside it.

### Iterative methods and the optimal relaxation parameter

1. L. F. Richardson, "The approximate arithmetical solution by finite differences
   of physical problems involving differential equations, with an application to
   the stresses in a masonry dam," *Philosophical Transactions of the Royal
   Society of London, Series A* **210** (1911), 307–357.
   [doi:10.1098/rsta.1911.0009](https://doi.org/10.1098/rsta.1911.0009). Read
   13 January 1910; commonly cited as Richardson (1910).
2. Y. Saad, *Iterative Methods for Sparse Linear Systems*, 2nd ed., SIAM,
   Philadelphia, 2003.
   [doi:10.1137/1.9780898718003](https://doi.org/10.1137/1.9780898718003).
   Theorem 4.1 (convergence iff spectral radius below 1) and Example 4.1
   (Richardson's iteration and its optimal α).
3. G. H. Golub and R. S. Varga, "Chebyshev semi-iterative methods, successive
   overrelaxation iterative methods, and second order Richardson iterative
   methods, Parts I and II," *Numerische Mathematik* **3** (1961), 147–156 and
   157–168. [doi:10.1007/BF01386013](https://doi.org/10.1007/BF01386013).
4. R. S. Varga, *Matrix Iterative Analysis*, 2nd rev. ed., Springer Series in
   Computational Mathematics **27**, Springer, Berlin, 2000.
   [doi:10.1007/978-3-642-05156-2](https://doi.org/10.1007/978-3-642-05156-2).
   Chapter 5, "Semi-Iterative Methods."

### Minimax approximation and equioscillation

5. E. W. Cheney, *Introduction to Approximation Theory*, 2nd ed., AMS Chelsea,
   1982. Alternation Theorem, p. 75.
6. L. N. Trefethen, *Approximation Theory and Approximation Practice*, SIAM,
   Philadelphia, 2013.
   [doi:10.1137/1.9781611975949](https://doi.org/10.1137/1.9781611975949).
   Theorem 10.1, equioscillation characterisation of best approximants.

### Spectral projectors and polynomial filters

7. T. Kato, *Perturbation Theory for Linear Operators*, Grundlehren der
   mathematischen Wissenschaften **132**, Springer, 1966; reprinted in Classics in
   Mathematics, 1995.
   [doi:10.1007/978-3-642-66282-9](https://doi.org/10.1007/978-3-642-66282-9).
   III-§6.4, separation of the spectrum and the Riesz projection; V-§3,
   self-adjointness of that projection in Hilbert space.
8. Y. Zhou, Y. Saad, M. L. Tiago and J. R. Chelikowsky, "Self-consistent-field
   calculations using Chebyshev-filtered subspace iteration," *Journal of
   Computational Physics* **219**(1) (2006), 172–184.
   [doi:10.1016/j.jcp.2006.03.017](https://doi.org/10.1016/j.jcp.2006.03.017).
9. H.-r. Fang and Y. Saad, "A filtered Lanczos procedure for extreme and interior
   eigenvalue problems," *SIAM Journal on Scientific Computing* **34**(4) (2012),
   A2220–A2246.
   [doi:10.1137/110836535](https://doi.org/10.1137/110836535).
10. H. Rutishauser, "Computational aspects of F. L. Bauer's simultaneous iteration
    method," *Numerische Mathematik* **13** (1969), 4–13.
    [doi:10.1007/BF02165269](https://doi.org/10.1007/BF02165269).

### Angular momentum and the Casimir decomposition

11. A. R. Edmonds, *Angular Momentum in Quantum Mechanics*, Princeton University
    Press, 1957; 2nd ed. 1960. Chapter 3, the coupling of angular momentum
    vectors.
12. D. A. Varshalovich, A. N. Moskalev and V. K. Khersonskii, *Quantum Theory of
    Angular Momentum*, World Scientific, Singapore, 1988.
    [doi:10.1142/0270](https://doi.org/10.1142/0270). Chapter 8, Clebsch–Gordan
    coefficients and 3jm symbols.
13. B. C. Hall, *Lie Groups, Lie Algebras, and Representations: An Elementary
    Introduction*, 2nd ed., Graduate Texts in Mathematics **222**, Springer, Cham,
    2015.
    [doi:10.1007/978-3-319-13467-3](https://doi.org/10.1007/978-3-319-13467-3).
    §10.2, the Casimir element.

### Quantum channels and dilation

14. W. F. Stinespring, "Positive functions on C*-algebras," *Proceedings of the
    American Mathematical Society* **6**(2) (1955), 211–216.
    [doi:10.1090/S0002-9939-1955-0069403-4](https://doi.org/10.1090/S0002-9939-1955-0069403-4).
15. K. Kraus, "General state changes in quantum theory," *Annals of Physics*
    **64**(2) (1971), 311–335.
    [doi:10.1016/0003-4916(71)90108-4](https://doi.org/10.1016/0003-4916(71)90108-4).
16. V. Paulsen, *Completely Bounded Maps and Operator Algebras*, Cambridge Studies
    in Advanced Mathematics **78**, Cambridge University Press, 2002. Theorem 4.1,
    Stinespring's dilation theorem, p. 43.
17. J. Watrous, *The Theory of Quantum Information*, Cambridge University Press,
    2018.
    [doi:10.1017/9781316848142](https://doi.org/10.1017/9781316848142).
    Theorem 2.22, the Choi, Kraus and Stinespring characterisations of complete
    positivity.
18. M. A. Nielsen and I. L. Chuang, *Quantum Computation and Quantum Information*,
    10th anniversary ed., Cambridge University Press, 2010. Theorem 8.1, the
    operator-sum representation, p. 368.

### The logistic law

19. P.-F. Verhulst, "Notice sur la loi que la population suit dans son
    accroissement," *Correspondance mathématique et physique* **10** (1838),
    113–121.
20. P.-F. Verhulst, "Recherches mathématiques sur la loi d'accroissement de la
    population," *Nouveaux Mémoires de l'Académie Royale des Sciences et
    Belles-Lettres de Bruxelles* **18** (1845), 1–42.
    [doi:10.3406/marb.1845.3438](https://doi.org/10.3406/marb.1845.3438). The
    paper that names the curve *logistique*.

**A note on two attributions.** The equioscillation theorem is habitually credited
to Chebyshev, but historians of the subject hold that he did not prove the general
result; the first proofs are usually assigned to Kirchberger (1902) and
Borel (1905). And the claim that an iterated polynomial filter converges to the
spectral projector is not a named classical theorem; it is a corollary of the
spectral theorem, which is why Deduction 2 proves it in a line rather than citing
it.

---

*Companion material: the Half-Occupancy Theorem, which takes Γ and Ω_c as given
and derives the metric signature, is in [README.md](README.md), with its
certificates in `certificate.py`, `quantum_simulation.py`, `HalfOccupancy.lean`
and `HalfOccupancy.v`. A live explainer is published at
<https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/emergent-spacetime/>.*
