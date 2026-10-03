
#!/usr/bin/env python3
"""
TIP: Transported Identity Projector
===================================

A computational-physics reference implementation of the construction:

    carrier X_t
        -> relational complex R_eps[X_t]
        -> Hodge operator Delta_1(t)
        -> harmonic identity sector ker Delta_1(t)
        -> projector P_t
        -> admissible transport
        -> prediction
        -> seal
        -> reveal / score

Dependencies: numpy only.

Interpretation:
- For a classical swarm/city, rho is a classical/probabilistic embedding.
- For a genuine quantum system, replace the classical state model with a
  physically specified density operator/channel.
- "Quantum-information language" here is a mathematical interface, not a claim
  that the swarm itself is physically quantum.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
import hashlib
import itertools
import json
import math

import numpy as np


Array = np.ndarray
Edge = Tuple[int, int]
Triangle = Tuple[int, int, int]


# ---------------------------------------------------------------------------
# Canonical serialization / Mnemosyne-style commitments
# ---------------------------------------------------------------------------

def _jsonable(x: Any) -> Any:
    if isinstance(x, np.ndarray):
        return x.tolist()
    if isinstance(x, (np.floating, np.integer)):
        return x.item()
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    return x


def canonical_json(obj: Any) -> str:
    """Deterministic JSON representation suitable for hashing."""
    return json.dumps(
        _jsonable(obj),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_commit(obj: Any) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def verify_commit(obj: Any, seal: str) -> bool:
    return sha256_commit(obj) == seal


# ---------------------------------------------------------------------------
# Ambient edge coordinates
# ---------------------------------------------------------------------------

def ambient_edges(n: int) -> List[Edge]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def ambient_edge_index(n: int) -> Dict[Edge, int]:
    return {e: k for k, e in enumerate(ambient_edges(n))}


# ---------------------------------------------------------------------------
# Vietoris-Rips complex and Hodge Laplacian
# ---------------------------------------------------------------------------

def rips_complex(points: Array, epsilon: float) -> Tuple[List[Edge], List[Triangle]]:
    """
    Build the Vietoris-Rips 2-skeleton at scale epsilon.
    Edges and triangles use the canonical orientation i < j < k.
    """
    x = np.asarray(points, dtype=float)
    n = x.shape[0]

    d2 = np.sum((x[:, None, :] - x[None, :, :]) ** 2, axis=-1)
    eps2 = float(epsilon) ** 2

    edges = [(i, j) for i in range(n) for j in range(i + 1, n)
             if d2[i, j] <= eps2]

    edge_set = set(edges)
    triangles: List[Triangle] = []
    for i, j, k in itertools.combinations(range(n), 3):
        if ((i, j) in edge_set and
            (i, k) in edge_set and
            (j, k) in edge_set):
            triangles.append((i, j, k))

    return edges, triangles


def boundary_matrices(
    n_vertices: int,
    edges: Sequence[Edge],
    triangles: Sequence[Triangle],
) -> Tuple[Array, Array]:
    """
    Return B1: C1 -> C0 and B2: C2 -> C1.

    Edge [i,j] with i<j has boundary v_j - v_i.
    Triangle [i,j,k] with i<j<k has boundary
        [j,k] - [i,k] + [i,j].
    """
    m = len(edges)
    t = len(triangles)

    edge_to_col = {e: c for c, e in enumerate(edges)}

    B1 = np.zeros((n_vertices, m), dtype=float)
    for c, (i, j) in enumerate(edges):
        B1[i, c] = -1.0
        B1[j, c] = +1.0

    B2 = np.zeros((m, t), dtype=float)
    for c, (i, j, k) in enumerate(triangles):
        B2[edge_to_col[(j, k)], c] += +1.0
        B2[edge_to_col[(i, k)], c] += -1.0
        B2[edge_to_col[(i, j)], c] += +1.0

    return B1, B2


def hodge_laplacian_1(
    n_vertices: int,
    edges: Sequence[Edge],
    triangles: Sequence[Triangle],
) -> Array:
    """
    1-Hodge Laplacian:
        Delta_1 = B1^T B1 + B2 B2^T
    """
    B1, B2 = boundary_matrices(n_vertices, edges, triangles)
    return B1.T @ B1 + B2 @ B2.T


def _kernel_basis_symmetric(A: Array, atol: float = 1e-10, rtol: float = 1e-9):
    """Orthonormal basis for the numerical kernel of a real symmetric matrix."""
    if A.size == 0:
        return np.zeros((A.shape[0], 0)), np.array([], dtype=float)

    evals, evecs = np.linalg.eigh((A + A.T) * 0.5)
    scale = max(1.0, float(np.max(np.abs(evals))))
    mask = np.abs(evals) <= (atol + rtol * scale)
    return evecs[:, mask], evals


@dataclass
class HodgeSnapshot:
    n_agents: int
    dimension: int
    epsilon: float
    edges: List[Edge]
    triangles: List[Triangle]
    beta1: int
    local_eigenvalues: Array
    harmonic_basis_ambient: Array
    projector_ambient: Array
    snapshot_hash: str


def hodge_snapshot(
    points: Array,
    epsilon: float,
    atol: float = 1e-10,
    rtol: float = 1e-9,
) -> HodgeSnapshot:
    """
    Compute beta_1 and lift the harmonic basis into a FIXED ambient edge space
    containing all N choose 2 possible edges.

    This is what makes projector comparison across changing complexes meaningful.
    """
    x = np.asarray(points, dtype=float)
    n, d = x.shape

    edges, triangles = rips_complex(x, epsilon)
    Delta1 = hodge_laplacian_1(n, edges, triangles)
    Q_local, evals = _kernel_basis_symmetric(Delta1, atol=atol, rtol=rtol)

    amb = ambient_edges(n)
    amb_idx = {e: k for k, e in enumerate(amb)}
    Q_amb = np.zeros((len(amb), Q_local.shape[1]), dtype=float)

    for local_row, e in enumerate(edges):
        Q_amb[amb_idx[e], :] = Q_local[local_row, :]

    # Numerical eigensolvers already give orthonormal columns locally;
    # lifting with zero padding preserves orthonormality.
    P = Q_amb @ Q_amb.T
    beta1 = Q_amb.shape[1]

    payload = {
        "n_agents": n,
        "dimension": d,
        "epsilon": float(epsilon),
        "edges": edges,
        "triangles": triangles,
        "beta1": beta1,
        "projector": np.round(P, 15),
    }

    return HodgeSnapshot(
        n_agents=n,
        dimension=d,
        epsilon=float(epsilon),
        edges=list(edges),
        triangles=list(triangles),
        beta1=beta1,
        local_eigenvalues=evals,
        harmonic_basis_ambient=Q_amb,
        projector_ambient=P,
        snapshot_hash=sha256_commit(payload),
    )


# ---------------------------------------------------------------------------
# Admissible transport and invariant metrics
# ---------------------------------------------------------------------------

def edge_transport_from_relabeling(
    n: int,
    new_to_old: Sequence[int],
) -> Array:
    """
    Build the orthogonal transport matrix T on ambient edge coordinates.

    Convention:
        new_points[a] = old_points[new_to_old[a]]

    Then the expected new-coordinate projector is
        P_new_expected = T P_old T^T.
    """
    perm = np.asarray(new_to_old, dtype=int)
    if sorted(perm.tolist()) != list(range(n)):
        raise ValueError("new_to_old must be a permutation of 0..n-1")

    edges = ambient_edges(n)
    idx = {e: k for k, e in enumerate(edges)}
    m = len(edges)
    T = np.zeros((m, m), dtype=float)

    for new_k, (a, b) in enumerate(edges):
        old_edge = tuple(sorted((int(perm[a]), int(perm[b]))))
        old_k = idx[old_edge]
        T[new_k, old_k] = 1.0

    return T


def transport_projector(P: Array, T: Optional[Array] = None) -> Array:
    if T is None:
        return np.asarray(P, dtype=float)
    return T @ P @ T.T


def projector_rank(P: Array, tol: float = 1e-8) -> int:
    return int(np.sum(np.linalg.eigvalsh((P + P.T) * 0.5) > 0.5 - tol))


def projector_metrics(P_expected: Array, P_observed: Array) -> Dict[str, float]:
    """
    Metrics between two orthogonal projectors in the same ambient coordinates.

    overlap = Tr(PQ) / sqrt(rank(P) rank(Q))
    equals 1 iff equal-rank subspaces coincide.
    """
    P = np.asarray(P_expected, dtype=float)
    Q = np.asarray(P_observed, dtype=float)
    rP = int(round(float(np.trace(P))))
    rQ = int(round(float(np.trace(Q))))
    frob = float(np.linalg.norm(P - Q, ord="fro"))

    if rP == 0 and rQ == 0:
        overlap = 1.0
    elif rP == 0 or rQ == 0:
        overlap = 0.0
    else:
        overlap = float(np.trace(P @ Q) / math.sqrt(rP * rQ))
        overlap = max(0.0, min(1.0, overlap))

    return {
        "rank_expected": rP,
        "rank_observed": rQ,
        "projector_frobenius_distance": frob,
        "normalized_subspace_overlap": overlap,
    }


# ---------------------------------------------------------------------------
# Information state and fidelity
# ---------------------------------------------------------------------------

def identity_density_from_projector(P: Array) -> Array:
    """
    Maximum-entropy state supported on the selected sector:
        rho_I = P / rank(P)
    """
    r = int(round(float(np.trace(P))))
    if r == 0:
        return np.zeros_like(P, dtype=float)
    return np.asarray(P, dtype=float) / r


def _psd_sqrt(A: Array, tol: float = 1e-12) -> Array:
    A = (np.asarray(A, dtype=float) + np.asarray(A, dtype=float).T) * 0.5
    vals, vecs = np.linalg.eigh(A)
    vals = np.clip(vals, 0.0, None)
    vals[vals < tol] = 0.0
    return (vecs * np.sqrt(vals)) @ vecs.T


def uhlmann_fidelity(rho: Array, sigma: Array) -> float:
    """
    Uhlmann fidelity:
        F(rho,sigma) = [Tr sqrt(sqrt(rho) sigma sqrt(rho))]^2
    """
    rho = np.asarray(rho, dtype=float)
    sigma = np.asarray(sigma, dtype=float)

    tr_r = float(np.trace(rho))
    tr_s = float(np.trace(sigma))
    if tr_r == 0.0 and tr_s == 0.0:
        return 1.0
    if tr_r == 0.0 or tr_s == 0.0:
        return 0.0

    rho = rho / tr_r
    sigma = sigma / tr_s
    sr = _psd_sqrt(rho)
    mid = sr @ sigma @ sr
    smid = _psd_sqrt(mid)
    F = float(np.trace(smid) ** 2)
    return max(0.0, min(1.0, F))


# ---------------------------------------------------------------------------
# Horizon-style prospective event forecast
# ---------------------------------------------------------------------------

def _positive_edge_crossing_roots(
    X: Array,
    V: Array,
    epsilon: float,
    min_tau: float = 1e-12,
) -> List[float]:
    """
    Candidate times tau>0 satisfying
        ||(x_i-x_j) + tau(v_i-v_j)|| = epsilon
    """
    X = np.asarray(X, dtype=float)
    V = np.asarray(V, dtype=float)
    n = X.shape[0]
    eps2 = float(epsilon) ** 2
    roots: List[float] = []

    for i in range(n):
        for j in range(i + 1, n):
            r = X[i] - X[j]
            u = V[i] - V[j]

            a = float(u @ u)
            b = float(2.0 * (r @ u))
            c = float(r @ r - eps2)

            if a < 1e-15:
                if abs(b) > 1e-15:
                    tau = -c / b
                    if tau > min_tau:
                        roots.append(float(tau))
                continue

            disc = b * b - 4.0 * a * c
            if disc < -1e-12:
                continue
            disc = max(0.0, disc)
            s = math.sqrt(disc)

            for tau in ((-b - s) / (2.0 * a), (-b + s) / (2.0 * a)):
                if tau > min_tau:
                    roots.append(float(tau))

    roots.sort()
    return roots


def _group_roots(roots: Sequence[float], rel_tol: float = 1e-8) -> List[List[float]]:
    groups: List[List[float]] = []
    for r in roots:
        if not groups:
            groups.append([r])
            continue
        ref = groups[-1][-1]
        tol = rel_tol * max(1.0, abs(ref), abs(r))
        if abs(r - ref) <= tol:
            groups[-1].append(r)
        else:
            groups.append([r])
    return groups


@dataclass
class ForecastPacket:
    t0: int
    epsilon: float
    tau_hat_top: Optional[float]
    beta1_before: int
    beta1_after: Optional[int]
    delta_beta1: Optional[int]
    event_sign: str
    projector_after: Optional[Array]
    predictor: str
    input_hash: str
    packet_hash: str


def forecast_next_topological_event(
    X_prev: Array,
    X_curr: Array,
    epsilon: float,
    *,
    t0: int = 0,
    root_group_rel_tol: float = 1e-8,
    post_crossing_delta: float = 1e-6,
    max_tau: Optional[float] = None,
) -> ForecastPacket:
    """
    Two-frame constant-velocity prospective forecast.

    Finds the first positive Vietoris-Rips edge-crossing group after which
    beta_1 changes. The future is NOT required for this computation.
    """
    X_prev = np.asarray(X_prev, dtype=float)
    X_curr = np.asarray(X_curr, dtype=float)
    if X_prev.shape != X_curr.shape:
        raise ValueError("X_prev and X_curr must have the same shape")

    V = X_curr - X_prev
    before = hodge_snapshot(X_curr, epsilon)
    roots = _positive_edge_crossing_roots(X_curr, V, epsilon)
    groups = _group_roots(roots, root_group_rel_tol)

    tau_hat = None
    after_snap = None

    for g in groups:
        tau = max(g)
        if max_tau is not None and tau > max_tau:
            break

        delta = post_crossing_delta * max(1.0, abs(tau))
        X_after = X_curr + (tau + delta) * V
        snap = hodge_snapshot(X_after, epsilon)

        if snap.beta1 != before.beta1:
            tau_hat = float(tau)
            after_snap = snap
            break

    if after_snap is None:
        beta_after = None
        delta_beta = None
        sign = "none"
        P_after = None
    else:
        beta_after = after_snap.beta1
        delta_beta = beta_after - before.beta1
        sign = "birth" if delta_beta > 0 else "death"
        P_after = after_snap.projector_ambient

    input_payload = {
        "X_prev": np.round(X_prev, 15),
        "X_curr": np.round(X_curr, 15),
        "epsilon": float(epsilon),
        "t0": int(t0),
    }
    input_hash = sha256_commit(input_payload)

    packet_body = {
        "t0": int(t0),
        "epsilon": float(epsilon),
        "tau_hat_top": tau_hat,
        "beta1_before": before.beta1,
        "beta1_after": beta_after,
        "delta_beta1": delta_beta,
        "event_sign": sign,
        "projector_after": None if P_after is None else np.round(P_after, 15),
        "predictor": "two_frame_constant_velocity_vr_hodge_v1",
        "input_hash": input_hash,
    }
    packet_hash = sha256_commit(packet_body)

    return ForecastPacket(
        t0=int(t0),
        epsilon=float(epsilon),
        tau_hat_top=tau_hat,
        beta1_before=before.beta1,
        beta1_after=beta_after,
        delta_beta1=delta_beta,
        event_sign=sign,
        projector_after=P_after,
        predictor="two_frame_constant_velocity_vr_hodge_v1",
        input_hash=input_hash,
        packet_hash=packet_hash,
    )


def seal_forecast(packet: ForecastPacket) -> str:
    """
    Seal the COMPLETE forecast body. The hash itself is the commitment.
    """
    body = asdict(packet)
    body.pop("packet_hash", None)
    return sha256_commit(body)


# ---------------------------------------------------------------------------
# Reveal / scoring
# ---------------------------------------------------------------------------

def score_forecast(
    packet: ForecastPacket,
    tau_observed: float,
    observed_snapshot_after: HodgeSnapshot,
) -> Dict[str, Any]:
    """
    Deterministic score against a revealed post-event Hodge snapshot.
    """
    if packet.tau_hat_top is None or packet.projector_after is None:
        return {
            "forecasted_event": False,
            "observed_beta1_after": observed_snapshot_after.beta1,
        }

    delta_obs = observed_snapshot_after.beta1 - packet.beta1_before
    sign_obs = "birth" if delta_obs > 0 else ("death" if delta_obs < 0 else "none")

    metrics = projector_metrics(
        packet.projector_after,
        observed_snapshot_after.projector_ambient,
    )

    rho_hat = identity_density_from_projector(packet.projector_after)
    rho_obs = identity_density_from_projector(observed_snapshot_after.projector_ambient)

    return {
        "forecasted_event": True,
        "event_sign_correct": packet.event_sign == sign_obs,
        "beta1_after_correct": packet.beta1_after == observed_snapshot_after.beta1,
        "timing_absolute_error": abs(float(packet.tau_hat_top) - float(tau_observed)),
        "timing_signed_error": float(packet.tau_hat_top) - float(tau_observed),
        "identity_state_fidelity": uhlmann_fidelity(rho_hat, rho_obs),
        **metrics,
    }


# ---------------------------------------------------------------------------
# Dynamic Invariant Carrier / TIP state
# ---------------------------------------------------------------------------

@dataclass
class TIPState:
    t: float
    X: Array
    hodge: HodgeSnapshot
    rho_identity: Array
    memory_head: str


class TransportedIdentityProjector:
    """
    Minimal stateful wrapper.

    Memory is a hash chain:
        M_t = SHA256(M_{t-1} || state_payload_t)
    """

    def __init__(self, epsilon: float):
        self.epsilon = float(epsilon)
        self.memory_head = "GENESIS"
        self.history: List[TIPState] = []

    def observe(self, t: float, X: Array) -> TIPState:
        snap = hodge_snapshot(X, self.epsilon)
        rho = identity_density_from_projector(snap.projector_ambient)

        payload = {
            "previous_memory_head": self.memory_head,
            "t": float(t),
            "snapshot_hash": snap.snapshot_hash,
            "beta1": snap.beta1,
            "projector": np.round(snap.projector_ambient, 15),
        }
        self.memory_head = sha256_commit(payload)

        state = TIPState(
            t=float(t),
            X=np.asarray(X, dtype=float).copy(),
            hodge=snap,
            rho_identity=rho,
            memory_head=self.memory_head,
        )
        self.history.append(state)
        return state

    def compare_last_two(
        self,
        transport: Optional[Array] = None,
    ) -> Dict[str, Any]:
        if len(self.history) < 2:
            raise RuntimeError("Need at least two observations")

        a = self.history[-2]
        b = self.history[-1]

        P_expected = transport_projector(a.hodge.projector_ambient, transport)
        metrics = projector_metrics(P_expected, b.hodge.projector_ambient)

        rho_expected = identity_density_from_projector(P_expected)
        fidelity = uhlmann_fidelity(rho_expected, b.rho_identity)

        return {
            "t_prev": a.t,
            "t_curr": b.t,
            "beta1_prev": a.hodge.beta1,
            "beta1_curr": b.hodge.beta1,
            "delta_beta1": b.hodge.beta1 - a.hodge.beta1,
            "identity_fidelity": fidelity,
            "memory_head": b.memory_head,
            **metrics,
        }


# ---------------------------------------------------------------------------
# Tiny demo
# ---------------------------------------------------------------------------

def annulus_points(n: int = 24, radius: float = 1.0) -> Array:
    theta = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return np.column_stack([radius * np.cos(theta), radius * np.sin(theta)])


def demo() -> None:
    # A ring that contracts slightly. Tune epsilon so H1 is present.
    X0 = annulus_points(24, 1.00)
    X1 = annulus_points(24, 0.97)

    eps = 0.42
    tip = TransportedIdentityProjector(eps)

    s0 = tip.observe(0, X0)
    s1 = tip.observe(1, X1)

    print("TIP snapshot")
    print("  beta1(t=0):", s0.hodge.beta1)
    print("  beta1(t=1):", s1.hodge.beta1)
    print("  continuity :", tip.compare_last_two())

    forecast = forecast_next_topological_event(
        X0, X1, eps, t0=1, max_tau=50.0
    )
    seal = seal_forecast(forecast)

    print("\nProspective packet")
    print("  tau_hat_top :", forecast.tau_hat_top)
    print("  beta1       :", forecast.beta1_before, "->", forecast.beta1_after)
    print("  event_sign  :", forecast.event_sign)
    print("  input_hash  :", forecast.input_hash)
    print("  seal        :", seal)


if __name__ == "__main__":
    demo()
