"""Wire-level lock for the E47 stack."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "e47"))


def test_stack_loads():
    from runtime import load_stack
    stack = load_stack()
    assert stack["dim_e47"] == 47
    assert abs(stack["omega_c"] - 0.376) < 1e-12
    assert stack["n_units"] == 29
    eng = stack["eidolon"](stack["craft"](mode="acquire"), dt=1.0, duration=2.0).run()
    assert len(eng.history) > 0
    assert 0.0 <= eng.lock() <= 1.0


if __name__ == "__main__":
    test_stack_loads()
    print("test_e47_stack PASS")
