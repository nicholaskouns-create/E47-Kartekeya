from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_moment_dynamics_certificate.py"
CERT_NAME = "E47_MOMENT_DYNAMICS_CERTIFICATE.json"


def test_e47_moment_dynamics_certificate(tmp_path):
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
    assert cert["schema"] == "MC-E47-MOMENT-DYNAMICS/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 13
    assert all(cert["checks"].values())

    family = {row["k"]: row for row in cert["exact"]["family"]}
    cube = family[5]
    assert (cube["gap_sector"], cube["top_sector"]) == ("3", "6")
    assert (cube["Delta"], cube["Lambda"]) == ("11664", "186624")
    assert (cube["sqrt_kappa"], cube["kappa"]) == ("4", "16")
    assert (cube["rho_star"], cube["chebyshev"], cube["eps_star"]) == ("15/17", "3/5", "1/99144")
    assert cube["finite_termination_steps"] == 5
    assert family[7]["sqrt_kappa"] == "900/49"
    assert cert["exact"]["integral_sqrt_kappa_for_2j_up_to_4000"] == ["2"]

    machine = cert["machine"]
    assert machine["flow"] and machine["discrete"] and machine["stability"] and machine["projector"]
    assert machine["termination_steps"] == 5
