# Committed certificates

[Repository home](../README.md) · [Reproduce](../docs/reproducibility.md) · [Provenance](../docs/provenance.md)

| Record | Contents |
|---|---|
| [e47_pipeline.json](e47_pipeline.json) | E47 pipeline snapshot |
| [qutip_validation.json](qutip_validation.json) | QuTiP validation snapshot |

## September 27, 2026 · E47 certificates

The first four records below live in `artifacts/`. Their theorem notes and executable validators are indexed in [E47 research notes](../research/e47/README.md).

| Record | Result |
|---|---|
| [Condition lock](../artifacts/E47_CONDITION_LOCK_CERTIFICATE.json) | Optimal constant step, five-factor projector and five-step termination · 25/25 |
| [Signature and symmetry](../artifacts/E47_SIGNATURE_SYMMETRY_CERTIFICATE.json) | SU(2) × S₃ resolution, K inertia and Krein-form isometries · 28/28 |
| [Casimir census](../artifacts/E47_CASIMIR_CENSUS_CERTIFICATE.json) | Multiplicity vector and unique quadratic 47-dimensional selector · 12/12 |
| [Profile injection](../artifacts/E47_PROFILE_INJECTION_CERTIFICATE.json) | Vacuum plane-wave family and conditional unmarked-moduli injectivity · 9/9 |
| [G_E47 machine status](MC-G-E47-MACHINE-STATUS-20260927.json) | Locked core, structural carrier, external L, and uninstantiated maps · 5/5; [scope note](MC-G-E47-MACHINE-STATUS-20260927.md) |
| [E47 × KKP-RADAR bridge](MC-E47-RADAR-BRIDGE-20260927-001.json) | Exact 5×5×5 I/Q → E47 operator bridge; isotropic-null occupancy 47/125; synthetic seven-shell benchmark PASS; measured-radar validation not claimed |
| [Convergence + noiseless multiplicities](MC-E47-CONVERGENCE-NOISELESS-20260928-001.json) | Uniform `||K Γ*^n(I−P47)||₂ < 10⁻¹²` first at n=270; explicit `C⁵⊗V₂ ⊕ C²⊗V₅` collective-SU(2) noiseless-subsystem factorization PASS · [related electroweak instrument](https://github.com/nicholaskouns-create/E47-Electroweak-Identities) |
| [Neutrino flavor snapshot](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/3159377e2b176c457e0a7ccf3cb3beb87f4d79fb/certificates/MC-E47-NEUTRINO-FLAVOR-20260929-001.json) | `MC-E47-NEUTRINO-FLAVOR-20260929-001` · E2 classical state-vector snapshot at `τ=π`; carrier 125, rank `P47=47`, slots `[10,11,12]`; probabilities reproduce `0.04720552, 0.00314068, 0.94965381` at 8 d.p.; normalization defect `1.1102230246251565e-16`; supplied mixing inputs are not derived from `C` |
| [Canonical 47-face dual crystal](MC-E47-CANONICAL-47FACE-CRYSTAL-20260930-001.json) | Coupled `|J,j12,m>` basis → 47 spherical channels → polar dual with exactly 47 facets; 21/21 PASS; V=90, E=135, F=47, χ=2 |

| [45-check harness correction](MC-E47-HARNESS-CORRECTION-20260930-001.json) | 45/45 reported PASS · exit 0 · spectral-norm harness repaired to exact `(15/17)^n` · √5 limit replaced by exact Pell identity · Lagrange denominators `1741824, -43545600` · kernel ranks `47,1,10` · E1 finite-search boundary retained for n=25,243 through s≤1000 · [formalism note](../research/e47/E47_45_Check_Harness_Correction_20260930.md) |

These files are committed records. Their JSON content and Git history identify the recorded results; they do not assert that a new validation ran when this page was opened.

The website carries copies of the two snapshot records in [website/data/](../website/data/). Existing website checks compare those copies with the corresponding certificate files.

Other records remain with their components:

- [E47 theorem notes](../research/e47/README.md)
- [Stargate validation](../research/stargate/validation/README.md)
- [AETHERIS/EIDOLON receipt](../docs/certificates/CITY-AETHERIS-WAVEFORGE-EIDOLON-001.json)
- [Flight-replay records](../trajectories/README.md)

Use the [validation scope](../docs/validation_scope.md) to interpret each claim.

## Golden-ratio mass ladder · 19/19 PASS

[Live validation and original image](https://nicholaskouns-create.github.io/E47-Kartekeya/notes/omega-recursive/) · [Python](../research/omega-recursive/omega_recursive_closure_validator.py) · [Original certificate](../research/omega-recursive/omega_recursive_closure_certificate.json) · [Executed reproduction](../website/notes/omega-recursive/reproduction-20260929.json).
