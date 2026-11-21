# KKP-R scalar update and Heron iteration

Heron.lean and Heron.v independently prove orbit equality, the positive fixed
point, the exact one-step quadratic error, an all-iterate tail bound, and
convergence from every positive real seed for every positive real target.
They specialize the result to 47/125 and the inverse fifth power of the
golden ratio. They prove the radical and real-power identities, strict target
ordering, the derivative of the linear scaling, and constancy of the assigned
energy function. The scaled_step theorem gives the conjugacy law under positive
changes of scale. References to historical authors are outside the formal claims.

## Reproduction

* Lean 4.19.0 with mathlib tag v4.19.0. From the mathlib project directory run
  `lake env lean /absolute/path/to/Heron.lean`.
* Coq 8.20.1 with its standard library. Run `coqc Heron.v`.
* Python with SymPy 1.14.0. Run `python check.py`.

The convergence proofs use the standard real-number libraries of each system.
Both source files print the foundations used by the dual-limit theorem.
