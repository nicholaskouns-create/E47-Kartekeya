from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_einstein_full_closure_certificate.py"
RECEIPT = ROOT / "artifacts" / "E47_EINSTEIN_FULL_CLOSURE_CERTIFICATE.json"


def test_e47_einstein_full_closure_certificate():
    run = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    assert run.returncode == 0, run.stdout + "\n" + run.stderr

    cert = json.loads(RECEIPT.read_text())
    assert cert["schema"] == "MC-E47-EINSTEIN-FULL-CLOSURE/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 28
    assert all(cert["checks"].values())

    assert cert["e47"]["kernel_dimension"] == 47
    assert cert["e47"]["commutant_dimension"] == 29
    assert cert["dynamics"]["zero_mult"] == 11
    assert cert["product_kernel"]["nullity"] == 47
    assert cert["einstein_ppwave"]["vacuum"] is True
    assert cert["einstein_ppwave"]["independent_47"] is True
