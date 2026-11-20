import Certificate

namespace E47

set_option maxRecDepth 2048
set_option maxHeartbeats 0

abbrev Vec := State → Int

private def isum {α : Type} (xs : List α) (f : α → Int) : Int := (xs.map f).sum

private theorem isum_congr {α : Type} (xs : List α) (f g : α → Int)
    (h : ∀ i, f i = g i) : isum xs f = isum xs g := by
  rw [show f = g from funext h]

private theorem isum_zero {α : Type} (xs : List α) : isum xs (fun _ => 0) = 0 := by
  induction xs <;> simp_all [isum]

private theorem isum_add {α : Type} (xs : List α) (f g : α → Int) :
    isum xs (fun k => f k + g k) = isum xs f + isum xs g := by
  induction xs with
  | nil => simp [isum]
  | cons x xs ih =>
    simp only [isum, List.map_cons, List.sum_cons] at *
    rw [ih]
    omega

private theorem isum_left {α : Type} (xs : List α) (a : Int) (f : α → Int) :
    isum xs (fun k => a * f k) = a * isum xs f := by
  induction xs with
  | nil => simp [isum]
  | cons x xs ih =>
    change a * f x + isum xs (fun k => a * f k) = a * (f x + isum xs f)
    rw [ih, Int.mul_add]

private theorem isum_right {α : Type} (xs : List α) (a : Int) (f : α → Int) :
    isum xs (fun k => f k * a) = isum xs f * a := by
  simpa only [Int.mul_comm] using isum_left xs a f

private theorem isum_swap {α β : Type} (xs : List α) (ys : List β) (f : α → β → Int) :
    isum xs (fun i => isum ys (f i)) = isum ys (fun j => isum xs (fun i => f i j)) := by
  induction xs with
  | nil =>
    simp only [isum, List.map_nil, List.sum_nil]
    exact (isum_zero ys).symm
  | cons x xs ih =>
    change isum ys (f x) + isum xs (fun i => isum ys (f i)) =
      isum ys (fun j => f x j + isum xs (fun i => f i j))
    rw [ih, isum_add]

def action (A : Mat) (x : Vec) : Vec :=
  fun i => isum entries (fun j => A i j * x j)

theorem action_mul (A B : Mat) (x : Vec) :
    action (mul A B) x = action A (action B x) := by
  funext i
  change (isum entries fun j => (isum entries fun k => A i k * B k j) * x j) =
    isum entries fun k => A i k * (isum entries fun j => B k j * x j)
  calc
    _ = isum entries (fun j => isum entries (fun k => A i k * (B k j * x j))) := by
      apply isum_congr
      intro j
      change (isum entries fun k => A i k * B k j) * x j = _
      rw [← isum_right]
      apply isum_congr
      intro k
      exact Int.mul_assoc _ _ _
    _ = isum entries (fun k => isum entries (fun j => A i k * (B k j * x j))) :=
      isum_swap entries entries _
    _ = _ := by
      apply isum_congr
      intro k
      exact isum_left entries _ _

theorem casimir_action_on_basis (x : Vec) :
    action casimir (action W x) = action W (fun j => eigenvalue j * x j) := by
  rw [← action_mul]
  funext i
  unfold action
  apply isum_congr
  intro j
  rw [eigenbasis_equation, Int.mul_assoc]

private theorem sum_delta (i : State) : isum entries (delta i) = 1 := by
  have h : ∀ j : State, isum entries (delta j) = 1 := by native_decide
  exact h i

private theorem scaled_delta_entry (h : Int) (x : Vec) (i j : State) :
    (h * delta i j) * x j = delta i j * (h * x i) := by
  by_cases e : i = j
  · subst j
    simp [delta]
  · simp [delta, e]

