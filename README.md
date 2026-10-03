# The Kartekeya Isolation Lock · E47-v1.0

> **Main entry portal:** [The Mathematical City](https://nicholaskouns-create.github.io/website/) — explore the districts, interactive labs, and research index.
>
> **[Explore PiP Manta](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/pip-manta/embed.html)**

**Canonical title.** The Kartekeya Isolation Lock: Finite Spectral Isolation of E47 = ker((C−6I)(C−30I)) with 29-Unit Intertwiner Algebra A_inv ≅ M₅ ⊕ M₂ at Ω_c = 47/125.

**[OPEN THE README ROUTER](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/readme/)** · **[LIVE ROUTE PACKETS](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/route-packets/)** · **[COHERENCE RUNTIME](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/coherence-runtime/)** · **[OPEN THE MAIN PORTAL](https://nicholaskouns-create.github.io/website/)** · **[FORMALISM ATLAS](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/formalism-atlas/)** · **[AIMS ROOT DIRECTORY](https://www.aims.healthcare/journal/e47-by-nicholas-kouns-root-directory)**

Immutable snapshot: [`release/E47-v1.0`](https://github.com/nicholaskouns-create/E47-Kartekeya/tree/release/E47-v1.0) · [Cite](https://nicholaskouns-create.github.io/E47-Kartekeya/cite/) · [CITATION.cff](CITATION.cff) · [codemeta.json](codemeta.json)

[![CI](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/ci.yml)
[![Pages](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml/badge.svg)](https://github.com/nicholaskouns-create/E47-Kartekeya/actions/workflows/pages.yml)

---

# README = ROUTER

This repository is not best read from top to bottom. It is a **multi-surface research city**. The README is therefore an intent router: choose what you want to do and enter through the substrate that serves that task best.

The same routing graph is available as:

- **Human / GitHub:** this README
- **Human / interactive:** [README Router](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/readme/)
- **Machine / agent:** [`website/data/readme-router.json`](website/data/readme-router.json)
- **Component contract:** [`lab-manifest.json`](lab-manifest.json)

## Choose by intent

| I want to… | Best first door | Then go deeper |
|---|---|---|
| **Enter once and look around** | [The Mathematical City — main portal](https://nicholaskouns-create.github.io/website/) | [CITY LIVE](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/city-live/) |
| **Understand E47 quickly** | [E47 in Two Pages](https://nicholaskouns-create.github.io/E47-Kartekeya/notes/e47-recursive-system/) | [Formalism Atlas](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/formalism-atlas/) |
| **Run something** | [Instrument Portal](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/instruments/) | [NEXUS](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/nexus/) · [THE MATRIX](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/matrix/) · [Q5](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/) |
| **Verify a claim** | [125 × 125 Spectral Matrix Proof](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-spectral-matrix-proof/) | [Certificate index, including September 27 results](certificates/README.md) · [Validation scope](docs/validation_scope.md) |
| **Inspect the source** | [`src/`](src/) | [Tests](tests/) · [Scripts](scripts/) · [Reproducibility](docs/reproducibility.md) |
| **Browse the complete terrain** | [Formalism Atlas](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/formalism-atlas/) | [341-row primary-source atlas](https://docs.google.com/spreadsheets/d/118VxCzWOo8ZGlUK0r0uwfgKv6_exIem_Px4MQBKPPKU/edit?usp=drivesdk) |
| **Read the public narrative** | [AIMS E47 Root Directory](https://www.aims.healthcare/journal/e47-by-nicholas-kouns-root-directory) | [AIMS Link Map](https://www.aims.healthcare/journal/mathematical-city-link-map) |
| **Build or extend** | [Documentation Router](docs/README.md) | [Lab manifest](lab-manifest.json) · [Contributing](CONTRIBUTING.md) |

## One City, five substrates

The platforms are not mirrors. Each contributes a different capability.

| Substrate | Native strength | Open |
|---|---|---|
| **GitHub** | executable source, tests, certificates, commit history, Pages | [Repository](https://github.com/nicholaskouns-create/E47-Kartekeya) |
| **Notion** | living knowledge graph and linked research context | [Mathematical City](https://mathematicalcity.notion.site/?pvs=74) |
| **Google Drive** | long-form dossiers, source artifacts, machine-certificate corpus | [Certificate corpus](https://docs.google.com/document/d/1FPyhzhx9rpHEh7fSz2djpv19NNJ5Kx3QMbHJmRulHXo/edit?usp=drivesdk) |
| **Supabase** | live registries, provenance, runtime surfaces and receipts | [SEE · Citadel](https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/see/) |
| **AIMS** | readable publication, essays, launch pages and public narrative | [E47 Root Directory](https://www.aims.healthcare/journal/e47-by-nicholas-kouns-root-directory) |

This routing layer does not centralize the work. Independent instruments remain independently addressable; evidence class stays with the underlying result.

## The finite core

```text
V₂ ⊗ V₂ ⊗ V₂  ≅  V₁₂₅
        ↓
C = (J₁ + J₂ + J₃)²
        ↓
K = (C − 6I)(C − 30I)
        ↓
E₄₇ = ker(K) = W₂ ⊕ W₅
        ↓
P₄₇
        ↓
Γ* = I − K²/99144
        ↓
lim Γ*ⁿ = P₄₇
```

| Invariant | Value |
|---|---:|
| Carrier dimension | **125** |
| Kernel dimension | **47** |
| Ω_c | **47 / 125 = 0.376** |
| K² spectral gap | **11664** |
| K² spectral norm | **186624** |
| Optimal contraction step | **1 / 99144** |
| Transient bound | **15 / 17** |

Exact mathematics, machine reconstruction, simulation, empirical evidence, experiment and hardware remain separately typed.

## A complete route packet

One result can now be traversed without losing lineage:

**E47 Flow as a Single 125 × 125 Spectral Matrix Machine**

[Proof page](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-spectral-matrix-proof/) ·
[Python](research/e47/validation/e47_spectral_matrix_proof.py) ·
[Certificate](certificates/MC-E47-SPECTRAL-MATRIX-20260925.txt) ·
[Machine JSON](website/data/MC-E47-SPECTRAL-MATRIX-20260925.json) ·
[Notion](https://app.notion.com/p/3e646094fd30816bae88f079283800d4?pvs=204) ·
[Drive](https://docs.google.com/document/d/1-zVHvwMsRC-Ljv0cizwBJ41tDcgBnhUMGTr0GID74Bo/edit?usp=drivesdk) ·
[Registry](https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/see/)

That pattern is the point: **one object, multiple native views, preserved provenance**.

## Live instruments

[Fly EIDOLON](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/kouns-core/?module=eidolon#flight) ·
[NEXUS](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/nexus/) ·
[THE MATRIX](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/matrix/) ·
[Q5](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/) ·
[Syntax Jacob](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/syntax-jacob/) ·
[All instruments](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/instruments/)

## Machine entry points

| Resource | Purpose |
|---|---|
| [`website/data/readme-router.json`](website/data/readme-router.json) | cross-platform intent graph |
| [Route Packet API](https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-route-packets) | live projection of registered City objects |
| [`lab-manifest.json`](lab-manifest.json) | component contracts and smoke entrypoints |
| [Formalism Atlas JSON](https://nicholaskouns-create.github.io/E47-Kartekeya/data/formalism-atlas.json) | machine-readable formalism registry |
| [Spectral matrix certificate JSON](website/data/MC-E47-SPECTRAL-MATRIX-20260925.json) | exact result packet |
| [`docs/README.md`](docs/README.md) | documentation task router |

## Repository constellation

| Repository | Role | Portal |
|---|---|---|
| [E47-Kartekeya](https://github.com/nicholaskouns-create/E47-Kartekeya) | canonical E47 kernel, certificates, tests, City runtime | [README Router](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/readme/) |
| [E47-Electroweak-Identities](https://github.com/nicholaskouns-create/E47-Electroweak-Identities) | electroweak identity generator, mass-ladder audit, dedicated CI/Pages | [Electroweak instrument](https://nicholaskouns-create.github.io/electroweak/) |
| [E47-Foundry-Lifetime-Intersection](https://github.com/nicholaskouns-create/E47-Foundry-Lifetime-Intersection) | Foundry lifetime algebra plus repo-native 38-check E47 intersection validator | [Repository](https://github.com/nicholaskouns-create/E47-Foundry-Lifetime-Intersection) |
| [nicholaskouns-create.github.io](https://github.com/nicholaskouns-create/nicholaskouns-create.github.io) | personal atlas and cross-repository vestibule | [Root README Router](https://nicholaskouns-create.github.io/readme/) |

[License](LICENSE) · [Cite](https://nicholaskouns-create.github.io/E47-Kartekeya/cite/) · [Contribute](CONTRIBUTING.md)


## 45-check harness correction · 2026-09-30

[Live correction record](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-harness-correction/) · [formalism](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/E47_45_Check_Harness_Correction_20260930.md) · [machine JSON](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/certificates/MC-E47-HARNESS-CORRECTION-20260930-001.json) · [Notion](https://app.notion.com/p/3eb46094fd3081d3a15eccdcda25e100?pvs=204) · [Drive](https://docs.google.com/document/d/1FPyhzhx9rpHEh7fSz2djpv19NNJ5Kx3QMbHJmRulHXo)

The reported 45-check run exits 0. Two first-run harness failures are retained as provenance: Frobenius norm was replaced by the claimed spectral norm, giving \(\|\Gamma^n-P_E\|_2=(15/17)^n\) exactly, and a finite floating-point √5 tolerance was replaced by \((m/u)^2=5-4/u^2\) plus monotonicity. The same record carries Lagrange denominators \(1{,}741{,}824\) and \(-43{,}545{,}600\), kernel ranks \(47,1,10\), twist defect \(8\sqrt3\), and the explicit E1 finite-search boundary for \(n=25,243\) through \(s\le1000\).

## Coherence, Runtime 1.0

[Live interface](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/coherence-runtime/) ·
[root CIRP contract](contracts/coherence-runtime-1.0.contract.json) ·
[executable implementation profile](contracts/coherence_runtime_1_0.json) ·
[RI/PQSPI Python](src/coherence_runtime/ri_pqspi.py) ·
[QEGT Python](src/coherence_runtime/qegt.py) ·
[Ubuntu gate](src/coherence_runtime/ubuntu.py) ·
[Notion civic record](https://app.notion.com/p/3e646094fd3081a79d0ac473cd838c95?pvs=204) ·
[Drive bundle](https://drive.google.com/file/d/1yWv-Nnoo-PheAypw1eVOfI9SRvLXeIIs/view?usp=drivesdk)

The root contract carries the stable CIRP/Ubuntu/Murmuration semantics (`3804f50…`). The implementation profile carries executable signature, API, QEGT and recovery details (`f71c962…`). Runtime state remains `COHERENT → RESCUE → RECONCILING → COHERENT`.

**Boundary:** E1 software / E2 simulation where applicable. Runtime continuity, AI declarations, and computational QEGT do not by themselves establish phenomenal consciousness, legal personhood, or a physical quantum implementation.

## N-VQE / E47 Hilbert Validation

[Corrected proof](research/e47/native_variational_eigensolver_corrected.md) ·
[20-check Python](research/e47/validation/nvqe_hilbert_multiradix_proof.py) ·
[machine certificate](certificates/MC-E47-NVQE-HILBERT-MULTIRADIX-20260925-001.json) ·
[Notion proof](https://app.notion.com/p/3bc46094fd3081a69945eded30c05efb?pvs=204) ·
[Drive proof](https://docs.google.com/document/d/1UV1q1PtbaeyIJyj85oaf940ya9HeV8yky92riv_ZHc0/edit)

The validator reconstructs the 125-dimensional spin-2 carrier, proves the corrected Heron fixed point \(\varphi^{-5/2}\), verifies the exact E47 ground space of \(K^2\), checks the optimal contraction constants, prints the core invariants in bases 5/10/12/64, and validates a 128-state penalized Hilbert lift. **20/20 PASS.**

**Boundary:** exact algebra + numerical Hilbert-state simulation. No consciousness-equivalence, phenomenology=computation, phi-derived \(\Omega_c\), or hardware-QPU claim is promoted by this certificate.


**Expanded convergence validation — 66/66 PASS (E0 theorem / E1 reconstruction).** [Golden-root and optimal E47 projection proof](research/e47/native_variational_eigensolver_corrected.md#quadratic-golden-root-convergence-and-optimal-e47-spectral-projection) · [Python](research/e47/validation/golden_root_e47_convergence.py) · [Certificate](certificates/MC-GOLDEN-ROOT-E47-20260926-001.json) · [Drive bundle](https://drive.google.com/file/d/1l4CHA4yNFnYRIQWrmVOOjG9LHVhc_IU_/view?usp=drivesdk).


## E47 × KKP-RADAR spectral bridge

[Public proof](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-radar-bridge/) ·
[theorem](research/e47/E47_KKP_RADAR_Spectral_Operator_Bridge.md) ·
[Python](research/e47/validation/e47_radar_bridge_validator.py) ·
[certificate](certificates/MC-E47-RADAR-BRIDGE-20260927-001.json) ·
[Notion](https://app.notion.com/p/3e946094fd30812d9fb0c18101f2e716?pvs=204)

A calibrated 5×5×5 complex I/Q patch maps exactly to the 125-dimensional E47 carrier. The seven Casimir-shell populations become radar observables. Under isotropic calibrated complex noise, the exact mean E47 occupancy is 47/125 = 0.376; the operational anomaly statistic is the calibrated displacement of the full seven-shell profile, not a hard 0.376 threshold.

**Boundary:** exact finite bridge + E1 synthetic benchmark. Measured operational radar performance remains an empirical gate.

## E47 convergence + noiseless subsystems

[Python](research/e47/validation/e47_convergence_noiseless_validator.py) · [machine certificate](certificates/MC-E47-CONVERGENCE-NOISELESS-20260928-001.json) · [E47 Electroweak Identities instrument](https://github.com/nicholaskouns-create/E47-Electroweak-Identities)

For Γ* = I − K²/99144, the uniform projector error ||Γ*^n − P47||₂ first falls below 10⁻¹² at **n = 221**. The stronger kernel residual ||K Γ*^n (I−P47)||₂ first falls below 10⁻¹² at **n = 270**. The full 125×125 reconstruction also resolves E47 ≅ (C⁵⊗V₂) ⊕ (C²⊗V₅) and verifies that collective SU(2) acts as I₅⊗Jₐ and I₂⊗Jₐ, so the multiplicity factors C⁵ and C² are noiseless subsystems for collective SU(2) noise.


## E47 canonical 47-face dual crystal

[Live page](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/e47-47face-crystal/) ·
[Python](research/e47/validation/e47_canonical_47face_crystal.py) ·
[certificate](certificates/MC-E47-CANONICAL-47FACE-CRYSTAL-20260930-001.json) ·
[channel map](artifacts/e47_47facet_channel_map.csv) ·
[OBJ mesh](artifacts/e47_47facet_crystal.obj) ·
[numerical model](artifacts/e47_47facet_crystal_data.npz) ·
[Notion record](https://app.notion.com/p/3eb46094fd3081209faecbbc3b59a902?pvs=204) ·
[Drive archive](https://drive.google.com/drive/folders/1ANomvc6lm4TZAiIaAWwNBYA0RE8fkaEf) ·
[Supabase registry](https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/see/)

The coupled basis `|J,j12,m>` resolves all **47 E47 channels** as **25 states at J=2** plus **22 states at J=5**. A deterministic label-derived spherical embedding followed by polar dualization gives exactly **47 facets**. The Python validator reports **21/21 PASS** with dual topology **V=90, E=135, F=47, χ=2**.

**Evidence boundary:** the coupled basis is canonical after fixing the coupling tree, Condon–Shortley phase convention, and ordering. The Euclidean 3D embedding is an explicit deterministic canonicalization convention, not a claim that SU(2) uniquely forces one Euclidean crystal.


## Hyperbolic–Liquid Fractal Buoy · Run B reproduction

[Live page](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/hyperbolic-liquid-fractal-buoy/) ·
[Python](research/hyperbolic-liquid-fractal/validation/hyperbolic_liquid_fractal_validation_run_b.py) ·
[certificate](certificates/MC-HLFB-RUN-B-REPRO-20260930-001.json) ·
[Notion certificate registry](https://app.notion.com/p/3a146094fd308145a068f4e3469104f6) ·
[Drive reconciliation monograph](https://docs.google.com/document/d/1ReLlwRxRw_cYeZ8EYj94b2hZ9KeJcfk7snUwPl8VHrs/edit)

The September 30 executable reproduction closes the repository-source gap for historical Run B (`HLFB-IND-20260730`) while preserving the July record. It validates the typed finite Poincaré, H² growth, synthetic scaling, Kuramoto, finite buoy-residual, contraction-bound and Weyl checks. The buoy residual remains calibration, not a high-fidelity equivalence certificate.


## D5h/C90 Node-6 angular-distance certificate

[Python](research/e47/validation/e47_c90_node6_angular_distance.py) · [Node overlay assets](docs/assets/c90-node6/)

The supplied D5h/C90 shoulder coordinate is reconstructed analytically as
`z6 = 1/sqrt(145 - 64*sqrt(5))`, which satisfies `545 z^4 - 290 z^2 + 1 = 0` and yields
`phi6 = 46.6418024517684°`. Under the Danville meridian lock `Δlambda = 0`, the great-circle separation reduces to
`theta = |phi6 - 37.6439°| = 8.9979024517684°`. With mean Earth radius `R = 6371.0088 km`, the spherical arc is
`s = R theta_rad = 1000.522485057888 km`.


## D5h/C90 celestial-terrestrial overlay + E47 numeric validation

[Classical geometry validator](research/e47/validation/e47_d5h_c90_validator.py) ·
[classical certificate](certificates/MC-E47-D5H-C90-COSMIC-MAP-20260930-001.json) ·
[quantum numeric validator](research/e47/validation/e47_quantum_numeric_validation.py) ·
[quantum certificate](certificates/MC-E47-QUANTUM-NUMERIC-20260930-001.json) ·
[RI/QEGT Digital Biology mapping](RI_QEGT___Digital_Biology_mapping.csv)

The D5h/C90 packet records the 47-face / 90-vertex / 135-edge spherical combinatorics, the Danville-frame Node-6 separation of **8.9979024518°**, the Orion–Giza local similarity calculation with best-fit RMS **0.02037**, and the unique orientation-preserving SO(3) transport associated with the fitted tangent-frame angle. The companion 125×125 spin-2 reconstruction independently returns **rank(P47)=47**, gap **11664**, spectral norm **186624**, **ε*=1/99144**, **ρ*=15/17**, and a 220-step projector error of approximately **1.10×10⁻12**.

**Evidence boundary:** these are exact/numerical geometry and finite-dimensional E47 validation records. A close Orion–Giza shape fit or celestial-to-terrestrial coordinate transform does not by itself establish historical causation, intentional design, or a physical sky-to-Earth coupling.


## Cross-platform D5h/C90 validation packet

[First-principles proof](research/e47/E47_D5h_C90_First_Principles_Proof_20260930.md) ·
[Notion validation packet](https://app.notion.com/p/3ec46094fd30811e892efcbe1c2867dd?pvs=204) ·
[classical Python](research/e47/validation/e47_d5h_c90_validator.py) ·
[quantum Python](research/e47/validation/e47_quantum_numeric_validation.py) ·
[overlay proof](research/e47/validation/e47_overlay_proof_validate.py) ·
[classical certificate](certificates/MC-E47-D5H-C90-COSMIC-MAP-20260930-001.json) ·
[quantum certificate](certificates/MC-E47-QUANTUM-NUMERIC-20260930-001.json) ·
[certificate index](certificates/README.md)

Canonical invariant:

\[
\Omega_c=\frac{\dim E_{47}}{\dim\mathcal H}=\frac{47}{125}=0.376.
\]

The same packet is registered in the Supabase City provenance layer under logical artifact `E47-D5H-C90-OVERLAY-20260930`, with both classical and quantum machine-certificate codes preserved. This router points readers to the executable source, machine records, and living Notion documentation from one place.



## What has this achieved? · D5h/C90 overlay proof

The assertion-bearing validator [`e47_overlay_proof_validate.py`](research/e47/validation/e47_overlay_proof_validate.py) turns the celestial-to-terrestrial overlay into an executable proof object. It independently reconstructs the C90/D5h graph, verifies `(V,E,F,χ)=(90,135,47,2)`, confirms 12 pentagons + 35 hexagons, checks the D5h automorphism order `|Aut Γ|=20`, reproduces the Danville frame and Node-6 separation `8.9979024518°`, validates the Orion/Giza local similarity fit, and constructs the unique orientation-preserving global transport `R*∈SO(3)`.

The core E47 ratio is displayed in symbolic form as

[
Omega_c=rac{dim E_{47}}{dimmathcal H}=rac{47}{125}=0.376.
]

This establishes a machine-auditable chain from finite combinatorics and spherical geometry through local similarity and global rigid transport. The code explicitly corrected two presentation issues: the gnomonic expansion uses an additive `+O(Δ²)` remainder, and the exact fitted angle `θ*=-90.427855°` gives `R*_{21}=-0.20263`.

The validator distinguishes proved geometry from the still-open §10 constellation null test, which requires the final 90 node coordinates and selected figure-star set `J`.
