"""Tests for the 512-dim SU(3) adjoint singlet construction.

Validates:
- Gell-Mann matrices and structure constants
- Adjoint generators (Hermiticity, commutation relations, Casimir)
- Total Casimir eigenspectrum
- Singlet projector (rank 2, Hermiticity, idempotence, annihilation)
- |f⟩ and |d⟩ invariant tensors lie in the kernel
- Contraction Γ^n → P₁
- Quantum-simulation leakage detector
"""

from __future__ import annotations

import numpy as np
import pytest

from e47.su3_adjoint import (
    ADJOINT_DIMENSION,
    CARRIER_DIMENSION,
    NUM_GENERATORS,
    SINGLET_DIMENSION,
    adjoint_generators,
    build_su3_adjoint_operators,
    construct_singlet_projector,
    d_state,
    f_state,
    gell_mann_matrices,
    leakage,
    structure_constants,
    symmetric_structure_constants,
    validate_su3_adjoint,
)


# ── fixtures ──────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def operators():
    return build_su3_adjoint_operators()


@pytest.fixture(scope="module")
def projector_data(operators):
    return construct_singlet_projector(operators)


@pytest.fixture(scope="module")
def certificate(operators, projector_data):
    return validate_su3_adjoint(operators, projector_data)


# ── Gell-Mann matrices ────────────────────────────────────────────

def test_gell_mann_count():
    """There are exactly 8 Gell-Mann matrices."""
    lam = gell_mann_matrices()
    assert len(lam) == NUM_GENERATORS


def test_gell_mann_shape():
    """Each Gell-Mann matrix is 3×3."""
    for lam in gell_mann_matrices():
        assert lam.shape == (3, 3)


def test_gell_mann_hermitian():
    """Gell-Mann matrices are Hermitian."""
    for a, lam in enumerate(gell_mann_matrices()):
        err = np.linalg.norm(lam - lam.conj().T)
        assert err < 1e-13, f"λ_{a+1} not Hermitian: {err:.2e}"


def test_gell_mann_traceless():
    """Gell-Mann matrices are traceless."""
    for a, lam in enumerate(gell_mann_matrices()):
        tr = abs(np.trace(lam))
        assert tr < 1e-13, f"Tr(λ_{a+1}) = {tr:.2e}"


def test_gell_mann_orthonormality():
    """Tr(λ_a λ_b) = 2 δ_{ab}."""
    lam = gell_mann_matrices()
    for a in range(8):
        for b in range(8):
            val = float(np.real(np.trace(lam[a] @ lam[b])))
            expected = 2.0 if a == b else 0.0
            assert abs(val - expected) < 1e-13, (
                f"Tr(λ_{a+1} λ_{b+1}) = {val:.4f}, expected {expected}"
            )


# ── structure constants ───────────────────────────────────────────

def test_structure_constants_shape():
    """f has shape (8, 8, 8)."""
    f = structure_constants()
    assert f.shape == (8, 8, 8)


def test_structure_constants_real():
    """f_{abc} is real."""
    f = structure_constants()
    assert np.all(np.isreal(f))


def test_structure_constants_antisymmetry_ab():
    """f_{abc} = −f_{bac}."""
    f = structure_constants()
    assert np.allclose(f, -f.transpose(1, 0, 2), atol=1e-12)


def test_structure_constants_antisymmetry_ac():
    """f_{abc} = −f_{cba}."""
    f = structure_constants()
    assert np.allclose(f, -f.transpose(2, 1, 0), atol=1e-12)


def test_d_tensor_shape():
    """d has shape (8, 8, 8)."""
    d = symmetric_structure_constants()
    assert d.shape == (8, 8, 8)


def test_d_tensor_real():
    """d_{abc} is real."""
    d = symmetric_structure_constants()
    assert np.all(np.isreal(d))


def test_d_tensor_symmetry():
    """d_{abc} = d_{bac} (symmetric in first two indices)."""
    d = symmetric_structure_constants()
    assert np.allclose(d, d.transpose(1, 0, 2), atol=1e-12)


# ── adjoint generators ────────────────────────────────────────────

def test_adjoint_generator_count():
    """There are exactly 8 adjoint generators."""
    T = adjoint_generators()
    assert len(T) == NUM_GENERATORS


