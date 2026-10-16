#!/usr/bin/env python3
"""E47 kernel filter: PyTorch validation (V1-V6).

Checks the PyTorch realisation of the benchmark's filter
    Gamma = I - K^2/99144,   K = (C - 6)(C - 30),   C = J.J on (C^5)^{x3},
run as an L-layer network N_L = Gamma^L (one shared layer: a gradient step on |K psi|^2/2),
against the exact law ||Gamma^L - P||_2 = (15/17)^L, P the projector onto the 47-dimensional kernel.

  V1  error law at every depth L = 0..220 (operator level: the identity pushed through the network)
  V2  every input: operator bound, plus 10,000 random inputs
  V3  agreement with the NumPy implementation (operator level)
  V4  agreement with the exact spectral operator U diag(gamma^L) U^+, i.e. the quantum branch's operator
  V5  SO(3) equivariance: generators and 20 random finite rotations
  V6  the benchmark's own seed-47 state

Certificate: MC-E47-NEURAL-QUANTUM-RI-20261016-001 (written by e47_neural_quantum_validation_suite.py)
Usage: python3 e47_neural_quantum_pytorch_validation.py [path/to/e47_neural_quantum_benchmark.py]
Needs: numpy, scipy, torch. Runs on CPU in complex128.
"""
from __future__ import annotations

import importlib.util
import platform
import sys
from pathlib import Path

import numpy as np
import scipy
import scipy.linalg as sla
import torch

HERE = Path(__file__).resolve().parent
R, LMAX = 15 / 17, 220


