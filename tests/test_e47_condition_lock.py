from __future__ import annotations

import json
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_condition_lock_certificate.py"
CERT_NAME = "E47_CONDITION_LOCK_CERTIFICATE.json"


def test_e47_condition_lock_certificate(tmp_path):
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
    assert cert["schema"] == "MC-E47-CONDITION-LOCK/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 25
    assert all(cert["checks"].values())

    exact = cert["exact"]
    assert exact["abs_K_on_complement"] == [108, 112, 140, 180, 432]
    assert exact["condition_number_K"] == "4"
    assert exact["condition_number_K2"] == "16"
    assert exact["epsilon_star"] == "1/99144"
    assert exact["rho_star"] == "15/17"
    assert exact["chebyshev_rate"] == "3/5"
    assert min(map(Fraction, exact["gamma_on_complement"])) == Fraction(-15, 17)
    assert max(map(Fraction, exact["gamma_on_complement"])) == Fraction(15, 17)
    assert cert["machine"]["K_inertia"] == {"positive": 23, "negative": 55, "zero": 47}
    assert cert["machine"]["krylov_dimension"] == 5
