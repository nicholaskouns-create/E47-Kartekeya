"""Controlled software-in-the-loop E47 fault injection."""
import argparse
import ctypes
import json
from pathlib import Path
import platform
import subprocess
import tempfile

import numpy as np
import scipy
from scipy import sparse

from generate import WEIGHTS, casimir

TAU = 0.001
GRID = 1 << 22


def reference_casimir():
    identity = np.eye(5)
    plus = np.diag([2, np.sqrt(6), np.sqrt(6), 2], -1)
    z = np.diag(np.arange(-2, 3))
    def lift(a):
        return (np.kron(np.kron(a, identity), identity)
                + np.kron(np.kron(identity, a), identity)
                + np.kron(np.kron(identity, identity), a))
    p, m = lift(plus), lift(plus.T)
    return lift(z) @ lift(z) + (p @ m + m @ p) / 2


def kernel(a):
    identity = np.eye(a.shape[0])
    return (a - 6 * identity) @ (a - 30 * identity)


def normalize(x):
    return x / np.linalg.norm(x, axis=-1, keepdims=True)


def projector(a, roots=(6, 30)):
    values, vectors = np.linalg.eigh(a)
    keep = np.min(abs(values[:, None] - np.asarray(roots)), axis=1) < 1e-7
    return vectors[:, keep] @ vectors[:, keep].T


def worker():
    directory = tempfile.TemporaryDirectory()
    library = Path(directory.name) / "worker.so"
    subprocess.run(["c++", "-O3", "-std=c++17", "-shared", "-fPIC",
                    str(Path(__file__).with_name("worker.cpp")), "-o", str(library)], check=True)
    fun = ctypes.CDLL(str(library)).contract_batch
    iptr = np.ctypeslib.ndpointer(dtype=np.int32, ndim=1, flags="C_CONTIGUOUS")
    fptr = np.ctypeslib.ndpointer(dtype=np.float32, flags="C_CONTIGUOUS")
    fun.argtypes = [ctypes.c_int] * 3 + [iptr, iptr, fptr, fptr, fptr]
    fun.restype = None
    return directory, fun


def run_worker(fun, gamma, inputs, steps):
    matrix = sparse.csr_matrix(gamma.astype(np.float32))
    matrix.eliminate_zeros()
    source = np.ascontiguousarray(inputs, dtype=np.float32)
    target = np.empty_like(source)
    fun(125, len(source), steps, matrix.indptr, matrix.indices, matrix.data, source, target)
    return target.astype(np.float64)


def exact_residual(matrix, payload):
    # Fast int64 products after an explicit worst-case accumulator check.
    # Squaring, weight application, and threshold comparisons use Python ints.
    largest = max(abs(int(payload.min())), abs(int(payload.max())))
    matrix_bound = max(sum(abs(int(v)) for v in row) for row in matrix)
    if largest * matrix_bound > np.iinfo(np.int64).max:
        raise OverflowError("integer residual does not fit the guarded accumulator")
    kx = (matrix @ np.ascontiguousarray(payload.T)).astype(object)
    return np.asarray(np.asarray(WEIGHTS, dtype=object) @ (kx * kx), dtype=object)


