# Committed certificates

[Repository home](../README.md) · [Reproduce](../docs/reproducibility.md) · [Provenance](../docs/provenance.md)

| Record | Contents |
|---|---|
| [e47_pipeline.json](e47_pipeline.json) | E47 pipeline snapshot |
| [qutip_validation.json](qutip_validation.json) | QuTiP validation snapshot |

## September 28, 2026 · E47 closure certificate

| Record | Result |
|---|---|
| [Noiseless-subsystem + uniform convergence](MC-E47-NOISELESS-CONVERGENCE-20260928-001.json) | Uniform worst-case `< 1e-12` threshold first guaranteed at `n=270`; `E47 ≅ (C^5 ⊗ V₂) ⊕ (C^2 ⊗ V₅)`; both multiplicity factors certified noiseless under collective SU(2) noise · [scope note](MC-E47-NOISELESS-CONVERGENCE-20260928-001.md) · [validator](../research/e47/validation/e47_noiseless_subsystem_and_convergence_certificate.py) |

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
| [Convergence + noiseless multiplicities](MC-E47-CONVERGENCE-NOISELESS-20260928-001.json) | Uniform `||K Γ*^n(I−P47)||₂ < 10⁻¹²` first at n=270; explicit `C⁵⊗V₂ ⊕ C²⊗V₅` collective-SU(2) noiseless-subsystem factorization PASS |

These files are committed records. Their JSON content and Git history identify the recorded results; they do not assert that a new validation ran when this page was opened.

The website carries copies of the two snapshot records in [website/data/](../website/data/). Existing website checks compare those copies with the corresponding certificate files.

Other records remain with their components:

- [E47 theorem notes](../research/e47/README.md)
- [Stargate validation](../research/stargate/validation/README.md)
- [AETHERIS/EIDOLON receipt](../docs/certificates/CITY-AETHERIS-WAVEFORGE-EIDOLON-001.json)
- [Flight-replay records](../trajectories/README.md)

Use the [validation scope](../docs/validation_scope.md) to interpret each claim.
