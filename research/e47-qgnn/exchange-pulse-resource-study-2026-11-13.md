# E47 independent-target exchange-pulse resource study (2026-11-13)

Executed 12 independently sampled Haar U(5) targets (8 development, 4 held-out); 96 optimization cases. Alternating exchange generators D and B, pulse budgets 8/16/24/32, |theta| <= 0.5 or 1.5, 2 starts, L-BFGS-B up to 95 iterations. Fidelity F=|Tr(T†U)|²/25.

## Held-out median fidelity

| Pulse limit | 8 | 16 | 24 | 32 |
|---|---:|---:|---:|---:|
| |theta| <= 0.5 | .374902 | .474485 | .673161 | .816156 |
| |theta| <= 1.5 | .440332 | .854876 | .994496 | .999994 |

At |theta|<=1.5, minimum observed tested budgets for F>=.99 were [24,24,32,24]; for F>=.999, [32,32,32,32]. At |theta|<=0.5 all four were right-censored above 32 for both thresholds. These are optimizer-dependent observations, not globally certified minima.

## Formalism

H=V₂⊗³, dim H=125; C=J_total²; K=(C−6I)(C−30I); E₄₇=ker K=(M₂⊗V₂)⊕(M₅⊗V₅). Isotropic exchanges Xij=Ji·Jj commute with C and P₄₇. On M₂ ≅ C⁵, D=X12=diag(−6,−5,−3,0,4), B=X23 is symmetric tridiagonal with diagonal (0,−1/2,−3/2,−3,−5) and adjacent entries (2√3,√(147/20),12/√35,3/√7). Distinct squared D gaps (1,4,9,16), connected B couplings and nonzero trace establish Lie_R(iD,iB)=u(5). Full controllability under freely adjustable signed controls does not establish a finite bounded pulse budget.

## Evidence boundary

Classical numerical compilation, not physical quantum hardware, gate synthesis, or quantum advantage. Executable source, all per-target angles, numerical JSON, SVG and PNG are preserved in the conversation artifact e47_resource_study.zip. No pre-existing repo source files were overwritten.