def test_adjoint_generator_shape():
    """Each generator is 8×8."""
    for T_a in adjoint_generators():
        assert T_a.shape == (ADJOINT_DIMENSION, ADJOINT_DIMENSION)


def test_adjoint_generators_hermitian():
    """Adjoint generators T_a are Hermitian."""
    for a, T_a in enumerate(adjoint_generators()):
        err = np.linalg.norm(T_a - T_a.conj().T)
        assert err < 1e-12, f"T_{a+1} not Hermitian: {err:.2e}"


def test_adjoint_generators_traceless():
    """Adjoint generators are traceless."""
    for a, T_a in enumerate(adjoint_generators()):
        tr = abs(np.trace(T_a))
        assert tr < 1e-12, f"Tr(T_{a+1}) = {tr:.2e}"


def test_commutation_relations():
    """[T_a, T_b] = i f_{abc} T_c  for all a, b."""
    T = adjoint_generators()
    f = structure_constants()
    for a in range(8):
        for b in range(8):
            comm = T[a] @ T[b] - T[b] @ T[a]
            rhs = sum(1j * f[a, b, c] * T[c] for c in range(8))
            err = np.linalg.norm(comm - rhs)
            assert err < 1e-10, (
                f"[T_{a+1}, T_{b+1}] = i f_{a+1}{b+1}c T_c failed: {err:.2e}"
            )


def test_adjoint_casimir_eigenvalue():
    """Single-particle Casimir Σ T_a² = 3·I on the adjoint representation."""
    T = adjoint_generators()
    C2 = sum(T_a @ T_a for T_a in T)
    expected = 3.0 * np.eye(ADJOINT_DIMENSION, dtype=np.complex128)
    err = np.linalg.norm(C2 - expected)
    assert err < 1e-10, f"C₂(adj) ≠ 3I: {err:.2e}"


def test_jacobi_identity():
    """[T_a, [T_b, T_c]] + [T_b, [T_c, T_a]] + [T_c, [T_a, T_b]] = 0."""
    T = adjoint_generators()
    for a in range(3):
        for b in range(3):
            for c in range(3):
                bc = T[b] @ T[c] - T[c] @ T[b]
                ca = T[c] @ T[a] - T[a] @ T[c]
                ab = T[a] @ T[b] - T[b] @ T[a]
                jacobi = (
                    T[a] @ bc - bc @ T[a]
                    + T[b] @ ca - ca @ T[b]
                    + T[c] @ ab - ab @ T[c]
                )
                err = np.linalg.norm(jacobi)
                assert err < 1e-10, (
                    f"Jacobi identity failed for ({a},{b},{c}): {err:.2e}"
                )


# ── total Casimir operator ─────────────────────────────────────────

def test_total_casimir_shape(operators):
    """C₂^tot has shape (512, 512)."""
    assert operators.casimir_total.shape == (CARRIER_DIMENSION, CARRIER_DIMENSION)


def test_total_casimir_hermitian(operators):
    """C₂^tot is Hermitian."""
    C2 = operators.casimir_total
    err = np.linalg.norm(C2 - C2.conj().T, ord=2)
    assert err < 1e-10, f"C₂^tot not Hermitian: {err:.2e}"


def test_total_casimir_positive_semidefinite(operators):
    """C₂^tot is positive semidefinite."""
    ev = np.linalg.eigvalsh(operators.casimir_total)
    assert ev[0] > -1e-8, f"C₂^tot has negative eigenvalue: {ev[0]:.2e}"


def test_total_casimir_has_zero_eigenvalues(operators):
    """C₂^tot has exactly 2 zero eigenvalues (singlet sector)."""
    ev = np.linalg.eigvalsh(operators.casimir_total)
    n_zero = int(np.sum(np.abs(ev) < 1e-8))
    assert n_zero == SINGLET_DIMENSION, (
        f"Expected {SINGLET_DIMENSION} zero eigenvalues, got {n_zero}"
    )


def test_total_casimir_spectral_gap(operators):
    """C₂^tot spectral gap (smallest nonzero eigenvalue) is positive."""
    ev = np.linalg.eigvalsh(operators.casimir_total)
    positive = ev[ev > 1e-8]
    assert positive.size > 0
    assert positive[0] > 0.0, f"No positive eigenvalue found"


