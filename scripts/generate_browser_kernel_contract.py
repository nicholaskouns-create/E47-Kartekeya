#!/usr/bin/env python3
"""Emit the browser-facing canonical E47 kernel contract from src/e47."""

from __future__ import annotations

import json
from pathlib import Path

from e47.spectral_compilation import compile_spectral_kernel, parse_spin

OUTPUT = Path("website/data/e47-canonical-kernel.json")


def main() -> int:
    c = compile_spectral_kernel(
        parse_spin("2"),
        3,
        [parse_spin("2"), parse_spin("5")],
        build_matrix_witness=False,
    )
    payload = {
        "schema": "E47-CANONICAL-KERNEL-1.0",
        "authority": "src/e47/spectral_compilation.py",
        "kernel_source": "src/e47/su2_kernel.py",
        "canonical": {
            "spin": 2,
            "copies": 3,
            "selected_spins": [2, 5],
            "casimir_roots": [int(x) for x in c.kernel_roots],
            "carrier_dimension": c.carrier_dimension,
            "kernel_dimension": c.selected_dimension,
            "coherence_fraction": f"{c.coherence_fraction.numerator}/{c.coherence_fraction.denominator}",
            "kernel_polynomial": [int(x) for x in c.kernel_polynomial_coefficients],
            "q_gap": int(c.spectral_gap),
            "q_max": int(c.maximum_q_eigenvalue),
            "epsilon_max": f"{c.epsilon_max.numerator}/{c.epsilon_max.denominator}",
            "epsilon_star": f"{c.optimal_epsilon.numerator}/{c.optimal_epsilon.denominator}",
            "rho_star": f"{c.optimal_rate.numerator}/{c.optimal_rate.denominator}",
        },
        "evidence": "E0/E1",
        "scope": "Finite-dimensional canonical E47 kernel contract. Browser runtimes consume this object; it does not promote simulation outputs to physical evidence.",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
