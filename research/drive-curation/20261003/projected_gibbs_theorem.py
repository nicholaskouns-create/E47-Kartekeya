#!/usr/bin/env python3
"""
Projected Gibbs Theorem
=======================

Finite-dimensional theorem:

Let H be Hermitian, P an orthogonal projector, beta > 0, and [P,H]=0.
Among all density matrices rho satisfying P rho P = rho, the unique minimizer of

    F_beta(rho) = Tr(rho H) + beta^{-1} Tr(rho log rho)

is

    rho_* = P exp(-beta H) P / Tr(P exp(-beta H)).

Equivalently, if H_P is H restricted to im(P),

    rho_* = exp(-beta H_P) / Tr(exp(-beta H_P))

embedded back into the ambient space.

The proof identity is

    F_beta(rho) - F_beta(rho_*)
      = beta^{-1} D(rho || rho_*) >= 0,

with equality iff rho = rho_*.

This script validates:
1. projector, support, positivity, and trace conditions;
2. the free-energy / relative-entropy identity;
3. numerical minimality over many random feasible density matrices;
4. uniqueness at machine precision;
5. the E47-sized case dim=125, rank(P)=47;
6. a negative control showing the commutator hypothesis matters.
"""

from __future__ import annotations

import json
import math
import platform
import sys
from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import scipy
import scipy.linalg as la


TOL = 1e-10


@dataclass
class ValidationResult:
    theorem_name: str
    ambient_dimension: int
    projector_rank: int
    beta: float
    random_seed: int
    sample_count: int
    projector_idempotence_residual: float
    projector_hermiticity_residual: float
    commutator_residual: float
    state_trace_residual: float
    state_support_residual: float
    state_hermiticity_residual: float
    state_min_eigenvalue: float
    max_free_energy_identity_residual: float
    minimum_sampled_free_energy_gap: float
    uniqueness_residual: float
    negative_control_free_energy_excess: float
    negative_control_state_distance: float
    pass_all: bool


def hermitian_random(rng: np.random.Generator, n: int, scale: float = 1.0) -> np.ndarray:
    a = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    h = (a + a.conj().T) / 2.0
    return scale * h / max(1.0, np.linalg.norm(h, ord=2))


def orthogonal_projector(n: int, rank: int) -> np.ndarray:
    if not (0 < rank <= n):
        raise ValueError("rank must satisfy 0 < rank <= n")
    p = np.zeros((n, n), dtype=np.complex128)
    p[:rank, :rank] = np.eye(rank)
    return p


def commuting_hamiltonian(
    rng: np.random.Generator,
    n: int,
    rank: int,
) -> np.ndarray:
    """
    Build H block-diagonal relative to P, so [P,H]=0 exactly up to floating point.
    """
    h1 = hermitian_random(rng, rank, scale=2.0)
    h2 = hermitian_random(rng, n - rank, scale=3.0) if rank < n else np.zeros((0, 0), complex)
    h = np.zeros((n, n), dtype=np.complex128)
    h[:rank, :rank] = h1
    if rank < n:
        h[rank:, rank:] = h2
    return h


def matrix_log_on_support(rho_sub: np.ndarray) -> np.ndarray:
    """
    Matrix logarithm for a strictly positive density matrix on its support.
    """
    vals, vecs = la.eigh((rho_sub + rho_sub.conj().T) / 2)
    vals = np.clip(vals, 1e-300, None)
    return (vecs * np.log(vals)) @ vecs.conj().T


def von_neumann_entropy_term(rho_sub: np.ndarray) -> float:
    """
    Returns Tr(rho log rho), with 0 log 0 := 0.
    """
    vals = la.eigvalsh((rho_sub + rho_sub.conj().T) / 2)
    vals = np.clip(vals.real, 0.0, None)
    mask = vals > 0
    return float(np.sum(vals[mask] * np.log(vals[mask])))


def free_energy(rho_sub: np.ndarray, h_sub: np.ndarray, beta: float) -> float:
    energy = float(np.trace(rho_sub @ h_sub).real)
    entropy_term = von_neumann_entropy_term(rho_sub)
    return energy + entropy_term / beta


def relative_entropy(rho_sub: np.ndarray, sigma_sub: np.ndarray) -> float:
    """
    D(rho || sigma) for full-rank sigma on the same finite support.
    """
    log_rho = matrix_log_on_support(rho_sub)
    log_sigma = matrix_log_on_support(sigma_sub)
    return float(np.trace(rho_sub @ (log_rho - log_sigma)).real)


def random_density(rng: np.random.Generator, n: int) -> np.ndarray:
    a = rng.normal(size=(n, n)) + 1j * rng.normal(size=(n, n))
    x = a @ a.conj().T
    x += 1e-8 * np.eye(n)  # strict positivity for stable logarithms
    return x / np.trace(x).real