def load_bench(path=None):
    path = Path(path) if path else HERE / "e47_neural_quantum_benchmark.py"
    spec = importlib.util.spec_from_file_location("e47_neural_quantum_benchmark", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(bench=None):
    eb = load_bench(bench)
    C, P, G, U, gam, spin = eb.build()
    I5 = np.eye(5, dtype=complex)
    J = [np.kron(np.kron(a, I5), I5) + np.kron(np.kron(I5, a), I5) + np.kron(np.kron(I5, I5), a) for a in eb.spin2()]
    Gt = torch.from_numpy(np.ascontiguousarray(G))
    Pt = torch.from_numpy(np.ascontiguousarray(P))
    out = {"environment": {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__,
                           "scipy": scipy.__version__, "dtype": str(Gt.dtype), "device": str(Gt.device)}}
    checks = {}

    # V1
    M = torch.eye(125, dtype=torch.complex128)
    norms = []
    for L in range(LMAX + 1):
        if L:
            M = Gt @ M
        norms.append(torch.linalg.matrix_norm(M - Pt, ord=2).item())
    dev = max(abs(e - R ** L) for L, e in enumerate(norms))
    N = M.numpy()
    nN = float(np.linalg.norm(N - P, 2))
    out["V1"] = {"max_abs_deviation_from_law": dev, "norm_at_220": nN, "law_at_220": R ** LMAX, "norms_by_depth": norms}
    checks["V1_error_law_every_depth"] = dev < 1e-13

    # V2
    X = torch.from_numpy(np.random.default_rng(7).normal(size=(125, 10000)) + 1j * np.random.default_rng(8).normal(size=(125, 10000)))
    Y = X.clone()
    for _ in range(LMAX):
        Y = Gt @ Y
    ratio = (torch.linalg.vector_norm(Y - Pt @ X, dim=0) / torch.linalg.vector_norm(X, dim=0)).max().item()
    out["V2"] = {"operator_bound": nN, "max_ratio_10000_inputs": ratio}
    checks["V2_every_input_within_operator_bound"] = ratio <= nN * (1 + 1e-9) and nN < 1.2e-12

    # V3
    v3 = float(np.linalg.norm(N - np.linalg.matrix_power(G, LMAX), 2))
    out["V3"] = {"torch_vs_numpy_operator": v3}
    checks["V3_agrees_with_numpy"] = v3 < 1e-12

    # V4
    Q = (U * gam ** LMAX) @ U.conj().T
    D, Rp = N - Q, np.eye(125) - P
    unit = np.sort(np.linalg.eigvalsh((G + G.conj().T) / 2))[-47:]
    drift = float(np.abs(unit - 1).max())
    v4 = {"complement": float(np.linalg.norm(Rp @ D @ Rp, 2)), "coupling": float(np.linalg.norm(P @ D @ Rp, 2)),
          "kernel": float(np.linalg.norm(P @ D @ P, 2)), "stored_unit_eigenvalue_offset": drift,
          "offset_times_220": LMAX * drift}
    out["V4"] = v4
    checks["V4_matches_exact_operator_off_kernel"] = v4["complement"] < 1e-14 and v4["coupling"] < 1e-12
    checks["V4_kernel_deviation_explained_by_rounding"] = v4["kernel"] < 2 * LMAX * drift + 1e-14

    # V5
    comm = float(max(np.linalg.norm(N @ j - j @ N, 2) for j in J))
    rng = np.random.default_rng(2026)
    worst = 0.0
    for _ in range(20):
        n = rng.normal(size=3)
        n /= np.linalg.norm(n)
        Dr = sla.expm(-1j * rng.uniform(0, 2 * np.pi) * sum(c * j for c, j in zip(n, J)))
        worst = max(worst, float(np.linalg.norm(Dr @ N @ Dr.conj().T - N, 2)))
    out["V5"] = {"max_generator_commutator": comm, "max_rotation_defect_20_random": worst}
    checks["V5_so3_equivariant"] = comm < 1e-11 and worst < 1e-11

    # V6
    rng = np.random.default_rng(47)
    psi = rng.normal(size=125) + 1j * rng.normal(size=125)
    psi /= np.linalg.norm(psi)
    vt, vn = torch.from_numpy(psi.copy()), psi.copy()
    for _ in range(LMAX):
        vt, vn = Gt @ vt, G @ vn
    v = vt.numpy()
    tgt = P @ psi
    q = float(np.vdot(tgt, tgt).real)
    fid = float(abs(np.vdot(tgt / np.sqrt(q), v)) ** 2 / np.vdot(v, v).real)
    out["V6"] = {"torch_vs_numpy": float(np.linalg.norm(v - vn)), "distance_to_P_psi": float(np.linalg.norm(v - tgt)),
                 "fidelity": fid, "squared_norm": float(np.vdot(v, v).real), "projected_probability_q": q}
    checks["V6_seed47_state"] = (out["V6"]["torch_vs_numpy"] < 1e-12 and out["V6"]["distance_to_P_psi"] < R ** LMAX
                                 and abs(fid - 1) < 1e-12 and abs(out["V6"]["squared_norm"] - q) < 1e-12)
    return out, checks


def main():
    out, checks = run(sys.argv[1] if len(sys.argv) > 1 else None)
    e = out["environment"]
    print(f"Environment: Python {e['python']} | PyTorch {e['torch']} | NumPy {e['numpy']} | SciPy {e['scipy']}")
    print(f"PyTorch tensors: {e['dtype']} on {e['device']}\n")
    v = out
    print(f"V1  max over L = 0..{LMAX} of | ||N_L - P||_2 - (15/17)^L | = {v['V1']['max_abs_deviation_from_law']:.2e}")
    print(f"    ||N_{LMAX} - P||_2 = {v['V1']['norm_at_220']:.4e}   vs   (15/17)^{LMAX} = {v['V1']['law_at_220']:.4e}")
    print(f"V2  every input: ||N psi - P psi|| <= {v['V2']['operator_bound']:.4e} ||psi||;  largest ratio over 10,000 random inputs = {v['V2']['max_ratio_10000_inputs']:.2e}")
    print(f"V3  ||N_{LMAX}(PyTorch) - N_{LMAX}(NumPy)||_2 = {v['V3']['torch_vs_numpy_operator']:.2e}")
    print(f"V4  vs exact spectral operator: complement {v['V4']['complement']:.1e} | coupling {v['V4']['coupling']:.1e} | kernel {v['V4']['kernel']:.1e}")
    print(f"    stored Gamma: its 47 unit eigenvalues lie within {v['V4']['stored_unit_eigenvalue_offset']:.1e} of 1;  x {LMAX} layers = {v['V4']['offset_times_220']:.1e}")
    print(f"V5  max_a ||[N_{LMAX}, J_a]||_2 = {v['V5']['max_generator_commutator']:.2e};  max over 20 random rotations ||D N D^+ - N||_2 = {v['V5']['max_rotation_defect_20_random']:.2e}")
    print(f"V6  seed 47: ||PyTorch - NumPy|| = {v['V6']['torch_vs_numpy']:.2e} | ||output - P psi|| = {v['V6']['distance_to_P_psi']:.2e} | "
          f"fidelity = {v['V6']['fidelity']:.16f} | | ||output||^2 - ||P psi||^2 | = {abs(v['V6']['squared_norm'] - v['V6']['projected_probability_q']):.1e}\n")
    print("\n".join(f"[{'PASS' if ok else 'FAIL'}] {k}" for k, ok in checks.items()))
    sys.exit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
