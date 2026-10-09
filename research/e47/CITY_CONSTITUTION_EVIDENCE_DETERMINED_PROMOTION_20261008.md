# Mathematical City Constitution Amendment — Evidence-Determined Assignment
Effective 2026-10-08 | normative rule CIVIC-EVIDENCE/2

## Article I — Mathematical sovereignty
A claim's civic status is a deterministic consequence of its stated proposition, hypotheses, proof, dependencies, reproducible evidence, and declared scope. No human or model may promote, withhold, or demote a claim by reputation, preference, rhetorical confidence, ceremony, or subjective crowning. The mathematical claim and its exact proof are assessed independently of the author's identity.

## Article II — Prima facie entitlement
A well-formed claim accompanied by a complete, inspectable proof or executable witness earns **PRIMA_FACIE** status for its *exact stated scope* immediately upon successful mechanical admission checks. Prima facie means sufficient on-face evidence for a mathematically specified claim, not a claim of empirical realization, universal applicability, or unexamined implications. An admissible exact derivation earns E0; an executable reconstruction earns E1 for the checks it executes. No separate endorsement is needed.

## Article III — Evidence is typed, not a single ladder
E0 = exact proof (assumptions explicit); E1 = executable reconstruction; E2 = simulation; E3 = observation or external benchmark with provenance; E4 = experiment/physical or hardware realization; OPEN = unresolved obligation. E0/E1/E2 describe mathematical/computational support, while E3/E4 are independent empirical axes. Evidence of one type never automatically substitutes for another. Historical H0 remains a legacy alias for hardware evidence, not a new ordinal rung.

## Article IV — Automatic escalation
For each claim, the city computes a proof-obligation closure and records (i) strongest established support for each precise proposition, (ii) inherited hypotheses and dependencies, (iii) empirical tags, (iv) failed obligations, (v) certificate and source hashes, (vi) superseded versions. If an exact proof discharges an earlier numerical-only objection, the exact proposition is reclassified E0 and the older objection is marked RESOLVED/SUPERSEDED with a pointer to the proof. A later valid proof must be considered; historical criticisms may not silently persist as current objections. Escalation is *automatic on successful validation*, not discretionary.

## Article V — Inference guard
For every derived claim C with premises D_i, its evidence may not exceed what the inference rule, hypotheses, and premises justify. The proof of a stronger claim must be separately supplied; shared dimensions, similar numbers, a signature, a simulation, or a validated submodel cannot by themselves assert equivalence, physical existence, or universal closure. Every conditional assumption propagates. Every dependency must exist; the dependency graph is acyclic.

## Article VI — Adjudication by counterexample
A claim may be challenged only by a concrete counterexample, failed exact identity, unfulfilled named proof obligation, invalid assumption, reproducibility failure, or scope mismatch. A challenge must cite the affected theorem clause and reproducible evidence. On repair, the city automatically reevaluates the claim and every dependent claim. Unresolved and superseded objections remain visible in provenance, but are not current vetoes.

## Article VII — Civic state machine
DRAFT -> ADMISSIBLE -> PRIMA_FACIE -> CERTIFIED_EXACT (E0) / CERTIFIED_EXECUTABLE (E1) / SIMULATED (E2) / OBSERVED (E3) / EXPERIMENTALLY_REALIZED (E4). The states are *typed concurrent facets*, not an implication that E0 automatically gives E4. INVALID or OPEN_OBLIGATION is attached to the affected clause only. Versioned changes trigger deterministic recomputation. The city must distinguish a theorem from its interpretation.

## Article VIII — Computational assignment rule
Given claim c and artifact set A:
1. Parse and normalize statement, scope, hypotheses, dependencies, proof obligations, and certificate IDs.
2. Verify referenced artifacts and content hashes, checks and exact boolean semantics (only literal true is PASS).
3. Reproduce exact symbolic identities where possible; rerun E1/E2 validators under pinned environments; validate E3/E4 provenance separately.
4. Resolve DAG dependencies and inherited assumptions; reject cycles and unsupported implication edges.
5. Assign PRIMA_FACIE to each claim with adequate on-face proof and no identified defect, with typed evidence classes only for verified artifacts.
6. Record unresolved obligations *per claim*, never as a blanket veto on the entire formalism.
7. Compare with prior version and mark each objection ACTIVE, RESOLVED, SUPERSEDED, or REOPENED, with an evidence-linked reason.
8. Publish the ledger, machine-readable decision, proof/certificate links, and reproducibility instructions.

## Article IX — Non-discretionary publication
Citadel, Path, Monorail, Proof Forge, Citizenship Bureau, website, and other city surfaces must consume one canonical evidence ledger. No UI badge, narrative summary, or agent may change the evidence class without a validated ledger transition. Human review may identify errors or supply evidence, but may not substitute for a mathematical test. Publication is not experimental validation.

## Article X — Migration and compatibility
Preserve existing E0/E1/E2, E3/E4, legacy H0, and the existing 18-claim evidence ledger. This amendment adds a non-discretionary promotion procedure, supersession tracking, prima-facie facet, and computational reassessment. Do not relabel all claims globally. Migrate per theorem and proof obligation. Older 'movement never upgrades a claim' remains true for *mere transit*; new verified proof evidence does upgrade the supported proposition.

## Formal rule
PROMOTE(c, level) iff VALID_ARTIFACT(c, level) and DISCHARGED_OBLIGATIONS(c, level) and DEPENDENCY_CLOSURE_VALID(c) and SCOPE_PRESERVED(c).

REASSESS(c, new_proof) = closure of all descendants of c in the claim DAG; old invalidations are resolved iff the new proof addresses their exact failing premise or inference.

**Authority:** Mathematical validity and recorded evidence. **No subjective crowning.**
