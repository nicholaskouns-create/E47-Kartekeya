# E47 — corrected formalism

Five presentations of one object. Every claim below is either compiled, run, or
marked as not-compiled-here.

| presentation | file | status |
|---|---|---|
| symbolic | this file, §1–§2 | — |
| Lie algebra | this file, §3 | — |
| Lean 4 | `E47Certificate.lean` | **13/13 compile, Lean 4.35.0 core, zero axioms** |
| Coq | `E47Certificate.v` | written; **not compiled here** (no toolchain reachable) |
| Python | `validate_e47.py` | **all checks pass, exit 0** |

---

## §1 Typed signature

```
g            : LieAlgebra                       := su(2)
U(g)         : AssocAlgebra                     -- universal envelope
Δ⁽²⁾         : U(g) → U(g)^⊗3                   := X ↦ X⊗1⊗1 + 1⊗X⊗1 + 1⊗1⊗X
π            : g → End(V₂)                      -- spin-2 irrep, dim V₂ = 5
Σₑ           : Type                             := V₂^⊗3,        dim Σₑ = 125
ρ            : U(g) → End(Σₑ)                   := π^⊗3 ∘ Δ⁽²⁾
Ω            : Z(U(g))                          := Σₐ JₐJₐ        -- Casimir
C            : End(Σₑ)                          := ρ(Ω)
p            : ℂ[t]                             := (t−6)(t−30)
Kₑ           : End(Σₑ)                          := ρ(p(Ω)) = (C−6I)(C−30I)
Ψₑ           : Submodule_g Σₑ                   := ker Kₑ,        dim Ψₑ = 47
P            : End(Σₑ)                          := proj_{Ψₑ}
Γ(ε)         : ℝ → End(Σₑ)                      := ε ↦ I − ε Kₑ²
Ωc           : ℚ                                := dim Ψₑ / dim Σₑ = 47/125
M_J          : MultiplicitySpace                -- dim M_J = m_J
```

**Why `Ψₑ : Submodule_g`, not merely a subspace.** `p(Ω) ∈ Z(U(g))`, so `ρ(p(Ω))`
commutes with the whole action. The kernel of a central element is a submodule.
That is the structural reason the kernel is a union of isotypic components, and it
is not an accident of the chosen polynomial.

## §2 Claims, as judgements

Two judgement forms. `⊢ φ` carries a machine witness. `⊬ φ` carries an exhibited
obstruction — a refutation that names its counterexample, not a shrug.

```
L1  ⊢  Σₑ ≅ ⊕_{J=0}^{6} V_J ⊗ M_J ,   (m₀…m₆) = (1,3,5,4,3,2,1) ,  Σ(2J+1)m_J = 125
L2  ⊢  P² = P ,  P† = P ,  Tr P = 47 ,  KₑP = PKₑ = 0
L3  ⊢  spec(Kₑ²)∖{0} = {11664, 12544, 19600, 32400, 186624}
    ⊢  κ = λmax/λmin = 16 ,  ε* = 2/(λmin+λmax) = 1/99144 ,  ρ* = (κ−1)/(κ+1) = 15/17
    ⊢  ‖Γ(ε*)ⁿ − P‖₂ = (15/17)ⁿ            -- EQUALITY, verified to 12 digits
L4  ⊢  Ψₑ = (V₂⊗M₂) ⊕ (V₅⊗M₅) ,  dim = 5·5 + 11·2 = 47
L5  ⊢  Comm_{End Ψₑ}(ρ(g)) ≅ M₅(ℂ) ⊕ M₂(ℂ) ,  dim = 5² + 2² = 29
L6  ⊢  [C, ρ(σ)] = 0  ∀σ ∈ S₃

R1  ⊬  Ψₑ corrects single-factor errors.   WITNESS: ‖PJ₁ᶻ²P − αP‖_F = 6.25
R2  ⊬  Ψₑ corrects collective errors.      WITNESS: ‖PJ_tot,z²P − αP‖_F = 50.3
                                           WITNESS: ‖PC²P − αP‖_F = 2956
R3  ⊬  S₄ acts by symmetries.              WITNESS: ‖[e^{iπJ₁ˣ}, C]‖_F = 178.89
R4  ⊬  HBr derivation.                     OBSTRUCTION: the isometry W : H_HBr → ℂ¹²⁵
                                           is posited, never constructed
R5  ⊬  "Enochian" carries content.         OBSTRUCTION: it is a label on Σₑ
R6  ⊬  dim ker K₄ = 187.                   WITNESS: m₂ = 16, m₅ = 10 ⇒ 16·5 + 10·11 = 190
```

