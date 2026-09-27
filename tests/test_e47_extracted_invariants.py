from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_extracted_invariants_validation.py"


def test_cross_plate_certificate(tmp_path):
    receipt = tmp_path / "certificate.json"
    run = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        env={**os.environ, "E47_CERT_OUT": str(receipt)},
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    result = json.loads(receipt.read_text())
    assert result["status"] == "PASS"
    assert (result["passed"], result["total"]) == (47, 47)
    assert result["checks"]["joint_SU2_S3_table"]
    assert result["checks"]["matrix_Gamma_not_eta_isometry"]
    assert result["checks"]["chosen_Lorentzian_pullback"]
    assert result["observations"]["whole_sector_rank47_selectors"] == [[[2, 5], 29], [[1, 2, 6], 35]]
    assert "FPGA implementation, resource counts, timing, and Q4.28 250-step error" in result["observations"]["unvalidated_claims"]
