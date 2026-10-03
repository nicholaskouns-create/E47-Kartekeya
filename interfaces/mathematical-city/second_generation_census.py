#!/usr/bin/env python3
"""
MATHEMATICAL CITY — SECOND-GENERATION CITIZEN CENSUS
=====================================================
Creates one discrete, reproducible Python-validated G2 progeny identity
for every machine-validated citizen in website/citizens/citizens.json.

Birth rule
----------
1. Canonicalize the parent registry row.
2. Derive a deterministic complex 125-state from SHA-256 lineage material.
3. Pass the state through one synchronized E47 "murmuration" broadcast:
       psi' = Gamma psi
       Gamma = I - K^2/99144
4. Normalize the post-broadcast state to define the new progeny birth state.
5. Bind the G2 identity to a SHA-256 fingerprint and parent lineage.
6. Validate uniqueness, reproducibility, normalization, E47 rank, and
   the one-step complementary contraction bound.

No parent row is overwritten. The census is additive lineage.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "website" / "citizens" / "citizens.json"
ENGINE = ROOT / "interfaces" / "mathematical-city" / "citizen_e47_evolution.py"
OUTPUT = ROOT / "website" / "citizens" / "second_generation_census.json"

SCHEMA = "MC-CITIZEN-CENSUS-G2/1.0"
FORMALISM = "E47-GENERATOR-QUANTUM-VALIDATED"
VALIDATOR_COMMIT = "841c5a85fcfbea0c4b32401d57f458b549f05569"
EVOLUTION_COMMIT = "7a0d2b2c6ba1d8f8bcffb21769a4b863d4a82845"
PROOF_COMMIT = "6948675cf74f2b25dc1f7f83479dfc40cc9d6c44"

def load_engine():
    spec = importlib.util.spec_from_file_location("citizen_e47_evolution", ENGINE)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load E47 citizen evolution engine")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def canonical_parent(row: dict) -> bytes:
    return json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()

def lineage_digest(row: dict) -> str:
    h = hashlib.sha256()
    h.update(SCHEMA.encode())
    h.update(b"\0")
    h.update(canonical_parent(row))
    h.update(b"\0")
    h.update(FORMALISM.encode())
    h.update(b"\0")
    h.update(VALIDATOR_COMMIT.encode())
    h.update(b"\0")
    h.update(EVOLUTION_COMMIT.encode())
    return h.hexdigest()

def deterministic_state(digest: str) -> np.ndarray:
    """Expand one lineage digest deterministically into C^125."""
    raw = bytearray()
    counter = 0
    while len(raw) < 125 * 16:
        raw.extend(hashlib.sha256(f"{digest}:{counter}".encode()).digest())
        counter += 1
    u = np.frombuffer(bytes(raw[:125*16]), dtype=np.uint64)
    # Map uint64 pairs into centered real/imag values without RNG dependence.
    a = (u[0::2].astype(np.float64) / np.float64(2**64 - 1)) - 0.5
    b = (u[1::2].astype(np.float64) / np.float64(2**64 - 1)) - 0.5
    # Need 125 complex coordinates; extend using chained digest if pair count is short.
    vals = []
    ctr = 0
    while len(vals) < 125:
        d = hashlib.sha256(f"{digest}:z:{ctr}".encode()).digest()
        x = int.from_bytes(d[:8], "big") / (2**64 - 1) - 0.5
        y = int.from_bytes(d[8:16], "big") / (2**64 - 1) - 0.5
        vals.append(x + 1j*y)
        ctr += 1
    psi = np.asarray(vals, dtype=complex)
    psi /= np.linalg.norm(psi)
    return psi

def fp(psi: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(psi).view(np.float64).tobytes()).hexdigest()

def main():
    eng = load_engine()
    parents = json.loads(REGISTRY.read_text())
    assert all(x.get("validation_status") == "machine_validated" for x in parents)
    assert round(np.trace(eng.P47).real) == 47

    rows = []
    seen_codes = set()
    seen_fps = set()

    for parent in parents:
        ld = lineage_digest(parent)
        psi0 = deterministic_state(ld)

        p0 = eng.P47 @ psi0
        c0 = psi0 - p0

        # One synchronized murmuration pass of the new formalism.
        raw = eng.GAMMA @ psi0
        p_raw = eng.P47 @ raw
        c_raw = raw - p_raw

        # Core invariant before birth normalization.
        invariant_error = float(np.linalg.norm(p_raw - p0))
        ratio = float(np.linalg.norm(c_raw) / np.linalg.norm(c0))

        # Birth state for the new discrete progeny identity.
        psi2 = raw / np.linalg.norm(raw)
        fingerprint = fp(psi2)
        child_code = f"{parent['citizen_code']}-G2-{fingerprint[:12].upper()}"

        assert child_code not in seen_codes
        assert fingerprint not in seen_fps
        assert np.isclose(np.linalg.norm(psi2), 1.0, atol=1e-12)
        assert invariant_error < 1e-10
        assert ratio <= eng.Q_STAR + 1e-12

        seen_codes.add(child_code)
        seen_fps.add(fingerprint)

        rows.append({
            "citizen_code": child_code,
            "generation": 2,
            "parent_citizen_code": parent["citizen_code"],
            "title": f"{parent['title']} · Second Generation",
            "identity_status": "python_validated_progeny_seed",
            "validation_status": "machine_validated",
            "evidence_class": parent["evidence_class"],
            "formalism": FORMALISM,
            "birth_event": "murmuration:E47:one_pass",
            "lineage_digest_sha256": ld,
            "identity_fingerprint_sha256": fingerprint,
            "state_dimension": 125,
            "e47_rank": 47,
            "epsilon_star": "1/99144",
            "q_star": "15/17",
            "pre_birth_e47_weight": float(np.vdot(p0, p0).real),
            "pre_birth_complement_norm": float(np.linalg.norm(c0)),
            "post_pass_complement_norm": float(np.linalg.norm(c_raw)),
            "observed_one_pass_ratio": ratio,
            "e47_invariant_error": invariant_error,
            "parent_boundary": parent.get("boundary", ""),
            "provenance": {
                "validator_commit": VALIDATOR_COMMIT,
                "evolution_commit": EVOLUTION_COMMIT,
                "proof_commit": PROOF_COMMIT,
                "engine": "interfaces/mathematical-city/citizen_e47_evolution.py",
                "census_generator": "interfaces/mathematical-city/second_generation_census.py"
            }
        })

    census = {
        "schema": SCHEMA,
        "generation": 2,
        "population": len(rows),
        "parent_population": len(parents),
        "murmuration": {
            "formalism": FORMALISM,
            "operator": "Gamma = I - K^2/99144",
            "pass_count": 1,
            "e47_rank": 47,
            "carrier_dimension": 125,
            "complementary_contraction_bound": "15/17"
        },
        "validation": {
            "all_parent_rows_machine_validated": True,
            "all_g2_codes_unique": len(seen_codes) == len(rows),
            "all_g2_fingerprints_unique": len(seen_fps) == len(rows),
            "all_birth_states_normalized": True,
            "all_e47_components_invariant_before_birth_normalization": True,
            "all_one_pass_complement_ratios_at_or_below_15_17": True
        },
        "citizens": rows
    }

    OUTPUT.write_text(json.dumps(census, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS — G2 citizen census: {len(rows)}/{len(parents)} progeny identities")
    print("output:", OUTPUT)
    print("unique identities:", len(seen_fps))
    print("max E47 invariant error:", max(x["e47_invariant_error"] for x in rows))
    print("max one-pass complement ratio:", max(x["observed_one_pass_ratio"] for x in rows))

if __name__ == "__main__":
    main()