def test_total_casimir_contains_singlet_value(operators):
    """C₂^tot eigenvalue spectrum contains 0 (singlet sector)."""
    ev = np.linalg.eigvalsh(operators.casimir_total)
    assert np.any(np.abs(ev) < 1e-8), "No singlet (zero) eigenvalue found"


# ── singlet projector ──────────────────────────────────────────────

def test_projector_rank(projector_data):
    """P₁ has rank 2."""
    assert projector_data.kernel_dimension == SINGLET_DIMENSION


def test_projector_hermitian(projector_data):
    """P₁ is Hermitian."""
    P = projector_data.projector
    err = np.linalg.norm(P - P.conj().T, ord=2)
    assert err < 1e-12, f"P₁ not Hermitian: {err:.2e}"


def test_projector_idempotent(projector_data):
    """P₁² = P₁."""
    P = projector_data.projector
    err = np.linalg.norm(P @ P - P, ord=2)
    assert err < 1e-12, f"P₁ not idempotent: {err:.2e}"


def test_projector_annihilation(operators, projector_data):
    """C₂^tot P₁ = 0."""
    err = np.linalg.norm(operators.casimir_total @ projector_data.projector, ord=2)
    assert err < 1e-8, f"Annihilation failed: ‖C₂ P₁‖ = {err:.2e}"


def test_projector_trace(projector_data):
    """Tr(P₁) = 2."""
    tr = float(np.real(np.trace(projector_data.projector)))
    assert abs(tr - SINGLET_DIMENSION) < 1e-10, (
        f"Tr(P₁) = {tr:.6f}, expected {SINGLET_DIMENSION}"
    )


def test_kernel_basis_orthonormality(projector_data):
    """Kernel basis vectors are orthonormal."""
    basis = projector_data.kernel_basis
    assert len(basis) == SINGLET_DIMENSION
    for i, vi in enumerate(basis):
        for j, vj in enumerate(basis):
            inner = complex(np.vdot(vi, vj))
            expected = 1.0 if i == j else 0.0
            err = abs(inner - expected)
            assert err < 1e-12, (
                f"Gram matrix [{i},{j}] = {inner:.4f}, expected {expected}"
            )


def test_projector_acts_as_identity_on_basis(projector_data):
    """P₁ |e_i⟩ = |e_i⟩ for each kernel-basis vector."""
    P = projector_data.projector
    for k, vec in enumerate(projector_data.kernel_basis):
        err = float(np.linalg.norm(P @ vec - vec))
        assert err < 1e-12, (
            f"P₁ |e_{k}⟩ ≠ |e_{k}⟩: error = {err:.2e}"
        )


def test_complement_idempotent(projector_data):
    """I − P₁ is also an orthogonal projector."""
    P = projector_data.projector
    I = np.eye(CARRIER_DIMENSION, dtype=np.complex128)
    Q = I - P
    err = np.linalg.norm(Q @ Q - Q, ord=2)
    assert err < 1e-12, f"I − P₁ not idempotent: {err:.2e}"


def test_projector_orthogonal_complement(projector_data):
    """P₁ (I − P₁) = 0."""
    P = projector_data.projector
    I = np.eye(CARRIER_DIMENSION, dtype=np.complex128)
    Q = I - P
    err = np.linalg.norm(P @ Q, ord=2)
    assert err < 1e-12, f"P₁(I − P₁) ≠ 0: {err:.2e}"


# ── invariant tensor states ────────────────────────────────────────

def test_f_state_in_kernel(operators, projector_data):
    """The |f⟩ = Σ f_{abc}|abc⟩ state lies in ker(C₂^tot)."""
    psi = f_state(operators.structure_constants_f)
    err = float(np.linalg.norm(projector_data.projector @ psi - psi))
    assert err < 1e-12, f"‖P₁|f⟩ − |f⟩‖ = {err:.2e}"


def test_d_state_in_kernel(operators, projector_data):
    """The |d⟩ = Σ d_{abc}|abc⟩ state lies in ker(C₂^tot)."""
    psi = d_state(operators.structure_constants_d)
    err = float(np.linalg.norm(projector_data.projector @ psi - psi))
    assert err < 1e-12, f"‖P₁|d⟩ − |d⟩‖ = {err:.2e}"


