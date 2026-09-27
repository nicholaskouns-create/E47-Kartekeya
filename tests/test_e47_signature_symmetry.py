from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_signature_symmetry_certificate.py"
CERT_NAME = "E47_SIGNATURE_SYMMETRY_CERTIFICATE.json"


def test_e47_signature_symmetry_certificate(tmp_path):
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
    assert cert["schema"] == "MC-E47-SIGNATURE-SYMMETRY/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 21
    assert all(cert["checks"].values())

    exact = cert["exact"]
    assert exact["e47_s3_dimensions"] == {"trivial": 5, "sign": 0, "standard": 42}
    assert exact["su2_s3_multiplicities"]["2"] == {"trivial": 1, "sign": 0, "standard": 2}
    assert exact["su2_s3_multiplicities"]["5"] == {"trivial": 0, "sign": 0, "standard": 1}
    assert exact["K_inertia"]["positive"] == 23
    assert exact["K_inertia"]["negative"] == 55
    assert exact["K_inertia"]["zero"] == 47

    machine = cert["machine"]
    assert machine["e47_s3_dimensions"] == exact["e47_s3_dimensions"]
    assert machine["trace_fingerprint"] == [47, 5, -16]
    assert machine["eta_signature"] == {"positive": 47, "negative": 78}
