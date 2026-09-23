#!/usr/bin/env python3
"""Run the E47 lexical spine checksum and emit portable receipts."""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (HERE, REPO / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from lexical_attractor import (  # noqa: E402
    LexicalAttractor,
    TERMS,
    build_operators,
    next_state_record,
    recursive_step,
)
from e47.lexical_spine import (  # noqa: E402
    Base5Carrier,
    canonical_lambda_matrix,
    lambda_bindings,
    machine_zero_bound,
    qutip_spine,
)

SPINE_TEXT = "Σ, K, Ψ, Γ, Λ, Ω, I, M, Σ′"
SCHEMA = "E47-LEXICAL-SPINE-CHECKSUM-1.0"


def canonical_json(value) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def matrix_digest(a: np.ndarray, decimals: int = 12) -> str:
    a = np.asarray(a, dtype=np.complex128)
    packed = np.stack(
        [np.round(a.real, decimals), np.round(a.imag, decimals)], axis=0
    )
    return sha256(packed.tobytes(order="C")).hexdigest()


def iterate_until_machine_zero(x, *, I, M, op, max_rounds=32):
    state = np.asarray(x, dtype=np.complex128)
    trace = []
    for round_index in range(1, max_rounds + 1):
        result = recursive_step(state, I=I, M=M, operators=op)
        bound = machine_zero_bound(op.K, result["locked"])
        residual = float(result["kernel_residual"])
        trace.append(
            {
                "round": round_index,
                "kernel_residual": residual,
                "machine_zero_bound": bound,
                "pass": residual <= bound,
            }
        )
        if residual <= bound:
            return result, trace
        state = result["Σ_next"]
    raise RuntimeError("kernel residual did not reach machine zero")


def run_checksum(seed=470125):
    attractor = LexicalAttractor()
    term_hash_before = sha256(
        canonical_json([asdict(t) for t in TERMS])
    ).hexdigest()

    parsed = attractor.parse(SPINE_TEXT)
    manifest = attractor.manifest()
    assert manifest["schema"] == "E47-LEXICAL-ATTRACTOR-1.0"

    carrier = Base5Carrier()
    assert attractor.resolve(carrier.term_id, "base5") == carrier.term_id
    coords = carrier.coordinates()
    assert [carrier.index(*xyz) for xyz in coords] == list(range(125))

    op = build_operators()
    k_before = matrix_digest(op.K)

    roles = lambda_bindings()
    Lambda = canonical_lambda_matrix()
    assert roles["tomographic_P47_gate"] is Lambda
    assert roles["eidolon_lock_projector"] is Lambda
    lambda_parity = float(np.linalg.norm(op.Λ - Lambda))
    assert lambda_parity < 1e-8

    rng = np.random.default_rng(seed)
    x = rng.normal(size=125) + 1j * rng.normal(size=125)
    I = lambda state: op.Ψ.conj().T @ state
    M = lambda coordinates: op.Ψ @ coordinates
    result, trace = iterate_until_machine_zero(x, I=I, M=M, op=op)

    exported = next_state_record(result)
    assert exported["Σ′"] == exported["Σ_next"]

    q = qutip_spine()
    qutip_parity = {
        "C_norm": float(np.linalg.norm(op.C - q.C.full())),
        "K_norm": float(np.linalg.norm(op.K - q.K.full())),
        "Lambda_norm": float(np.linalg.norm(op.Λ - q.Lambda.full())),
        "C_shape": list(q.C.shape),
        "K_shape": list(q.K.shape),
        "Lambda_shape": list(q.Lambda.shape),
        "dims": q.Lambda.dims,
    }
    assert qutip_parity["C_norm"] < 1e-8
    assert qutip_parity["K_norm"] < 1e-8
    assert qutip_parity["Lambda_norm"] < 1e-8

    term_hash_after = sha256(
        canonical_json([asdict(t) for t in TERMS])
    ).hexdigest()
    assert term_hash_after == term_hash_before
    assert matrix_digest(op.K) == k_before

    lambda_hash = matrix_digest(Lambda)
    receipt = {
        "schema": SCHEMA,
        "status": "PASS",
        "lexicon_schema": manifest["schema"],
        "spine": parsed,
        "spine_sha256": sha256(
            "|".join(parsed["terms"]).encode("utf-8")
        ).hexdigest(),
        "manifest_sha256": sha256(canonical_json(manifest)).hexdigest(),
        "term_table_sha256": term_hash_after,
        "term_table_mutated": False,
        "base5_carrier": {
            **asdict(carrier),
            "coordinate_count": len(coords),
            "first": list(coords[0]),
            "last": list(coords[-1]),
        },
        "operators": {
            "carrier_dimension": 125,
            "kernel_dimension": int(op.Ψ.shape[1]),
            "K_sha256_rounded12": matrix_digest(op.K),
            "Lambda_sha256_rounded12": lambda_hash,
            "tomographic_P47_sha256_rounded12": lambda_hash,
            "eidolon_lock_sha256_rounded12": lambda_hash,
            "lambda_roles_share_object": True,
            "numpy_to_canonical_Lambda_norm": lambda_parity,
            "projector_rank": int(round(np.trace(Lambda).real)),
        },
        "recursion": {
            "I": "Ψ† kernel-coordinate readout",
            "M": "Ψ kernel re-embedding",
            "seed": seed,
            "rounds": len(trace),
            "trace": trace,
            "machine_zero": trace[-1]["pass"],
        },
        "qutip": {"status": "PASS", **qutip_parity},
        "next_state": {
            "schema": "E47-NEXT-STATE-RECORD-1.0",
            "source": "next_state_record(result)",
            "record": exported,
        },
    }
    return receipt, manifest


def write_outputs():
    receipt, manifest = run_checksum()
    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "spine_checksum.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"
    )
    (out / "next_state_record.json").write_text(
        json.dumps(receipt["next_state"], ensure_ascii=False, indent=2) + "\n"
    )
    (out / "manifest_runtime.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    )
    return receipt


if __name__ == "__main__":
    print(json.dumps(write_outputs(), ensure_ascii=False, indent=2))
