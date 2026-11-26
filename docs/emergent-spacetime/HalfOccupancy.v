(*
  Emergent Spacetime -- the decidable core of the Half-Occupancy Theorem.

  An independent mirror of HalfOccupancy.lean in Coq, sharing no code and no
  library with it.  Every theorem is closed by kernel computation on integers
  (vm_compute), so Print Assumptions at the foot of the file reports that
  nothing here rests on an axiom.

  Two proof assistants with different kernels, different arithmetic
  implementations and different tactic languages agree on the same integers.

  Compile:  coqc -q docs/emergent-spacetime/HalfOccupancy.v
*)

Require Import ZArith List.
Import ListNotations.
Open Scope Z_scope.

(* ------------------------------------------------------------------ *)
(* 1.  The Casimir spectrum of V2 (x) V2 (x) V2                        *)
(* ------------------------------------------------------------------ *)

(* Eigenvalues j(j+1) of the total Casimir, j = 0 .. 6. *)
Definition spec : list Z := [0; 2; 6; 12; 20; 30; 42].

(* Dimension of each isotypic block: (multiplicity) * (2j+1). *)
Definition counts : list Z := [1; 9; 25; 28; 27; 22; 13].

Definition dot (xs ys : list Z) : Z :=
  fold_left (fun s p => s + fst p * snd p) (combine xs ys) 0.

(* The carrier is 125-dimensional. *)
Theorem total_dimension : fold_left Z.add counts 0 = 125.
Proof. vm_compute. reflexivity. Qed.

(* The spectral mean is exactly 18.  Stated as 2250 = 18 * 125. *)
Theorem spectral_mean : dot spec counts = 18 * 125.
Proof. vm_compute. reflexivity. Qed.

(* The spectral variance is exactly 144.  Stated as 18000 = 144 * 125. *)
Theorem spectral_variance :
  dot (map (fun c => (c - 18) * (c - 18)) spec) counts = 144 * 125.
Proof. vm_compute. reflexivity. Qed.

(* 144 is a perfect square, so the standard deviation is the integer 12. *)
Theorem sigma_is_twelve : 12 * 12 = 144.
Proof. vm_compute. reflexivity. Qed.

(* The two selector roots are mu - sigma and mu + sigma.  Forced, not chosen. *)
Theorem roots_are_mean_plus_minus_sigma : 18 - 12 = 6 /\ 18 + 12 = 30.
Proof. split; vm_compute; reflexivity. Qed.

(* ------------------------------------------------------------------ *)
(* 2.  The selector and its kernel                                     *)
(* ------------------------------------------------------------------ *)

Definition K (c : Z) : Z := (c - 6) * (c - 30).

(* K vanishes on exactly the j = 2 and j = 5 eigenvalues. *)
Theorem kernel_sectors : filter (fun c => Z.eqb (K c) 0) spec = [6; 30].
Proof. vm_compute. reflexivity. Qed.

(* Those two blocks carry 25 + 22 = 47 dimensions. *)
Theorem kernel_dimension : 25 + 22 = 47.
Proof. vm_compute. reflexivity. Qed.

(* The coherence fraction 47/125 = 0.376, cross-multiplied. *)
Theorem coherence_fraction : 47 * 1000 = 376 * 125.
Proof. vm_compute. reflexivity. Qed.

(* ------------------------------------------------------------------ *)
(* 3.  A = K^2, and the minimax step                                   *)
(* ------------------------------------------------------------------ *)

Definition A (c : Z) : Z := K c * K c.

Definition offKernel : list Z := filter (fun c => negb (Z.eqb (K c) 0)) spec.

Theorem a_spectrum :
  map A offKernel = [32400; 12544; 11664; 19600; 186624].
Proof. vm_compute. reflexivity. Qed.

Definition aMin : Z := 11664.
Definition aMax : Z := 186624.

(* The condition number of A off the kernel is exactly 16. *)
Theorem condition_number : aMax = 16 * aMin.
Proof. vm_compute. reflexivity. Qed.

(*
  The minimax step is forced.  With Lambda = I - eps A the error factor
  1 - eps a is extremal at a = aMin or a = aMax, and the minimum of that
  maximum is attained exactly when the two equioscillate:
     1 - eps aMin = -(1 - eps aMax),  i.e.  2 = eps (aMin + aMax).
  With eps = 1/99144 this reads 2 * 99144 = aMin + aMax.
*)
Theorem minimax_step : 2 * 99144 = aMin + aMax.
Proof. vm_compute. reflexivity. Qed.

(* rho* = 1 - aMin/99144 = 87480/99144 = 15/17, cross-multiplied. *)
Theorem rate_is_fifteen_seventeenths : (99144 - aMin) * 17 = 15 * 99144.
Proof. vm_compute. reflexivity. Qed.

(* It equioscillates: the factor at aMax is -15/17, equal in magnitude. *)
Theorem equioscillation : (99144 - aMax) * 17 = -(15 * 99144).
Proof. vm_compute. reflexivity. Qed.

(* Two sectors attain the rate, which is what makes the step optimal. *)
Theorem rate_attained_twice :
  length (filter (fun c => orb (Z.eqb ((99144 - A c) * 17) (15 * 99144))
                               (Z.eqb ((99144 - A c) * 17) (-(15 * 99144))))
                 offKernel) = 2%nat.
