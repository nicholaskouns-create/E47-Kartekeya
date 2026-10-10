#!/usr/bin/env python3
"""Regenerate an EIDOLON E2 flight-replay NDJSON from its certificate.

Re-runs EidolonEngine under the certificate's craft configuration and the
lock-cap rule in force when the certificate was issued, writes one canonical
record per line, and keeps the file only if it passes the certificate
bind-check (canonical_sha256 and merkle_root). Evidence class stays E2.

Needs the package installed: pip install -e .
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "check_eidolon_replay_ndjson", ROOT / "scripts" / "check_eidolon_replay_ndjson.py"
)
checker = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(checker)


def _eidolon():
    try:
        import eidolon
    except ImportError:
        checker.die("the eidolon package is not importable; run `pip install -e .` first")
    return eidolon


def replay_engine(cert: dict):
    """Run the engine as configured by the certificate's craft block."""
    eidolon = _eidolon()
    craft = cert["craft"]
    # Certificates issued before the cap rule was recorded used the legacy rule.
    config = eidolon.Craft(
        mass_kg=craft["mass_kg"],
        lock_target=craft["lock_target"],
        gain=craft["scalar_amp"],
        mode=craft["engine_mode"],
        scale=craft["scale"],
        seed=craft["seed"],
        lock_cap=craft.get("lock_cap", "legacy"),
    )
    return eidolon.EidolonEngine(config, dt=craft["dt"], duration=craft["duration_s"]).run()


def replay_records(cert: dict) -> list[dict]:
    """One record per engine sample, in the certificate's channels and rounding."""
    omega_c = _eidolon().OMEGA_C
    craft = cert["craft"]
    records = []
    for sample in replay_engine(cert).history:
        envelope = min(max(craft["scalar_amp"] * sample.L / omega_c, 0.0), 3.0)
        records.append(
            {
                "t": round(sample.t, 6),
                "W": round(envelope, 9),
                "L": round(sample.L, 9),
                "m_eff": round(sample.m_eff, 9),
                "mode": craft["engine_mode"],
                "lab_mode": craft["lab_mode"],
            }
        )
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--cert",
        default=ROOT / "artifacts" / "CITY-EIDOLON-FLIGHT-REPLAY-001.json",
        type=Path,
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="output path (default: the certificate's trajectory.uri under the repository root)",
    )
    args = parser.parse_args(argv)
    cert = checker.load_cert(args.cert)
    out = args.out or ROOT / cert["trajectory"]["uri"]

    text = "".join(checker.canonical(record) + "\n" for record in replay_records(cert))
    out.parent.mkdir(parents=True, exist_ok=True)
    draft = out.with_name(out.name + ".tmp")
    draft.write_text(text, encoding="utf-8", newline="\n")
    try:
        report = checker.check_ndjson(draft, cert)
    except SystemExit:
        draft.unlink()
        raise
    draft.replace(out)

    print("REGENERATED")
    print(f"  file             {out}")
    print(f"  n_samples        {report['n_samples']}")
    print(f"  canonical_sha256 {report['canonical_sha256']}")
    print(f"  merkle_root      {report['merkle_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
