"""EIDOLON E2 flight replay: the published log binds to its certificate and replays.

Evidence class E2. Nothing here promotes the game rules.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from eidolon import OMEGA_C

ROOT = Path(__file__).resolve().parents[1]
CERT = ROOT / "artifacts" / "CITY-EIDOLON-FLIGHT-REPLAY-001.json"
LOG = ROOT / "trajectories" / "CITY-EIDOLON-FLIGHT-REPLAY-001.ndjson"
MIRROR = ROOT / "website" / "data" / "trajectories" / LOG.name


def _script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _script("check_eidolon_replay_ndjson")
regenerate = _script("regenerate_eidolon_replay")


def certificate() -> dict:
    return json.loads(CERT.read_text(encoding="utf-8"))


def records() -> list[dict]:
    return [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines()]


def test_committed_log_binds_to_certificate():
    cert = certificate()
    report = checker.check_ndjson(LOG, cert)
    assert report["n_samples"] == cert["trajectory"]["n_samples"] == 961
    assert report["canonical_sha256"] == cert["trajectory"]["canonical_sha256"]
    assert report["merkle_root"] == cert["trajectory"]["merkle_root"]


def test_pages_mirror_is_the_same_log():
    assert MIRROR.read_bytes() == LOG.read_bytes()


def test_binding_rejects_altered_logs(tmp_path):
    cert = certificate()
    lines = LOG.read_text(encoding="utf-8").splitlines()
    altered = {
        "changed value": lines[:500] + [lines[500].replace('"L":0.9', '"L":0.8', 1)] + lines[501:],
        "missing sample": lines[:-1],
        "reordered samples": [lines[1], lines[0]] + lines[2:],
        "reformatted record": [lines[0].replace(",", ", ")] + lines[1:],
    }
    for name, body in altered.items():
        assert body != lines, name
        path = tmp_path / f"{name.replace(' ', '_')}.ndjson"
        path.write_text("\n".join(body) + "\n", encoding="utf-8")
        with pytest.raises(SystemExit):
            checker.check_ndjson(path, cert)


def test_certificate_checks_reproduce_from_log():
    cert = certificate()
    craft, checks, traj = cert["craft"], cert["checks"], cert["trajectory"]
    rows = records()

    envelope_error = max(
        abs(r["W"] - min(max(craft["scalar_amp"] * r["L"] / OMEGA_C, 0.0), 3.0)) for r in rows
    )
    inertia_error = max(
        abs(r["m_eff"] - craft["mass_kg"] * ((78 / 125) * (1.0 - r["L"]) + 1e-6)) for r in rows
    )
    assert envelope_error == pytest.approx(checks["W_recomputed_from_L"]["max_abs_error"], rel=1e-9)
    assert inertia_error == pytest.approx(checks["m_eff_recomputed_from_L"]["max_abs_error"], rel=1e-9)

    first, last, summary = rows[0], rows[-1], traj["summary"]
    assert (first["t"], last["t"]) == (traj["t0"], traj["t1"])
    assert (first["L"], last["L"]) == (summary["L0"], summary["L_final"])
    assert (first["W"], last["W"]) == (summary["W0"], summary["W_final"])
    assert (first["m_eff"], last["m_eff"]) == (summary["m_eff_0"], summary["m_eff_final"])
    assert all(0.0 <= r["L"] <= 1.0 for r in rows)
    assert {r["mode"] for r in rows} == {craft["engine_mode"]}
    assert {r["lab_mode"] for r in rows} == {craft["lab_mode"]}


def test_issue_time_rule_replays_certified_log():
    cert = certificate()
    replayed = regenerate.replay_records(cert)
    logged = records()
    assert len(replayed) == len(logged)
    for new, old in zip(replayed, logged):
        assert new["mode"] == old["mode"] and new["lab_mode"] == old["lab_mode"]
        for channel in ("t", "W", "L", "m_eff"):
            assert new[channel] == pytest.approx(old[channel], abs=1.5e-9)

    final = regenerate.replay_engine(cert).history[-1]
    summary = cert["trajectory"]["summary"]
    assert final.speed == pytest.approx(summary["airspeed_final_mps"], abs=1e-6)
    assert final.range_m == pytest.approx(summary["range_m"], abs=1e-6)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "CITY-EIDOLON-FLIGHT-REPLAY-001: signature.payload_sha256 is not reproduced by the "
        "canonical JSON of the published certificate without its signature object, so the "
        "Ed25519 signature cannot be checked from repository contents. Remove this marker "
        "when the certificate is re-signed or the signed bytes are published."
    ),
)
def test_certificate_signature_is_checkable():
    verified, note = checker.signature_status(certificate())
    assert verified or "Ed25519 not checked" in note, note
