import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "web" / "city_graphics_profiles.json"


def load_manifest():
    return json.loads(MANIFEST.read_text())


def test_graphics_manifest_contract_and_proof_gates():
    data = load_manifest()
    assert data["contract"] == "CITY-GRAPHICS-ACCELERATOR-1.0"
    assert data["proof_gates"] == [
        "accelerated_vs_reference_state_equivalence",
        "frame_rate_independence",
        "backend_fallback_equivalence",
    ]
    assert "must not alter solver timestep" in data["invariant"]


def test_public_lab_orders_are_complete_and_unique():
    data = load_manifest()
    ordered = [s for s in data["surfaces"] if isinstance(s.get("order"), int)]
    assert [s["order"] for s in ordered] == list(range(1, len(ordered) + 1))
    assert len({s["name"] for s in ordered}) == len(ordered)
    assert ordered[10]["name"] == "SCALAR"
    assert ordered[11]["name"] == "EIDOLON"
    assert ordered[12]["name"] == "SYNTAX JACOB"
    assert ordered[13]["name"] == "InvariFold"
    assert [s["name"] for s in ordered[14:18]] == [
        "SKYRMION", "MANTA", "UFO PROPULSION LAB", "CITY FLIGHT SHELL"
    ]


def test_runtime_has_safe_fallback_chain():
    runtime = load_manifest()["default_runtime"]
    assert runtime["preferred_backend"] == "webgpu"
    assert runtime["fallbacks"][-1] == "canvas2d"
    assert runtime["adaptive_resolution"] is True
    assert runtime["fixed_timestep"] is True


def test_external_hosts_are_not_falsely_marked_integrated():
    data = load_manifest()
    prohibited = {"integrated", "complete", "done"}
    external_names = {
        "SPECTRA", "Fold", "Murmuration", "Mnemosyne", "Density", "Horizon",
        "Wave", "Identity", "BUILD", "SOAR", "SCALAR", "EIDOLON", "InvariFold",
        "THE MATRIX", "City OS",
    }
    for surface in data["surfaces"]:
        if surface["name"] in external_names:
            assert surface["host_status"] not in prohibited
