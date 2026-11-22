(* EinsteinRecovery.v — Coq 8.18 standard library.
   Conditional Einstein recovery and conservation, not microscopic emergence. *)
From Coq Require Import Reals Lra Psatz FunctionalExtensionality.
Open Scope R_scope.
Module EinsteinRecovery.
Definition Index := nat.
Definition Tensor := Index -> Index -> R.
Definition addTensor (A B : Tensor) : Tensor := fun i j => A i j + B i j.
Theorem stationary_recovery :
  forall (G L T correction : Tensor),
  (forall i j, G i j + L i j = T i j + correction i j) ->
  (forall i j, correction i j = 0) ->
  forall i j, G i j + L i j = T i j.
Proof.
  intros G L T correction hField hStationary i j.
  specialize (hField i j).
  rewrite (hStationary i j) in hField.
  lra.
Qed.
Theorem conserved_source :
  forall (G L T : Tensor) (div : Tensor -> Index -> R),
  (forall A B j, div (addTensor A B) j = div A j + div B j) ->
  (forall j, div G j = 0) ->
  (forall j, div L j = 0) ->
  (forall i j, G i j + L i j = T i j) ->
  forall j, div T j = 0.
Proof.
  intros G L T div hLinear hBianchi hMetric hEinstein j.
  assert (hEq : addTensor G L = T).
  { apply functional_extensionality; intro i.
    apply functional_extensionality; intro k.
    exact (hEinstein i k). }
  rewrite <- hEq.
  rewrite (hLinear G L j), (hBianchi j), (hMetric j).
  lra.
Qed.
End EinsteinRecovery.
