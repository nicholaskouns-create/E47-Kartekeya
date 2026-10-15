from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "research" / "e47" / "validation" / "e47_moment_selector_certificate.py"
CERT_NAME = "E47_MOMENT_SELECTOR_CERTIFICATE.json"


def test_e47_moment_selector_certificate(tmp_path):
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
    assert cert["schema"] == "MC-E47-MOMENT-SELECTOR/1.0"
    assert cert["status"] == "PASS"
    assert len(cert["checks"]) == 13
    assert all(cert["checks"].values())

    exact = cert["exact"]
    assert exact["rational_sigma_tensor_powers"] == [3, 25, 243]
    assert exact["carriers_with_both_roots_in_spectrum_2j_up_to_400"] == [1, 4, 12, 33, 88, 232]

    family = {row["k"]: row for row in exact["family"]}
    assert (family[3]["dim_kernel"], family[3]["dim_carrier"]) == (8, 8)
    assert family[5]["j"] == "2" and family[5]["J"] == "5"
    assert (family[5]["mu"], family[5]["sigma"]) == ("18", "12")
    assert (family[5]["dim_kernel"], family[5]["dim_carrier"]) == (47, 125)
    assert [family[k]["F_k"] for k in (3, 5, 7, 9, 11, 13)] == [2, 5, 13, 34, 89, 233]
    assert [family[k]["L_k"] for k in (3, 5, 7, 9, 11, 13)] == [4, 11, 29, 76, 199, 521]

    assert cert["machine"]["nullity"] == 47
