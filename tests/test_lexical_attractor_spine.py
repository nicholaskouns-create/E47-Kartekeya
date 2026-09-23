from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
LEX = REPO / "research" / "e47-lexical-attractor-20260923"
VAL = REPO / "research" / "e47" / "validation"
EID = REPO / "src" / "eidolon"
for p in (LEX, VAL, EID, REPO / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from e47.lexical_spine import canonical_lambda_matrix  # noqa: E402
from lexical_attractor import LexicalAttractor  # noqa: E402
import eidolon_engine  # noqa: E402
import tomographic_visualizer  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "e47_lexical_spine_checksum", LEX / "spine_checksum.py"
)
assert spec and spec.loader
checksum = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checksum
spec.loader.exec_module(checksum)


def test_lexical_spine_checksum_full_contract():
    parsed = LexicalAttractor().parse("Σ, K, Ψ, Γ, Λ, Ω, I, M, Σ′")
    assert len(parsed["terms"]) == 9
    assert LexicalAttractor().manifest()["schema"] == "E47-LEXICAL-ATTRACTOR-1.0"

    Lambda = canonical_lambda_matrix()
    assert tomographic_visualizer.lambda_p47_matrix() is Lambda
    assert eidolon_engine.lambda_p47_matrix() is Lambda

    receipt, _ = checksum.run_checksum()
    assert receipt["status"] == "PASS"
    assert receipt["operators"]["carrier_dimension"] == 125
    assert receipt["operators"]["kernel_dimension"] == 47
    assert receipt["operators"]["lambda_roles_share_object"] is True
    assert receipt["recursion"]["machine_zero"] is True
    assert receipt["qutip"]["status"] == "PASS"
    assert receipt["next_state"]["record"]["Σ′"] == receipt["next_state"]["record"]["Σ_next"]
    assert receipt["term_table_mutated"] is False
