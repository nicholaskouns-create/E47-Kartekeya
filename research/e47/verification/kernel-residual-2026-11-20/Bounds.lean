import Certificate

namespace E47

private theorem sum_le_scaled {α : Type} (xs : List α) (f g : α → Nat) (a b : Nat)
    (h : ∀ x ∈ xs, a * f x ≤ b * g x) :
    a * (xs.map f).sum ≤ b * (xs.map g).sum := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
    simp only [List.map_cons, List.sum_cons, Nat.mul_add]
    exact Nat.add_le_add (h x (by simp)) (ih fun y hy => h y (by simp [hy]))

def complement (j : State) : Nat := if k j = 0 then 0 else 1

def numerator (j : State) : Nat := (99144 - square j).natAbs

/-- Weighted squared norm of the unscaled residual after n discrete steps.
The squared denominator of the true residual is 99144^(2*n). -/
def residualEnergy (n : Nat) (mass : State → Nat) : Nat :=
  (entries.map fun j => complement j * ((numerator j ^ n)^2 * mass j)).sum

def initialEnergy (mass : State → Nat) : Nat :=
  (entries.map fun j => complement j * mass j).sum

/-- Exact, all-step, weighted squared-norm contraction in spectral coordinates.
The mass is arbitrary and can in particular encode squared amplitudes and Gram weights. -/
theorem contraction_all_steps (n : Nat) (mass : State → Nat) :
    ((17) ^ n)^2 * residualEnergy n mass ≤
      ((15 * 99144) ^ n)^2 * initialEnergy mass := by
  apply sum_le_scaled
  intro j _
  by_cases hj : k j = 0
  · simp [complement, hj]
  · simp only [complement, hj, if_false, Nat.one_mul]
    rw [← Nat.mul_assoc, ← Nat.mul_pow, ← Nat.mul_pow]
    apply Nat.mul_le_mul_right
    exact Nat.pow_le_pow_left (Nat.pow_le_pow_left (discrete_bound.1 j hj) n) 2

theorem k_residual_extrema :
    (∀ j : State, k j ≠ 0 → 108 ≤ (k j).natAbs ∧ (k j).natAbs ≤ 432) ∧
    (∃ j : State, (k j).natAbs = 108) ∧
    (∃ j : State, (k j).natAbs = 432) := by
  exact ⟨by native_decide, ⟨35, by native_decide⟩, ⟨112, by native_decide⟩⟩

theorem signed_k_has_negative_mode : ∃ j : State, k j = -108 := by
  exact ⟨35, by native_decide⟩

#print axioms contraction_all_steps

end E47
