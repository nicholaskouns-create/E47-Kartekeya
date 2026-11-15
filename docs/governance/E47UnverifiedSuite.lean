/- E47UnverifiedSuite.lean — standalone source supplied with the Complete Edition.
   Preservation of submitted formal verification appendix; publication does not itself execute Lean. -/
namespace E47UnverifiedSuite

structure AuthContext where
  sigValid : Bool
  subjectActive : Bool

def canInvoke (ctx : AuthContext) : Bool := ctx.sigValid && ctx.subjectActive

theorem sig_does_not_derive_invoke :
    ∃ ctx : AuthContext, ctx.sigValid = true ∧ canInvoke ctx = false := by
  exact ⟨{ sigValid := true, subjectActive := false }, rfl, rfl⟩

theorem invoke_requires_active_subject (ctx : AuthContext) :
    canInvoke ctx = true → ctx.subjectActive = true := by
  intro h
  cases ctx with
  | mk sig subj =>
    simp [canInvoke] at h
    exact h.2

theorem p27_carrier_partition (d27 d98 : Nat)
    (h1 : d27 = 27) (h2 : d98 = 98) : d27 + d98 = 125 := by
  omega

theorem p27_inside_e47 (d27 d20 : Nat)
    (h1 : d27 = 27) (h2 : d27 + d20 = 47) :
    d20 = 20 ∧ d27 < 47 := by
  omega

structure RatPair where
  num : Int
  den : Int

def ratEq (a b : RatPair) : Prop := a.num * b.den = b.num * a.den
def omegaC : RatPair := { num := 47, den := 125 }
def omegaComp : RatPair := { num := 78, den := 125 }

theorem omega_c_complement_unity :
    (omegaC.num * omegaComp.den + omegaComp.num * omegaC.den) =
    omegaC.den * omegaComp.den := by
  decide

theorem omega_c_squared_exact :
    ratEq { num := omegaC.num * omegaC.num, den := omegaC.den * omegaC.den }
      { num := 2209, den := 15625 } := by
  decide

structure LinearAction (V : Type) where
  zero : V
  K : V → V
  G : V → V

theorem foundry_generator_preserves_e47 {V : Type} (sys : LinearAction V)
    (hComm : ∀ x : V, sys.K (sys.G x) = sys.G (sys.K x))
    (hZero : sys.G sys.zero = sys.zero) (x : V)
    (hxInE47 : sys.K x = sys.zero) :
    sys.K (sys.G x) = sys.zero := by
  rw [hComm x, hxInE47, hZero]

def q5Index (x y z : Nat) : Nat := 25 * x + 5 * y + z

theorem q5_index_injective (x1 y1 z1 x2 y2 z2 : Nat)
    (hx1 : x1 < 5) (hy1 : y1 < 5) (hz1 : z1 < 5)
    (hx2 : x2 < 5) (hy2 : y2 < 5) (hz2 : z2 < 5)
    (hEq : q5Index x1 y1 z1 = q5Index x2 y2 z2) :
    x1 = x2 ∧ y1 = y2 ∧ z1 = z2 := by
  unfold q5Index at hEq
  omega

structure Block2x2 (R : Type) where
  b00 : R
  b01 : R
  b10 : R
  b11 : R

def matMul2x2 {R : Type} (add mul : R → R → R)
    (A B : Block2x2 R) : Block2x2 R :=
  { b00 := add (mul A.b00 B.b00) (mul A.b01 B.b10),
    b01 := add (mul A.b00 B.b01) (mul A.b01 B.b11),
    b10 := add (mul A.b10 B.b00) (mul A.b11 B.b10),
    b11 := add (mul A.b10 B.b01) (mul A.b11 B.b11) }

theorem unitary_dilation_orthogonality (g s : Int)
    (hUnit : g * g + s * s = 1) :
    let D : Block2x2 Int := { b00 := g, b01 := s, b10 := s, b11 := -g }
    matMul2x2 (· + ·) (· * ·) D D =
    { b00 := 1, b01 := 0, b10 := 0, b11 := 1 } := by
  dsimp [matMul2x2]
  have h2 : g * s + s * -g = 0 := by omega
  have h3 : s * g + -g * s = 0 := by omega
  have h4 : s * s + -g * -g = 1 := by
    have : -g * -g = g * g := Int.neg_mul_neg g g
    omega
  simp [hUnit, h2, h3, h4]

def casimir (j : Nat) : Int := (j : Int) * ((j : Int) + 1)
def K_poly (c : Int) : Int := (c - 6) * (c - 30)
def gammaNum (c : Int) : Int := 99144 - K_poly c * K_poly c

theorem gamma_contraction_bound_15_17 :
    ∀ j ∈ [0, 1, 2, 3, 4, 5, 6],
      K_poly (casimir j) ≠ 0 →
        17 * (gammaNum (casimir j)).natAbs ≤ 15 * 99144 := by
  decide

structure SplitState (α β : Type) where
  e47 : α
  q78 : β

def projP {α β : Type} (z78 : β) (x : SplitState α β) :
    SplitState α β := { e47 := x.e47, q78 := z78 }

def splitLayer {α β : Type} (f47 : α → α) (f78 : β → β)
    (x : SplitState α β) : SplitState α β :=
  { e47 := f47 x.e47, q78 := f78 x.q78 }

theorem splitLayer_commutes_with_P {α β : Type} (z78 : β)
    (f47 : α → α) (f78 : β → β)
    (hZero : f78 z78 = z78) (x : SplitState α β) :
    projP z78 (splitLayer f47 f78 x) =
      splitLayer f47 f78 (projP z78 x) := by
  simp [projP, splitLayer, hZero]

end E47UnverifiedSuite
