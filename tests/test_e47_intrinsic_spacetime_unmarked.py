from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_intrinsic_spacetime_unmarked.py"
RECEIPT = ROOT / "artifacts" / "E47_INTRINSIC_SPACETIME_UNMARKED_CERTIFICATE.json"

def test_e47_intrinsic_spacetime_unmarked_certificate():
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
    assert cert["schema"] == "MC-E47-INTRINSIC-SPACETIME-UNMARKED/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 24
    assert all(cert["checks"].values())
    assert cert["intrinsic_spacetime"]["eta_inertia"] == {"positive":47,"negative":78}
    assert abs(cert["intrinsic_spacetime"]["determinant"] + 1.0) < 1e-10
    assert cert["unmarked_moduli_embedding"]["real_domain_dimension"] == 47
    assert "bijection" not in cert["boundary"].lower()
