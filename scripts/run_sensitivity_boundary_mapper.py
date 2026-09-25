#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "research" / "e47" / "validation" / "sensitivity_boundary_mapper.py"
sys.path.insert(0, str(MOD.parent))
runpy.run_path(str(MOD), run_name="__main__")
