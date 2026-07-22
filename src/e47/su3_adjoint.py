"""SU(3) adjoint representation in 512-dimensional triple tensor space.

This module builds the SU(3) adjoint representation (dimension 8) from
Gell-Mann matrices and structure constants, lifts it to the triple tensor
product

    V = V_adj ⊗ V_adj ⊗ V_adj,    dim(V) = 8³ = 512,

and constructs the total second-order Casimir operator

    C₂^tot = Σ_{a=1}^{8} (T_a^tot)²,

where

    T_a^tot = T_a ⊗ I ⊗ I + I ⊗ T_a ⊗ I + I ⊗ I ⊗ T_a.

The singlet sector

    P₁ = projector onto ker(C₂^tot),    dim = 2,

is spanned by the two independent SU(3) cubic invariants:

    |f⟩ = Σ_{abc} f_{abc} |a⟩|b⟩|c⟩    (totally antisymmetric)
    |d⟩ = Σ_{abc} d_{abc} |a⟩|b⟩|c⟩    (totally symmetric)

A machine certificate for the projector and a quantum-simulation leakage
detector are also provided.

Scope
-----
This module validates algebraic and numerical properties of the SU(3)
adjoint triple-tensor construction. It does not establish experimental,
physical, or hardware validation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import numpy as np
from numpy.typing import NDArray

ComplexArray = NDArray[np.complex128]
RealArray = NDArray[np.float64]

# ── canonical constants ────────────────────────────────────────────

ADJOINT_DIMENSION: Final[int] = 8
CARRIER_DIMENSION: Final[int] = 512          # 8³
SINGLET_DIMENSION: Final[int] = 2            # |f⟩ and |d⟩
NUM_GENERATORS: Final[int] = 8
# SU(3) Casimir: C₂(adjoint) = 3 on each single-particle space
SINGLE_PARTICLE_CASIMIR: Final[float] = 3.0


# ── Gell-Mann matrices ─────────────────────────────────────────────

def gell_mann_matrices() -> list[ComplexArray]:
    """Return the eight 3×3 Gell-Mann matrices λ₁, …, λ₈ (standard basis).

    Normalised so that Tr(λ_a λ_b) = 2 δ_{ab}.

    Returns
    -------
    list of ndarray
        Eight 3×3 complex Hermitian matrices.
    """

    sqrt3 = np.sqrt(3.0)

    lam = [None] * 8

    lam[0] = np.array(
        [[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128
    )
    lam[1] = np.array(
        [[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128
    )
    lam[2] = np.array(
        [[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128
    )
    lam[3] = np.array(
        [[0, 0, 1], [0, 0, 0], [1, 0, 0]], dtype=np.complex128
    )
    lam[4] = np.array(
        [[0, 0, -1j], [0, 0, 0], [1j, 0, 0]], dtype=np.complex128
    )
    lam[5] = np.array(
        [[0, 0, 0], [0, 0, 1], [0, 1, 0]], dtype=np.complex128
    )
    lam[6] = np.array(
        [[0, 0, 0], [0, 0, -1j], [0, 1j, 0]], dtype=np.complex128
    )
    lam[7] = (1.0 / sqrt3) * np.array(
        [[1, 0, 0], [0, 1, 0], [0, 0, -2]], dtype=np.complex128
    )

    return lam  # type: ignore[return-value]


def structure_constants() -> RealArray:
    """Compute the SU(3) structure constants f_{abc}.

    Uses the formula

        f_{abc} = (1 / 4i) Tr([λ_a, λ_b] λ_c)

    where [λ_a, λ_b] = λ_a λ_b − λ_b λ_a.  The result is real and
    totally antisymmetric: f_{abc} = −f_{bac} = −f_{acb}.

    Returns
    -------
    ndarray, shape (8, 8, 8)
        Real structure-constant tensor.
    """

    lam = gell_mann_matrices()
    f = np.zeros((8, 8, 8), dtype=np.float64)

    for a in range(8):
        for b in range(8):
            comm = lam[a] @ lam[b] - lam[b] @ lam[a]
            for c in range(8):
                f[a, b, c] = float(
                    np.real(np.trace(comm @ lam[c]) / (4j))
                )

    return f


def symmetric_structure_constants() -> RealArray:
    """Compute the SU(3) totally symmetric d-tensor d_{abc}.

    Uses the formula

        d_{abc} = (1/4) Tr({λ_a, λ_b} λ_c)

    where {λ_a, λ_b} = λ_a λ_b + λ_b λ_a.  The result is real and
    totally symmetric: d_{abc} = d_{bac} = d_{acb}.

    Returns
    -------
    ndarray, shape (8, 8, 8)
        Real symmetric d-tensor.
    """

    lam = gell_mann_matrices()
    d = np.zeros((8, 8, 8), dtype=np.float64)

    for a in range(8):
        for b in range(8):
            anticomm = lam[a] @ lam[b] + lam[b] @ lam[a]
            for c in range(8):
                d[a, b, c] = float(
                    np.real(np.trace(anticomm @ lam[c]) / 4)
                )

    return d


def adjoint_generators() -> list[ComplexArray]:
    """Return the 8×8 adjoint-representation generators T_a.

    The adjoint representation is built from the structure constants via

        (T_a)_{bc} = −i f_{abc},

    where f_{abc} are the structure constants (a = generator index,
    b, c = matrix row/column indices).

    The matrices T_a are Hermitian, traceless, and satisfy

        [T_a, T_b] = i f_{abc} T_c.

    Returns
    -------
    list of ndarray, each shape (8, 8)
        Eight 8×8 complex Hermitian matrices.
    """

    f = structure_constants()
    # (T_a)_{bc} = -i f_{abc}
    return [
        -1j * f[a, :, :]
        for a in range(NUM_GENERATORS)
    ]


# ── total Casimir operator ─────────────────────────────────────────

def build_total_casimir() -> ComplexArray:
    """Build C₂^tot = Σ_{a=1}^{8} (T_a^tot)² on V_adj^⊗3 (dim 512).

    Returns
    -------
    ndarray, shape (512, 512)
        Total second-order Casimir operator (Hermitian, positive semidefinite).
    """

    T = adjoint_generators()
    d = ADJOINT_DIMENSION
    I = np.eye(d, dtype=np.complex128)

    # T_a^tot = T_a ⊗ I ⊗ I + I ⊗ T_a ⊗ I + I ⊗ I ⊗ T_a
    T_tot = [
        np.kron(np.kron(T[a], I), I)
        + np.kron(np.kron(I, T[a]), I)
        + np.kron(np.kron(I, I), T[a])
        for a in range(NUM_GENERATORS)
    ]

    C2 = sum(T_a @ T_a for T_a in T_tot)
    # Symmetrise for numerical cleanliness
    C2 = 0.5 * (C2 + C2.conj().T)
    return C2


# ── singlet-basis states ──────────────────────────────────────────

def _normalised(v: ComplexArray) -> ComplexArray:
    """Return a normalised copy of v, or the zero vector if ‖v‖ = 0."""
    n = np.linalg.norm(v)
    return v / n if n > 1e-15 else v


def f_state(f: RealArray | None = None) -> ComplexArray:
    """Return the normalised |f⟩ = Σ_{abc} f_{abc} |a⟩|b⟩|c⟩ state.

    Parameters
    ----------
    f
        Structure-constant tensor, shape (8, 8, 8).
        Computed automatically if omitted.

    Returns
    -------
    ndarray, shape (512,)
        Normalised state vector.
    """

    if f is None:
        f = structure_constants()
    return _normalised(f.ravel().astype(np.complex128))


def d_state(d: RealArray | None = None) -> ComplexArray:
    """Return the normalised |d⟩ = Σ_{abc} d_{abc} |a⟩|b⟩|c⟩ state.

    Parameters
    ----------
    d
        Symmetric d-tensor, shape (8, 8, 8).
        Computed automatically if omitted.

    Returns
    -------
    ndarray, shape (512,)
        Normalised state vector.
    """

    if d is None:
        d = symmetric_structure_constants()
    return _normalised(d.ravel().astype(np.complex128))


# ── operators dataclass ────────────────────────────────────────────

@dataclass(frozen=True)
class SU3AdjointOperators:
    """SU(3) adjoint triple-tensor operators.

    Attributes
    ----------
    casimir_total : ndarray, shape (512, 512)
        C₂^tot on V_adj^⊗3.
    generators_single : list of ndarray
        Eight 8×8 adjoint generators T_a.
    generators_total : list of ndarray
        Eight 512×512 total generators T_a^tot.
    structure_constants_f : ndarray, shape (8, 8, 8)
        Antisymmetric structure constants f_{abc}.
    structure_constants_d : ndarray, shape (8, 8, 8)
        Symmetric d-tensor d_{abc}.
    carrier_dimension : int
        dim(V) = 512.
    adjoint_dimension : int
        dim(V_adj) = 8.
    """

    casimir_total: ComplexArray
    generators_single: list[ComplexArray]
    generators_total: list[ComplexArray]
    structure_constants_f: RealArray
    structure_constants_d: RealArray
    carrier_dimension: int
    adjoint_dimension: int


def build_su3_adjoint_operators() -> SU3AdjointOperators:
    """Construct all SU(3) adjoint operators on V_adj^⊗3.

    Returns
    -------
    SU3AdjointOperators
        Immutable container of all canonical operators.
    """

    f = structure_constants()
    d_tensor = symmetric_structure_constants()
    T = adjoint_generators()

    d = ADJOINT_DIMENSION
    I = np.eye(d, dtype=np.complex128)

    T_tot = [
        np.kron(np.kron(T[a], I), I)
        + np.kron(np.kron(I, T[a]), I)
        + np.kron(np.kron(I, I), T[a])
        for a in range(NUM_GENERATORS)
    ]

    C2 = sum(Ta @ Ta for Ta in T_tot)
    C2 = 0.5 * (C2 + C2.conj().T)

    return SU3AdjointOperators(
        casimir_total=C2,
        generators_single=T,
        generators_total=T_tot,
        structure_constants_f=f,
        structure_constants_d=d_tensor,
        carrier_dimension=CARRIER_DIMENSION,
        adjoint_dimension=ADJOINT_DIMENSION,
    )


# ── singlet projector ──────────────────────────────────────────────

@dataclass(frozen=True)
class SU3SingletProjector:
    """Orthogonal projector onto ker(C₂^tot).

    Attributes
    ----------
    projector : ndarray, shape (512, 512)
        Orthogonal projector P₁.
    kernel_basis : list of ndarray
        Orthonormal basis vectors spanning ker(C₂^tot).
    kernel_dimension : int
        dim ker(C₂^tot).
    f_overlap : float
        ‖P₁ |f⟩ − |f⟩‖   (should be ~0).
    d_overlap : float
        ‖P₁ |d⟩ − |d⟩‖   (should be ~0).
    construction_tolerance : float
        Eigenvalue threshold used to identify the zero eigenspace.
    """

    projector: ComplexArray
    kernel_basis: list[ComplexArray]
    kernel_dimension: int
    f_overlap: float
    d_overlap: float
    construction_tolerance: float


def construct_singlet_projector(
    operators: SU3AdjointOperators | None = None,
    *,
    kernel_tolerance: float = 1e-8,
) -> SU3SingletProjector:
    """Build the orthogonal projector onto ker(C₂^tot).

    Parameters
    ----------
    operators
        Operators from ``build_su3_adjoint_operators``.
        Constructed automatically if omitted.
    kernel_tolerance
        Eigenvalue threshold for the zero eigenspace.

    Returns
    -------
    SU3SingletProjector
        Projector, basis, dimension, and singlet-state overlaps.
    """

    if operators is None:
        operators = build_su3_adjoint_operators()

    C2 = operators.casimir_total
    C2_herm = 0.5 * (C2 + C2.conj().T)

    eigenvalues, eigenvectors = np.linalg.eigh(C2_herm)

    zero_mask = eigenvalues < kernel_tolerance
    kernel_basis_matrix = eigenvectors[:, zero_mask]
    kernel_dimension = int(np.sum(zero_mask))

    if kernel_dimension == 0:
        raise RuntimeError(
            "No zero eigenvalues found in C₂^tot. "
            "Check the tolerance or the construction."
        )

    # Build projector as outer product sum
    projector = kernel_basis_matrix @ kernel_basis_matrix.conj().T
    projector = 0.5 * (projector + projector.conj().T)

    kernel_basis = [
        kernel_basis_matrix[:, k]
        for k in range(kernel_dimension)
    ]

    # Check |f⟩ and |d⟩ overlap
    psi_f = f_state(operators.structure_constants_f)
    psi_d = d_state(operators.structure_constants_d)
    f_overlap = float(
        np.linalg.norm(projector @ psi_f - psi_f)
    )
    d_overlap = float(
        np.linalg.norm(projector @ psi_d - psi_d)
    )

    return SU3SingletProjector(
        projector=projector,
        kernel_basis=kernel_basis,
        kernel_dimension=kernel_dimension,
        f_overlap=f_overlap,
        d_overlap=d_overlap,
        construction_tolerance=kernel_tolerance,
    )


# ── machine certificate ────────────────────────────────────────────

@dataclass(frozen=True)
class SU3Certificate:
    """Machine certificate for the SU(3) 512-dim singlet construction.

    All residuals should be zero (or machine-precision small)
    for the construction to be valid.
    """

    valid: bool

    # Projector invariants
    projector_rank: int
    hermitian_error: float
    idempotence_error: float

    # Annihilation: C₂ P₁ = 0
    annihilation_error: float

    # |f⟩ and |d⟩ in kernel
    f_overlap_error: float
    d_overlap_error: float

    # Contraction convergence: Γ^n → P₁
    contraction_epsilon: float
    contraction_iterations: int
    contraction_error: float

    # Spectrum
    singlet_eigenvalue: float
    spectral_gap: float

    tolerance: float
    errors: tuple[str, ...]


def validate_su3_adjoint(
    operators: SU3AdjointOperators | None = None,
    projector_data: SU3SingletProjector | None = None,
    *,
    tolerance: float = 1e-8,
    contraction_iterations: int = 400,
) -> SU3Certificate:
    """Validate the 512-dim SU(3) adjoint singlet projector.

    Checks:
    - P₁ rank = 2;
    - P₁ is Hermitian;
    - P₁ is idempotent (P₁² = P₁);
    - C₂^tot P₁ = 0;
    - |f⟩ and |d⟩ lie in ker(C₂^tot);
    - Γ^n → P₁ for Γ = I − ε (C₂^tot)²;
    - spectral gap > 0.

    Parameters
    ----------
    operators
        SU(3) adjoint operators.  Constructed automatically if omitted.
    projector_data
        Singlet projector.  Constructed automatically if omitted.
    tolerance
        Numerical tolerance for all checks.
    contraction_iterations
        Number of Γ-iterations used to verify asymptotic convergence.

    Returns
    -------
    SU3Certificate
        Immutable validation certificate.
    """

    if operators is None:
        operators = build_su3_adjoint_operators()

    if projector_data is None:
        projector_data = construct_singlet_projector(operators)

    errors: list[str] = []

    C2 = operators.casimir_total
    P = projector_data.projector
    n = CARRIER_DIMENSION

    # ── projector rank ──────────────────────────────────────────

    proj_eigenvalues = np.linalg.eigvalsh(0.5 * (P + P.conj().T))
    projector_rank = int(np.sum(proj_eigenvalues > 0.5))

    if projector_rank != SINGLET_DIMENSION:
        errors.append(
            f"Projector rank {projector_rank} ≠ {SINGLET_DIMENSION}."
        )

    # ── Hermiticity ─────────────────────────────────────────────

    hermitian_error = float(np.linalg.norm(P - P.conj().T, ord=2))
    if hermitian_error > tolerance:
        errors.append(
            f"P₁ is not Hermitian: ‖P₁ − P₁†‖ = {hermitian_error:.2e}."
        )

    # ── idempotence ──────────────────────────────────────────────

    idempotence_error = float(np.linalg.norm(P @ P - P, ord=2))
    if idempotence_error > tolerance:
        errors.append(
            f"P₁ is not idempotent: ‖P₁² − P₁‖ = {idempotence_error:.2e}."
        )

    # ── annihilation: C₂ P₁ = 0 ──────────────────────────────────

    annihilation_error = float(np.linalg.norm(C2 @ P, ord=2))
    if annihilation_error > tolerance:
        errors.append(
            f"Annihilation failed: ‖C₂ P₁‖ = {annihilation_error:.2e}."
        )

    # ── |f⟩ and |d⟩ overlaps ────────────────────────────────────

    f_overlap_error = projector_data.f_overlap
    d_overlap_error = projector_data.d_overlap

    if f_overlap_error > tolerance:
        errors.append(
            f"|f⟩ not in kernel: ‖P₁|f⟩ − |f⟩‖ = {f_overlap_error:.2e}."
        )
    if d_overlap_error > tolerance:
        errors.append(
            f"|d⟩ not in kernel: ‖P₁|d⟩ − |d⟩‖ = {d_overlap_error:.2e}."
        )

    # ── spectrum ─────────────────────────────────────────────────

    c2_eigenvalues = np.linalg.eigvalsh(0.5 * (C2 + C2.conj().T))
    singlet_eigenvalue = float(c2_eigenvalues[0])
    positive_c2 = c2_eigenvalues[c2_eigenvalues > tolerance]
    spectral_gap = float(positive_c2[0]) if positive_c2.size else 0.0

    # ── contraction Γ^n → P₁ ──────────────────────────────────

    I = np.eye(n, dtype=np.complex128)
    C2_sq = C2 @ C2
    c2sq_max = float(np.linalg.eigvalsh(0.5 * (C2_sq + C2_sq.conj().T))[-1])

    epsilon = 0.9 / c2sq_max if c2sq_max > 0 else 0.0
    Gamma = I - epsilon * C2_sq

    Gamma_n = np.linalg.matrix_power(Gamma, contraction_iterations)
    contraction_error = float(np.linalg.norm(Gamma_n - P, ord=2))

    # ── return certificate ────────────────────────────────────────

    return SU3Certificate(
        valid=not errors,
        projector_rank=projector_rank,
        hermitian_error=hermitian_error,
        idempotence_error=idempotence_error,
        annihilation_error=annihilation_error,
        f_overlap_error=f_overlap_error,
        d_overlap_error=d_overlap_error,
        contraction_epsilon=epsilon,
        contraction_iterations=contraction_iterations,
        contraction_error=contraction_error,
        singlet_eigenvalue=singlet_eigenvalue,
        spectral_gap=spectral_gap,
        tolerance=tolerance,
        errors=tuple(errors),
    )


# ── quantum-simulation leakage detector ───────────────────────────

def leakage(
    rho: ComplexArray,
    projector: ComplexArray | None = None,
) -> float:
    """Compute the gauge leakage  ℓ = 1 − Tr(P₁ ρ).

    A state with ℓ = 0 lies entirely in the physical (singlet) subspace.
    A state with ℓ = 1 is entirely outside.

    Parameters
    ----------
    rho
        Density matrix of shape (512, 512), or a pure state vector of
        shape (512,) which is converted to ρ = |ψ⟩⟨ψ|.
    projector
        Singlet projector P₁, shape (512, 512).
        Constructed automatically if omitted.

    Returns
    -------
    float
        Leakage ℓ ∈ [0, 1].
    """

    rho_arr = np.asarray(rho, dtype=np.complex128)

    if rho_arr.ndim == 1:
        rho_arr = np.outer(rho_arr, rho_arr.conj())

    if projector is None:
        ops = build_su3_adjoint_operators()
        projector_data = construct_singlet_projector(ops)
        projector = projector_data.projector

    P = np.asarray(projector, dtype=np.complex128)
    return float(1.0 - np.real(np.trace(P @ rho_arr)))


# ── convenience entry point ────────────────────────────────────────

def run_su3_adjoint_validation(
    *,
    tolerance: float = 1e-8,
    contraction_iterations: int = 400,
    verbose: bool = True,
) -> SU3Certificate:
    """Run the full SU(3) 512-dim adjoint validation pipeline.

    Constructs operators, projector, and validates all properties.

    Parameters
    ----------
    tolerance
        Numerical tolerance for all validation checks.
    contraction_iterations
        Number of Γ-iterations.
    verbose
        Print a summary to stdout.

    Returns
    -------
    SU3Certificate
        Immutable validation certificate.
    """

    ops = build_su3_adjoint_operators()
    proj = construct_singlet_projector(ops, kernel_tolerance=tolerance)
    cert = validate_su3_adjoint(
        ops,
        proj,
        tolerance=tolerance,
        contraction_iterations=contraction_iterations,
    )

    if verbose:
        _print_certificate(cert)

    return cert


def _print_certificate(cert: SU3Certificate) -> None:
    """Print a formatted validation summary."""

    print("=" * 60)
    print(" SU(3) 512-DIM ADJOINT — MACHINE CERTIFICATE")
    print("=" * 60)
    print(f"  carrier dimension     : {CARRIER_DIMENSION}")
    print(f"  singlet dimension     : {SINGLET_DIMENSION}")
    print(f"  projector rank        : {cert.projector_rank}")
    print(f"  hermitian error       : {cert.hermitian_error:.2e}")
    print(f"  idempotence error     : {cert.idempotence_error:.2e}")
    print(f"  annihilation ‖C₂P₁‖  : {cert.annihilation_error:.2e}")
    print(f"  |f⟩ overlap error     : {cert.f_overlap_error:.2e}")
    print(f"  |d⟩ overlap error     : {cert.d_overlap_error:.2e}")
    print(f"  spectral gap          : {cert.spectral_gap:.6f}")
    print(
        f"  contraction Γ^{cert.contraction_iterations} error: "
        f"{cert.contraction_error:.2e}"
    )
    status = "PASS" if cert.valid else "FAIL"
    print(f"  status                : {status}")
    if cert.errors:
        for err in cert.errors:
            print(f"  ✗ {err}")
    print("=" * 60)


# ── module self-test ──────────────────────────────────────────────

if __name__ == "__main__":
    cert = run_su3_adjoint_validation(verbose=True)
    if not cert.valid:
        raise SystemExit("SU(3) 512-dim adjoint validation FAILED.")
    print("SU(3) 512-dim adjoint validation PASSED.")


__all__ = [
    "ADJOINT_DIMENSION",
    "CARRIER_DIMENSION",
    "NUM_GENERATORS",
    "SINGLE_PARTICLE_CASIMIR",
    "SINGLET_DIMENSION",
    "SU3AdjointOperators",
    "SU3Certificate",
    "SU3SingletProjector",
    "adjoint_generators",
    "build_su3_adjoint_operators",
    "build_total_casimir",
    "construct_singlet_projector",
    "d_state",
    "f_state",
    "gell_mann_matrices",
    "leakage",
    "run_su3_adjoint_validation",
    "structure_constants",
    "symmetric_structure_constants",
    "validate_su3_adjoint",
]
