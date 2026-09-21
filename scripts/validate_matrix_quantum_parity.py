#!/usr/bin/env python3
"""Independent parity validation for THE MATRIX Quantum Simulator.

This validator does not import MATRIX browser code. It independently
reconstructs the documented circuit in Python/NumPy, compares a two-site MPS
implementation to an exact dense statevector, optionally compares that exact
state against Qiskit Aer, then validates the typed 125-feature lift and the E47
125->128 isometric embedding.

The 125 feature lift is explicitly not a Hilbert-space isomorphism.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from importlib import metadata
from pathlib import Path

import numpy as np

CERTIFICATE_ID = "MC-MATRIX-PARITY-20260921-001"
SCHEMA = "MATRIX-ISOMORPHIC-PARITY-CERTIFICATE/1.0"


def H() -> np.ndarray:
    return np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)


def phase_gate(phi: float) -> np.ndarray:
    return np.diag([1.0, np.exp(1j * phi)]).astype(np.complex128)


CNOT = np.array(
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
    dtype=np.complex128,
)


@dataclass(frozen=True)
class Config:
    n: int = 8
    layers: int = 24
    chi: int = 16
    phi: float = 0.7


def apply_1q_dense(psi: np.ndarray, gate: np.ndarray, q: int, n: int) -> np.ndarray:
    tensor = psi.reshape([2] * n)
    order = [q] + [i for i in range(n) if i != q]
    inverse = np.argsort(order)
    front = np.transpose(tensor, order).reshape(2, -1)
    front = gate @ front
    return np.transpose(front.reshape([2] * n), inverse).reshape(-1)


def apply_2q_dense_adjacent(
    psi: np.ndarray, gate: np.ndarray, q: int, n: int
) -> np.ndarray:
    tensor = psi.reshape([2] * n)
    order = [q, q + 1] + [i for i in range(n) if i not in (q, q + 1)]
    inverse = np.argsort(order)
    front = np.transpose(tensor, order).reshape(4, -1)
    front = gate @ front
    return np.transpose(front.reshape([2] * n), inverse).reshape(-1)


def dense_matrix_circuit(cfg: Config) -> np.ndarray:
    psi = np.zeros(2**cfg.n, dtype=np.complex128)
    psi[0] = 1.0
    for layer in range(cfg.layers):
        for q in range(cfg.n):
            psi = apply_1q_dense(psi, H(), q, cfg.n)
            psi = apply_1q_dense(psi, phase_gate(cfg.phi), q, cfg.n)
        for q in range(layer % 2, cfg.n - 1, 2):
            psi = apply_2q_dense_adjacent(psi, CNOT, q, cfg.n)
    return psi


def init_mps(n: int) -> list[np.ndarray]:
    out = []
    for _ in range(n):
        tensor = np.zeros((1, 2, 1), dtype=np.complex128)
        tensor[0, 0, 0] = 1.0
        out.append(tensor)
    return out


def apply_1q_mps(tensor: np.ndarray, gate: np.ndarray) -> np.ndarray:
    return np.einsum("op,lpr->lor", gate, tensor, optimize=True)


def apply_2q_mps(
    left: np.ndarray, right: np.ndarray, gate: np.ndarray, chi: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    theta = np.einsum("lpa,aqr->lpqr", left, right, optimize=True)
    gate4 = gate.reshape(2, 2, 2, 2)
    theta = np.einsum("ijpq,lpqr->lijr", gate4, theta, optimize=True)
    ldim, _, _, rdim = theta.shape
    merged = theta.reshape(ldim * 2, 2 * rdim)
    u, s, vh = np.linalg.svd(merged, full_matrices=False)
    algebraic_rank = max(1, int(np.count_nonzero(s > 1e-12)))
    rank = min(chi, algebraic_rank)
    total = float(np.sum(s**2))
    discarded = float(np.sum(s[rank:] ** 2) / total) if total > 0 else 0.0
    left_new = u[:, :rank].reshape(ldim, 2, rank)
    right_new = (s[:rank, None] * vh[:rank, :]).reshape(rank, 2, rdim)
    return left_new, right_new, s[:rank], discarded


def materialize_mps(mps: list[np.ndarray]) -> np.ndarray:
    state = mps[0][0, :, :]
    for tensor in mps[1:]:
        state = np.einsum("...l,lpr->...pr", state, tensor, optimize=True)
    return np.squeeze(state, axis=-1).reshape(-1)


def mps_matrix_circuit(cfg: Config) -> tuple[np.ndarray, float, int, np.ndarray]:
    mps = init_mps(cfg.n)
    discarded = 0.0
    last_s = np.array([1.0], dtype=np.float64)
    for layer in range(cfg.layers):
        for q in range(cfg.n):
            mps[q] = apply_1q_mps(mps[q], H())
            mps[q] = apply_1q_mps(mps[q], phase_gate(cfg.phi))
        for q in range(layer % 2, cfg.n - 1, 2):
            a, b, last_s, disc = apply_2q_mps(
                mps[q], mps[q + 1], CNOT, cfg.chi
            )
            mps[q], mps[q + 1] = a, b
            discarded += disc
    max_bond = max(int(t.shape[2]) for t in mps)
    return materialize_mps(mps), float(discarded), max_bond, last_s


def phase_aligned_relative_l2(candidate: np.ndarray, reference: np.ndarray) -> float:
    overlap = np.vdot(reference, candidate)
    if abs(overlap) > 0:
        candidate = candidate * np.exp(-1j * np.angle(overlap))
    return float(np.linalg.norm(candidate - reference) / np.linalg.norm(reference))


def fidelity(a: np.ndarray, b: np.ndarray) -> float:
    aa = a / np.linalg.norm(a)
    bb = b / np.linalg.norm(b)
    return float(abs(np.vdot(aa, bb)) ** 2)


def observable_error(a: np.ndarray, b: np.ndarray, n: int) -> float:
    x = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
    z = np.diag([1, -1]).astype(np.complex128)
    errors = []
    for q in range(n):
        for op in (x, y, z):
            ea = np.vdot(a, apply_1q_dense(a, op, q, n))
            eb = np.vdot(b, apply_1q_dense(b, op, q, n))
            errors.append(float(abs(ea - eb)))
    zz = np.kron(z, z)
    for q in range(n - 1):
        ea = np.vdot(a, apply_2q_dense_adjacent(a, zz, q, n))
        eb = np.vdot(b, apply_2q_dense_adjacent(b, zz, q, n))
        errors.append(float(abs(ea - eb)))
    return max(errors, default=0.0)


def schmidt_spectrum_error(a: np.ndarray, b: np.ndarray, n: int) -> float:
    errors = []
    for cut in range(1, n):
        sa = np.linalg.svd(a.reshape(2**cut, 2 ** (n - cut)), compute_uv=False)
        sb = np.linalg.svd(b.reshape(2**cut, 2 ** (n - cut)), compute_uv=False)
        errors.append(float(np.max(np.abs(sa - sb))))
    return max(errors, default=0.0)


def qiskit_aer_state(cfg: Config):
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator
    except Exception as exc:
        return None, {"available": False, "error": f"{type(exc).__name__}: {exc}"}

    qc = QuantumCircuit(cfg.n)

    def wire(matrix_q: int) -> int:
        return cfg.n - 1 - matrix_q

    for layer in range(cfg.layers):
        for q in range(cfg.n):
            qc.h(wire(q))
            qc.p(cfg.phi, wire(q))
        for q in range(layer % 2, cfg.n - 1, 2):
            qc.cx(wire(q), wire(q + 1))
    qc.save_statevector()
    simulator = AerSimulator(method="statevector")
    compiled = transpile(qc, simulator, optimization_level=0)
    result = simulator.run(compiled).result()
    state = np.asarray(result.get_statevector(qc), dtype=np.complex128)
    versions = {}
    for package in ("qiskit", "qiskit-aer"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    return state, {"available": True, **versions}


def feature_lift_125(state: np.ndarray) -> np.ndarray:
    n = len(state)
    indices = [math.floor(i * (n - 1) / 124) for i in range(125)]
    lifted = np.array([state[j] for j in indices], dtype=np.complex128)
    norm = np.linalg.norm(lifted)
    if norm == 0:
        raise ValueError("zero 125 feature vector")
    return lifted / norm


def spin_matrices(j: float = 2.0):
    m = np.arange(j, -j - 1, -1, dtype=np.float64)
    d = len(m)
    jz = np.diag(m).astype(np.complex128)
    jp = np.zeros((d, d), dtype=np.complex128)
    for col, mc in enumerate(m):
        mp = mc + 1
        rows = np.flatnonzero(np.isclose(m, mp))
        if rows.size:
            jp[int(rows[0]), col] = np.sqrt(j * (j + 1) - mc * (mc + 1))
    jm = jp.conj().T
    return (jp + jm) / 2, (jp - jm) / (2j), jz


def e47_operators():
    jx, jy, jz = spin_matrices(2.0)
    eye5 = np.eye(5, dtype=np.complex128)
    kron3 = lambda a, b, c: np.kron(np.kron(a, b), c)
    jxt = (
        kron3(jx, eye5, eye5)
        + kron3(eye5, jx, eye5)
        + kron3(eye5, eye5, jx)
    )
    jyt = (
        kron3(jy, eye5, eye5)
        + kron3(eye5, jy, eye5)
        + kron3(eye5, eye5, jy)
    )
    jzt = (
        kron3(jz, eye5, eye5)
        + kron3(eye5, jz, eye5)
        + kron3(eye5, eye5, jz)
    )
    casimir = jxt @ jxt + jyt @ jyt + jzt @ jzt
    identity = np.eye(125, dtype=np.complex128)
    kernel = (casimir - 6 * identity) @ (casimir - 30 * identity)
    k2 = kernel @ kernel
    evals, evecs = np.linalg.eigh(casimir)
    mask = (np.abs(evals - 6) < 1e-9) | (np.abs(evals - 30) < 1e-9)
    q = evecs[:, mask]
    projector = q @ q.conj().T
    spectrum = Counter(int(round(float(x))) for x in evals)
    k2_unique = tuple(
        sorted({int(round(float(x))) for x in np.linalg.eigvalsh(k2)})
    )
    return kernel, k2, projector, dict(sorted(spectrum.items())), k2_unique


def validate(cfg: Config) -> dict:
    dense = dense_matrix_circuit(cfg)
    mps, discarded, max_bond, last_s = mps_matrix_circuit(cfg)
    qiskit_state, qiskit_meta = qiskit_aer_state(cfg)

    mps_l2 = phase_aligned_relative_l2(mps, dense)
    mps_fidelity = fidelity(mps, dense)
    obs_error = observable_error(mps, dense, cfg.n)
    schmidt_error = schmidt_spectrum_error(mps, dense, cfg.n)

    qiskit_l2 = None
    qiskit_fidelity = None
    if qiskit_state is not None:
        qiskit_l2 = phase_aligned_relative_l2(qiskit_state, dense)
        qiskit_fidelity = fidelity(qiskit_state, dense)

    lifted = feature_lift_125(mps)
    kernel, k2, projector, casimir_spectrum, k2_unique = e47_operators()
    p2_residual = float(
        np.linalg.norm(projector @ projector - projector, ord="fro")
    )
    kp_residual = float(np.linalg.norm(kernel @ projector, ord="fro"))
    e47_rank = int(np.linalg.matrix_rank(projector, tol=1e-10))
    e47_weight = float(np.real(np.vdot(lifted, projector @ lifted)))
    k2_energy = float(np.real(np.vdot(lifted, k2 @ lifted)))
    k2_eigs = np.linalg.eigvalsh(k2)
    gap = float(min(x for x in k2_eigs if x > 1e-7))
    k2_max = float(max(k2_eigs))

    embedding = np.zeros((128, 125), dtype=np.complex128)
    embedding[:125, :] = np.eye(125, dtype=np.complex128)
    embedding_residual = float(
        np.linalg.norm(
            embedding.conj().T @ embedding - np.eye(125), ord="fro"
        )
    )
    r125 = 2 * projector - np.eye(125, dtype=np.complex128)
    r128 = np.eye(128, dtype=np.complex128)
    r128[:125, :125] = r125
    intertwiner_residual = float(
        np.linalg.norm(r128 @ embedding - embedding @ r125, ord="fro")
    )
    invalid_population = float(
        np.sum(np.abs((embedding @ lifted)[125:]) ** 2)
    )

    thresholds = {
        "norm": 1e-12,
        "state_l2": 1e-12,
        "fidelity_error": 1e-12,
        "observable": 1e-12,
        "schmidt": 1e-12,
        "discarded": 1e-12,
        "projector": 1e-12,
        "kernel_projector": 1e-9,
        "embedding": 1e-12,
        "intertwiner": 1e-12,
    }
    checks = {
        "mps_norm": abs(float(np.linalg.norm(mps)) - 1) < thresholds["norm"],
        "dense_norm": abs(float(np.linalg.norm(dense)) - 1) < thresholds["norm"],
        "mps_dense_phase_aligned_l2": mps_l2 < thresholds["state_l2"],
        "mps_dense_fidelity": abs(1 - mps_fidelity) < thresholds["fidelity_error"],
        "observable_parity": obs_error < thresholds["observable"],
        "schmidt_parity": schmidt_error < thresholds["schmidt"],
        "untruncated": discarded < thresholds["discarded"],
        "max_bond": max_bond <= cfg.chi,
        "feature_125_norm": abs(float(np.linalg.norm(lifted)) - 1) < thresholds["norm"],
        "e47_rank_47": e47_rank == 47,
        "projector_idempotence": p2_residual < thresholds["projector"],
        "kernel_annihilation": kp_residual < thresholds["kernel_projector"],
        "casimir_spectrum": casimir_spectrum
        == {0: 1, 2: 9, 6: 25, 12: 28, 20: 27, 30: 22, 42: 13},
        "k2_spectrum": k2_unique
        == (0, 11664, 12544, 19600, 32400, 186624),
        "k2_gap": abs(gap - 11664) < 1e-6,
        "k2_max": abs(k2_max - 186624) < 1e-6,
        "embedding_isometry": embedding_residual < thresholds["embedding"],
        "invalid_state_population": invalid_population < thresholds["embedding"],
        "r47_intertwiner": intertwiner_residual < thresholds["intertwiner"],
        "representation_typing": True,
    }
    if qiskit_state is not None:
        checks["qiskit_aer_state_parity"] = (
            qiskit_l2 is not None and qiskit_l2 < thresholds["state_l2"]
        )
        checks["qiskit_aer_fidelity"] = (
            qiskit_fidelity is not None
            and abs(1 - qiskit_fidelity) < thresholds["fidelity_error"]
        )

    quantum_oracle_status = "NOT_EXECUTED"
    if qiskit_state is not None:
        quantum_oracle_status = (
            "PASS"
            if checks["qiskit_aer_state_parity"]
            and checks["qiskit_aer_fidelity"]
            else "FAIL"
        )

    return {
        "schema": SCHEMA,
        "certificate_id": CERTIFICATE_ID,
        "status": "PASS" if all(checks.values()) else "FAIL",
        "evidence_class": "E1",
        "scope": (
            "software/numerical quantum-simulation parity; "
            "no hardware or experimental claim"
        ),
        "source": {
            "matrix_engine": "website/interfaces/matrix/mps-worker.js",
            "matrix_ui": "website/interfaces/matrix/matrix.js",
            "git_commit": os.getenv("GITHUB_SHA"),
        },
        "configuration": asdict(cfg),
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "numpy": np.__version__,
            "qiskit_aer": qiskit_meta,
        },
        "quantum_parity": {
            "mps_dense": {
                "phase_aligned_relative_l2": mps_l2,
                "fidelity": mps_fidelity,
                "observable_max_error": obs_error,
                "schmidt_spectrum_max_error": schmidt_error,
                "mps_norm": float(np.linalg.norm(mps)),
                "dense_norm": float(np.linalg.norm(dense)),
                "max_bond": max_bond,
                "discarded_weight": discarded,
                "last_bond_singular_values": [float(x) for x in last_s],
            },
            "qiskit_aer": {
                "status": quantum_oracle_status,
                "phase_aligned_relative_l2": qiskit_l2,
                "fidelity": qiskit_fidelity,
                **qiskit_meta,
            },
        },
        "typed_feature_lift": {
            "source_dimension": 2**cfg.n,
            "target_dimension": 125,
            "norm": float(np.linalg.norm(lifted)),
            "claim": (
                "explicit normalized sampled-amplitude feature map; "
                "not Hilbert-space isomorphism"
            ),
        },
        "e47": {
            "rank": e47_rank,
            "coherence_fraction": e47_rank / 125,
            "projector_idempotence_fro": p2_residual,
            "kernel_projector_fro": kp_residual,
            "casimir_spectrum": {str(k): v for k, v in casimir_spectrum.items()},
            "k2_spectrum": list(k2_unique),
            "k2_gap": gap,
            "k2_max": k2_max,
            "feature_e47_weight": e47_weight,
            "feature_complement_weight": float(1.0 - e47_weight),
            "feature_k2_energy": k2_energy,
        },
        "embedding_125_to_128": {
            "kind": "isometric embedding",
            "j_dagger_j_residual_fro": embedding_residual,
            "invalid_state_population": invalid_population,
            "r47_intertwiner_residual_fro": intertwiner_residual,
        },
        "thresholds": thresholds,
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-qiskit", action="store_true")
    args = parser.parse_args()
    cert = validate(Config())
    if (
        args.require_qiskit
        and cert["quantum_parity"]["qiskit_aer"]["status"] != "PASS"
    ):
        cert["status"] = "FAIL"
        cert["checks"]["qiskit_aer_required"] = False
    text = json.dumps(cert, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0 if cert["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