theorem W_left_inverse (x : Vec) (i : State) :
    action leftInverseNumerator (action W x) i = scalar * x i := by
  rw [← action_mul]
  unfold action
  have h := isum_congr entries (fun j => mul leftInverseNumerator W i j * x j)
    (fun j => delta i j * (scalar * x i)) (fun j => by
      change mul leftInverseNumerator W i j * x j = _
      rw [inverse_equations.1]
      exact scaled_delta_entry scalar x i j)
  rw [h, isum_right, sum_delta, Int.one_mul]

theorem W_right_inverse (y : Vec) (i : State) :
    action W (action leftInverseNumerator y) i = scalar * y i := by
  rw [← action_mul]
  unfold action
  have h := isum_congr entries (fun j => mul W leftInverseNumerator i j * y j)
    (fun j => delta i j * (scalar * y i)) (fun j => by
      change mul W leftInverseNumerator i j * y j = _
      rw [inverse_equations.2]
      exact scaled_delta_entry scalar y i j)
  rw [h, isum_right, sum_delta, Int.one_mul]

theorem W_injective {x y : Vec} : action W x = action W y → x = y := by
  intro h
  funext i
  have same := congrArg (fun v => action leftInverseNumerator v i) h
  change action leftInverseNumerator (action W x) i =
    action leftInverseNumerator (action W y) i at same
  rw [W_left_inverse, W_left_inverse] at same
  exact Int.eq_of_mul_eq_mul_left (by have := normalization.1; omega) same

private theorem action_sub_scaled (a : Int) (x y : Vec) :
    action W (fun i => x i - a * y i) =
      fun i => action W x i - a * action W y i := by
  funext i
  unfold action
  have h := isum_congr entries
    (fun j => W i j * (x j - a * y j))
    (fun j => W i j * x j + (-a) * (W i j * y j)) (fun j => by
      change W i j * (x j - a * y j) = W i j * x j + (-a) * (W i j * y j)
      rw [Int.mul_sub, Int.sub_eq_add_neg, Int.neg_mul,
        ← Int.mul_assoc (W i j) a, Int.mul_comm (W i j) a, Int.mul_assoc])
  rw [h, isum_add, isum_left]
  simp [Int.sub_eq_add_neg, Int.neg_mul]

def shifted (a : Int) (x : Vec) : Vec := fun i => action casimir x i - a * x i

theorem shifted_on_basis (a : Int) (x : Vec) :
    shifted a (action W x) = action W (fun i => (eigenvalue i - a) * x i) := by
  unfold shifted
  rw [casimir_action_on_basis, ← action_sub_scaled]
  apply congrArg (action W)
  funext i
  exact (Int.sub_mul _ _ _).symm

def nativeK (x : Vec) : Vec := shifted 6 (shifted 30 x)

theorem nativeK_on_basis (x : Vec) :
    nativeK (action W x) = action W (fun j => k j * x j) := by
  rw [nativeK, shifted_on_basis, shifted_on_basis]
  apply congrArg (action W)
  funext i
  simp [k, Int.mul_assoc]

private theorem action_zero : action W (fun _ => 0) = (fun _ => 0) := by
  funext i
  simpa only [action, Int.mul_zero] using isum_zero entries

theorem native_kernel (x : Vec) :
    nativeK (action W x) = (fun _ => 0) ↔ ∀ j : State, k j ≠ 0 → x j = 0 := by
  rw [nativeK_on_basis, ← action_zero]
  constructor
  · intro h j hj
    have heq := congrFun (W_injective h) j
    exact (Int.mul_eq_zero.mp heq).resolve_left hj
  · intro h
    apply congrArg (action W)
    funext j
    by_cases hj : k j = 0
    · simp [hj]
    · simp [h j hj]

private theorem action_scale (A : Mat) (a : Int) (x : Vec) :
    action A (fun i => a * x i) = (fun i => a * action A x i) := by
  funext i
  unfold action
  rw [← isum_left]
  apply isum_congr
  intro j
  change A i j * (a * x j) = a * (A i j * x j)
  ac_rfl

