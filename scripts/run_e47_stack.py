#!/usr/bin/env python3
"""Run the wired E47 stack."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "e47"))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--tomo", action="store_true")
    p.add_argument("--eidolon-render", action="store_true")
    args = p.parse_args()
    from runtime import load_stack, smoke
    smoke()
    stack = load_stack()
    if args.eidolon_render:
        from eidolon_engine import Craft, EidolonEngine, _repo_artifacts
        art = _repo_artifacts()
        path = str(art / "Eidolon_Propulsion_Sim_Dashboard.png")
        print("RENDER", EidolonEngine(Craft(mode="translate"), duration=24.0).run().render(path))
    if args.tomo:
        from density_app import DensityApp
        app = DensityApp(n2=65, n3=33, n_iter=4)
        app.run()
        print(app.report())
        print("RENDER", app.render())


if __name__ == "__main__":
    main()
