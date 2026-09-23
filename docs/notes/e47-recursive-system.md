# E47 in Two Pages

**K², why V₂ has dimension 5, recursive invariant selection, and the boundary of the claim.**

Public reading surface: https://nicholaskouns-create.github.io/E47-Kartekeya/notes/e47-recursive-system/  
Notion: https://app.notion.com/p/3e446094fd30811ba779f8af95af5c02?pvs=204  
Supabase: https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/e47-recursive-note

---

## PAGE 1 · What the object is

### Why V₂ has dimension 5

The starting object is the spin-2 irreducible representation of SU(2), denoted V₂. A spin-j irreducible representation has dimension 2j+1. For j=2, dim V₂=5.

The carrier is V = V₂⊗V₂⊗V₂, with dim V = 5³ = 125.

### The selector

Let C = J_tot². On this carrier its eigenvalues are {0,2,6,12,20,30,42}, with state multiplicities {1,9,25,28,27,22,13}.

Define K = (C−6I)(C−30I). Then E₄₇ = ker K = E₆ ⊕ E₃₀ and dim E₄₇ = 25+22 = 47. The orthogonal projector is P₄₇=P₆+P₃₀.

### What K² is and why it matters

K is Hermitian but has signed nonzero eigenvalues. K²=K†K is positive semidefinite and preserves the same kernel.

Define Γε = I−εK². For 0<ε<2/186624, the complement of E₄₇ contracts while E₄₇ is fixed, so Γεⁿ→P₄₇.

The optimal uniform step is ε*=1/99144 with complement factor ρ*=15/17. The exact rank fraction is Ωc=47/125=0.376.

---

## PAGE 2 · Recursive execution

### Executable residual-gated runtime

The finite contraction is now implemented as the explicit cycle:

**Σ → Ψ → Γⁿ → Ω → Λ → Σ′ → α → Σ**

with

- K=(C−6I)(C−30I)
- Γ=I−K²/99144
- Λ=P₆+P₃₀
- Ω := ||K M_pre|| ≤ τ

The certainty gate Ω is evaluated **before** Λ. Projecting first would make KΛM≈0 by construction and turn the gate into a tautology instead of a convergence test.

Validated seeded smoke test at tolerance 1e−10:

- certificate: PASS
- rank Λ: 47
- Ωc: 47/125 = 0.376
- positive spec(K²): {11664,12544,19600,32400,186624}
- transient bound: 15/17
- contractions: 252
- final pre-projection residual: 9.353585941533422e−11
- post-projection residual: 4.833244591885603e−12
- source SHA-256: `8ec779cbb5247f9dc733cd2f4e341c8378d5ec6acfc21d56d9d3da33b322e716`

Runtime source: https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/src/e47/recursive_runtime.py

### Claim boundary

- 47 is not asserted to be the universal dimensionality of nature.
- 47/125 is the exact rank fraction of this construction, not a universal measured constant.
- The finite spectral theorem does not by itself establish gravity, spacetime, consciousness, biology, propulsion, particle physics, or quantum hardware.
- A downstream application of E47 is an additional map whose validity must be established in the destination domain.
- Similar dimensions, ratios, or visual structures do not identify another system with E47 without an explicit map or intertwiner.

**Core exact claim:** V₂⊗³ is a 125-dimensional carrier. K=(C−6I)(C−30I) has a 47-dimensional kernel. K² generates a stable contraction whose powers converge to P₄₇ under the stated step-size bound.

**Executable interpretation:** preserve what satisfies the kernel condition, contract what does not, evaluate certainty on the unprojected residual, then project and pass the invariant forward.
