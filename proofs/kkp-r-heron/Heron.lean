import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.NormNum

open Filter Topology
namespace KKP
noncomputable section

def step (s x : ℝ) := (x + s / x) / 2
def orbit (s x : ℝ) : ℕ → ℝ
  | 0 => x
  | n + 1 => step s (orbit s x n)

theorem same_orbit (s x : ℝ) (a : ℕ → ℝ) (ha : a 0 = x)
    (hs : ∀ n, a (n+1) = (a n + s / a n) / 2) (n : ℕ) :
    a n = orbit s x n := by
  induction n with
  | zero => exact ha
  | succ n ih => rw [hs, ih]; rfl

theorem error_identity {s x r : ℝ} (hx : 0 < x) (hr : r^2 = s) :
    step s x - r = (x-r)^2 / (2*x) := by
  rw [← hr]; unfold step; field_simp; ring

theorem step_bounds {s x r : ℝ} (hx : 0 < x) (hr : 0 < r) (hs : r^2 = s) :
    0 ≤ step s x-r ∧ (r ≤ x → step s x-r ≤ (x-r)/2) := by
  rw [error_identity hx hs]
  constructor
  · positivity
  · intro h
    apply (div_le_iff₀ (by positivity : 0 < 2*x)).2
    nlinarith [mul_nonneg (sub_nonneg.mpr h) hr.le]

theorem tail_bound {s x r : ℝ} (hx : 0 < x) (hr : 0 < r) (hs : r^2 = s) (n : ℕ) :
    0 ≤ orbit s x (n+1)-r ∧
    orbit s x (n+1)-r ≤ (step s x-r)*(1/2:ℝ)^n := by
  induction n with
  | zero => simpa [orbit] using And.intro (step_bounds hx hr hs).1 (le_refl (step s x-r))
  | succ n ih =>
    have b := step_bounds (by linarith [ih.1] : 0 < orbit s x (n+1)) hr hs
    refine ⟨b.1, ?_⟩
    change step s (orbit s x (n+1)) - r ≤ _
    rw [pow_succ]
    linarith [b.2 (by linarith [ih.1]), ih.2]

theorem converges {s x : ℝ} (hs : 0 < s) (hx : 0 < x) :
    Tendsto (orbit s x) atTop (𝓝 (Real.sqrt s)) := by
  let r := Real.sqrt s
  have b := tail_bound hx (Real.sqrt_pos.2 hs) (Real.sq_sqrt hs.le)
  have hpow := tendsto_pow_atTop_nhds_zero_of_lt_one (by norm_num : (0:ℝ) ≤ 1/2)
    (by norm_num : (1/2:ℝ) < 1)
  have h : Tendsto (fun n => orbit s x (n+1)-r) atTop (𝓝 0) :=
    squeeze_zero (fun n => (b n).1) (fun n => (b n).2)
      (by simpa using hpow.const_mul (step s x-r))
  apply (tendsto_add_atTop_iff_nat 1).mp
  simpa using h.add (tendsto_const_nhds (x := r))

theorem fixed_iff {s x : ℝ} (hs : 0 < s) (hx : 0 < x) :
    step s x = x ↔ x = Real.sqrt s := by
  have hr := Real.sqrt_pos.2 hs
  have he := Real.sq_sqrt hs.le
  constructor
  · intro h
    unfold step at h
    field_simp at h
    nlinarith
  · intro h
    subst x
    have e := error_identity hr he
    exact sub_eq_zero.mp (by simpa using e)

def spec : ℝ := 47/125
def phi : ℝ := (1 + Real.sqrt 5)/2
def geom : ℝ := 1/phi^5

theorem golden : geom = (5*Real.sqrt 5-11)/2 := by
  have h := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 5)
  have hp : 0 < phi := by unfold phi; positivity
  have h2 : phi*phi = phi+1 := by unfold phi; nlinarith
  have h5 : phi^5 = 5*phi+3 := calc
    phi^5 = (phi*phi)*(phi*phi)*phi := by ring
    _ = 5*phi+3 := by rw [h2]; nlinarith [congrArg (fun t : ℝ => t*phi) h2]
  unfold geom
  rw [h5, div_eq_iff (by linarith : 5*phi+3 ≠ 0)]
  unfold phi
  nlinarith

theorem targets : 0 < geom ∧ geom < spec := by
  rw [golden]; unfold spec
  have h := Real.sq_sqrt (by norm_num : (0:ℝ) ≤ 5)
  have h0 := Real.sqrt_nonneg (5:ℝ)
  constructor <;> nlinarith

theorem both_limits {x : ℝ} (hx : 0 < x) :
    Tendsto (orbit spec x) atTop (𝓝 (Real.sqrt spec)) ∧
    Tendsto (orbit geom x) atTop (𝓝 (Real.sqrt geom)) :=
  ⟨converges (lt_trans targets.1 targets.2) hx, converges targets.1 hx⟩

theorem scaling (q : ℝ) : HasDerivAt (fun y : ℝ => 125*y) 125 q := by
  simpa using (hasDerivAt_id q).const_mul (125:ℝ)

def energy (_ : ℝ) : ℝ := -1/24
theorem energy_constant (s x : ℝ) : energy (step s x) = energy x := rfl

theorem scaled_step (s x c : ℝ) (hx : 0 < x) (hc : 0 < c) :
    step (c^2*s) (c*x) = c*step s x := by
  unfold step
  field_simp
  ring

theorem geometric_exponent : Real.sqrt geom = phi ^ (-5/2 : ℝ) := by
  have hp : 0 ≤ phi := by unfold phi; positivity
  have h : geom = phi ^ (-(5:ℝ)) := by
    rw [Real.rpow_neg hp, geom, one_div]
    norm_cast
  rw [Real.sqrt_eq_rpow, h, ← Real.rpow_mul hp]
  norm_num

#print axioms both_limits
end
end KKP