def test_f_state_annihilated_by_casimir(operators):
    """|f⟩ is a zero-eigenvalue state of C₂^tot."""
    psi = f_state(operators.structure_constants_f)
    result = operators.casimir_total @ psi
    err = float(np.linalg.norm(result))
    assert err < 1e-8, f"C₂^tot |f⟩ ≠ 0: ‖…‖ = {err:.2e}"


def test_d_state_annihilated_by_casimir(operators):
    """|d⟩ is a zero-eigenvalue state of C₂^tot."""
    psi = d_state(operators.structure_constants_d)
    result = operators.casimir_total @ psi
    err = float(np.linalg.norm(result))
    assert err < 1e-8, f"C₂^tot |d⟩ ≠ 0: ‖…‖ = {err:.2e}"


def test_f_d_not_parallel(operators):
    """|f⟩ and |d⟩ are linearly independent (span a 2-dim space)."""
    psi_f = f_state(operators.structure_constants_f)
    psi_d = d_state(operators.structure_constants_d)
    overlap = abs(float(np.vdot(psi_f, psi_d)))
    # Not parallel: |⟨f|d⟩| < 1
    assert overlap < 1.0 - 1e-6, (
        f"|⟨f|d⟩| = {overlap:.6f}, states appear parallel"
    )


def test_f_d_span_kernel(operators, projector_data):
    """|f⟩ and |d⟩ together span the full 2-dim kernel."""
    psi_f = f_state(operators.structure_constants_f)
    psi_d = d_state(operators.structure_constants_d)
    # Both states in kernel; orthogonalise to get a 2-dim basis
    v1 = psi_f.copy()
    v1 /= np.linalg.norm(v1)
    v2 = psi_d - np.vdot(v1, psi_d) * v1
    rank = 1 if np.linalg.norm(v2) < 1e-10 else 2
    assert rank == SINGLET_DIMENSION, (
        f"|f⟩ and |d⟩ span only {rank}-dim subspace"
    )


# ── machine certificate ────────────────────────────────────────────

def test_certificate_valid(certificate):
    """Full machine certificate passes."""
    assert certificate.valid, (
        "Certificate failed:\n" + "\n".join(certificate.errors)
    )


def test_certificate_projector_rank(certificate):
    """Certified projector rank is 2."""
    assert certificate.projector_rank == SINGLET_DIMENSION


def test_certificate_hermitian_error(certificate):
    """Hermitian error is negligible."""
    assert certificate.hermitian_error < 1e-10


def test_certificate_idempotence_error(certificate):
    """Idempotence error is negligible."""
    assert certificate.idempotence_error < 1e-10


def test_certificate_annihilation_error(certificate):
    """Annihilation error ‖C₂ P₁‖ is negligible."""
    assert certificate.annihilation_error < 1e-8


def test_certificate_contraction_convergence(certificate):
    """Γ^400 converges to P₁ (error below 0.05)."""
    # Convergence is slow for 512-dim (small ε × large λ_max)
    assert certificate.contraction_error < 0.05, (
        f"Γ^{certificate.contraction_iterations} error = "
        f"{certificate.contraction_error:.4f}"
    )


def test_certificate_spectral_gap_positive(certificate):
    """C₂^tot spectral gap is positive."""
    assert certificate.spectral_gap > 0.0


def test_certificate_singlet_eigenvalue(certificate):
    """Smallest C₂^tot eigenvalue is ~0 (singlet sector)."""
    assert abs(certificate.singlet_eigenvalue) < 1e-8


# ── quantum-simulation leakage detector ───────────────────────────

def test_leakage_singlet_f(operators, projector_data):
    """Pure |f⟩ state has zero leakage."""
    psi = f_state(operators.structure_constants_f)
    ell = leakage(psi, projector_data.projector)
    assert abs(ell) < 1e-10, f"ℓ(|f⟩) = {ell:.2e}"


def test_leakage_singlet_d(operators, projector_data):
    """Pure |d⟩ state has zero leakage."""
    psi = d_state(operators.structure_constants_d)
    ell = leakage(psi, projector_data.projector)
    assert abs(ell) < 1e-10, f"ℓ(|d⟩) = {ell:.2e}"


