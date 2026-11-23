/-
KKP-R G47 dynamics — review draft, not compiler-attested.
Uses Mathlib for ring and rational arithmetic. No sorry/axiom in the stated
stationary theorem; the concrete integer U47 certificate is checked in Python,
not formalized by this source.
-/
import Mathlib

namespace KKPR_G47
def omega : ℚ := 47 / 125
def step (a δ ψ : ℚ) : ℚ := a * ψ + omega * δ
def trajectory (a δ ψ₀ : ℚ) : ℕ → ℚ
  | 0 => ψ₀
  | n + 1 => step a δ (trajectory a δ ψ₀ n)

theorem stationary_error (a δ ψ₀ ψstar : ℚ)
    (h : step a δ ψstar = ψstar) (n : ℕ) :
    trajectory a δ ψ₀ n - ψstar = a ^ n * (ψ₀ - ψstar) := by
  induction n with
  | zero => simp [trajectory]
  | succ n ih =>
      simp only [trajectory, step, pow_succ]
      rw [show a * ψstar + omega * δ = ψstar from h]
      rw [← h, ih]
      ring

theorem stationary_abs_bound (a δ ψ₀ ψstar : ℚ)
    (h : step a δ ψstar = ψstar) (n : ℕ) :
    |trajectory a δ ψ₀ n - ψstar| ≤ |a| ^ n * |ψ₀ - ψstar| := by
  rw [stationary_error a δ ψ₀ ψstar h n, abs_mul, abs_pow]
  exact le_refl _

/-- A scalar defect surrogate; this is not the tensorial divergence itself. -/
def scalarDefect (coeff grad : ℚ) : ℚ := coeff * grad

theorem scalar_defect_bound (coeff grad ε : ℚ)
    (hε : 0 ≤ ε) (hc : |coeff| ≤ 1) (hg : |grad| ≤ ε) :
    |scalarDefect coeff grad| ≤ ε := by
  rw [scalarDefect, abs_mul]
  calc
    |coeff| * |grad| ≤ 1 * |grad| :=
      mul_le_mul_of_nonneg_right hc (abs_nonneg _)
    _ = |grad| := one_mul _
    _ ≤ ε := hg
end KKPR_G47
