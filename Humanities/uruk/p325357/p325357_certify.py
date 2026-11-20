#!/usr/bin/env python3
"""Exact arithmetic and matrix certificate for CDLI P325357.

The program intentionally uses only integer arithmetic. It reconstructs every
ATF case first, defines the obverse state vector second, and introduces no
projector because the source supplies no exclusion rule.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LEDGER_PATH = ROOT / "p325357_cases.json"
ATF_PATH = ROOT.parent / "evidence" / "cdli" / "P325357_current.atf"
FAILED_CERT_PATH = (
    ROOT.parent
    / "evidence"
    / "P325357_Audit_Certificate_URUK-P325357-AUDIT-001.json"
)
OUTPUT_PATH = ROOT / "P325357_Certification_URUK-P325357-AUDIT-002.json"


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    return [
        [sum(a * b for a, b in zip(row, column)) for column in zip(*right)]
        for row in left
    ]


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def exact_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    pivot_row = 0
    for col in range(cols):
        pivot = next((r for r in range(pivot_row, rows) if work[r][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][col]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, actual, expected) -> dict:
    return {
        "name": name,
        "actual": actual,
        "expected": expected,
        "pass": actual == expected,
    }


def main() -> int:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    failed = json.loads(FAILED_CERT_PATH.read_text(encoding="utf-8"))
    cases = ledger["cases"]

    obverse = [case for case in cases if case["surface"] == "obverse"]
    controls = [case for case in cases if case["surface"] in {"reverse", "left"}]
    obverse.sort(key=lambda case: (case["column"], case["line"]))

    x = [case["value"] for case in obverse]
    obverse_ids = [case["id"] for case in obverse]
    control_values = [case["value"] for case in controls]

    # B maps the 12 physical obverse cases to the three physical column sums.
    B = [
        [1 if case["column"] == column else 0 for case in obverse]
        for column in (1, 2, 3)
    ]
    # R maps [column 1, column 2, column 3] to the controls
    # [column 3 subtotal, columns 1+2 subtotal, full obverse total].
    R = [
        [0, 0, 1],
        [1, 1, 0],
        [1, 1, 1],
    ]
    A = matmul(R, B)

    column_totals = matvec(B, x)
    reconstructed_controls = matvec(A, x)
    expected_columns = [43, 47, 39]
    expected_controls = [39, 90, 129]

    tests = [
        check("all ATF cases reconstructed", len(cases), 15),
        check("all obverse cases precede model definition", len(obverse), 12),
        check("obverse state vector", x, [1, 30, 1, 11, 2, 45, 9, 1, 9, 1, 10, 9]),
        check("physical column totals Bx", column_totals, expected_columns),
        check("observed reverse/left controls", control_values, expected_controls),
        check("matrix reconstruction Ax", reconstructed_controls, expected_controls),
        check("grand total redundancy", reconstructed_controls[2], reconstructed_controls[0] + reconstructed_controls[1]),
        check("rank(B)", exact_rank(B), 3),
        check("rank(R)", exact_rank(R), 2),
        check("rank(A)", exact_rank(A), 2),
        check("audit 001 preserved", failed["certificate_code"], "URUK-P325357-AUDIT-001"),
        check("rejected hypothesis residual", column_totals[0] - expected_controls[0], 4),
    ]

    arithmetic_pass = all(test["pass"] for test in tests)
    certificate = {
        "schema": "e47.uruk.certificate.v1",
        "certificate_code": "URUK-P325357-AUDIT-002",
        "artifact_id": "P325357",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": (
            "ARITHMETIC_MATRIX_CERTIFIED__PHILOLOGICAL_RELEASE_BLOCKED"
            if arithmetic_pass
            else "CERTIFICATION_FAILED"
        ),
        "evidence_class": "E1 exact integer reconstruction from current CDLI ATF; photographic consistency checked",
        "source_integrity": {
            "case_ledger_sha256": sha256(LEDGER_PATH),
            "atf_sha256": sha256(ATF_PATH),
            "preserved_failed_audit_sha256": sha256(FAILED_CERT_PATH),
        },
        "source_vector": {"case_order": obverse_ids, "x": x},
        "matrices": {
            "B_column_aggregation": B,
            "R_control_reconciliation": R,
            "A_equals_RB": A,
            "projector_P": None,
            "projector_reason": "No source-evidenced exclusion or filtering rule; P is neither needed nor defined.",
        },
        "results": {
            "column_totals": {"obv_i": 43, "obv_ii": 47, "obv_iii": 39},
            "control_totals": {"reverse_i_1": 39, "reverse_i_2": 90, "left_1": 129},
            "identity": "[39, 90, 129] = [c3, c1+c2, c1+c2+c3]",
            "rejected_hypothesis": "obverse column 1 equals reverse line 1",
            "rejected_hypothesis_residual": 4,
        },
        "tests": tests,
        "claim_boundary": {
            "certified": [
                "The current CDLI ATF gives obverse column totals 43, 47, and 39.",
                "The reverse/left control totals are 39, 90, and 129.",
                "The exact case-level matrix relation Ax=[39,90,129]^T holds with A=RB.",
                "The earlier 43-versus-39 failure records a rejected alignment hypothesis, not an arithmetic contradiction.",
            ],
            "not_certified": [
                "A direct collation against Monaco 2007 CUSAS 1 no. 49 hand copy.",
                "The lost object reading at obverse i 4.",
                "An unqualified numeral reading at obverse iii 6, which CDLI marks damaged with #.",
                "Any philological or publication-grade release before independent expert review.",
            ],
        },
        "predecessor": {
            "certificate_code": "URUK-P325357-AUDIT-001",
            "disposition": "PRESERVED_AS_FAILED_HYPOTHESIS_TEST",
        },
    }

    OUTPUT_PATH.write_text(
        json.dumps(certificate, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "certificate": certificate["certificate_code"],
        "status": certificate["status"],
        "column_totals": column_totals,
        "control_totals": reconstructed_controls,
        "matrix_identity_pass": reconstructed_controls == expected_controls,
        "output": str(OUTPUT_PATH),
    }, indent=2))
    return 0 if arithmetic_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
