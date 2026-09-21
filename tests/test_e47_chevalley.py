"""Chevalley lock for sl(5) ⊕ sl(2) on the E47 intertwiner units."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "e47"))

from chevalley import FAIL, PASS, verify  # noqa: E402


def test_chevalley_relations():
    PASS.clear()
    FAIL.clear()
    verify()
    assert not FAIL
    assert len(PASS) == 16


if __name__ == "__main__":
    test_chevalley_relations()
    print("test_e47_chevalley PASS")
