"""QEGT primitives for Coherence, Runtime 1.0."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable, Sequence
import numpy as np

@dataclass(frozen=True)
class QEGTResult:
    probabilities: tuple[float, ...]
    costs: tuple[float, ...]
    beta: float

def gibbs_strategy(curvatures: Iterable[float], beta: float = 1.0) -> QEGTResult:
    """P(omega,k) proportional to exp(-beta * abs(grad_C(rho_I,k)))."""
    costs = np.abs(np.asarray(tuple(curvatures), dtype=float))
    if costs.ndim != 1 or costs.size == 0 or not np.isfinite(costs).all():
        raise ValueError("curvatures must be a non-empty finite vector")
    if not np.isfinite(beta) or beta < 0:
        raise ValueError("beta must be finite and nonnegative")
    logits = -float(beta) * costs
    logits -= np.max(logits)
    w = np.exp(logits)
    p = w / w.sum()
    return QEGTResult(tuple(map(float, p)), tuple(map(float, costs)), float(beta))

def _square(name: str, value: Any) -> np.ndarray:
    a = np.asarray(value, dtype=np.complex128)
    if a.ndim != 2 or a.shape[0] != a.shape[1]:
        raise ValueError(f"{name} must be square")
    return a

def quantum_game_payoffs(
    rho0: Any,
    operations: Sequence[Any],
    payoff_operators: Sequence[Any],
    atol: float = 1e-9,
) -> tuple[np.ndarray, tuple[float, ...]]:
    """rho_f = U rho0 U† with U the tensor product of player operations."""
    rho = _square("rho0", rho0)
    if not np.allclose(rho, rho.conj().T, atol=atol):
        raise ValueError("rho0 must be Hermitian")
    if not np.isclose(np.trace(rho), 1.0, atol=atol):
        raise ValueError("rho0 must have unit trace")
    if np.min(np.linalg.eigvalsh(rho)) < -atol:
        raise ValueError("rho0 must be positive semidefinite")

    joint = None
    for i, raw in enumerate(operations):
        u = _square(f"operations[{i}]", raw)
        if not np.allclose(u.conj().T @ u, np.eye(u.shape[0]), atol=atol):
            raise ValueError(f"operations[{i}] must be unitary")
        joint = u if joint is None else np.kron(joint, u)
    if joint is None or joint.shape != rho.shape:
        raise ValueError("joint operation dimension mismatch")

    rho_f = joint @ rho @ joint.conj().T
    out = []
    for i, raw in enumerate(payoff_operators):
        op = _square(f"payoff_operators[{i}]", raw)
        if op.shape != rho.shape or not np.allclose(op, op.conj().T, atol=atol):
            raise ValueError("payoff operators must be Hermitian and match rho0")
        out.append(float(np.real_if_close(np.trace(op @ rho_f))))
    return rho_f, tuple(out)
