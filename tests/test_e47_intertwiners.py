"""Lock the 29-dimensional SU(2) intertwiner units on E47."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "e47"))
sys.path.insert(0, str(ROOT / "research" / "e47" / "validation"))

from intertwiners import DIM_E47, DIM_REG, N_UNITS, lock, unit_names


def test_unit_count_and_names():
    names = unit_names()
    assert N_UNITS == 29
    assert len(names) == 29
    assert names[0] == "E2[0,0]"
    assert names[24] == "E2[4,4]"
    assert names[25] == "E5[0,0]"
    assert names[-1] == "E5[1,1]"


def test_register_and_lift_lock():
    reg, lift = lock()
    assert DIM_REG == 7
    assert DIM_E47 == 47
    for cert in (reg, lift):
        assert cert.n_units == 29
        assert cert.dim_algebra == 29
        assert cert.product_ok
        assert cert.trace_ok
        assert cert.commute_blocks_ok
        assert cert.completeness_ok
    assert reg.lift_traces == (1, 1)
    assert lift.lift_traces == (5, 11)


if __name__ == "__main__":
    test_unit_count_and_names()
    test_register_and_lift_lock()
    print("test_e47_intertwiners PASS")