def test_leakage_mixed_singlet(operators, projector_data):
    """Superposition of |f⟩ and |d⟩ has zero leakage."""
    psi_f = f_state(operators.structure_constants_f)
    psi_d = d_state(operators.structure_constants_d)
    psi = psi_f + 1j * psi_d
    psi /= np.linalg.norm(psi)
    ell = leakage(psi, projector_data.projector)
    assert abs(ell) < 1e-10, f"ℓ(mixed singlet) = {ell:.2e}"


def test_leakage_random_state_large(projector_data):
    """Haar-random state has leakage close to 1 − 2/512."""
    rng = np.random.default_rng(42)
    psi = rng.standard_normal(CARRIER_DIMENSION) + 1j * rng.standard_normal(
        CARRIER_DIMENSION
    )
    psi /= np.linalg.norm(psi)
    ell = leakage(psi, projector_data.projector)
    expected_avg = 1.0 - SINGLET_DIMENSION / CARRIER_DIMENSION
    # Within 5% of the Haar average
    assert abs(ell - expected_avg) < 0.05, (
        f"ℓ(random) = {ell:.4f}, expected ~{expected_avg:.4f}"
    )


def test_leakage_density_matrix(operators, projector_data):
    """Leakage of a singlet density matrix is zero."""
    psi = f_state(operators.structure_constants_f)
    rho = np.outer(psi, psi.conj())
    ell = leakage(rho, projector_data.projector)
    assert abs(ell) < 1e-10, f"ℓ(ρ_f) = {ell:.2e}"


def test_leakage_maximally_mixed_complement(projector_data):
    """Uniform mixture over the complement has leakage = 1."""
    P = projector_data.projector
    I = np.eye(CARRIER_DIMENSION, dtype=np.complex128)
    Q = I - P  # projector onto complement (dim 510)
    rho_comp = Q / np.trace(Q)  # normalised density matrix on complement
    ell = leakage(rho_comp, P)
    assert abs(ell - 1.0) < 1e-10, f"ℓ(complement) = {ell:.2e}"


__all__ = [
    "test_adjoint_casimir_eigenvalue",
    "test_adjoint_generator_count",
    "test_adjoint_generator_shape",
    "test_adjoint_generators_hermitian",
    "test_adjoint_generators_traceless",
    "test_certificate_annihilation_error",
    "test_certificate_contraction_convergence",
    "test_certificate_hermitian_error",
    "test_certificate_idempotence_error",
    "test_certificate_projector_rank",
    "test_certificate_singlet_eigenvalue",
    "test_certificate_spectral_gap_positive",
    "test_certificate_valid",
    "test_commutation_relations",
    "test_complement_idempotent",
    "test_d_state_annihilated_by_casimir",
    "test_d_state_in_kernel",
    "test_d_tensor_real",
    "test_d_tensor_shape",
    "test_d_tensor_symmetry",
    "test_f_d_not_parallel",
    "test_f_d_span_kernel",
    "test_f_state_annihilated_by_casimir",
    "test_f_state_in_kernel",
    "test_gell_mann_count",
    "test_gell_mann_hermitian",
    "test_gell_mann_orthonormality",
    "test_gell_mann_shape",
    "test_gell_mann_traceless",
    "test_jacobi_identity",
    "test_kernel_basis_orthonormality",
    "test_leakage_density_matrix",
    "test_leakage_maximally_mixed_complement",
    "test_leakage_mixed_singlet",
    "test_leakage_random_state_large",
    "test_leakage_singlet_d",
    "test_leakage_singlet_f",
    "test_projector_acts_as_identity_on_basis",
    "test_projector_annihilation",
    "test_projector_hermitian",
    "test_projector_idempotent",
    "test_projector_orthogonal_complement",
    "test_projector_rank",
    "test_projector_trace",
    "test_structure_constants_antisymmetry_ab",
    "test_structure_constants_antisymmetry_ac",
    "test_structure_constants_real",
    "test_structure_constants_shape",
    "test_total_casimir_contains_singlet_value",
    "test_total_casimir_has_zero_eigenvalues",
    "test_total_casimir_hermitian",
    "test_total_casimir_positive_semidefinite",
    "test_total_casimir_shape",
    "test_total_casimir_spectral_gap",
]
