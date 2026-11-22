/- EinsteinRecovery.lean — Lean 4 core.
   Conditional stationary scalar-tensor recovery; not microscopic action emergence. -/
import Init
namespace EinsteinRecovery
abbrev Index := Fin 4
abbrev Tensor := Index → Index → Int
def addTensor (A B : Tensor) : Tensor := fun i j => A i j + B i j

theorem stationary_recovery
    (einstein cosmological matter correction : Tensor)
    (hField : ∀ i j, einstein i j + cosmological i j =
                           matter i j + correction i j)
    (hStationary : ∀ i j, correction i j = 0) :
    ∀ i j, einstein i j + cosmological i j = matter i j := by
  intro i j
  simpa [hStationary i j] using hField i j

theorem conserved_source
    (einstein cosmological matter : Tensor)
    (div : Tensor → Index → Int)
    (hLinear : ∀ (A B : Tensor) (j : Index),
      div (addTensor A B) j = div A j + div B j)
    (hBianchi : ∀ j, div einstein j = 0)
    (hMetric : ∀ j, div cosmological j = 0)
    (hEinstein : ∀ i j, einstein i j + cosmological i j = matter i j) :
    ∀ j, div matter j = 0 := by
  intro j
  have hEq : addTensor einstein cosmological = matter := by
    funext i k
    exact hEinstein i k
  rw [← hEq, hLinear einstein cosmological j, hBianchi j, hMetric j]
  rfl
end EinsteinRecovery
