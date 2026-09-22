from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_e47_prism_matrix.py"


def test_matrix_e47_prism_local_certificate():
    run = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=180,
        check=False,
    )
    assert run.returncode == 0, run.stdout + "\n" + run.stderr
    cert = json.loads(run.stdout)
    assert cert["status"] == "PASS"
    assert cert["checks"]["spectral_weight_sum"] is True
    assert abs(sum(b["weight"] for b in cert["bands"]) - 1.0) < 1e-12
    assert abs(cert["e47"]["weight"] - sum(b["weight"] for b in cert["bands"] if b["selected"])) < 1e-12
    assert abs(cert["e47"]["rank_fraction"] - 47 / 125) < 1e-15
