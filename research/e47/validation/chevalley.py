#!/usr/bin/env python3
"""Chevalley relations for sl(5) ⊕ sl(2) in the E47 intertwiner units."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from intertwiners import register_units  # noqa: E402

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "e47_chevalley_src",
    HERE.parents[2] / "src" / "e47" / "chevalley.py",
)
# Prefer the sibling copy of the verifier living next to this file after the
# package module is imported via path below.
sys.path.insert(0, str(HERE.parents[2] / "src" / "e47"))
from chevalley import verify  # noqa: E402

if __name__ == "__main__":
    verify()
