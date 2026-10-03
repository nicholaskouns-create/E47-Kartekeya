#!/usr/bin/env python3
"""Mathematical City generic spectral contraction engine.

Shared operator grammar used by the City's finite spectral interfaces:

    K -> Q = K^† K -> ker(K) -> P -> Gamma = I - eps Q -> Gamma^n -> P

This module is domain-agnostic. It deliberately contains no E47 constants.
A caller supplies the typed constraint/operator K.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from typing import Any

import numpy as np


TOL = 1.0e-10


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _stable_scalar(label: str) -> float:
    """Deterministic FNV-1a signal in [-1,1], shared exactly with browser JS."""
    h = 2166136261
    for b in label.encode("utf-8"):
        h ^= b
        h = (h * 16777619) & 0xFFFFFFFF
    n = h / float(0xFFFFFFFF)
    return 2.0 * n - 1.0


@dataclass
class SpectralContraction:
    dimension: int
    constraint_rows: int
    kernel_dimension: int
    rank: int
    positive_min: float
    positive_max: float
    epsilon_max: float
    epsilon_star: float
    rho_star: float
    projector_residual: float
    annihilation_residual: float
    gamma_projector_residual: float
    spectrum: list[float]
    operator_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def compile_spectral_contraction(K: np.ndarray, *, tol: float = TOL) -> tuple[SpectralContraction, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Compile K into Q, P, Gamma using the shared positive-generator rule.

    Returns: report, Q, P, Gamma, eigenvalues(Q)
    """
    K = np.asarray(K)
    if K.ndim != 2:
        raise ValueError("K must be a 2D matrix")
    # Preserve a complex operator when supplied. The canonical positive generator is
    # Q = K^† K; real incidence operators are a strict specialization.
    dtype = complex if np.iscomplexobj(K) else float
    K = K.astype(dtype, copy=False)
    d = K.shape[1]
    Q = K.conj().T @ K
    Q = 0.5 * (Q + Q.conj().T)
    evals, evecs = np.linalg.eigh(Q)
    scale = max(1.0, float(np.max(np.abs(evals))) if evals.size else 1.0)
    zero = np.abs(evals) <= tol * scale
    V0 = evecs[:, zero]
    P = V0 @ V0.conj().T if V0.size else np.zeros((d, d), dtype=Q.dtype)
    pos = evals[~zero]

    if pos.size:
        pmin = float(np.min(pos))
        pmax = float(np.max(pos))
        eps_max = 2.0 / pmax
        eps_star = 2.0 / (pmin + pmax)
        rho_star = (pmax - pmin) / (pmax + pmin)
        Gamma = np.eye(d, dtype=Q.dtype) - eps_star * Q
    else:
        pmin = pmax = 0.0
        eps_max = eps_star = 0.0
        rho_star = 0.0
        Gamma = np.eye(d, dtype=Q.dtype)

    projector_residual = float(np.linalg.norm(P @ P - P, ord=2)) if d else 0.0
    annihilation_residual = float(np.linalg.norm(K @ P, ord=2)) if K.size and P.size else 0.0
    gamma_projector_residual = float(np.linalg.norm(Gamma @ P - P, ord=2)) if d else 0.0

    report = SpectralContraction(
        dimension=d,
        constraint_rows=K.shape[0],
        kernel_dimension=int(np.sum(zero)),
        rank=int(d - np.sum(zero)),
        positive_min=pmin,
        positive_max=pmax,
        epsilon_max=eps_max,
        epsilon_star=eps_star,
        rho_star=rho_star,
        projector_residual=projector_residual,
        annihilation_residual=annihilation_residual,
        gamma_projector_residual=gamma_projector_residual,
        spectrum=[float(x) for x in evals],
        operator_hash=_sha(
            np.round(K.real, 12).tolist()
            if not np.iscomplexobj(K) or float(np.max(np.abs(K.imag))) <= tol
            else {"real": np.round(K.real, 12).tolist(), "imag": np.round(K.imag, 12).tolist()}
        ),
    )
    return report, Q, P, Gamma, evals


def contraction_trajectory(Gamma: np.ndarray, P: np.ndarray, labels: list[str], *, steps: int = 42) -> dict[str, Any]:
    d = Gamma.shape[0]
    if d != len(labels):
        raise ValueError("labels must match operator dimension")
    if d == 0:
        return {"states": [], "residuals": [], "limit": [], "initial": []}
    x = np.array([_stable_scalar(label) for label in labels], dtype=float)
    if np.linalg.norm(x) < 1e-15:
        x = np.linspace(-1.0, 1.0, d)
    target = P @ x
    states = [x.tolist()]
    residuals = [float(np.linalg.norm(x - target))]
    cur = x.copy()
    for _ in range(max(1, steps)):
        cur = Gamma @ cur
        states.append(cur.tolist())
        residuals.append(float(np.linalg.norm(cur - target)))
    return {
        "initial": x.tolist(),
        "limit": target.tolist(),
        "states": states,
        "residuals": residuals,
    }


