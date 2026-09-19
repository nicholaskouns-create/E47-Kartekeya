#!/usr/bin/env python3
"""Validate the repository's descriptive research-lab contract."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "lab-manifest.json"

ALLOWED_MATURITY = {"validated-core", "research", "experimental", "prototype", "archived"}
ALLOWED_EVIDENCE = {"E0", "E1", "E2", "E3", "E4", "H0"}


def fail(message: str) -> None:
    raise SystemExit(f"LAB CONTRACT FAIL: {message}")


def main() -> None:
    if not MANIFEST.is_file():
        fail("lab-manifest.json is missing")

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if data.get("schema") != "E47-LAB-MANIFEST-1.0":
        fail("unexpected manifest schema")

    if data.get("canonical_web_root") != "website/":
        fail("website/ must remain the canonical public web root")

    if data.get("package_root") != "src/":
        fail("src/ must remain the package root")

    website = ROOT / "website"
    if not (website / "index.html").is_file():
        fail("canonical website/index.html is missing")

    for required in [
        "README.md",
        "CONTRIBUTING.md",
        "CITATION.cff",
        "docs/lab_architecture.md",
        "docs/reproducibility.md",
        "docs/validation_scope.md",
        "research/README.md",
        "research/e47/README.md",
    ]:
        if not (ROOT / required).exists():
            fail(f"research envelope file is missing: {required}")

    # web/ is a shared runtime library, not a competing deployable homepage.
    if (ROOT / "web" / "index.html").exists():
        fail("web/index.html would create an ambiguous second public web root")

    component_ids: set[str] = set()
    components = data.get("components")
    if not isinstance(components, list) or not components:
        fail("manifest must declare at least one component")

    for component in components:
        cid = component.get("id")
        path = component.get("path")
        maturity = component.get("maturity")
        evidence = component.get("evidence")
        contract = component.get("contract")

        if not isinstance(cid, str) or not cid:
            fail("component id is missing")
        if cid in component_ids:
            fail(f"duplicate component id: {cid}")
        component_ids.add(cid)

        if not isinstance(path, str) or not path:
            fail(f"{cid}: path is missing")
        if not (ROOT / path).exists():
            fail(f"{cid}: declared path does not exist: {path}")

        if maturity not in ALLOWED_MATURITY:
            fail(f"{cid}: unsupported maturity state: {maturity}")

        if not isinstance(evidence, list) or not evidence:
            fail(f"{cid}: evidence classes are missing")
        unknown = set(evidence) - ALLOWED_EVIDENCE
        if unknown:
            fail(f"{cid}: unknown evidence classes: {sorted(unknown)}")

        if not isinstance(contract, str) or len(contract.strip()) < 12:
            fail(f"{cid}: component contract is too weak or missing")

    if "e47-core" not in component_ids:
        fail("canonical e47-core component is not declared")

    print(
        "LAB CONTRACT PASS: "
        f"{len(components)} components; canonical web root=website/; "
        "maturity/evidence/path checks valid."
    )


if __name__ == "__main__":
    main()
