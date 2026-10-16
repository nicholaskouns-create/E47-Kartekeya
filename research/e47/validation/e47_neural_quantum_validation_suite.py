#!/usr/bin/env python3
"""E47 neural-quantum benchmark and Recursive Identity: full validation suite.

Runs, in order:
  1. e47_neural_quantum_benchmark.py      the benchmark itself (NumPy, PyTorch, postselected quantum statevector)
  2. e47_neural_quantum_spectral_checks.py spectral checks behind the validated analysis
  3. e47_neural_quantum_pytorch_validation.py  PyTorch validation V1-V6
  4. e47_recursive_identity_checks.py      Recursive Identity formalization checks
and writes the machine record certificates/MC-E47-NEURAL-QUANTUM-RI-20261016-001.json.

Usage: python3 research/e47/validation/e47_neural_quantum_validation_suite.py [--output PATH]
Needs: numpy, scipy, torch (CPU is enough; all arithmetic is complex128).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERT = "MC-E47-NEURAL-QUANTUM-RI-20261016-001"
SOURCES = ["e47_neural_quantum_benchmark.py", "e47_neural_quantum_spectral_checks.py",
           "e47_neural_quantum_pytorch_validation.py", "e47_recursive_identity_checks.py",
           "e47_neural_quantum_validation_suite.py"]


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def benchmark_checks(b):
    c, info = b["checks"], b["information_retention"]
    r = 15 / 17
    trace_ok = all(b["numpy_trace"][k]["numpy_residual"] <= r ** int(k) for k in b["numpy_trace"])
    return {
        "B_kernel_rank_47": b["configuration"]["kernel_rank"] == 47,
        "B_sector_dimensions": [b["spin_sector_dimensions"][str(j)] for j in range(7)] == [1, 9, 25, 28, 27, 22, 13],
        "B_casimir_hermitian": c["casimir_hermiticity_error"] < 1e-12,
        "B_projector_idempotent": c["projector_idempotence_error"] < 1e-12,
        "B_projector_commutes_with_Gamma": c["projector_commutator_error"] < 1e-12,
        "B_rate_15_over_17": abs(c["gamma_eigenvalue_radius_complement"] - r) < 1e-12,
        "B_numpy_torch_agree": c["numpy_torch_branch_difference"] < 1e-12,
        "B_block_unitary": c["quantum_block_unitarity_error"] < 1e-12,
        "B_numpy_quantum_agree": c["numpy_quantum_final_branch_difference"] < 1e-11,
        "B_success_probability_equals_projected_probability": abs(info["final_unconditional_branch_probability"] - info["initial_projected_probability"]) < 1e-12,
        "B_final_fidelity_1": abs(info["final_conditional_fidelity"] - 1) < 1e-12,
        "B_residual_below_law_at_every_checkpoint": trace_ok,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(ROOT / "certificates" / f"{CERT}.json"))
    args = ap.parse_args()

    import torch  # the real library: the benchmark's PyTorch path must not run through a stand-in
    if not hasattr(torch, "Tensor") or not hasattr(torch, "__version__"):
        raise SystemExit("PyTorch is required for this suite")

    bench = load("e47_neural_quantum_benchmark")
    b = bench.bench(220, 47)
    spectral, spectral_checks = load("e47_neural_quantum_spectral_checks").run()
    torchv, torch_checks = load("e47_neural_quantum_pytorch_validation").run()
    ri, ri_checks = load("e47_recursive_identity_checks").run()

    checks = benchmark_checks(b)
    checks.update({f"S_{k}": v for k, v in spectral_checks.items()})
    checks.update(torch_checks)
    checks.update({f"RI_{k}": v for k, v in ri_checks.items()})
    pf = [b["numpy_trace"][str(n)]["projected_fidelity"] for n in (0, 1, 5, 10, 25, 50)]
    checks["RI_X2_coherence_equals_benchmark_projected_fidelity"] = max(
        abs(x - y) for x, y in zip(pf, ri["coherence"]["values_n_0_1_5_10_25_50"])) < 1e-12
    checks = {k: bool(v) for k, v in checks.items()}

    b.pop("time_seconds", None)
    cert = {
        "certificate": CERT,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "evidence": "E0 exact representation-theoretic identities (rational sector spectra, optimal step, rate 15/17); "
                    "E1 deterministic machine reconstruction in NumPy and PyTorch, complex128",
        "subject": "E47 classical neural and postselected quantum statevector benchmark; PyTorch validation V1-V6; "
                   "Recursive Identity formalization (Theorems 1-2, descent, dilation) and five consequences",
        "kernel": {"carrier": "V2 x V2 x V2 = C^125", "K": "(C-6I)(C-30I)", "E47": "ker K = 5V2 + 2V5", "dim_E47": 47,
                   "Gamma": "I - K^2/99144", "rate": "15/17"},
        "environment": torchv["environment"],
        "sources_sha256": {s: hashlib.sha256((HERE / s).read_bytes()).hexdigest() for s in SOURCES},
        "benchmark": b,
        "spectral_checks": spectral,
        "pytorch_validation": torchv,
        "recursive_identity": ri,
        "checks": checks,
        "check_count": len(checks),
        "pass_count": sum(checks.values()),
    }
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cert, indent=1) + "\n", encoding="utf-8")
    for k, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {k}")
    print(f"\n{CERT}: {cert['status']} ({cert['pass_count']}/{cert['check_count']}) -> {out}")
    sys.exit(0 if cert["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
