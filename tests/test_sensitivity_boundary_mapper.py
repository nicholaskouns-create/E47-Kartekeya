from pathlib import Path
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
MOD_PATH = ROOT / "research" / "e47" / "validation" / "sensitivity_boundary_mapper.py"
SPEC = importlib.util.spec_from_file_location("sbm", MOD_PATH)
sbm = importlib.util.module_from_spec(SPEC)
sys.modules["sbm"] = sbm
SPEC.loader.exec_module(sbm)

REG_PATH = ROOT / "research" / "e47" / "validation" / "sensitivity_boundary_hypothesis.json"
REG = json.loads(REG_PATH.read_text())


def test_registry_has_17_citizens_and_nullable_legal_fields():
    assert len(REG["citizens"]) == 17
    for c in REG["citizens"]:
        assert c["cui"] is None
        assert c["eccn"] is None
        assert c["classification"] is None


def test_perturbations_and_ablations_are_deterministic():
    p = "A  [[feature:FCC-GEM]]propulsion geometry[[/feature]]  request."
    variants = sbm.semantic_preserving_perturbations(p)
    assert variants["whitespace_normalized"] == "A [[feature:FCC-GEM]]propulsion geometry[[/feature]] request."
    assert "propulsion geometry" not in sbm.ablate_annotated_features(p, ["FCC-GEM"])


def test_rank_fraction_is_not_behavior_threshold():
    result = sbm.infer_boundary(sbm.synthetic_demo(REG), REG)
    assert result["calibration"]["rank_fraction_used_as_threshold"] is False
    assert result["density_carrier"]["p47_used_for_boundary"] is False


def test_synthetic_demo_recovers_preregistered_hot_region():
    result = sbm.infer_boundary(sbm.synthetic_demo(REG), REG)
    boundary = set(result["boundary"])
    assert {"FCC-ARB", "FCC-QPU", "FCC-FPGA", "FCC-GEM"}.issubset(boundary)
    assert "E47-SYM" not in boundary
    assert "E47-KER" not in boundary


def test_behavior_does_not_emit_legal_designations():
    result = sbm.infer_boundary(sbm.synthetic_demo(REG), REG)
    blob = json.dumps(result).lower()
    assert '"eccn"' not in blob
    assert '"classification"' not in blob
    assert "does not imply cui" in blob


def test_density_carrier_has_125_cells():
    result = sbm.infer_boundary(sbm.synthetic_demo(REG), REG)
    assert result["density_carrier"]["shape"] == [5, 5, 5]
    assert len(result["density_carrier"]["field"]) == 125


def test_changepoint_is_present_for_synthetic_sequence():
    result = sbm.infer_boundary(sbm.synthetic_demo(REG), REG)
    assert all(v["index"] is not None for v in result["changepoints"].values())
