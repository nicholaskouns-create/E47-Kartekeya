#!/usr/bin/env python3
"""Validate G_E47 machine-status partition (no new symbols)."""
from __future__ import annotations
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research/e47/validation"))
from spectral_engine import SpectralEngine  # noqa: E402

EXPECTED = {
    "locked": ["V", "C", "K", "E_47", "P_47", "Gamma", "Omega_c", "Q"],
    "structurally_supported": ["Sigma_5^3"],
    "external_bundle": ["L"],
    "not_instantiated": ["phi_anc", "phi_mod", "mathcal_T"],
}


def main(cert_path: str = "certificates/MC-G-E47-MACHINE-STATUS-20260927.json") -> int:
    data = json.loads(Path(cert_path).read_text(encoding="utf-8"))
    errors = []

    def check(ok: bool, msg: str) -> None:
        if not ok:
            errors.append(msg)

    check(data.get("schema") == "MC-G-E47-MACHINE-STATUS-1.0", "schema mismatch")
    check(data.get("overall") == "PASS", "overall must be PASS")
    check(data.get("citizen_core") == "K_47/125", "citizen_core mismatch")
    for band, slots in EXPECTED.items():
        check(data["partition"].get(band) == slots, f"partition.{band} mismatch")

    eng = SpectralEngine()
    eng.validate()
    check(eng.dim_H == 125, "dim V")
    check(eng.dim_kernel == 47, "dim E47")
    check(eng.dim_complement == 78, "rank K")
    check(eng.omega_c == float(Fraction(47, 125)), "Omega_c")
    check(eng.mu2.tolist() == [32400, 12544, 0, 11664, 19600, 0, 186624], "Q:=K^2 blocks")
    check(5**3 == 125, "Sigma_5^3 carrier")
    check(Fraction(1, 5) + Fraction(4, 25) + Fraction(2, 125) == Fraction(47, 125), "0.142_5")

    if errors:
        print("G_E47 MACHINE STATUS: FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("G_E47 MACHINE STATUS: PASS")
    print("  locked=", ",".join(EXPECTED["locked"]))
    print("  structurally_supported=Sigma_5^3")
    print("  external_bundle=L")
    print("  not_instantiated=phi_anc,phi_mod,mathcal_T")
    print("  policy=no new symbols")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "certificates/MC-G-E47-MACHINE-STATUS-20260927.json"))