def semantic_constraint_system(envelope: Any) -> dict[str, Any]:
    """Build a typed incidence operator from a SemanticEnvelope-like object.

    Nodes are claims plus typed semantic atoms. Edges connect an atom to the claim(s)
    that explicitly contain or own it. Shared atoms therefore join claims into the same
    semantic component. K is the weighted incidence matrix; Q=K^T K is the graph Laplacian.

    This is a structural visualization/audit operator. It is not a truth metric.
    """
    if isinstance(envelope, dict):
        raw = dict(envelope)
    else:
        raw = {name: getattr(envelope, name, []) for name in [
            "claims", "entities", "actions", "objects", "relations", "negations",
            "conditions", "quantities", "times", "modalities", "provenance",
            "evidence_class", "authority", "confidence", "dependencies",
            "contradictions", "unresolved"
        ]}
    claims = list(raw.get("claims", []) or [])
    typed_fields = [
        "entities", "actions", "objects", "negations", "conditions", "quantities",
        "times", "modalities", "provenance", "evidence_class", "authority",
        "confidence", "dependencies", "contradictions", "unresolved",
    ]

    nodes: list[dict[str, Any]] = []
    index: dict[tuple[str, str], int] = {}

    def add_node(kind: str, label: str) -> int:
        key = (kind, label)
        if key in index:
            return index[key]
        idx = len(nodes)
        index[key] = idx
        nodes.append({"id": idx, "kind": kind, "label": label})
        return idx

    claim_ids = [add_node("claim", c) for c in claims]
    edges: list[dict[str, Any]] = []

    # Typed atoms connect only where the source envelope explicitly associates them.
    for field in typed_fields:
        values = list(raw.get(field, []) or [])
        for value in values:
            label = str(value)
            atom_id = add_node(field, label)
            matches = []
            low = label.lower()
            for ci, claim in enumerate(claims):
                if low and low in claim.lower():
                    matches.append(claim_ids[ci])
            # Sentence-valued fields (negations/conditions/etc.) often equal a claim.
            if not matches and label in claims:
                matches.append(claim_ids[claims.index(label)])
            for cid in matches:
                edges.append({"source": cid, "target": atom_id, "weight": 1.0, "kind": field})

    # Explicit relations, when present, are encoded without inventing endpoints.
    for rel in list(raw.get("relations", []) or []):
        if not isinstance(rel, dict):
            continue
        s = rel.get("source") or rel.get("subject")
        t = rel.get("target") or rel.get("object")
        if s is None or t is None:
            continue
        sid = add_node("relation_entity", str(s))
        tid = add_node("relation_entity", str(t))
        edges.append({"source": sid, "target": tid, "weight": 1.0, "kind": "relation"})

    # If parsing produced claims but no typed edges, preserve independent claim components.
    n = len(nodes)
    if not edges:
        K = np.zeros((0, n), dtype=float)
    else:
        K = np.zeros((len(edges), n), dtype=float)
        for r, edge in enumerate(edges):
            w = float(edge.get("weight", 1.0)) ** 0.5
            K[r, edge["source"]] = w
            K[r, edge["target"]] = -w

    report, Q, P, Gamma, _ = compile_spectral_contraction(K)
    trajectory = contraction_trajectory(Gamma, P, [f'{n["kind"]}:{n["label"]}' for n in nodes])
    return {
        "nodes": nodes,
        "edges": edges,
        "K": K,
        "Q": Q,
        "P": P,
        "Gamma": Gamma,
        "report": report,
        "trajectory": trajectory,
    }


def compact_payload(system: dict[str, Any], *, max_spectrum: int = 64) -> dict[str, Any]:
    report: SpectralContraction = system["report"]
    spectrum = report.spectrum
    if len(spectrum) > max_spectrum:
        spectrum = spectrum[:max_spectrum]
    return {
        "nodes": system["nodes"],
        "edges": system["edges"],
        "report": {**report.to_dict(), "spectrum": spectrum},
        "trajectory": system["trajectory"],
    }


def self_test() -> None:
    class E:
        claims = ["Alpha is linked to 2.", "Beta is not linked to 2."]
        entities = ["Alpha", "Beta"]
        actions = []
        objects = []
        relations = []
        negations = ["Beta is not linked to 2."]
        conditions = []
        quantities = ["2"]
        times = []
        modalities = []
        provenance = []
        evidence_class = []
        authority = []
        confidence = []
        dependencies = []
        contradictions = []
        unresolved = []
    s = semantic_constraint_system(E())
    r = s["report"]
    assert r.dimension == len(s["nodes"])
    assert r.kernel_dimension >= 1
    assert r.projector_residual < 1e-8
    assert r.annihilation_residual < 1e-8
    assert s["trajectory"]["residuals"][-1] <= s["trajectory"]["residuals"][0] + 1e-12
    print("CITY SPECTRAL ENGINE SELF-TEST: PASS")


if __name__ == "__main__":
    self_test()
