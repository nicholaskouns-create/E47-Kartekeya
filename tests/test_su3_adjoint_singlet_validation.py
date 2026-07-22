from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "su3_adjoint_singlet_validation.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "su3_adjoint_singlet_validation",
        SCRIPT_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to load SU(3) validation script module.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def validation_results():
    module = _load_module()
    return module.validate_su3_adjoint_singlets()


def test_validation_passes(validation_results) -> None:
    assert validation_results.valid is True


def test_singlet_sector_is_two_dimensional(validation_results) -> None:
    assert validation_results.carrier_dimension == 512
    assert validation_results.singlet_dimension == 2
    assert validation_results.projector_rank == 2
    assert validation_results.spectrum["0"] == 2


def test_invariant_tensors_span_singlet_sector(validation_results) -> None:
    assert abs(validation_results.f_d_overlap) < 1e-10
    assert validation_results.f_total_generator_error < 1e-10
    assert validation_results.d_total_generator_error < 1e-10
    assert validation_results.invariant_span_projector_error < 1e-8


def test_contraction_and_leakage_metrics(validation_results) -> None:
    assert validation_results.positive_casimir_gap == pytest.approx(3.0, abs=1e-8)
    assert validation_results.max_casimir_eigenvalue == pytest.approx(15.0, abs=1e-8)
    assert validation_results.positive_k2_gap == pytest.approx(9.0, abs=1e-8)
    assert validation_results.max_k2_eigenvalue == pytest.approx(225.0, abs=1e-8)
    assert validation_results.theoretical_contraction_factor == pytest.approx(
        24.0 / 25.0,
        abs=1e-12,
    )
    assert validation_results.leakage_f < 1e-10
    assert validation_results.leakage_d < 1e-10
    assert validation_results.leakage_equal_mixture < 1e-10
    assert validation_results.expected_random_leakage == pytest.approx(255.0 / 256.0)
