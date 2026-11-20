# From the concrete Lean equalities to the kernel dimension

The existing Mathlib source `Identity/formal/e47/E47ConcreteMatrix.lean` defines the spin-2 tensor matrices `z`, `up`, and `down` on `Fin 125`, constructs `C = z*z + z + down*up`, and computes `K = (C-6I)(C-30I)` over the integers. Successful [CI run 44105525416](https://github.com/nicholaskouns-create/Identity/actions/runs/44105525416) compiled the same certificate inputs as the pinned Identity checkout. The source prints its axiom dependencies and uses Lean's native decision procedure for the concrete finite computations.

Let R be the compiled projector numerator, Q the compiled Bézout quotient at C, and d = 1814400. Over the rationals, set P = R/d. The compiled identities are R² = dR, KR = 0, tr(R) = 47d, and R + KQ = dI.

1. P² = P and KP = 0, so im P is contained in ker K.
2. Q commutes with K because both are polynomials in C. For any x in ker K, KQx = QKx = 0. The Bézout identity then gives Rx = dx, so Px = x and x lies in im P.
3. For an idempotent, the vector space splits as im P ⊕ ker P. In a basis adapted to that split, P is the identity on im P and zero on ker P. Thus dim ker K = dim im P = tr P = 47.

The final rank bridge above is a mathematical derivation. The standalone Lean theorem stating the dimension over ℚ remains open in this packet. The exact Python census independently recomputes the dimension.
