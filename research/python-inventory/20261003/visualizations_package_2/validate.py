#!/usr/bin/env python3
"""Invariant evals for algebraic-visualizations. Exit 0 iff all pass."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from algebra import (  # noqa: E402
    OMEGA,
    OMEGA_DEN,
    OMEGA_NUM,
    compute_operator,
    cube_cells,
    diagonal_sector,
    kernel_sector,
    shifted_product,
)


def check(name: str, pass_: bool, detail: str) -> dict:
    return {"name": name, "pass": bool(pass_), "detail": detail}


def run() -> list[dict]:
    cells = cube_cells(5)
    ker = kernel_sector(cells, 47)
    diag = diagonal_sector(cells)
    locked = compute_operator(5, "cycle", lock=True, eig_index1=0, eig_index2=1)
    unlocked = compute_operator(
        5, "cycle", lock=False, lam1_input=6.0, lam2_input=30.0
    )
    C = locked["C"]
    K_named = shifted_product(C, 6.0, 30.0)
    sym = all(
        abs(K_named[i][j] - K_named[j][i]) < 1e-10
        for i in range(5)
        for j in range(5)
    )

    return [
        check(
            "Ω_c = 47/125",
            OMEGA_NUM == 47 and OMEGA_DEN == 125 and abs(OMEGA - 47 / 125) < 1e-15,
            f"{OMEGA_NUM}/{OMEGA_DEN} = {OMEGA}",
        ),
        check("ambient 125 = 5³", len(cells) == 125, f"{len(cells)} cells"),
        check(
            "invariant sector 47",
            len(ker) == 47,
            f"{len(ker)} cells by |φ| rank",
        ),
        check(
            "residual 5 (space diagonal)",
            len(diag) == 5,
            f"{len(diag)} cells i = j = k",
        ),
        check(
            "lock-to-spectrum kernel",
            locked["dimKer"] > 0 and locked["dimKer"] <= 5,
            f"cycle n=5  dim ker K = {locked['dimKer']}",
        ),
        check(
            "named shifts stay honest",
            unlocked["dimKer"] <= 5,
            f"K=(C−6I)(C−30I)  dim ker = {unlocked['dimKer']} ≤ n",
        ),
        check("K symmetric when C is", sym, "K_ij = K_ji"),
        check(
            "5×5 cannot hold E47",
            locked["dimKer"] <= locked["n"],
            f"dim ker {locked['dimKer']} ≤ n {locked['n']}",
        ),
        check(
            "kernel residual small when dim ker > 0",
            locked["residual"] is not None and locked["residual"] < 1e-6,
            f"‖Kv‖/‖v‖ = {locked['residual']}",
        ),
    ]


def main() -> int:
    results = run()
    failed = [r for r in results if not r["pass"]]
    print(json.dumps({"passed": len(results) - len(failed), "total": len(results), "results": results}, indent=2))
    if failed:
        print(f"\nFAILED {len(failed)}/{len(results)}", file=sys.stderr)
        return 1
    print(f"\nOK {len(results)}/{len(results)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
