(* KKP-R spectral bridge. Coq 8.18 Reals.
   Source prepared; no claim of compilation without a coqc run. *)
From Coq Require Import Reals Psatz Field.
Open Scope R_scope.
Module KKPSpectralBridge.

Theorem five_cycle_ratio : forall s:R,
  s*s=5 -> 5+s<>0 ->
  (5-s)/(5+s)=(3-s)/2.
Proof.
  intros s hs hden.
  field_simplify [hden]; nra.
Qed.

Theorem alpha_radical : forall s:R,
  (47/125)*((3-s)/2) = (141-47*s)/250.
Proof.
  intro s; field; lra.
Qed.

Theorem alpha_from_cycle : forall s:R,
  s*s=5 -> 5+s<>0 ->
  (47/125)*((5-s)/(5+s)) = (141-47*s)/250.
Proof.
  intros s hs hd.
  rewrite (five_cycle_ratio s hs hd).
  apply alpha_radical.
Qed.

Theorem normalized_trace_identity : forall r N w:R,
  N<>0 -> (r*w)/N=(r/N)*w.
Proof.
  intros r N w hN; field; auto.
Qed.

End KKPSpectralBridge.