#!/usr/bin/env python3
"""Audit pinned PyTorch state dicts and exercise a pinned auth-kernel policy artifact."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile

CASES = {
    "active": [True], "inactive": [False], "wrong_principal": [False],
    "revoked": [False], "ungranted": [False], "invalid_signature": [False],
    "out_of_scope": [False], "replay": [True, False],
}


def read_pinned(path, expected):
    if not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise ValueError("Expected a lowercase SHA-256 from the deployment record")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"SHA-256 mismatch for {path.name}")
    return data


def projector(torch):
    # Orthonormal |m1,m2,m3> basis, descending m = 2, 1, 0, -1, -2.
    m = torch.arange(2, -3, -1, dtype=torch.float64)
    up = torch.diag(torch.sqrt(6 - m[1:] * (m[1:] + 1)), diagonal=1)
    eye = torch.eye(5, dtype=torch.float64)

    def total(x):
        return torch.kron(torch.kron(x, eye), eye) + torch.kron(torch.kron(eye, x), eye) + torch.kron(torch.kron(eye, eye), x)

    z = total(torch.diag(m))
    j = total(up)
    c = z @ z + (j @ j.T + j.T @ j) / 2
    values, vectors = torch.linalg.eigh(c)
    selected = ((values - 6).abs() < 1e-9) | ((values - 30).abs() < 1e-9)
    basis = vectors[:, selected]
    if basis.shape[1] != 47:
        raise ValueError("Unexpected E47 projector rank")
    return basis @ basis.T


def audit_weights(data, atol, rtol):
    import torch

    state = torch.load(io.BytesIO(data), map_location="cpu", weights_only=True)
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    if not isinstance(state, dict) or not state:
        raise ValueError("Expected a nonempty state_dict")
    p = projector(torch)
    q = torch.eye(125, dtype=p.dtype) - p
    checks = {}
    for name, tensor in sorted(state.items()):
        if not isinstance(name, str) or not isinstance(tensor, torch.Tensor) or tensor.layout != torch.strided:
            raise ValueError(f"Unsupported state_dict entry: {name!r}")
        value = tensor.dequantize() if tensor.is_quantized else tensor
        if not (value.is_floating_point() or value.is_complex()):
            raise ValueError(f"Unsupported tensor dtype: {name}")
        value = value.to(torch.complex128 if value.is_complex() else torch.float64)
        if not bool(torch.isfinite(value).all()):
            raise ValueError(f"Nonfinite coefficients: {name}")
        if name == "weight" or name.endswith(".weight"):
            if value.shape != (125, 125):
                raise ValueError(f"Expected a 125 × 125 canonical weight: {name}")
            left, right = p.to(value.dtype), q.to(value.dtype)
            observed = max(float(torch.linalg.matrix_norm(left @ value @ right, ord=2)),
                           float(torch.linalg.matrix_norm(right @ value @ left, ord=2)))
            limit = atol + rtol * float(torch.linalg.matrix_norm(value, ord=2))
        elif name == "bias" or name.endswith(".bias"):
            if value.shape != (125,):
                raise ValueError(f"Expected a 125-entry bias: {name}")
            observed = float(torch.linalg.vector_norm(value))
            limit = atol
        else:
            raise ValueError(f"Unclassified entry: {name}")
        checks[name] = {"observed": observed, "limit": limit,
                        "passed": math.isfinite(observed) and math.isfinite(limit) and observed <= limit}
    if not any(name == "weight" or name.endswith(".weight") for name in checks):
        raise ValueError("Expected at least one audited weight")
    return {"torch": torch.__version__, "tensor_checks": checks,
            "passed": all(item["passed"] for item in checks.values())}


def audit_policy(data, timeout):
    with tempfile.TemporaryDirectory() as directory:
        artifact = Path(directory) / "policy.pyz"
        artifact.write_bytes(data)
        process = subprocess.run(
            [sys.executable, "-I", str(artifact)], input=json.dumps(list(CASES)),
            text=True, capture_output=True, cwd=directory, timeout=timeout, check=True,
        )
    reply = json.loads(process.stdout)
    if not isinstance(reply, dict) or set(reply) != set(CASES):
        raise ValueError("Incomplete policy receipts")
    checks = {}
    for name, expected in CASES.items():
        decisions = reply[name]
        checks[name] = isinstance(decisions, list) and all(type(x) is bool for x in decisions) and decisions == expected
    return {"case_checks": checks, "passed": all(checks.values())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for item in ("weights", "policy"):
        parser.add_argument(f"--{item}", type=Path, required=True)
        parser.add_argument(f"--{item}-sha256", required=True)
    parser.add_argument("--atol", type=float, required=True)
    parser.add_argument("--rtol", type=float, required=True)
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    if not all(math.isfinite(x) and x >= 0 for x in (args.atol, args.rtol)) or not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Tolerances must be finite and nonnegative and timeout must be finite and positive")
    results = {"schema": "e47.runtime-audit.v1", "python": sys.version.split()[0]}
    for name, path, digest, audit in (
        ("ITGC-AI-01", args.policy, args.policy_sha256, lambda data: audit_policy(data, args.timeout)),
        ("ITGC-AI-02", args.weights, args.weights_sha256, lambda data: audit_weights(data, args.atol, args.rtol)),
    ):
        try:
            results[name] = {"sha256": digest, **audit(read_pinned(path, digest))}
        except Exception as error:
            results[name] = {"expected_sha256": digest, "passed": False,
                             "error_type": type(error).__name__, "error": str(error) if isinstance(error, ValueError) else "Audit execution failed"}
    results["passed"] = all(results[name]["passed"] for name in ("ITGC-AI-01", "ITGC-AI-02"))
    print(json.dumps(results, indent=2, sort_keys=True, allow_nan=False))
    return 0 if results["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
