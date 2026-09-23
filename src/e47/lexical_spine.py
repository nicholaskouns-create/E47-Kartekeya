"""Canonical runtime bindings for the E47 lexical spine.

Additive only: this module does not redefine K, mutate the lexical term table,
or alter simulator evolution laws.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any
import numpy as np

from e47.projector import construct_e47_projector
from e47.su2_kernel import build_e47_operators


@dataclass(frozen=True)
class Base5Carrier:
    """Typed 5x5x5 register attached to base5.carrier."""

    term_id: str = "base5.carrier"
    register_type: str = "FiniteSet[125]"
    shape: tuple[int, int, int] = (5, 5, 5)
    size: int = 125
    packing: str = "index=25*x+5*y+z"

    def index(self, x: int, y: int, z: int) -> int:
        if not all(isinstance(v, int) and 0 <= v < 5 for v in (x, y, z)):
            raise ValueError("base5 coordinates must be integers in [0,4]")
        return 25 * x + 5 * y + z

    def coordinates(self) -> tuple[tuple[int, int, int], ...]:
        return tuple(
            (x, y, z)
            for x in range(5)
            for y in range(5)
            for z in range(5)
        )


@dataclass(frozen=True)
class QuTiPSpine:
    C: Any
    K: Any
    Lambda: Any


@lru_cache(maxsize=1)
def qutip_spine() -> QuTiPSpine:
    """QuTiP-wrap C, K and Lambda on the same 125-dimensional carrier."""
    operators = build_e47_operators()
    projector = construct_e47_projector(operators).projector
    return QuTiPSpine(
        C=operators.casimir,
        K=operators.kernel,
        Lambda=projector,
    )


@lru_cache(maxsize=1)
def canonical_lambda_matrix() -> np.ndarray:
    """Return the single cached full 125x125 Lambda=P47 ndarray."""
    matrix = np.array(qutip_spine().Lambda.full(), dtype=np.complex128, copy=True)
    matrix.setflags(write=False)
    return matrix


def lambda_bindings() -> dict[str, np.ndarray]:
    """Bind one exact ndarray object to tomography and Eidolon roles."""
    Lambda = canonical_lambda_matrix()
    return {
        "Lambda": Lambda,
        "tomographic_P47_gate": Lambda,
        "eidolon_lock_projector": Lambda,
    }


def project_e47_state(state) -> np.ndarray:
    x = np.asarray(state, dtype=np.complex128)
    if x.shape != (125,):
        raise ValueError("E47 projection requires a 125-amplitude state")
    return canonical_lambda_matrix() @ x


def machine_zero_bound(K: np.ndarray, state: np.ndarray) -> float:
    """Backward-error scale for declaring K@state numerically zero."""
    eps = np.finfo(np.float64).eps
    return float(
        eps
        * K.shape[0]
        * max(1.0, float(np.linalg.norm(K, 2)))
        * max(1.0, float(np.linalg.norm(state)))
    )
