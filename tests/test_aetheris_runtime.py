from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from aetheris import (
    AetherisRuntime,
    AssertionRecord,
    E47ProjectorModule,
    EvidenceClass,
    FunctionModule,
    IdentityModule,
    JsonlStore,
    ModuleResult,
    StatePacket,
)


def test_packet_digest_is_canonical_and_snapshot_is_read_only():
    source = np.array([1.0, 2.0, 3.0])
    a = StatePacket(kind="vector", payload={"b": 2, "a": source})
    b = StatePacket(kind="vector", payload={"a": np.array([1.0, 2.0, 3.0]), "b": 2})
    assert a.digest == b.digest
    source[0] = 99.0
    assert np.asarray(a.payload["a"])[0] == 1.0
    assert not np.asarray(a.payload["a"]).flags.writeable


def test_runtime_pipeline_is_deterministic():
    def scale(packet, context):
        payload = dict(packet.payload)
        payload["x"] = float(payload["x"]) * 2.0
        return packet.evolve(producer="demo.scale", payload=payload)

    runtime = AetherisRuntime()
    runtime.register(IdentityModule())
    runtime.register(FunctionModule(name="demo.scale", function=scale))
    initial = StatePacket(kind="scalar", payload={"x": 3.0})

    first = runtime.execute(initial, ["aetheris.identity", "demo.scale"])
    second = runtime.execute(initial, ["aetheris.identity", "demo.scale"])

    assert first.packet.payload["x"] == 6.0
    assert first.certificate.status == "PASS"
    assert first.certificate.digest == second.certificate.digest
    assert first.packet.digest == second.packet.digest


def test_failed_module_check_is_certified_and_stops_pipeline():
    def fail(packet, context):
        child = packet.evolve(producer="demo.fail")
        return ModuleResult(
            packet=child,
            checks=(
                AssertionRecord(
                    name="forced_failure",
                    passed=False,
                    observed=1,
                    expected=0,
                    evidence_class=EvidenceClass.E1,
                ),
            ),
        )

    runtime = AetherisRuntime()
    runtime.register(FunctionModule(name="demo.fail", function=fail))
    runtime.register(IdentityModule(name="after.failure"))
    initial = StatePacket(kind="test", payload={"x": 1})
    result = runtime.execute(initial, ["demo.fail", "after.failure"])

    assert result.certificate.status == "FAIL"
    assert len(result.certificate.receipts) == 1
    assert result.certificate.receipts[0].module == "demo.fail"


def test_jsonl_store_writes_portable_record(tmp_path):
    runtime = AetherisRuntime()
    runtime.register(IdentityModule())
    result = runtime.execute(StatePacket(kind="test", payload={"z": 7}), ["aetheris.identity"])
    path = tmp_path / "runs.jsonl"
    JsonlStore(path).append(result)

    record = json.loads(path.read_text().strip())
    assert record["certificate"]["status"] == "PASS"
    assert record["certificate"]["certificate_digest"] == result.certificate.digest
    assert record["packet"]["digest"] == result.packet.digest


def test_e47_projector_module_contract_when_qutip_available():
    pytest.importorskip("qutip")
    from e47.projector import construct_e47_projector
    from e47.su2_kernel import build_e47_operators

    runtime = AetherisRuntime()
    runtime.register(E47ProjectorModule())
    x = np.zeros(125, dtype=np.complex128)
    x[0] = 1.0
    x[37] = 0.25 - 0.5j
    result = runtime.execute(
        StatePacket(kind="quantum.state", payload={"state": x}),
        ["e47.projector"],
    )

    assert result.certificate.status == "PASS"
    receipt = result.certificate.receipts[0]
    measurements = receipt.measurements
    metadata = result.packet.metadata["aetheris.e47"]

    projector = construct_e47_projector().projector.full()
    projected = projector @ x
    expected_coherence = float(np.vdot(projected, projected).real / np.vdot(x, x).real)

    operators = build_e47_operators()
    eigenvalues, eigenvectors = np.linalg.eigh(operators.kernel_squared.full())
    weights = np.abs(eigenvectors.conj().T @ x) ** 2
    expected_k2 = float(np.dot(eigenvalues.real, weights) / np.vdot(x, x).real)

    assert measurements["carrier_amplitudes"] == 125
    assert measurements["projector_rank"] == 47
    assert measurements["projector_status"] == "PASS"
    assert measurements["projection_invariance_error"] <= 1e-8
    assert measurements["coherence"] == pytest.approx(expected_coherence, abs=1e-12)
    assert measurements["k2_expectation"] == pytest.approx(expected_k2, abs=1e-8)
    assert measurements["k2_spectrum"] == [0, 11664, 12544, 19600, 32400, 186624]
    assert "coherence_fraction" not in measurements
    assert "coherence_fraction" not in metadata
    assert metadata["coherence"] == pytest.approx(expected_coherence, abs=1e-12)
    assert np.asarray(result.packet.payload["state"]).shape == (125,)


def test_e47_projector_rejects_zero_state_when_qutip_available():
    pytest.importorskip("qutip")
    runtime = AetherisRuntime()
    runtime.register(E47ProjectorModule())
    x = np.zeros(125, dtype=np.complex128)

    with pytest.raises(ValueError, match="non-zero 125-amplitude state"):
        runtime.execute(
            StatePacket(kind="quantum.state", payload={"state": x}),
            ["e47.projector"],
            raise_on_error=True,
        )
