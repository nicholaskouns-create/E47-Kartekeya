"""QuTiP validation tests for the canonical E47 construction.

This test module verifies that the aggregated E47 validation results
satisfy all canonical invariants and are serializable.

Tests consume the validation aggregate without duplicating construction
or validation logic.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from e47.serialization import validation_results_to_dict
from e47.validation_results import (
    require_all_validations,
    run_all_validations,
)


def test_qutip_validation_via_aggregate() -> None:
    """Run all validations and assert the aggregate passes."""
    results = run_all_validations()
    require_all_validations(results)
    assert results.valid


def test_qutip_validation_is_valid() -> None:
    """Assert that the QuTiP validation layer passes."""
    results = run_all_validations()
    assert results.qutip_validation.valid


def test_qutip_validation_carrier_dimension() -> None:
    """Assert the carrier dimension is 125."""
    results = run_all_validations()
    assert results.qutip_validation.carrier_dimension == 125


def test_qutip_validation_kernel_dimension() -> None:
    """Assert the E47 kernel dimension is 47."""
    results = run_all_validations()
    assert results.qutip_validation.kernel_dimension == 47


def test_qutip_validation_coherence_fraction() -> None:
    """Assert the coherence fraction is 47/125 = 0.376."""
    results = run_all_validations()
    expected = 47 / 125
    assert abs(results.qutip_validation.coherence_fraction - expected) < 1e-12


def test_qutip_validation_k2_spectral_gap() -> None:
    """Assert the K² spectral gap is 11664."""
    results = run_all_validations()
    assert results.qutip_validation.k2_spectral_gap == 11664


def test_qutip_validation_no_errors() -> None:
    """Assert the QuTiP validation has no error messages."""
    results = run_all_validations()
    assert len(results.qutip_validation.errors) == 0


def test_aggregate_certificate_is_serializable() -> None:
    """Assert the aggregate certificate converts to a JSON-compatible dict."""
    results = run_all_validations()
    payload = validation_results_to_dict(results)

    assert isinstance(payload, dict)
    assert payload["valid"] is True
    assert payload["qutip_validation"]["valid"] is True


def test_kernel_validation_passes() -> None:
    """Assert the kernel validation layer passes."""
    results = run_all_validations()
    assert results.kernel_validation.status == "pass"


def test_projector_validation_passes() -> None:
    """Assert the projector validation layer passes."""
    results = run_all_validations()
    assert results.projector_validation.status == "pass"


def test_contraction_validation_passes() -> None:
    """Assert the contraction validation layer passes."""
    results = run_all_validations()
    assert results.contraction_validation.valid


def test_semigroup_validation_passes() -> None:
    """Assert the semigroup validation layer passes."""
    results = run_all_validations()
    assert results.semigroup_validation.valid


def test_all_five_layers_pass() -> None:
    """Assert that all five validation layers pass simultaneously."""
    results = run_all_validations()
    assert results.kernel_validation.status == "pass"
    assert results.projector_validation.status == "pass"
    assert results.contraction_validation.valid
    assert results.semigroup_validation.valid
    assert results.qutip_validation.valid
    assert results.valid


def test_aggregate_summarize_method() -> None:
    """Assert the summary method returns correct canonical values."""
    results = run_all_validations()
    summary = results.summarize()

    assert summary["valid"] is True
    assert summary["kernel_dimension"] == 47
    assert abs(summary["coherence_fraction"] - 47 / 125) < 1e-12
    assert summary["k2_spectral_gap"] == 11664
    assert summary["projector_rank"] == 47
    assert abs(summary["projector_trace"] - 47) < 1e-10


def test_serialized_certificate_preserves_structure() -> None:
    """Assert serialization preserves all five certificate structures."""
    results = run_all_validations()
    payload = validation_results_to_dict(results)

    assert "kernel_validation" in payload
    assert "projector_validation" in payload
    assert "contraction_validation" in payload
    assert "semigroup_validation" in payload
    assert "qutip_validation" in payload


def test_serialized_certificate_lists_not_tuples() -> None:
    """Assert that tuples are converted to lists in serialization."""
    results = run_all_validations()
    payload = validation_results_to_dict(results)

    # Error tuples should be converted to lists
    assert isinstance(payload["qutip_validation"]["errors"], list)
    assert isinstance(payload["contraction_validation"]["errors"], list)


def test_certificate_generation_script_runs_from_repo_root(tmp_path: Path) -> None:
    """Assert the standalone certificate generator can import the src package."""
    repo_root = Path(__file__).resolve().parents[1]
    output_path = tmp_path / "certificate.json"
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "generate_validation_certificate.py"),
            "--output",
            str(output_path),
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["valid"] is True


__all__ = [
    "test_aggregate_certificate_is_serializable",
    "test_aggregate_summarize_method",
    "test_all_five_layers_pass",
    "test_certificate_generation_script_runs_from_repo_root",
    "test_contraction_validation_passes",
    "test_kernel_validation_passes",
    "test_projector_validation_passes",
    "test_qutip_validation_carrier_dimension",
    "test_qutip_validation_coherence_fraction",
    "test_qutip_validation_is_valid",
    "test_qutip_validation_k2_spectral_gap",
    "test_qutip_validation_kernel_dimension",
    "test_qutip_validation_no_errors",
    "test_qutip_validation_via_aggregate",
    "test_semigroup_validation_passes",
    "test_serialized_certificate_lists_not_tuples",
    "test_serialized_certificate_preserves_structure",
]
