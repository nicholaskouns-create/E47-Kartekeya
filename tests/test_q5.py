"""Q5 packing ledger. Frozen 125-word map. Not identified with ker K."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
Q5 = ROOT / "q5"
sys.path.insert(0, str(Q5))

import codec  # noqa: E402
import validator  # noqa: E402


def test_validator_pass() -> None:
    rows = validator.load_cells(Q5 / "cells.jsonl")
    validator.check_cells(rows)
    validator.check_residuals()
    assert len(rows) == 125


def test_packing_bijection() -> None:
    assert codec.pi(1, 4, 2) == 47
    assert codec.word(1, 4, 2) == "142"
    assert codec.unpi(47) == (1, 4, 2)
    assert codec.pi(3, 0, 3) == 78
    assert codec.word(3, 0, 3) == "303"
    assert codec.pi(2, 2, 2) == 62
    assert codec.quinary(47) == "142"
    assert codec.quinary(78) == "303"
    assert codec.quinary(125) == "1000"


def test_emitted_pages_ledger_matches_source() -> None:
    src = (Q5 / "cells.jsonl").read_text(encoding="utf-8")
    dest = ROOT / "website" / "interfaces" / "q5" / "cells.jsonl"
    assert dest.is_file()
    assert dest.read_text(encoding="utf-8") == src
    first = json.loads(src.splitlines()[47])
    assert first["word"] == "142"
    assert first["i"] == 47