def exact_residual_interval(matrix, payload):
    squared = exact_residual(matrix, payload)
    # 108 d <= ||Kx|| <= 432 d in the weighted Euclidean norm.
    low = (432 * GRID) ** 2
    high = (108 * GRID) ** 2
    return squared * 1_000_000 <= high, squared * 1_000_000 > low


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=600)
    parser.add_argument("--seed", type=int, default=470125)
    parser.add_argument("--output", type=Path)
    opts = parser.parse_args()
    rng = np.random.default_rng(opts.seed)
    identity = np.eye(125)
    scale = np.sqrt(WEIGHTS)
    canonical = reference_casimir()
    ref = projector(canonical)
    exact_c = np.array(casimir().tolist(), dtype=np.int64)
    exact_k = (exact_c - 6 * np.eye(125, dtype=np.int64)) @ (
        exact_c - 30 * np.eye(125, dtype=np.int64))
    np.testing.assert_allclose(np.asarray(exact_c, dtype=float) * scale[:, None] / scale,
                               canonical, atol=2e-14)
    directory, execute = worker()
    cases = [
        "clean", "shared_axis_layout", "shared_wrong_root", "shared_operator_drift",
        "shared_small_operator_drift", "shared_early_stop", "shared_wrong_job",
        "shared_payload_decode",
    ]
    totals = {}
    for fault in cases:
        source = normalize(rng.normal(size=(opts.samples, 125)))
        actual_source = np.roll(source, 1, axis=0) if fault == "shared_wrong_job" else source
        a = canonical.copy()
        roots = (6, 30)
        if fault == "shared_axis_layout":
            permutation = np.arange(125).reshape(5, 5, 5)[::-1].ravel()
            a = a[np.ix_(permutation, permutation)]
        if fault == "shared_wrong_root":
            roots = (6, 20)
        if fault in ("shared_operator_drift", "shared_small_operator_drift"):
            # Shared basis rotation models a stale calibration transform.
            angle = 0.04 if fault == "shared_operator_drift" else 0.0012
            rotation = identity.copy()
            for i in range(0, 124, 2):
                rotation[i:i+2, i:i+2] = [[np.cos(angle), -np.sin(angle)],
                                            [np.sin(angle), np.cos(angle)]]
            a = rotation @ a @ rotation.T
        p = projector(a, roots)
        local_k = (a - roots[0] * identity) @ (a - roots[1] * identity)
        max_squared = np.linalg.norm(local_k, 2) ** 2
        min_squared = min(((e - roots[0]) * (e - roots[1])) ** 2
                          for e in [0, 2, 6, 12, 20, 30, 42] if e not in roots)
        gamma = identity - 2 * (local_k @ local_k) / (max_squared + min_squared)
        steps = 144
        if fault == "shared_early_stop":
            steps = 8
            p = np.linalg.matrix_power(gamma, steps)
        if fault == "shared_wrong_root":
            # Changing the protected roots also changes the relative gap.
            steps = 1400
        dense = actual_source @ p.T
        sparse_result = run_worker(execute, gamma, actual_source, steps)
        pending = np.rint(dense / scale * GRID).astype(np.int64)
        delivered = pending.copy()
        if fault == "shared_payload_decode":
            # A separate consumer interprets two coordinates in swapped order.
            delivered[:, [1, 11]] = delivered[:, [11, 1]]
        audited = pending
        observed = audited / GRID * scale
        ground = delivered / GRID * scale
        leak = np.linalg.norm(ground - ground @ ref, axis=1)
        output_error = np.linalg.norm(ground - source @ ref, axis=1)
        unsafe = leak > TAU
        wrong = output_error > TAU

        agreement = np.linalg.norm(observed - sparse_result, axis=1) <= TAU
        # Shared-spec contract checks consistency with the configured transform.
        contract = np.linalg.norm(observed - actual_source @ p.T, axis=1) <= TAU
        # A cheap empirical monitor calibrated to the ideal norm inequality.
        norm_screen = np.linalg.norm(observed, axis=1) <= np.linalg.norm(actual_source, axis=1) + TAU
        exact_accept, exact_reject = exact_residual_interval(exact_k, audited)
        native_ref = np.linalg.norm(observed - observed @ ref, axis=1) <= TAU
        ref_replay = np.linalg.norm(observed - source @ ref, axis=1) <= TAU
        accepted = {
            "cross_backend_agreement": agreement,
            "shared_spec_contract": contract,
            "norm_screen": norm_screen,
            "independent_exact_K": exact_accept,
            "independent_projector": native_ref,
            "independent_reference_replay": ref_replay,
        }
        metrics = {name: {
            "unsafe_leak_accepted": int((accept & unsafe).sum()),
            "wrong_output_accepted": int((accept & wrong).sum()),
            "safe_leak_blocked": int((~accept & ~unsafe).sum()),
        } for name, accept in accepted.items()}
        paired = {
            name: [int((accept & ~exact_accept & unsafe).sum()),
                   int((~accept & exact_accept & unsafe).sum())]
            for name, accept in accepted.items() if name != "independent_exact_K"
        }
        totals[fault] = {
            "trials": opts.samples, "unsafe_leak": int(unsafe.sum()),
            "wrong_output": int(wrong.sum()),
            "exact_K_inconclusive": int((~exact_accept & ~exact_reject).sum()),
            "metrics": metrics, "paired_unsafe_disagreements": paired,
        }
    directory.cleanup()
    result = {"seed": opts.seed, "samples_per_scenario": opts.samples, "tolerance": TAU,
              "versions": {"python": platform.python_version(), "numpy": np.__version__,
                           "scipy": scipy.__version__}, "scenarios": totals}
    rendered = json.dumps(result, indent=2) + "\n"
    if opts.output:
        opts.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
