(* KKP-R G47: rational stationary recursion; compiler-unverified draft.
   Tensorial Bianchi is a separate geometric obligation. *)
From Coq Require Import QArith Qring.
Open Scope Q_scope.

Definition omega : Q := 47#125.
Definition step (a delta psi : Q) : Q := a*psi + omega*delta.
Fixpoint trajectory (a delta psi0 : Q) (n : nat) : Q :=
  match n with O => psi0 | S k => step a delta (trajectory a delta psi0 k) end.
Fixpoint qpow (a : Q) (n : nat) : Q :=
  match n with O => 1 | S k => a * qpow a k end.

Theorem stationary_error :
  forall a delta psi0 psistar n,
    step a delta psistar == psistar ->
    trajectory a delta psi0 n - psistar ==
    qpow a n * (psi0 - psistar).
Proof.
  intros a delta psi0 psistar n hfix.
  induction n as [|n ih].
  - simpl. ring.
  - simpl.
    unfold step in hfix.
    setoid_replace psistar with (a*psistar+omega*delta)
      by (symmetry; exact hfix).
    setoid_replace (a*trajectory a delta psi0 n+omega*delta-
      (a*psistar+omega*delta))
      with (a*(trajectory a delta psi0 n-psistar)) by ring.
    setoid_rewrite ih.
    ring.
Qed.
