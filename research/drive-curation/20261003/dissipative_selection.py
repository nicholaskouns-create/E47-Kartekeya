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


def _kernel_rank(kernel, tolerance: float = 1e-9) -> int:
    """Rank of the projector onto ``ker K``, from the eigenvalues of ``K``."""

    eigenvalues = np.real(kernel.eigenenergies())
    return int(np.sum(np.abs(eigenvalues) < tolerance))


def _contraction_time(kernel, safety: float = 40.0) -> float:
    """Time at which ``exp(-t K^2)`` has contracted onto the kernel.

    Chosen so ``exp(-t * gap) <= exp(-safety)``; ``gap`` is the smallest
    non-zero eigenvalue of ``K^2``.
    """

    squared = np.real(kernel.eigenenergies()) ** 2
    nonzero = squared[squared > 1e-12]
    if nonzero.size == 0:
        return 1.0
    return float(safety / nonzero.min())


def monte_carlo_standard_error(kernel_dim: int, carrier_dim: int, samples: int) -> float:
    """Standard error of the sampled survival fraction.

    ``||P psi||^2`` for Haar-random ``psi`` is ``Beta(r, D-r)``-distributed with
    variance ``r(D-r) / (D^2 (D+1))``.
    """

    if samples < 1:
        raise ValueError("samples must be at least 1")
    r, d = kernel_dim, carrier_dim
    variance = r * (d - r) / (d**2 * (d + 1))
    return math.sqrt(variance / samples)


def omega_exact(
    base_spin: Fraction,
    copies: int,
    selected,
) -> DissipativeResult:
    """Compute Omega exactly from the kernel rank. Evidence class E1.

    This is the honest route: the long-time limit of the average survival
    fraction is ``tr(P)/D``, which is a rank computation, not a sample mean.
    """

    _require_qutip()
    selected = tuple(sorted(set(selected)))
    casimir, kernel = build_kernel_operator(base_spin, copies, selected)

    carrier_dim = int(np.prod(casimir.dims[0]))
    kernel_dim = _kernel_rank(kernel)
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
    selected,
    samples: int = 200,
    seed: int = 47125,
) -> DissipativeResult:
    """Estimate Omega by dissipative evolution of random states. Evidence class E2.

    Reports a standard error. Do not expect machine precision from this route —
    the error falls as ``1/sqrt(samples)``.
    """

    _require_qutip()
    selected = tuple(sorted(set(selected)))
    casimir, kernel = build_kernel_operator(base_spin, copies, selected)

    carrier_dim = int(np.prod(casimir.dims[0]))
    kernel_dim = _kernel_rank(kernel)
    propagator = (-_contraction_time(kernel) * kernel * kernel).expm()

    # QuTiP 5's rand_ket does not consult numpy's global seed, so Haar-random
    # states are drawn here directly: a complex Gaussian vector normalised to
    # unit length is Haar-uniform on the sphere. This keeps `seed` meaningful.
    rng = np.random.default_rng(seed)
    survivals = []
    for _ in range(samples):
        vector = rng.normal(size=carrier_dim) + 1j * rng.normal(size=carrier_dim)
        vector /= np.linalg.norm(vector)
        state = qt.Qobj(vector.reshape(-1, 1), dims=[casimir.dims[0], [1] * copies])
        survivals.append(float((propagator * state).norm() ** 2))

    return DissipativeResult(
        base_spin=base_spin,
        copies=copies,
        selected=selected,
        carrier_dimension=carrier_dim,
        kernel_dimension=kernel_dim,
        omega=Fraction(kernel_dim, carrier_dim),
        estimate=float(np.mean(survivals)),
        standard_error=monte_carlo_standard_error(kernel_dim, carrier_dim, samples),
        evidence_class="E2",
    )


def _main() -> int:  # pragma: no cover - manual entry point
    cases = [
        (Fraction(1), 3, [Fraction(2)]),
        (Fraction(2), 3, [Fraction(2), Fraction(5)]),
    ]
    for base_spin, copies, selected in cases:
        print(omega_exact(base_spin, copies, selected).summary())
        print(omega_monte_carlo(base_spin, copies, selected, samples=200).summary())
        print()
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
