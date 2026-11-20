(* Appendix B — Abstract specification sanity checks.
   Evidence scope: the encoded definitions and assumptions. *)
(* E47UnverifiedSuite.v — source supplied with the Complete Edition.
   Publication preserves author-submitted source; no coqc execution is claimed. *)
From Coq Require Import ZArith List Bool Lia.
Import ListNotations.
Open Scope Z_scope.
Module E47UnverifiedSuite.

Record AuthContext : Type := mkAuth { sigValid : bool; subjectActive : bool }.
Definition canInvoke (ctx : AuthContext) : bool :=
  andb (sigValid ctx) (subjectActive ctx).

Theorem sig_does_not_derive_invoke :
  exists ctx : AuthContext, sigValid ctx = true /\ canInvoke ctx = false.
Proof.
  exists (mkAuth true false). simpl. split; reflexivity.
Qed.

Theorem invoke_requires_active_subject :
  forall ctx : AuthContext, canInvoke ctx = true -> subjectActive ctx = true.
Proof.
  intros [sig subj] H. unfold canInvoke in H. simpl in *.
  apply andb_true_iff in H. destruct H as [_ Hsubj]. exact Hsubj.
Qed.

Theorem p27_carrier_partition :
  forall d27 d98 : Z, d27 = 27 -> d98 = 98 -> d27 + d98 = 125.
Proof. intros d27 d98 H1 H2. lia. Qed.

Theorem p27_inside_e47 :
  forall d27 d20 : Z, d27 = 27 -> d27 + d20 = 47 ->
    d20 = 20 /\ d27 < 47.
Proof. intros d27 d20 H1 H2. lia. Qed.

Record RatPair : Type := mkRat { num : Z; den : Z }.
Definition ratEq (a b : RatPair) : Prop :=
  (num a) * (den b) = (num b) * (den a).
Definition omegaC : RatPair := mkRat 47 125.
Definition omegaComp : RatPair := mkRat 78 125.

Theorem omega_c_complement_unity :
  (num omegaC) * (den omegaComp) + (num omegaComp) * (den omegaC) =
    (den omegaC) * (den omegaComp).
Proof. vm_compute. reflexivity. Qed.

Theorem omega_c_squared_exact :
  ratEq (mkRat ((num omegaC) * (num omegaC))
                ((den omegaC) * (den omegaC))) (mkRat 2209 15625).
Proof. unfold ratEq. vm_compute. reflexivity. Qed.

Record LinearAction (V : Type) : Type :=
  mkLin { zero : V; K : V -> V; G : V -> V }.
Arguments zero {V} _.
Arguments K {V} _.
Arguments G {V} _.

Theorem foundry_generator_preserves_e47 :
  forall {V : Type} (sys : LinearAction V),
    (forall x : V, K sys (G sys x) = G sys (K sys x)) ->
    G sys (zero sys) = zero sys ->
    forall x : V, K sys x = zero sys -> K sys (G sys x) = zero sys.
Proof.
  intros V sys Hcomm Hzero x Hker.
  rewrite Hcomm, Hker. exact Hzero.
Qed.

Definition q5Index (x y z : Z) : Z := 25 * x + 5 * y + z.

Theorem q5_index_injective :
  forall x1 y1 z1 x2 y2 z2 : Z,
    0 <= x1 < 5 -> 0 <= y1 < 5 -> 0 <= z1 < 5 ->
    0 <= x2 < 5 -> 0 <= y2 < 5 -> 0 <= z2 < 5 ->
    q5Index x1 y1 z1 = q5Index x2 y2 z2 ->
    x1 = x2 /\ y1 = y2 /\ z1 = z2.
Proof.
  intros. unfold q5Index in *. lia.
Qed.

Record Block2x2 (R : Type) : Type :=
  mkBlock { b00 : R; b01 : R; b10 : R; b11 : R }.
Arguments mkBlock {R} _ _ _ _.
Arguments b00 {R} _.
Arguments b01 {R} _.
Arguments b10 {R} _.
Arguments b11 {R} _.

Definition matMulZ (A B : Block2x2 Z) : Block2x2 Z :=
  mkBlock
    ((b00 A)*(b00 B) + (b01 A)*(b10 B))
    ((b00 A)*(b01 B) + (b01 A)*(b11 B))
    ((b10 A)*(b00 B) + (b11 A)*(b10 B))
    ((b10 A)*(b01 B) + (b11 A)*(b11 B)).

Theorem unitary_dilation_orthogonality :
  forall g s : Z, g * g + s * s = 1 ->
    let D := mkBlock g s s (-g) in
    matMulZ D D = mkBlock 1 0 0 1.
Proof.
  intros g s Hunit D. unfold D, matMulZ.
  simpl. f_equal; lia.
Qed.

Definition casimir (j : Z) : Z := j * (j + 1).
Definition K_poly (c : Z) : Z := (c - 6) * (c - 30).
Definition gammaNum (c : Z) : Z :=
  99144 - (K_poly c) * (K_poly c).

Definition check_off_kernel_contraction : bool :=
  forallb
    (fun j =>
      if negb (Z.eqb (K_poly (casimir j)) 0)
      then Z.leb (17 * Z.abs (gammaNum (casimir j))) (15 * 99144)
      else true) [0; 1; 2; 3; 4; 5; 6].

Theorem gamma_contraction_bound_15_17 :
  check_off_kernel_contraction = true.
Proof. vm_compute. reflexivity. Qed.

Record SplitState (A B : Type) : Type :=
  mkSplit { e47 : A; q78 : B }.
Arguments mkSplit {A B} _ _.
Arguments e47 {A B} _.
Arguments q78 {A B} _.

Definition projP {A B : Type}
    (z78 : B) (x : SplitState A B) : SplitState A B :=
  mkSplit (e47 x) z78.

Definition splitLayer {A B : Type}
    (f47 : A -> A) (f78 : B -> B)
    (x : SplitState A B) : SplitState A B :=
  mkSplit (f47 (e47 x)) (f78 (q78 x)).

Theorem splitLayer_commutes_with_P :
  forall {A B : Type} (z78 : B)
    (f47 : A -> A) (f78 : B -> B),
    f78 z78 = z78 ->
    forall x : SplitState A B,
      projP z78 (splitLayer f47 f78 x) =
        splitLayer f47 f78 (projP z78 x).
Proof.
  intros A B z78 f47 f78 Hzero [a b].
  unfold projP, splitLayer.
  simpl. rewrite Hzero. reflexivity.
Qed.
End E47UnverifiedSuite.
