from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_profile_injection_certificate.py"
CERT_NAME = "E47_PROFILE_INJECTION_CERTIFICATE.json"


def test_e47_profile_injection_certificate(tmp_path):
    receipt = tmp_path / CERT_NAME
    run = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        env={**os.environ, "E47_CERT_OUT": str(receipt)},
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    assert run.returncode == 0, run.stdout + "\n" + run.stderr

    cert = json.loads(receipt.read_text())
    assert cert["schema"] == "MC-E47-PROFILE-INJECTION/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 9
    assert all(cert["checks"].values())

    assert cert["grid"]["47,78"] == {"solutions": [[1, 1, 0]], "injective": True}
    assert cert["even_grid"]["46,78"]["solutions"] == [[1, -1, 0], [1, 1, 0]]
    assert len(cert["conditional_on"]) == 1
    assert "conditional" in cert["evidence"]["B"]
