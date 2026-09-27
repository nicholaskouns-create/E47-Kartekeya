from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "research" / "e47" / "evidence_ledger.json"

spec = importlib.util.spec_from_file_location("check_evidence_ledger", ROOT / "scripts" / "check_evidence_ledger.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def claim(data: dict, cid: str) -> dict:
    return next(c for c in data["claims"] if c["id"] == cid)


def test_committed_ledger_passes():
    assert checker.check(ledger()) == []


def test_unmarked_embedding_is_conditional():
    c = claim(ledger(), "einstein.unmarked_moduli_embedding")
    assert c["conditional_on"] == ["plane-wave-equivalence-group-exhausts-isometries"]


def test_claim_stronger_than_dependency_fails():
    data = copy.deepcopy(ledger())
    claim(data, "census.decomposition")["evidence"] = "E1"
    errors = checker.check(data)
    assert any("stronger than dependency census.decomposition" in e for e in errors)


def test_dropped_assumption_fails():
    data = copy.deepcopy(ledger())
    del claim(data, "einstein.unmarked_moduli_embedding")["conditional_on"]
    errors = checker.check(data)
    assert any("drops assumption" in e for e in errors)


def test_dropped_empirical_class_fails():
    data = copy.deepcopy(ledger())
    claim(data, "lock.condition_4")["empirical"] = ["E4"]
    errors = checker.check(data)
    assert any("drops empirical class ['E4']" in e for e in errors)


def test_cycle_fails():
    data = copy.deepcopy(ledger())
    claim(data, "census.decomposition")["depends_on"] = ["lock.condition_4"]
    assert checker.check(data) == ["dependency graph has a cycle"]


def test_unknown_dependency_and_assumption_fail():
    data = copy.deepcopy(ledger())
    claim(data, "profile.vacuum")["depends_on"] = ["no.such.claim"]
    claim(data, "profile.parity_obstruction")["conditional_on"] = ["undeclared"]
    errors = checker.check(data)
    assert any("unknown dependency no.such.claim" in e for e in errors)
    assert any("undeclared assumption undeclared" in e for e in errors)


def test_false_or_missing_check_fails():
    data = copy.deepcopy(ledger())
    claim(data, "profile.vacuum")["check"] = "no_such_check"
    errors = checker.check(data)
    assert any("check no_such_check is not true" in e for e in errors)
