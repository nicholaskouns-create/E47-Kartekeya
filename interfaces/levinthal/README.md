# 02 FOLD · Levinthal’s paradox, resolved by spectral depth

Public route: https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/levinthal/

The Levinthal visualizer of lab 02 FOLD. InvariFold remains the protein cinema.

- **The gap.** For each preset (CLN025, Trp-cage, Villin HP-35, Ala-14, N = 100): blind enumeration bᴺ, the measured folding time ÷ τ₀, and the spectral depth of a convex funnel of the same length, on one log scale.
- **§1 The count.** |Σ| = bᴺ and bᴺ·τ₀ with τ₀ = 10⁻¹³ s, the toy count of `research/levinthal-recursive-contraction.md`.
- **§2 The theorem.** D(δ) = ⌈ln(1/δ)/ln(1/q∗)⌉, q∗ = (ℛ − 1)/(ℛ + 1), with ½(ℛ − 1)ln(1/δ) ≤ D(δ) ≤ ⌈½(ℛ + 1)ln(1/δ)⌉.
- **§3 Fold it.** A 2D Gō funnel (compact β-meander native, contact-graph Laplacian L). Iterates Λ = I − ε∗A with A = L or A = L² (InvariFold’s form) and plots the residual against q∗ⁿ.
- **§4 The landscape decides ℛ.** Exact mean first-passage times of the single-residue Metropolis chain, lumped exactly onto the native count n, for the golf course and a uniform bias U; the funnel’s D(δ); measured fast folders.
- **§5 E₄₇.** ℛ = 16, ε∗ = 1/99144, q∗ = 15/17, D(10⁻¹²) = 221, five exact steps.

Everything is computed in the browser in double precision. The eigenvalue routine (Householder + implicit QL) and the first-passage formula were cross-checked against NumPy to 10⁻¹⁴.

Evidence: E0 for the depth law and the E₄₇ constants; E1 for the computed spectra, depths and first-passage times; E3 for the cited folding times (Davis et al. 2012; Qiu et al. 2002; Kubelka et al. 2008). The Gō fold is a model, and the presets set N only. This is a sufficient-condition resolution of the combinatorial paradox, not a proof of global molecular convergence.

Share card: `website/assets/og/interfaces-levinthal.jpg` (1200 × 630), rendered from the page’s own ledger code.
