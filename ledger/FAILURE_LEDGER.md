# KKP-E47 Failure Ledger

**Issued 2026-10-27 · 42 failure records · 6 standing results**

> A claim's epistemic type is part of the claim. A failure is a record, not an erasure.

## States

- **BLOCKED** — cannot progress: contradiction, circularity, or missing construction
- **FALSIFIED** — tested against a stated criterion and failed
- **CORRECTED** — a definite wrong value replaced by a definite right one
- **SUPERSEDED** — replaced by a stronger result
- **UNDER_REVIEW** — certificate not yet closed
- **UNPROVEN** — conjectural; no kill condition stated yet

## Evidence types

- **E0** — exact finite mathematics, decidable
- **E1** — computation at a stated precision and bound
- **P** — postulate / structural lift
- **C** — domain construction, needs empirical validation

## Failure records

| id | claim | state | type | found by | resolution / obstruction |
| --- | --- | --- | --- | --- | --- |
| F-001 | Omega_c = phi^-5 | **FALSIFIED** | P | author | half-integer depths supplied as inputs |
| F-002 | alpha^-1 = phi^107.5/(60 pi) | **FALSIFIED** | P | author | Planck mass imported |
| F-003 | first-principles derivation of the mass ladder | **FALSIFIED** | P | author | 13-level simulation reproduces an explicitly encoded Hamiltonian |
| F-004 | tensor-squaring conjecture | **FALSIFIED** | P | author | pre-registered kill conditions |
| F-005 | Phi operator fixed-point claim | **FALSIFIED** | P | author | pre-registered kill conditions |
| F-006 | Genesis H1: decoder beats CSP+LDA and tangent space+LR | **FALSIFIED** | C | author | dAUC -0.210 / -0.017 |
| F-007 | Genesis H2: the 47/125 fraction beats other fractions | **FALSIFIED** | C | author | signature constant tested and not supported; dAUC -0.006, p=0.79 |
| F-008 | Genesis H3: occupancy-gated trials decode better | **FALSIFIED** | C | author | 0.603 vs 0.592, p=0.285 |
| F-009 | Genesis H4: fractal shape adds to band power | **FALSIFIED** | C | author | better in 0 of 9 subjects |
| F-010 | Genesis H5: fractal shape adds to tangent space | **FALSIFIED** | C | author | dAUC -0.030, CI excludes zero |
| F-011 | Tc = 298 K at lambda=2.7, omega_log=1740 K | **CORRECTED** | E1 | author | → 378 K by numerical Eliashberg |
| F-012 | the closed form fits to a few percent | **FALSIFIED** | E1 | author | 21% low without f1 |
| F-013 | static V_ex valid at lambda=2.7 | **FALSIFIED** | P | author | Migdal parameter 0.998 |
| F-014 | Casimir SC contribution suppressed by (Delta/omega_p)^2 ~ 1e-3 | **FALSIFIED** | E1 | author | factor is 0.08 to 71; exclusion stands on the category argument instead |
| F-015 | P S P = 0 (vortex stretching annihilated on E47) | **FALSIFIED** | E1 | author | |P_E S|/|S| = 0.6219 against tolerance 1e-8 |
| F-016 | P S P = 0 for rank <= 2 tensor operators | **FALSIFIED** | E0 | collaborator | ||PSP||_F = 126.78, 38.59, 22.28, 24.62 for four natural operators; channels j=2->2 and j=5->5 are allowed and inside the kernel |
| F-017 | kernel sectors j=2,5 arise from symmetric coupling paths | **FALSIFIED** | E0 | collaborator | j=2 carries triv+2.std; j=5 carries std only, no trivial component. The orthogonality the proof needs is absent |
| F-018 | Navier-Stokes global regularity via Casimir projection | **BLOCKED** | P | both | four independent blocks: lift E:omega->C^125 undefined; cross terms P S(omega_perp) and P(u.grad)omega_perp dropped; complement evolution replaced by the contraction flow; BKM needs the integral of the true field |
| F-019 | blow-up exclusion on the typed manifold | **BLOCKED** | E0 | collaborator | CIRCULAR: Psi is defined by sup-boundedness, then solutions in Psi are concluded bounded. Non-trivial statement is that Psi is an attractor |
| F-020 | curvature-dissipation closure of vortex stretching | **UNDER_REVIEW** | P | collaborator | scaling chain is sound; the whole proof rests on the asserted kappa_max <~ k_d^-1. This is the Constantin-Fefferman geometric-depletion direction; state it as conditional on the curvature bound |
| F-021 | Clebsch-Gordan multiplicities (1,3,5,7,9,11,13) | **CORRECTED** | E0 | collaborator | → (1,3,5,4,3,2,1). document's own dimension check gives 455, not 125 |
| F-022 | 4D extension dim ker K_4 = 187 of 625 | **CORRECTED** | E0 | collaborator | → 190 of 625; Omega_c(4D) = 0.304 |
| F-023 | S4 character row chi(g) = (125,13,25,9,1) | **CORRECTED** | E0 | collaborator | → (125,5,5,5,5). Burnside orbit count 10 is correct; the row was the sector-dimension row d(J) for J=6,2,1,0 |
| F-024 | K eigenvalue signs: 68 negative, 47 zero, 57 positive | **CORRECTED** | E0 | collaborator | → 23 positive, 47 zero, 55 negative. stated counts sum to 172 > 125 |
| F-025 | deformed 47-face solid has V=56, E=84, F=47, chi=2 | **CORRECTED** | E0 | collaborator | → V=90, E=135, F=47. 56-84+47 = 19; with the face histogram unchanged E and V are forced |
| F-026 | facet histogram 24 tri + 12 pent + 6 hex + 4 hept + 1 oct | **CORRECTED** | E0 | collaborator | → 3x4 + 14x5 + 23x6 + 6x7 + 1x8. stated histogram forces E=102, V=57, contradicting the same plate's V=90, E=135 |
| F-027 | polar layer sizes 3+8+15+14+3 | **CORRECTED** | E0 | collaborator | → sums to 43; must total 47 |
| F-028 | V_void / V_sphere = 0.5076 | **CORRECTED** | E0 | collaborator | → that ratio is V_void/V_cube; void/sphere = 0.969 |
| F-029 | carrier has 150 cells (six 5x5 faces) | **CORRECTED** | E0 | collaborator | → 125 = 5^3, the volume; 150 is the surface of a net and a different object |
| F-030 | dim ker K = 7 (5V2 + 2V5) | **CORRECTED** | E0 | collaborator | → 47; the 7 is the multiplicity-space dimension 5+2 |
| F-031 | Gamma^n converges to 0 | **CORRECTED** | E0 | collaborator | → Gamma^n -> P_47, a rank-47 projector; ||Gamma^n - P|| = (15/17)^n |
| F-032 | E47 = E6 tensor E30 | **CORRECTED** | E0 | both | → direct sum, not tensor product. recurring; already a standing erratum |
| F-033 | monodromy tolerance 1e-100 | **CORRECTED** | E1 | author | → 1e-13. 1e-100 is unreachable in float64 |
| F-034 | contraction operator I - eps K | **SUPERSEDED** | E0 | author | → I - eps K^2; K is sign-indefinite |
| F-035 | kernel decomposition 5V2 tensor 2V3 | **CORRECTED** | E0 | author | → 5V2 direct-sum 2V5 |
| F-036 | Einstein-mode omega_log and omega2 identities (Lean/Coq) | **BLOCKED** | E0 | collaborator | alpha2F as an if-then-else is nonzero at one point, so the Lebesgue integral is 0 and both theorems are false as stated. Fix: put the delta in the MEASURE, not the integrand. File is not referenced by any workflow |
| F-037 | arccos(1/phi) = 51.83 deg is the golden angle | **CORRECTED** | E0 | collaborator | → the golden angle is 360/phi^2 = 137.5 deg; 51.83 deg is a different quantity |
| F-038 | tablet museum number Penn 51-01-105 | **CORRECTED** | C | collaborator | → CUNES 51-01-105, Cornell University |
| F-039 | tablet provenience: Uruk | **CORRECTED** | C | collaborator | → provenience uncertain; the PERIOD is Uruk III |
| F-040 | the 47-face realization independently forces the two sectors | **BLOCKED** | P | collaborator | CIRCULAR: the polyhedron is built FROM the 47 selected labels. Non-circular version: build the polar dual from all 125 coupled states and ask whether the 47 facets are topologically distinguished |
| F-041 | the discrete torus (Z5)^3 and the Casimir select the same 47 | **FALSIFIED** | E0 | collaborator | ||[C,L]||_F = 221.73; E47 is not L-invariant; 13.5% leakage; overlaps with all ten L-eigenspaces are non-integer. The two carriers are independent decompositions |
| F-042 | S3 isotypic content singles out the selected pair {2,5} | **FALSIFIED** | E0 | collaborator | no invariant of the S3 column separates {2,5} from {6,4,0}. Surviving observation: E47 is the sign-free part |

## Standing results (not failures)

| id | result | type |
| --- | --- | --- |
| S-001 | the moment selector is the unique traceless centred quadratic in C | E0 |
| S-002 | admissible tensor orders solve (2n-1)^2 - 6m^2 = 1; n=3 is the unique order with mu-sigma = j(j+1) | E0 |
| S-003 | upper root spectral iff (2J+1, 2j+1) = (L_k, F_k), k odd | E0 |
| S-004 | dim ker = F_k^2 + F_(k-2) L_k inside F_k^3; ratio to (2j+1)^2 tends to 3/phi | E0 |
| S-005 | k=5 is the unique member with 3j-J = 1; 47/125 is the largest proper occupancy | E0 |
| S-006 | ten Mathlib-free Lean modules: 41 theorems with no axioms, 6 with propext only, 0 sorry, 0 native_decide | E0 |

---

Validated by `validate_ledger.py`, which exits non-zero unless every entry is typed, 
every correction carries its replacement, every falsification carries its test, 
and every block names its obstruction.
