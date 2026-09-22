#!/usr/bin/env python3
"""Certified E47-prism experiment for THE MATRIX.

Reconstruct the certified 8-qubit MATRIX circuit, perform the documented
256 -> 125 typed feature lift, resolve the 125-vector across the seven
Casimir eigenspaces, and optionally compare those band weights against
the live Supabase matrix-cube-adapter used by the website.
"""
from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import numpy as np

from validate_matrix_quantum_parity import (
    Config,
    dense_matrix_circuit,
    feature_lift_125,
    mps_matrix_circuit,
    phase_aligned_relative_l2,
    spin_matrices,
)

CERTIFICATE_ID = "MC-MATRIX-E47-PRISM-20260922-001"
ENDPOINT = "https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter"
ROOTS = (0, 2, 6, 12, 20, 30, 42)
MULT = (1, 9, 25, 28, 27, 22, 13)


def e47_casimir() -> np.ndarray:
    jx, jy, jz = spin_matrices(2.0)
    eye5 = np.eye(5, dtype=np.complex128)
    k3 = lambda a, b, c: np.kron(np.kron(a, b), c)
    jxt = k3(jx, eye5, eye5) + k3(eye5, jx, eye5) + k3(eye5, eye5, jx)
    jyt = k3(jy, eye5, eye5) + k3(eye5, jy, eye5) + k3(eye5, eye5, jy)
    jzt = k3(jz, eye5, eye5) + k3(eye5, jz, eye5) + k3(eye5, eye5, jz)
    return jxt @ jxt + jyt @ jyt + jzt @ jzt


def spectral_bands(v125: np.ndarray, casimir: np.ndarray) -> list[dict]:
    evals, evecs = np.linalg.eigh(casimir)
    bands = []
    for root, mult in zip(ROOTS, MULT):
        q = evecs[:, np.isclose(evals, root, atol=1e-9)]
        pv = q @ (q.conj().T @ v125)
        weight = float(np.real(np.vdot(pv, pv)))
        bands.append(
            {
                "lambda": root,
                "multiplicity": mult,
                "dimension_fraction": mult / 125,
                "weight": weight,
                "selected": root in (6, 30),
            }
        )
    return bands


def live_adapter(v125: np.ndarray, cfg: Config) -> dict:
    state = [[float(z.real), float(z.imag)] for z in v125]
    circuit = {
        "schema": "MATRIX-CIRCUIT-3.0",
        "engine": "python-certified-reference",
        "n": cfg.n,
        "layers": cfg.layers,
        "phi": cfg.phi,
        "chi": cfg.chi,
        "entangler": "brickwork",
        "noise": "none",
        "lift": {
            "name": "sampled-amplitude-feature-lift-125-v3",
            "source_dimension": 2 ** cfg.n,
            "target_dimension": 125,
            "claim": "explicit normalized feature map; not Hilbert-space isomorphism",
        },
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"statevector": state, "circuit": circuit}).encode(),
        headers={"content-type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def validate(require_live: bool = False) -> dict:
    cfg = Config(n=8, layers=24, chi=16, phi=0.7)
    dense = dense_matrix_circuit(cfg)
    mps, discarded, max_bond, _ = mps_matrix_circuit(cfg)
    v125 = feature_lift_125(mps)
    casimir = e47_casimir()
    bands = spectral_bands(v125, casimir)

    weights = {b["lambda"]: b["weight"] for b in bands}
    e47_weight = weights[6] + weights[30]
    identity = np.eye(125, dtype=np.complex128)
    kernel = (casimir - 6 * identity) @ (casimir - 30 * identity)
    k2 = kernel @ kernel
    k2_energy = float(np.real(np.vdot(v125, k2 @ v125)))

    checks = {
        "mps_dense_parity": phase_aligned_relative_l2(mps, dense) < 1e-12,
        "untruncated": discarded < 1e-12 and max_bond <= cfg.chi,
        "feature_norm": abs(float(np.linalg.norm(v125)) - 1.0) < 1e-12,
        "spectral_weight_sum": abs(sum(weights.values()) - 1.0) < 1e-12,
        "e47_band_identity": abs(e47_weight - (weights[6] + weights[30])) < 1e-15,
    }

    live = None
    if require_live:
        live = live_adapter(v125, cfg)
        if not live.get("ok"):
            checks["live_adapter_ok"] = False
        else:
            witness = live["witness"]["witness"]
            observed = {int(b["lambda"]): float(b["weight"]) for b in witness["spectral_bands"]}
            checks["live_adapter_ok"] = True
            checks["live_band_parity"] = max(abs(observed[r] - weights[r]) for r in ROOTS) < 1e-10
            checks["live_e47_parity"] = abs(float(witness["e47_weight"]) - e47_weight) < 1e-10
            checks["live_band_sum"] = abs(float(witness["spectral_weight_sum"]) - 1.0) < 1e-10

    return {
        "schema": "MATRIX-E47-PRISM-CERTIFICATE/1.0",
        "certificate_id": CERTIFICATE_ID,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "evidence_class": "E1 software/numerical parity",
        "configuration": {
            "qubits": cfg.n,
            "layers": cfg.layers,
            "chi": cfg.chi,
            "phi": cfg.phi,
            "source_dimension": 2 ** cfg.n,
            "typed_target_dimension": 125,
        },
        "checks": checks,
        "bands": bands,
        "e47": {
            "weight": e47_weight,
            "percent": 100 * e47_weight,
            "rank_fraction": 47 / 125,
            "delta_from_rank_fraction": e47_weight - 47 / 125,
            "complement_weight": 1 - e47_weight,
            "k2_energy": k2_energy,
        },
        "live_adapter": live,
        "boundary": "The 256->125 step is the documented typed feature map, not a Hilbert-space isomorphism. The E47 spectral analysis starts after that lift.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live-adapter", action="store_true")
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    receipt = validate(require_live=args.live_adapter)
    payload = json.dumps(receipt, indent=2)
    print(payload)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(payload + "\n")
    if receipt["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