**New (not in the prior assessment):**

```
L7  ⊢  the image of ℂ[S₃] in Comm_{End Ψₑ}(ρ(g)) has rank 5, not 29.
       Schur–Weyl surjectivity FAILS for V₂^⊗3.
```

## §3 Lie-algebraic account

### 3.1 Why the kernel is a submodule

`Ω = Σₐ JₐJₐ` is central in `U(g)`, so by Schur it acts on `V_J` as the scalar
`J(J+1)`. Hence `ρ(p(Ω))` acts on `V_J ⊗ M_J` as `p(J(J+1)) · id`, and

```
ker ρ(p(Ω))  =  ⊕_{ J : p(J(J+1)) = 0 }  V_J ⊗ M_J
```

With `p(t) = (t−6)(t−30)` the roots are `J(J+1) ∈ {6,30}`, i.e. `J ∈ {2,5}`:

```
Ψₑ  =  (V₂ ⊗ M₂) ⊕ (V₅ ⊗ M₅),     dim M₂ = 5,  dim M₅ = 2
```

### 3.2 Commutant and noiseless subsystems

By the double-commutant theorem, the algebra commuting with `ρ(g)` on `Ψₑ` acts
only on the multiplicity factors:

```
Comm_{End Ψₑ}(ρ(g))  =  End(M₂) ⊕ End(M₅)  ≅  M₅(ℂ) ⊕ M₂(ℂ),   dim = 29
```

The protected objects are therefore **`M₂ ≅ ℂ⁵` and `M₅ ≅ ℂ²` — the multiplicity
spaces, not `Ψₑ` itself.** These are the noiseless subsystems. A logical qubit
lives in `M₅`; a logical five-level system lives in `M₂`.

### 3.3 Why Schur–Weyl does not save it

`S₃` permutes the tensor factors and commutes with `ρ`, giving an algebra map
`ℂ[S₃] → Comm`. For `(ℂ²)^⊗ⁿ` this map is **surjective** (Schur–Weyl duality).
For `V₂^⊗3` it is not: `dim ℂ[S₃] = 6`, and its image on `Ψₑ` has **rank 5**,
against a commutant of dimension 29. The permutation symmetry reaches a
five-dimensional sliver of the available logical algebra.

### 3.4 Why the error-correction claim fails, structurally

For a collective error `E = ρ(u)`, `u ∈ U(g)`, the Knill–Laflamme condition reads

```
P E†E P ∝ P     ⟺     ρ(u*u)|_{Ψₑ}  is a scalar
```

But **`Ψₑ` is not isotypic** — it carries `J = 2` and `J = 5`. Any central element
separating those two sectors breaks the condition, and the Casimir is the extreme
case:

```
Ω|_{Ψₑ}  =  6 ⊕ 30     (not a scalar)        ⇒   ‖PC²P − αP‖_F = 2956
```

For a single-factor error `E = J_{i,a}`, the obstruction is one step earlier:
`J_{i,a} ∉ ρ(U(g))`, and

```
[J_{1,z}, C]  =  2i ( J_{1,y}(J_{2,x}+J_{3,x}) − J_{1,x}(J_{2,y}+J_{3,y}) )  ≠  0
```

so `J_{1,z}` maps `Ψₑ` partly out of itself. It **leaks**, and leakage is detected
by `P`, not corrected.

### 3.5 The corrected statement

> `Ψₑ = ker (C−6I)(C−30I)` is a 47-dimensional `su(2)`-submodule of `V₂^⊗3`,
> realised as the limit of the contraction `Γ(ε*)ⁿ` at exact rate `(15/17)ⁿ`,
> carrying a 29-dimensional logical algebra `M₅(ℂ) ⊕ M₂(ℂ)` whose noiseless
> subsystems are the multiplicity spaces `ℂ⁵` and `ℂ²`.
>
> It **detects** errors that leak into `Ψₑ^⊥`.
> It **does not correct** single-factor errors — those fail at `[J_{i,a}, Ω] ≠ 0`.
> It **does not correct** collective errors — those fail because `Ψₑ` is not
> isotypic, `Ω|_{Ψₑ} = 6 ⊕ 30`.
> It is invariant under `S₃`, not under `S₄`.

## §4 Reproduce

```sh
python3 -I validate_e47.py          # exits 0; every lemma verified, not asserted
lean E47Certificate.lean            # 13/13, core Lean 4.35.0, zero axioms
coqc E47Certificate.v               # not run here — no toolchain was reachable
```
