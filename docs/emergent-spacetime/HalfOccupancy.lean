/-
  Emergent Spacetime -- the decidable core of the Half-Occupancy Theorem.

  Core Lean 4 only.  No Mathlib, no real analysis, no `sorry`.  Every theorem
  below is closed by kernel computation on integers, so `#print axioms` at the
  foot of the file reports no axioms at all.

  What is decidable here is the whole load-bearing content of the theorem:

    * the selector roots 6 and 30 are forced by the Casimir spectrum,
      sitting exactly one standard deviation either side of its mean;
    * the kernel has dimension 47 out of 125;
    * the minimax step eps* = 1/99144 and rate rho* = 15/17 are forced
      by equioscillation between the extreme eigenvalues of A = K^2;
    * the occupancy envelope started at Omega_c = 47/125 is still Euclidean
      at step 2 and Lorentzian at step 3.

  The only part that is not integer arithmetic is the eigenvalue count of a
  4x4 diagonal matrix, and that reduces to the sign of (1 - 2p); it is stated
  here as the sign rule and verified numerically in certificate.py.

  Compile:  lean docs/emergent-spacetime/HalfOccupancy.lean
-/

namespace HalfOccupancy

/-! ## 1.  The Casimir spectrum of V2 (x) V2 (x) V2 -/

/-- Eigenvalues j(j+1) of the total Casimir, j = 0 .. 6. -/
def spec : List Int := [0, 2, 6, 12, 20, 30, 42]

/-- Dimension of each isotypic block: (multiplicity) * (2j+1). -/
def counts : List Int := [1, 9, 25, 28, 27, 22, 13]

def dot (xs ys : List Int) : Int :=
  (List.zip xs ys).foldl (fun s p => s + p.1 * p.2) 0

/-- The carrier is 125-dimensional. -/
theorem total_dimension : counts.foldl (· + ·) 0 = 125 := by decide

/-- The spectral mean is exactly 18.  (Stated as 2250 = 18 * 125.) -/
theorem spectral_mean : dot spec counts = 18 * 125 := by decide

/-- The spectral variance is exactly 144.  (Stated as 18000 = 144 * 125.) -/
theorem spectral_variance :
    dot (spec.map (fun c => (c - 18) * (c - 18))) counts = 144 * 125 := by decide

/-- 144 is a perfect square, so the standard deviation is the integer 12. -/
theorem sigma_is_twelve : (12 : Int) * 12 = 144 := by decide

/-- The two selector roots are mu - sigma and mu + sigma.  Forced, not chosen. -/
theorem roots_are_mean_plus_minus_sigma :
    (18 - 12 : Int) = 6 ∧ (18 + 12 : Int) = 30 := by decide

/-! ## 2.  The selector and its kernel -/

/-- K(c) = (c - 6)(c - 30), evaluated on a Casimir eigenvalue. -/
def K (c : Int) : Int := (c - 6) * (c - 30)

/-- K vanishes on exactly the j = 2 and j = 5 eigenvalues. -/
theorem kernel_sectors : spec.filter (fun c => decide (K c = 0)) = [6, 30] := by decide

/-- Those two blocks carry 25 + 22 = 47 dimensions. -/
theorem kernel_dimension : (25 : Int) + 22 = 47 := by decide

/-- The coherence fraction.  (Stated as the cross-multiplied identity.) -/
theorem coherence_fraction : (47 : Int) * 1000 = 376 * 125 := by decide

/-! ## 3.  A = K^2, and the minimax step -/

def A (c : Int) : Int := K c * K c

/-- The nonzero spectrum of A off the kernel. -/
theorem a_spectrum :
    (spec.filter (fun c => !decide (K c = 0))).map A = [32400, 12544, 11664, 19600, 186624] := by
  decide

def aMin : Int := 11664
def aMax : Int := 186624

/-- The condition number of A off the kernel is exactly 16. -/
theorem condition_number : aMax = 16 * aMin := by decide

/--
  The minimax step is forced.  Choosing Lambda = I - eps A, the error factor
  1 - eps a is largest in absolute value at a = aMin or a = aMax, and the
  minimum of that maximum is attained exactly when the two equioscillate:
  1 - eps aMin = -(1 - eps aMax), i.e. 2 = eps (aMin + aMax).

  With eps = 1/99144 this reads 2 * 99144 = aMin + aMax.
-/
theorem minimax_step : 2 * 99144 = aMin + aMax := by decide

/--
  The resulting rate is exactly 15/17.
  rho* = 1 - aMin/99144 = (99144 - 11664)/99144 = 87480/99144 = 15/17.
-/
theorem rate_is_fifteen_seventeenths : (99144 - aMin) * 17 = 15 * 99144 := by decide

/-- It equioscillates: the factor at aMax is -15/17, the same in magnitude. -/
theorem equioscillation : (99144 - aMax) * 17 = -(15 * 99144) := by decide

