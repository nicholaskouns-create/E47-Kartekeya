from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aetheris.flight_runtime import (
    DEFAULT_VEHICLE_SPECS,
    E47Witness,
    ExperimentalE47Adapter,
    FunctionVehicleAdapter,
    State6DOF,
    VehicleBoundary,
    VehicleRegistry,
)


def state() -> State6DOF:
    return State6DOF(
        pos_wgs84=np.array([36.1699, -115.1398, 3658.0]),
        vel_body=np.array([216.0, 0.0, 0.0]),
        quat=np.array([1.0, 0.0, 0.0, 0.0]),
        ang_vel_body=np.zeros(3),
    )


def test_registry_marks_real_boundary_crossing():
    registry = VehicleRegistry()
    registry.register(FunctionVehicleAdapter(DEFAULT_VEHICLE_SPECS["sr71"], lambda s, dt, i: s))
    registry.register(FunctionVehicleAdapter(DEFAULT_VEHICLE_SPECS["eidolon"], lambda s, dt, i: s))

    first = registry.switch("sr71")
    second = registry.switch("eidolon")

    assert not first.crossed
    assert second.crossed
    assert second.to_record()["previous_boundary"] == VehicleBoundary.CONVENTIONAL.value
    assert second.to_record()["selected_boundary"] == VehicleBoundary.EXPERIMENTAL_SIMULATION.value
    assert second.to_record()["e47_witness_required"] is True


def test_state_digest_is_deterministic_and_snapshot_is_read_only():
    a = state()
    b = state()
    assert a.digest == b.digest
    assert not a.vel_body.flags.writeable


def test_e47_witness_distinguishes_rank_fraction_from_state_capture():
    pytest.importorskip("qutip")
    witness = E47Witness.compile()
    psi = witness.basis_125x47[:, 0]
    projection = witness.inspect(psi)

    assert witness.rank == 47
    assert witness.basis_125x47.shape == (125, 47)
    assert projection.coordinates_47.shape == (47,)
    assert projection.receipt.kernel_fraction == pytest.approx(47 / 125)
    assert projection.receipt.capture == pytest.approx(1.0, abs=1e-10)
    assert projection.receipt.capture != pytest.approx(47 / 125)
    assert projection.receipt.kp_zero
    assert projection.receipt.valid


def test_semigroup_fixes_an_already_projected_state():
    pytest.importorskip("qutip")
    witness = E47Witness.compile()
    psi = witness.basis_125x47[:, 3]
    filtered = witness.filter_state(psi, 1e-3)
    assert np.linalg.norm(filtered - psi) <= 1e-8


def test_experimental_adapter_keeps_e1_witness_separate_from_e2_model():
    pytest.importorskip("qutip")
    witness = E47Witness.compile()
    spec = DEFAULT_VEHICLE_SPECS["eidolon"]
    carrier = np.array(witness.basis_125x47[:, 0], copy=True)

    def carrier_state(_state, _inputs):
        return carrier

    def model_step(current, _dt, _inputs, projected, coords):
        assert projected.shape == (125,)
        assert coords.shape == (47,)
        return State6DOF(
            pos_wgs84=current.pos_wgs84,
            vel_body=current.vel_body + np.array([1.0, 0.0, 0.0]),
            quat=current.quat,
            ang_vel_body=current.ang_vel_body,
        ), {"adapter": "test-only"}

    adapter = ExperimentalE47Adapter(
        spec=spec,
        witness=witness,
        carrier_state_fn=carrier_state,
        model_step_fn=model_step,
    )
    result = adapter.step(state(), 1 / 120, {"throttle": 0.5})

    assert result.receipt["evidence_class"] == "E2"
    assert result.receipt["e47_witness"]["evidence_class"] == "E1"
    assert result.receipt["e47_witness"]["valid"] is True
    assert result.receipt["e47_witness"]["kp_zero"] is True
    assert result.state.vel_body[0] == pytest.approx(217.0)


def test_default_specs_match_browser_fleet_boundary():
    conventional = {"f16", "sr71", "x15"}
    experimental = {"eidolon", "manta", "skyrmion", "jacob"}

    assert {k for k, v in DEFAULT_VEHICLE_SPECS.items() if v.boundary is VehicleBoundary.CONVENTIONAL} == conventional
    assert {
        k for k, v in DEFAULT_VEHICLE_SPECS.items()
        if v.boundary is VehicleBoundary.EXPERIMENTAL_SIMULATION
    } == experimental
