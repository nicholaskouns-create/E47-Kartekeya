"""Fixed occupancy-matched orthogonal projection. Not the exact E47 Casimir projector."""
import numpy as np

OCCUPANCY = 47 / 125


def make_projector(feature_dim: int, seed: int = 0, occupancy: float = OCCUPANCY):
    """Return a symmetric idempotent d-by-d projector of rank floor(d*occupancy)."""
    if feature_dim < 1 or not (0 < occupancy <= 1):
        raise ValueError("feature_dim must be positive and occupancy in (0, 1]")
    rank = int(np.floor(feature_dim * occupancy))
    if rank == 0:
        raise ValueError("occupancy yields zero-dimensional subspace")
    rng = np.random.default_rng(seed)
    matrix = rng.standard_normal((feature_dim, rank))
    q, _ = np.linalg.qr(matrix, mode="reduced")
    return q @ q.T


def project_embeddings(embeddings, projector):
    """Project the final feature axis of a node-embedding matrix."""
    h = np.asarray(embeddings)
    p = np.asarray(projector)
    if h.ndim != 2 or p.shape != (h.shape[1], h.shape[1]):
        raise ValueError("expected embeddings [nodes, features] and matching projector")
    return h @ p
