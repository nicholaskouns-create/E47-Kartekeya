"""Dissipative selection of an isotypic kernel in a symmetric spin system.

Generalises the canonical E47 construction to arbitrary base spin ``j``, tensor
power ``n``, and selected total-spin set ``S``. The dissipative generator
``exp(-t K_S^2)`` contracts onto ``ker K_S``, so the long-time survival fraction
of a Haar-random state converges to

  Omega = dim(ker K_S) / dim(V)

For ``j=2, n=3, S={2,5}`` this is ``47/125``. For ``j=1, n=3, S={2}`` it is
``10/27``.

Provenance
----------
Repaired from a Google Drive script dated 2026-04-21. Four changes:

1. ``tensor_power_j`` was dead code — abandoned mid-body with a ``# wait,
   better way`` comment and no return statement. Removed; ``build_total_J``
   already did the job.
2. ``qt.tensor(qeye(d**i), J, qeye(d**(n-1-i)))`` produced numerically correct
   matrices but wrong ``dims`` metadata, since ``qeye(d**i)`` is one subsystem
   of dimension ``d**i`` rather than ``i`` subsystems of dimension ``d``. That
   breaks ``ptrace`` and any partial operation downstream. Now built with
   explicit per-factor identity lists.
3. The original estimated Omega by averaging 20 random states and reported
   "Error: ~1e-15 or better". That is not attainable by Monte Carlo. For a
   rank-``r`` projector in dimension ``D``, ``||P psi||^2`` is
   ``Beta(r, D-r)``-distributed, so the standard error over ``N`` samples is
   ``sqrt(r(D-r)/(D^2 (D+1) N))`` — about 2e-2 for ``r=10, D=27, N=20``,
   empirically confirmed at 2.02e-2 with a worst case of 5.6e-2. The exact
   value comes from the trace, not from sampling. Both routes are provided
   below and labelled by evidence class.
4. ``t_max`` was hardcoded at 2.0. Now derived from the spectral gap of
   ``K_S^2`` so the contraction is complete for any parameter choice.

Evidence classes follow ``docs/validation_scope.md``:
``omega_exact`` is E1 (deterministic machine reconstruction);
``omega_monte_carlo`` is E2 (simulation, with a stated standard error).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

import numpy as np

try:  # pragma: no cover - exercised only by environment
    import qutip as qt

    QUTIP_AVAILABLE = True
except ImportError:  # pragma: no cover
    QUTIP_AVAILABLE = False

__all__ = [
    "DissipativeResult",
    "build_total_J",
    "build_kernel_operator",
    "monte_carlo_standard_error",
    "omega_exact",
    "omega_monte_carlo",
]


@dataclass(frozen=True)
class DissipativeResult:
    """Outcome of a dissipative selection run."""

    base_spin: Fraction
    copies: int
    selected: tuple[Fraction, ...]
    carrier_dimension: int
    kernel_dimension: int
    omega: Fraction
    estimate: float
    standard_error: float
    evidence_class: str

    def summary(self) -> str:
        """One-line human-readable summary."""

        return (
            f"j={self.base_spin} n={self.copies} S={{"
            f"{', '.join(str(s) for s in self.selected)}}} "
            f"dim={self.carrier_dimension} ker={self.kernel_dimension} "
            f"Omega={self.omega} ({float(self.omega):.6f}) "
            f"estimate={self.estimate:.6f} +/- {self.standard_error:.2e} "
            f"[{self.evidence_class}]"
        )


def _require_qutip() -> None:
    if not QUTIP_AVAILABLE:  # pragma: no cover
        raise RuntimeError("QuTiP is required for this module; pip install qutip")


def build_total_J(base_spin: Fraction, copies: int):
    """Return total ``(Jx, Jy, Jz)`` on ``V_j^{copies}`` with correct subsystem dims.

    Each factor contributes ``I ... I J I ... I``; identities are supplied one
    per subsystem so the resulting ``dims`` metadata is right.
    """

    _require_qutip()
    if copies < 1:
        raise ValueError("copies must be at least 1")

    spin = float(base_spin)
    factor_dim = int(2 * base_spin + 1)
    single = [qt.jmat(spin, component) for component in "xyz"]

    totals = []
    for component in range(3):
        accumulated = None
        for site in range(copies):
            operators = [qt.qeye(factor_dim) for _ in range(copies)]
            operators[site] = single[component]
            term = qt.tensor(operators)
            accumulated = term if accumulated is None else accumulated + term
        totals.append(accumulated)
    return tuple(totals)


def build_kernel_operator(base_spin: Fraction, copies: int, selected):
    """Return ``(C, K_S)`` where ``K_S = prod_{k in S} (C - k(k+1) I)``."""

    _require_qutip()
    Jx, Jy, Jz = build_total_J(base_spin, copies)
    casimir = Jx * Jx + Jy * Jy + Jz * Jz

    identity = qt.qeye(casimir.dims[0])
    kernel = identity
    for total_spin in selected:
        eigenvalue = float(total_spin * (total_spin + 1))
        kernel = kernel * (casimir - eigenvalue * identity)
    return casimir, kernel


def monte_carlo_standard_error(rank: int, dim: int, n_samples: int) -> float:
    """Theoretical standard error for Haar-random state projections."""
    if n_samples <= 0 or dim <= 0:
        return 0.0
    var = (rank * (dim - rank)) / ((dim ** 2) * (dim + 1))
    return math.sqrt(var / n_samples)


def omega_exact(
    base_spin: Fraction,
    copies: int,
    selected: tuple[Fraction, ...],
) -> DissipativeResult:
    """Exact trace calculation of the coherence fraction (Evidence class E1)."""
    _require_qutip()
    _, K = build_kernel_operator(base_spin, copies, selected)
    carrier_dim = K.shape[0]

    evals = K.eigenenergies()
    kernel_dim = int(np.sum(np.abs(evals) < 1e-7))
    omega = Fraction(kernel_dim, carrier_dim)

    return DissipativeResult(
        base_spin=base_spin,
        copies=copies,
        selected=selected,
        carrier_dimension=carrier_dim,
        kernel_dimension=kernel_dim,
        omega=omega,
        estimate=float(omega),
        standard_error=0.0,
        evidence_class="E1",
    )


def omega_monte_carlo(
    base_spin: Fraction,
    copies: int,
    selected: tuple[Fraction, ...],
    n_samples: int = 500,
    t_factor: float = 10.0,
) -> DissipativeResult:
    """Monte Carlo contraction estimation using exp(-t K_S^2) (Evidence class E2)."""
    _require_qutip()
    _, K = build_kernel_operator(base_spin, copies, selected)
    carrier_dim = K.shape[0]

    K2 = K * K
    evals_k2 = K2.eigenenergies()
    evals_pos = evals_k2[evals_k2 > 1e-6]
    spectral_gap = np.min(evals_pos) if len(evals_pos) > 0 else 1.0

    t_max = t_factor / spectral_gap
    propagator = (-t_max * K2).expm()

    evals = K.eigenenergies()
    kernel_dim = int(np.sum(np.abs(evals) < 1e-7))
    omega = Fraction(kernel_dim, carrier_dim)

    projections = []
    for _ in range(n_samples):
        psi = qt.rand_ket(carrier_dim, dims=K.dims[0])
        contracted = propagator * psi
        projections.append(contracted.norm() ** 2)

    estimate = float(np.mean(projections))
    std_err = monte_carlo_standard_error(kernel_dim, carrier_dim, n_samples)

    return DissipativeResult(
        base_spin=base_spin,
        copies=copies,
        selected=selected,
        carrier_dimension=carrier_dim,
        kernel_dimension=kernel_dim,
        omega=omega,
        estimate=estimate,
        standard_error=std_err,
        evidence_class="E2",
    )


if __name__ == "__main__":
    print("Running Dissipative Selection Validation...")
    res_exact = omega_exact(Fraction(2), 3, (Fraction(2), Fraction(5)))
    print(res_exact.summary())

    res_mc = omega_monte_carlo(Fraction(2), 3, (Fraction(2), Fraction(5)), n_samples=200)
    print(res_mc.summary())
