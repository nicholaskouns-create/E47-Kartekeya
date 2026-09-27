from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_casimir_census_certificate.py"
CERT_NAME = "E47_CASIMIR_CENSUS_CERTIFICATE.json"


def test_e47_casimir_census_certificate(tmp_path):
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
    assert cert["schema"] == "MC-E47-CASIMIR-CENSUS/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 12
    assert all(cert["checks"].values())

    exact = cert["exact"]
    assert exact["census"]["multiplicity"] == [1, 3, 5, 4, 3, 2, 1]
    assert exact["census"]["sector_dimension"] == [1, 9, 25, 28, 27, 22, 13]
    assert exact["full_su2_commutant"] == 65
    assert exact["e47"] == {"selection": [2, 5], "dimension": 47, "commutant": 29}
    assert exact["dimension_47_selections"] == [
        {"spins": [2, 5], "commutant": 29},
        {"spins": [1, 2, 6], "commutant": 35},
    ]
