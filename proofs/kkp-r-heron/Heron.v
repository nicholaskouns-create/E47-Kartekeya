From Coq Require Import Reals Psatz Field Lia.
Open Scope R_scope.

Definition step (s x : R) := (x + s/x)/2.
Fixpoint orbit (s x : R) (n : nat) : R :=
  match n with O => x | S k => step s (orbit s x k) end.
Definition kkp (w x : R) := (x + w/x)/2.
Theorem same_orbit (s x : R) (a : nat -> R)
  (h0 : a O = x) (hs : forall n, a (S n) = kkp s (a n)) :
  forall n, a n = orbit s x n.
Proof. induction n; [exact h0 | cbn; rewrite hs, IHn; reflexivity]. Qed.

Lemma error_identity s x r : 0 < x -> r*r=s ->
  step s x-r = (x-r)^2/(2*x).
Proof. intros hx <-. unfold step. field; lra. Qed.

Lemma step_bounds s x r : 0 < r -> r*r=s -> 0<x ->
  0 <= step s x-r /\ (r<=x -> step s x-r <= (x-r)/2).
Proof.
  intros hr he hx. rewrite error_identity with (r:=r) by assumption. split.
  - unfold Rdiv; apply Rmult_le_pos; [apply pow2_ge_0|left; apply Rinv_0_lt_compat; nra].
  - intros h. apply (Rmult_le_reg_r (2*x)); [lra|].
    replace ((x-r)^2/(2*x)*(2*x)) with ((x-r)^2) by (field; lra).
    nra.
Qed.

Lemma tail_bound s x r : 0<r -> r*r=s -> 0<x -> forall n,
  0 <= orbit s x (S n)-r <= (step s x-r)/2^n.
Proof.
  intros hr he hx n. induction n as [|n [hl hu]].
  - simpl. split; [apply (step_bounds s x r hr he hx)|lra].
  - change (0 <= step s (orbit s x (S n))-r <= (step s x-r)/2^(S n)).
    destruct (step_bounds s (orbit s x (S n)) r hr he ltac:(lra)) as [a b].
    specialize (b ltac:(lra)). split; [exact a|].
    replace ((step s x-r)/2^(S n)) with (((step s x-r)/2^n)/2)
      by (simpl; field; apply pow_nonzero; lra). lra.
Qed.

Theorem converges s x : 0<s -> 0<x -> Un_cv (orbit s x) (sqrt s).
Proof.
  intros hs hx eps hp. set (r:=sqrt s).
  assert (hr:0<r) by (apply sqrt_lt_R0; exact hs).
  assert (he:r*r=s) by (apply sqrt_sqrt; lra).
  destruct (cv_pow_half (step s x-r) eps hp) as [N hn].
  exists (S N). intros [|k] hk; [lia|].
  specialize (hn k ltac:(lia)). pose proof (tail_bound s x r hr he hx k) as [a b].
  unfold Rdist in *. fold r. rewrite Rabs_right by lra.
  rewrite Rminus_0_r in hn. exact (Rle_lt_trans _ _ _ b (Rle_lt_trans _ _ _ (Rle_abs _) hn)).
Qed.

Theorem fixed_iff s x : 0<s -> 0<x -> (step s x=x <-> x=sqrt s).
Proof.
  intros hs hx. pose proof (sqrt_sqrt s ltac:(lra)).
  pose proof (sqrt_lt_R0 s hs). unfold step. split.
  - intro h. assert ((x+s/x)/2*x=x*x) by now rewrite h.
    replace ((x+s/x)/2*x) with ((x*x+s)/2) in H1 by (field; lra). nra.
  - intro h. subst x. apply Rminus_diag_uniq. change (step s (sqrt s) - sqrt s = 0). rewrite error_identity with (r:=sqrt s) by assumption. ring_simplify. unfold Rdiv; ring.
Qed.

Definition spec := 47/125.
Definition phi := (1+sqrt 5)/2.
Definition geom := / (phi^5).
Lemma golden : geom = (5*sqrt 5-11)/2.
Proof.
  pose proof (sqrt_sqrt 5 ltac:(lra)) as h.
  assert (hp:0<phi) by (unfold phi; pose proof (sqrt_pos 5); lra).
  assert (h2:phi*phi=phi+1) by (unfold phi; nra).
  assert (h5:phi^5=5*phi+3).
  { replace (phi^5) with ((phi*phi)*(phi*phi)*phi) by ring.
    rewrite h2. nra. }
  unfold geom. rewrite h5. apply (Rmult_eq_reg_r (5*phi+3)); [|lra].
  rewrite Rinv_l by lra. unfold phi. nra.
Qed.
Lemma targets : 0<geom /\ geom<spec.
Proof.
  rewrite golden. unfold spec. pose proof (sqrt_sqrt 5 ltac:(lra)).
  pose proof (sqrt_pos 5). split; nra.
Qed.
Corollary both_limits x : 0<x ->
  Un_cv (orbit spec x) (sqrt spec) /\ Un_cv (orbit geom x) (sqrt geom).
Proof. intros h. destruct targets. split; apply converges; lra. Qed.
Theorem scaling q : derivable_pt_lim (fun y => 125*y) q 125.
Proof.
  pose proof (derivable_pt_lim_scal id 125 q 1 (derivable_pt_lim_id q)) as H.
  rewrite Rmult_1_r in H. exact H.
Qed.
Definition energy (_ : R) := -1/24.
Theorem energy_constant s x : energy (step s x) = energy x.
Proof. reflexivity. Qed.
Print Assumptions both_limits.
Theorem scaled_step s x c : 0<x -> 0<c ->
  step (c^2*s) (c*x) = c*step s x.
Proof. intros. unfold step. field; nra. Qed.
Theorem geometric_exponent : sqrt geom = Rpower phi (-5/2).
Proof.
  assert (hp:0<phi) by (unfold phi; pose proof (sqrt_pos 5); lra).
  rewrite <- Rpower_sqrt by exact (proj1 targets).
  unfold geom. rewrite <- (Rpower_pow 5 phi hp), <- Rpower_Ropp.
  rewrite Rpower_mult. f_equal. change (- (1+1+1+1+1) * /2 = -5/2). lra.
Qed.