def projected_gibbs_state(h: np.ndarray, p: np.ndarray, beta: float) -> np.ndarray:
    """
    Uses the theorem formula. Requires [P,H]=0 for equality with the constrained Gibbs state.
    """
    x = p @ la.expm(-beta * h) @ p
    z = np.trace(x).real
    if z <= 0:
        raise RuntimeError("Partition function is not positive")
    return x / z


def constrained_gibbs_state(h: np.ndarray, rank: int, beta: float) -> np.ndarray:
    """
    True constrained minimizer on im(P), valid whether or not [P,H]=0:
        exp(-beta * P H P |_{im P}) / Z
    embedded in the ambient space.
    """
    h_sub = h[:rank, :rank]
    sigma_sub = la.expm(-beta * h_sub)
    sigma_sub /= np.trace(sigma_sub).real
    sigma = np.zeros_like(h, dtype=np.complex128)
    sigma[:rank, :rank] = sigma_sub
    return sigma


def validate_projected_gibbs(
    n: int = 125,
    rank: int = 47,
    beta: float = 1.7,
    seed: int = 47,
    sample_count: int = 200,
) -> ValidationResult:
    rng = np.random.default_rng(seed)

    p = orthogonal_projector(n, rank)
    h = commuting_hamiltonian(rng, n, rank)
    rho_star = projected_gibbs_state(h, p, beta)

    p2_res = float(la.norm(p @ p - p, ord="fro"))
    ph_res = float(la.norm(p - p.conj().T, ord="fro"))
    comm_res = float(la.norm(p @ h - h @ p, ord="fro"))

    trace_res = abs(float(np.trace(rho_star).real) - 1.0)
    support_res = float(la.norm(p @ rho_star @ p - rho_star, ord="fro"))
    herm_res = float(la.norm(rho_star - rho_star.conj().T, ord="fro"))
    min_eval = float(np.min(la.eigvalsh((rho_star + rho_star.conj().T) / 2)).real)

    h_sub = h[:rank, :rank]
    rho_star_sub = rho_star[:rank, :rank]
    f_star = free_energy(rho_star_sub, h_sub, beta)

    max_identity_res = 0.0
    min_gap = math.inf

    for _ in range(sample_count):
        rho_sub = random_density(rng, rank)
        f_rho = free_energy(rho_sub, h_sub, beta)
        d = relative_entropy(rho_sub, rho_star_sub)
        gap = f_rho - f_star
        identity_res = abs(gap - d / beta)
        max_identity_res = max(max_identity_res, identity_res)
        min_gap = min(min_gap, gap)

    uniqueness_res = float(la.norm(
        constrained_gibbs_state(h, rank, beta) - rho_star,
        ord="fro",
    ))

    # Negative control: violate [P,H]=0.
    n_nc, rank_nc = 20, 7
    p_nc = orthogonal_projector(n_nc, rank_nc)
    h_nc = hermitian_random(rng, n_nc, scale=4.0)
    # Ensure coupling across P and I-P is present.
    h_nc[:rank_nc, rank_nc:] += 0.25
    h_nc[rank_nc:, :rank_nc] = h_nc[:rank_nc, rank_nc:].conj().T

    sigma_wrong = projected_gibbs_state(h_nc, p_nc, beta)
    sigma_true = constrained_gibbs_state(h_nc, rank_nc, beta)

    h_nc_sub = h_nc[:rank_nc, :rank_nc]
    f_wrong = free_energy(sigma_wrong[:rank_nc, :rank_nc], h_nc_sub, beta)
    f_true = free_energy(sigma_true[:rank_nc, :rank_nc], h_nc_sub, beta)
    negative_excess = float(f_wrong - f_true)
    negative_distance = float(la.norm(sigma_wrong - sigma_true, ord="fro"))

    passed = all([
        p2_res < TOL,
        ph_res < TOL,
        comm_res < TOL,
        trace_res < TOL,
        support_res < TOL,
        herm_res < TOL,
        min_eval > -TOL,
        max_identity_res < 1e-8,
        min_gap > -1e-8,
        uniqueness_res < 1e-10,
        negative_excess > 1e-8,
        negative_distance > 1e-6,
    ])

    return ValidationResult(
        theorem_name="Projected Gibbs Theorem",
        ambient_dimension=n,
        projector_rank=rank,
        beta=beta,
        random_seed=seed,
        sample_count=sample_count,
        projector_idempotence_residual=p2_res,
        projector_hermiticity_residual=ph_res,
        commutator_residual=comm_res,
        state_trace_residual=trace_res,
        state_support_residual=support_res,
        state_hermiticity_residual=herm_res,
        state_min_eigenvalue=min_eval,
        max_free_energy_identity_residual=max_identity_res,
        minimum_sampled_free_energy_gap=min_gap,
        uniqueness_residual=uniqueness_res,
        negative_control_free_energy_excess=negative_excess,
        negative_control_state_distance=negative_distance,
        pass_all=passed,
    )


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> int:
    result = validate_projected_gibbs()
    payload: dict[str, Any] = {
        "certificate": asdict(result),
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }

    print(json.dumps(payload, indent=2))
    return 0 if result.pass_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
