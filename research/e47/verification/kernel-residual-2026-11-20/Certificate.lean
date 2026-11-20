import Std
import Witness

namespace E47

abbrev State := Fin 125
abbrev Mat := State → State → Int

def digit (i : State) (site : Fin 3) : Int :=
  Int.ofNat ((i.val / (5 ^ (2 - site.val))) % 5) - 2

def sites : List (Fin 3) := [0, 1, 2]

def casimirEntry (row col : State) : Int :=
  let m := digit col
  let n := digit row
  let diagonal := if row = col then 18 + 2 * (m 0 * m 1 + m 0 * m 2 + m 1 * m 2) else 0
  diagonal + (sites.flatMap fun a => sites.map fun b =>
    if a != b && sites.all (fun c =>
      n c == m c + (if c = a then 1 else if c = b then -1 else 0)) then
      (2 - m a) * (2 + m b)
    else 0).sum

def casimirTable : Array (Array Int) := Array.ofFn fun row : State =>
  Array.ofFn fun col : State => casimirEntry row col

def casimir : Mat := fun row col => (casimirTable[row.val]!)[col.val]!

def W : Mat := fun r c => (columns[c.val]!)[r.val]!
def eigenvalue (j : State) : Int := eigenvalues[j.val]!
def weight (i : State) : Int :=
  let w := fun a : Int => if a = -2 ∨ a = 2 then 12 else if a = 0 then 2 else 3
  w (digit i 0) * w (digit i 1) * w (digit i 2)

def scalar : Int := norms.toList.foldl (fun a b => Int.ofNat (Int.lcm a b)) 1

def inverseTable : Array (Array Int) := Array.ofFn fun i : State =>
  Array.ofFn fun j : State => scalar / norms[i.val]! * W j i * weight j

def leftInverseNumerator : Mat := fun i j => (inverseTable[i.val]!)[j.val]!

def entries : List State := List.finRange 125

def mul (a b : Mat) (i j : State) : Int :=
  (entries.map fun k => a i k * b k j).sum

def delta (i j : State) : Int := if i = j then 1 else 0

set_option maxRecDepth 2048
set_option maxHeartbeats 0

theorem mem_entries (i : State) : i ∈ entries := by
  have hi : i.val < entries.length := by
    rw [entries, List.length_finRange]
    exact i.isLt
  apply List.mem_iff_getElem.2
  refine ⟨i.val, hi, ?_⟩
  simp only [entries, List.getElem_finRange]
  apply Fin.ext
  rfl

private theorem matrix_checked (p : State → State → Bool)
    (h : entries.all (fun i => entries.all (p i)) = true) :
    ∀ i j : State, p i j = true := by
  intro i j
  exact List.all_eq_true.1 (List.all_eq_true.1 h i (mem_entries i)) j (mem_entries j)

theorem eigenbasis_equation :
    ∀ i j : State, mul casimir W i j = W i j * eigenvalue j := by
  intro i j
  exact beq_iff_eq.mp (matrix_checked (fun a b => mul casimir W a b == W a b * eigenvalue b)
    (by native_decide) i j)

theorem inverse_equations :
    (∀ i j : State, mul leftInverseNumerator W i j = scalar * delta i j) ∧
    (∀ i j : State, mul W leftInverseNumerator i j = scalar * delta i j) := by
  constructor
  · intro i j
    exact beq_iff_eq.mp (matrix_checked
      (fun a b => mul leftInverseNumerator W a b == scalar * delta a b)
      (by native_decide) i j)
  · intro i j
    exact beq_iff_eq.mp (matrix_checked
      (fun a b => mul W leftInverseNumerator a b == scalar * delta a b)
      (by native_decide) i j)

theorem normalization :
    scalar > 0 ∧ (∀ j : State, norms[j.val]! > 0 ∧ scalar % norms[j.val]! = 0) := by
  native_decide

def weightedTranspose : Mat :=
  fun i j => W j i * weight j

theorem gram_equation :
    ∀ i j : State, mul weightedTranspose W i j = norms[i.val]! * delta i j := by
  intro i j
  exact beq_iff_eq.mp (matrix_checked
    (fun a b => mul weightedTranspose W a b == norms[a.val]! * delta a b)
    (by native_decide) i j)

def ladder (raise : Bool) (row col : State) : Int :=
  (sites.map fun a =>
    if sites.all (fun c => digit row c == digit col c +
      (if c = a then if raise then 1 else -1 else 0)) then
      if raise then 2 - digit col a else 2 + digit col a
    else 0).sum

def ladderTable (raise : Bool) : Array (Array Int) :=
  Array.ofFn fun row : State => Array.ofFn fun col : State => ladder raise row col

def raisingTable := ladderTable true
def loweringTable := ladderTable false

def totalLadder (raise : Bool) : Mat :=
  fun row col => ((if raise then raisingTable else loweringTable)[row.val]!)[col.val]!

def magnetization (i : State) : Int := digit i 0 + digit i 1 + digit i 2

theorem casimir_from_ladders : ∀ i j : State,
    2 * casimir i j = 2 * magnetization i ^ 2 * delta i j +
      mul (totalLadder true) (totalLadder false) i j +
      mul (totalLadder false) (totalLadder true) i j := by
  intro i j
  exact beq_iff_eq.mp (matrix_checked
    (fun a b => 2 * casimir a b == 2 * magnetization a ^ 2 * delta a b +
      mul (totalLadder true) (totalLadder false) a b +
      mul (totalLadder false) (totalLadder true) a b)
    (by native_decide) i j)

theorem spectrum_multiplicities :
    ([0, 2, 6, 12, 20, 30, 42] : List Int).map
      (fun c => (entries.filter fun j => eigenvalue j == c).length) =
        [1, 9, 25, 28, 27, 22, 13] := by
  native_decide

def k (j : State) : Int := (eigenvalue j - 6) * (eigenvalue j - 30)
def square (j : State) : Int := k j * k j

theorem kernel_multiplicity :
    (entries.filter fun j => k j == 0).length = 47 ∧
    (entries.filter fun j => k j != 0).length = 78 := by
  native_decide

theorem squared_spectrum :
    (∀ j : State, square j ∈ ([0, 11664, 12544, 19600, 32400, 186624] : List Int)) ∧
    (∀ u : Int, u ∈ ([0, 11664, 12544, 19600, 32400, 186624] : List Int) →
      ∃ j : State, square j = u) := by
  constructor
  · native_decide
  · intro u h
    simp only [List.mem_cons, List.not_mem_nil, or_false] at h
    rcases h with rfl | rfl | rfl | rfl | rfl | rfl
    · exact ⟨10, by native_decide⟩
    · exact ⟨35, by native_decide⟩
    · exact ⟨1, by native_decide⟩
    · exact ⟨63, by native_decide⟩
    · exact ⟨0, by native_decide⟩
    · exact ⟨112, by native_decide⟩

theorem discrete_bound :
    (∀ j : State, k j ≠ 0 →
      17 * (99144 - square j).natAbs ≤ 15 * 99144) ∧
    (∃ j : State, k j ≠ 0 ∧
      17 * (99144 - square j).natAbs = 15 * 99144) := by
  exact ⟨by native_decide, 35, by native_decide⟩

#print axioms casimir_from_ladders
#print axioms gram_equation
#print axioms eigenbasis_equation
#print axioms inverse_equations
#print axioms discrete_bound

end E47