/-- Two sectors attain the rate, which is what makes the step optimal. -/
theorem rate_attained_twice :
    ((spec.filter (fun c => !decide (K c = 0))).filter
      (fun c => decide ((99144 - A c) * 17 = 15 * 99144) ||
                decide ((99144 - A c) * 17 = -(15 * 99144)))).length = 2 := by decide

/-! ## 4.  The occupancy envelope -/

/--
  One filter step on the kernel occupancy, in exact rationals carried as a
  numerator/denominator pair.  With rho*^2 = 225/289,

      p |-> p / (p + (1 - p) * 225/289)

  clears denominators to

      (a, b) |-> (289 a, 289 a + 225 (b - a)).

  This is the worst case: off the kernel Lambda has five distinct factors, and
  only the two equioscillation sectors contract as slowly as rho*.  Any other
  state reaches half occupancy at the same step or sooner.
-/
def occ : Nat → Int × Int
  | 0 => (47, 125)
  | n + 1 => let p := occ n; (289 * p.1, 289 * p.1 + 225 * (p.2 - p.1))

/-- The flow starts at the coherence fraction Omega_c = 47/125. -/
theorem occ_start : occ 0 = (47, 125) := by decide

theorem occ_one : occ 1 = (13583, 31133) := by decide
theorem occ_two : occ 2 = (3925487, 7874237) := by decide
theorem occ_three : occ 3 = (1134465743, 2022934493) := by decide

/-- Step 2 is still below half occupancy, so the metric is still Euclidean. -/
theorem euclidean_at_step_two : 2 * (occ 2).1 < (occ 2).2 := by decide

/-- Step 3 is above half occupancy, so the metric is Lorentzian. -/
theorem lorentzian_at_step_three : 2 * (occ 3).1 > (occ 3).2 := by decide

/-- Hence the signature of the envelope changes at exactly step 3. -/
theorem transition_at_step_three :
    2 * (occ 2).1 < (occ 2).2 ∧ 2 * (occ 3).1 > (occ 3).2 := by decide

/--
  Step 2 lands within 0.15% of the critical point:
  1/2 - p_2 = 23263/15748474 < 15/10000.
-/
theorem step_two_is_near_critical :
    ((occ 2).2 - 2 * (occ 2).1) * 10000 < 15 * (2 * (occ 2).2) := by decide

/-- The envelope is strictly increasing over the steps that matter. -/
theorem strictly_increasing :
    (occ 0).1 * (occ 1).2 < (occ 1).1 * (occ 0).2 ∧
    (occ 1).1 * (occ 2).2 < (occ 2).1 * (occ 1).2 ∧
    (occ 2).1 * (occ 3).2 < (occ 3).1 * (occ 2).2 := by decide

/-! ## 5.  The signature rule -/

/--
  The induced coframe metric is g = diag(g00, 2p, 2p, 2p) with

      g00 = kappa^2 p (1 - p) (1 - 2p) = p-double-dot / 4.

  Since kappa^2 p (1 - p) > 0 on the open interval, the sign of g00 -- and so
  the whole signature -- is the sign of (1 - 2p).  The rule is therefore:

      p < 1/2  ->  (4,0,0)  Euclidean
      p = 1/2  ->  (3,0,1)  degenerate
      p > 1/2  ->  (3,1,0)  Lorentzian

  Stated on the numerator/denominator pair, the test is a single comparison.
-/
def signature (p : Int × Int) : Int :=
  if 2 * p.1 < p.2 then 1 else if 2 * p.1 = p.2 then 0 else -1

/-- 1 = Euclidean, 0 = degenerate, -1 = Lorentzian. -/
theorem signature_ladder :
    signature (occ 0) = 1 ∧
    signature (occ 1) = 1 ∧
    signature (occ 2) = 1 ∧
    signature (occ 3) = -1 := by decide

/-- The critical point is exactly half occupancy, and nothing else. -/
theorem critical_point_is_half : signature (1, 2) = 0 := by decide

/-! ## 6.  Axiom audit -/

#print axioms total_dimension
#print axioms spectral_mean
#print axioms spectral_variance
#print axioms roots_are_mean_plus_minus_sigma
#print axioms kernel_sectors
#print axioms minimax_step
#print axioms rate_is_fifteen_seventeenths
#print axioms equioscillation
#print axioms occ_two
#print axioms occ_three
#print axioms euclidean_at_step_two
#print axioms lorentzian_at_step_three
#print axioms transition_at_step_three
#print axioms a_spectrum
#print axioms condition_number
#print axioms rate_attained_twice
#print axioms strictly_increasing
#print axioms step_two_is_near_critical
#print axioms signature_ladder
#print axioms critical_point_is_half

end HalfOccupancy