Proof. vm_compute. reflexivity. Qed.

(* ------------------------------------------------------------------ *)
(* 4.  The occupancy envelope                                          *)
(* ------------------------------------------------------------------ *)

(*
  One filter step on the kernel occupancy, in exact rationals carried as a
  numerator/denominator pair.  With rho*^2 = 225/289,

      p |-> p / (p + (1 - p) * 225/289)

  clears denominators to

      (a, b) |-> (289 a, 289 a + 225 (b - a)).

  This is the worst case.  Off the kernel Lambda has five distinct factors and
  only the two equioscillation sectors contract as slowly as rho*, so any other
  state reaches half occupancy at the same step or sooner.
*)
Fixpoint occ (n : nat) : Z * Z :=
  match n with
  | O => (47, 125)
  | S m => let p := occ m in (289 * fst p, 289 * fst p + 225 * (snd p - fst p))
  end.

(* The flow starts at the coherence fraction Omega_c = 47/125. *)
Theorem occ_start : occ 0 = (47, 125).
Proof. vm_compute. reflexivity. Qed.

Theorem occ_one : occ 1 = (13583, 31133).
Proof. vm_compute. reflexivity. Qed.

Theorem occ_two : occ 2 = (3925487, 7874237).
Proof. vm_compute. reflexivity. Qed.

Theorem occ_three : occ 3 = (1134465743, 2022934493).
Proof. vm_compute. reflexivity. Qed.

(* Step 2 is still below half occupancy: the metric is still Euclidean. *)
Theorem euclidean_at_step_two : 2 * fst (occ 2) < snd (occ 2).
Proof. vm_compute. reflexivity. Qed.

(* Step 3 is above half occupancy: the metric is Lorentzian. *)
Theorem lorentzian_at_step_three : 2 * fst (occ 3) > snd (occ 3).
Proof. vm_compute. reflexivity. Qed.

(* Hence the signature of the envelope changes at exactly step 3. *)
Theorem transition_at_step_three :
  2 * fst (occ 2) < snd (occ 2) /\ 2 * fst (occ 3) > snd (occ 3).
Proof. split; vm_compute; reflexivity. Qed.

(* Step 2 lands within 0.15% of the critical point:
   1/2 - p_2 = 23263/15748474 < 15/10000. *)
Theorem step_two_is_near_critical :
  (snd (occ 2) - 2 * fst (occ 2)) * 10000 < 15 * (2 * snd (occ 2)).
Proof. vm_compute. reflexivity. Qed.

(* The envelope is strictly increasing over the steps that matter. *)
Theorem strictly_increasing :
  fst (occ 0) * snd (occ 1) < fst (occ 1) * snd (occ 0) /\
  fst (occ 1) * snd (occ 2) < fst (occ 2) * snd (occ 1) /\
  fst (occ 2) * snd (occ 3) < fst (occ 3) * snd (occ 2).
Proof. repeat split; vm_compute; reflexivity. Qed.

(* ------------------------------------------------------------------ *)
(* 5.  The signature rule                                              *)
(* ------------------------------------------------------------------ *)

(*
  The induced coframe metric is g = diag(g00, 2p, 2p, 2p) with

      g00 = kappa^2 p (1 - p) (1 - 2p) = p'' / 4.

  Since kappa^2 p (1 - p) > 0 on the open interval, the sign of g00 -- and so
  the whole signature -- is the sign of (1 - 2p):

      p < 1/2  ->  (4,0,0)  Euclidean
      p = 1/2  ->  (3,0,1)  degenerate
      p > 1/2  ->  (3,1,0)  Lorentzian

  Returned as 1, 0 and -1 respectively.
*)
Definition signature (p : Z * Z) : Z :=
  if Z.ltb (2 * fst p) (snd p) then 1
  else if Z.eqb (2 * fst p) (snd p) then 0
  else -1.

Theorem signature_ladder :
  signature (occ 0) = 1 /\
  signature (occ 1) = 1 /\
  signature (occ 2) = 1 /\
  signature (occ 3) = -1.
Proof. repeat split; vm_compute; reflexivity. Qed.

(* The critical point is exactly half occupancy, and nothing else. *)
Theorem critical_point_is_half : signature (1, 2) = 0.
Proof. vm_compute. reflexivity. Qed.

(* ------------------------------------------------------------------ *)
(* 6.  Axiom audit                                                     *)
(* ------------------------------------------------------------------ *)

Print Assumptions total_dimension.
Print Assumptions spectral_mean.
Print Assumptions spectral_variance.
Print Assumptions roots_are_mean_plus_minus_sigma.
Print Assumptions kernel_sectors.
Print Assumptions a_spectrum.
Print Assumptions condition_number.
Print Assumptions minimax_step.
Print Assumptions rate_is_fifteen_seventeenths.
Print Assumptions equioscillation.
Print Assumptions rate_attained_twice.
Print Assumptions occ_two.
Print Assumptions occ_three.
Print Assumptions euclidean_at_step_two.
Print Assumptions lorentzian_at_step_three.
Print Assumptions transition_at_step_three.
Print Assumptions step_two_is_near_critical.
Print Assumptions strictly_increasing.
Print Assumptions signature_ladder.
Print Assumptions critical_point_is_half.