private theorem shifted_scale (a b : Int) (x : Vec) :
    shifted b (fun i => a * x i) = (fun i => a * shifted b x i) := by
  funext i
  unfold shifted
  rw [action_scale]
  change a * action casimir x i - b * (a * x i) =
    a * (action casimir x i - b * x i)
  rw [Int.mul_sub]
  have h : b * (a * x i) = a * (b * x i) := by ac_rfl
  rw [h]

/-- The kernel criterion applies to every native integer vector. The
left-inverse numerator gives its spectral coordinates with common scale. -/
theorem native_kernel_all (y : Vec) :
    nativeK y = (fun _ => 0) ↔
      ∀ j : State, k j ≠ 0 → action leftInverseNumerator y j = 0 := by
  have decode : action W (action leftInverseNumerator y) = (fun i => scalar * y i) :=
    funext (W_right_inverse y)
  rw [← native_kernel, decode]
  simp only [nativeK, shifted_scale]
  change nativeK y = (fun _ => 0) ↔ (fun j => scalar * nativeK y j) = (fun _ => 0)
  constructor
  · intro h
    rw [h]
    simp
  · intro h
    funext j
    have hj : scalar * nativeK y j = 0 := congrFun h j
    exact (Int.mul_eq_zero.mp hj).resolve_left (by have := normalization.1; omega)

def stepNumerator (x : Vec) : Vec :=
  fun j => 99144 * x j - nativeK (nativeK x) j

def signedNumerator (j : State) : Int := 99144 - square j

theorem step_on_basis (x : Vec) :
    stepNumerator (action W x) = action W (fun j => signedNumerator j * x j) := by
  unfold stepNumerator
  rw [nativeK_on_basis, nativeK_on_basis]
  have h := action_sub_scaled 1 (fun j => 99144 * x j) (fun j => k j * (k j * x j))
  simp only [Int.one_mul] at h
  have factors : (fun j => signedNumerator j * x j) =
      (fun j => 99144 * x j - k j * (k j * x j)) := by
    funext j
    change (99144 - k j * k j) * x j = 99144 * x j - k j * (k j * x j)
    rw [Int.sub_mul, Int.mul_assoc]
  rw [factors, h, action_scale]

def iterateNumerator : Nat → Vec → Vec
  | 0, x => x
  | n + 1, x => stepNumerator (iterateNumerator n x)

theorem iterate_on_basis (n : Nat) (x : Vec) :
    iterateNumerator n (action W x) = action W (fun j => signedNumerator j ^ n * x j) := by
  induction n with
  | zero => simp [iterateNumerator]
  | succ n ih =>
    rw [iterateNumerator, ih, step_on_basis]
    apply congrArg (action W)
    funext j
    rw [Int.pow_succ]
    ac_rfl

def kernelCoordinates (x : Vec) : Vec :=
  fun j => if k j = 0 then x j else 0

def projectorNumerator (y : Vec) : Vec :=
  action W (kernelCoordinates (action leftInverseNumerator y))

theorem projector_maps_into_kernel (y : Vec) :
    nativeK (projectorNumerator y) = (fun _ => 0) := by
  apply (native_kernel _).mpr
  intro j hj
  simp [kernelCoordinates, hj]

theorem projector_fixes_kernel_up_to_scale (y : Vec) (hy : nativeK y = (fun _ => 0)) :
    projectorNumerator y = (fun j => scalar * y j) := by
  have hz := (native_kernel_all y).mp hy
  have hm : kernelCoordinates (action leftInverseNumerator y) =
      action leftInverseNumerator y := by
    funext j
    by_cases hj : k j = 0
    · simp [kernelCoordinates, hj]
    · simp [kernelCoordinates, hj, hz j hj]
  unfold projectorNumerator
  rw [hm]
  exact funext (W_right_inverse y)

theorem projector_scaled_idempotent (y : Vec) :
    projectorNumerator (projectorNumerator y) =
      (fun j => scalar * projectorNumerator y j) :=
  projector_fixes_kernel_up_to_scale _ (projector_maps_into_kernel y)

#print axioms projector_scaled_idempotent
#print axioms native_kernel_all
#print axioms iterate_on_basis

end E47
