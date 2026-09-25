import numpy as np

from e47.native_variational_eigensolver import (
    HERON_FIXED_POINT,
    HERON_SEED,
    OPTIMAL_TRANSIENT_BOUND,
    construct_e47_ground_projector,
    heron_error_identity_residual,
    heron_step,
    e47_discrete_flow,
    e47_nve_energy,
    eigen_residual,
    seven_qubit_hamiltonian,
    simulate_seven_qubit_imaginary_time,
    validate_e47_nve,
)
from e47.su2_kernel import build_e47_operators


def _ground_and_excited():
    ops = build_e47_operators()
    values, states = ops.kernel_squared.eigenstates()
    pairs = sorted(
        [(float(np.real(v)), s) for v, s in zip(values, states)],
        key=lambda x: x[0],
    )
    ground = next(s for v, s in pairs if abs(v) < 1e-9)
    excited = next(s for v, s in pairs if v > 1e-9)
    return ops, ground, excited


def test_e47_nve_validation_passes():
    result = validate_e47_nve()
    assert result.status == "pass"
    assert result.ground_dimension == 47
    assert abs(result.ground_energy) < 1e-8
    assert abs(result.spectral_gap - 11664.0) < 1e-8
    assert abs(result.max_eigenvalue - 186624.0) < 1e-8
    assert abs(result.contraction_spectral_radius - OPTIMAL_TRANSIENT_BOUND) < 1e-8


def test_ground_energy_is_zero_and_excited_energy_positive():
    ops, ground, excited = _ground_and_excited()
    assert abs(e47_nve_energy(ground, ops)) < 1e-8
    assert e47_nve_energy(excited, ops) > 0.0


def test_generic_superposition_is_not_automatically_an_eigenstate():
    ops, ground, excited = _ground_and_excited()
    psi = (ground + excited).unit()
    assert eigen_residual(psi, ops.kernel_squared) > 1e-6


def test_discrete_native_flow_converges_to_e47_projection():
    ops, ground, excited = _ground_and_excited()
    psi = (ground + excited).unit()
    projector = construct_e47_ground_projector(ops)
    target = projector * psi
    flowed = e47_discrete_flow(psi, 200, ops)
    assert (flowed - target).norm() < 1e-8


def test_native_flow_lowers_e47_energy():
    ops, ground, excited = _ground_and_excited()
    psi = (ground + excited).unit()
    before = e47_nve_energy(psi, ops)
    after = e47_nve_energy(e47_discrete_flow(psi, 20, ops), ops)
    assert after < before


def test_golden_heron_fixed_point_and_quadratic_error_identity():
    target = HERON_FIXED_POINT
    assert abs(target * target - HERON_SEED) < 1e-15
    assert abs(heron_step(target) - target) < 1e-15
    assert heron_error_identity_residual(1.0) < 1e-15


def test_historical_phi_minus_five_fixed_point_claim_is_rejected():
    assert abs(heron_step(HERON_SEED) - HERON_SEED) > 1e-3
    assert abs(HERON_FIXED_POINT - 47.0 / 125.0) > 1e-2


def test_seven_qubit_padding_preserves_exact_ground_dimension():
    h = seven_qubit_hamiltonian().full()
    values = np.linalg.eigvalsh(h)
    assert int(np.sum(np.abs(values) < 1e-8)) == 47
    assert abs(np.min(values[values > 1e-8]) - 11664.0) < 1e-8
    assert abs(np.max(values) - 186624.0) < 1e-8


def test_seven_qubit_imaginary_time_projects_into_ground_space():
    samples = simulate_seven_qubit_imaginary_time()
    energies = [s.energy for s in samples]
    weights = [s.ground_weight for s in samples]
    assert all(b <= a + 1e-8 for a, b in zip(energies, energies[1:]))
    assert all(b >= a - 1e-12 for a, b in zip(weights, weights[1:]))
    assert weights[-1] > 0.999999999
    assert energies[-1] < 1e-5
