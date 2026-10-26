"""Resolve where generated certificates and reports are written.

The default is OUTSIDE the repository. A validation run must never overwrite
the committed evidence it is being checked against, and it must never leave
the working tree dirty.

Precedence, highest first:

  1. ``--out FILE``        explicit file path
  2. ``--out-dir DIR``     directory; the caller's filename is appended
  3. ``E47_CERT_OUT``      explicit file path (what the test suite sets)
  4. ``E47_OUT_DIR``       directory
  5. ``<tempdir>/e47-out`` default, outside the repository

The resolved path is announced on stderr so a run is discoverable without
polluting stdout, which carries the certificate JSON.

To regenerate committed evidence deliberately, name the destination:

    python3 research/e47/validation/e47_condition_lock_certificate.py \\
        --out-dir artifacts
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

DEFAULT_DIR_NAME = "e47-out"

__all__ = ["DEFAULT_DIR_NAME", "default_dir", "resolve_out", "resolve_out_dir"]


def default_dir() -> Path:
    """The out-of-tree directory used when nothing else is specified."""
    return Path(tempfile.gettempdir()) / DEFAULT_DIR_NAME


def _parse(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--out")
    ap.add_argument("--out-dir", dest="out_dir")
    args, _unknown = ap.parse_known_args(argv)
    return args


def resolve_out(
    filename: str,
    *,
    argv: list[str] | None = None,
    announce: bool = True,
) -> Path:
    """Return the path to write ``filename`` to, creating its parent."""
    args = _parse(argv)

    if args.out:
        path = Path(args.out)
    elif args.out_dir:
        path = Path(args.out_dir) / filename
    elif os.environ.get("E47_CERT_OUT"):
        path = Path(os.environ["E47_CERT_OUT"])
    elif os.environ.get("E47_OUT_DIR"):
        path = Path(os.environ["E47_OUT_DIR"]) / filename
    else:
        path = default_dir() / filename

    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    if announce:
        print(f"[e47-out] {path}", file=sys.stderr)

    return path


def resolve_out_dir(
    *,
    argv: list[str] | None = None,
    announce: bool = True,
) -> Path:
    """Return the directory to write into, for callers emitting several files."""
    args = _parse(argv)

    if args.out_dir:
        directory = Path(args.out_dir)
    elif args.out:
        directory = Path(args.out).parent
    elif os.environ.get("E47_OUT_DIR"):
        directory = Path(os.environ["E47_OUT_DIR"])
    elif os.environ.get("E47_CERT_OUT"):
        directory = Path(os.environ["E47_CERT_OUT"]).parent
    else:
        directory = default_dir()

    directory = directory.expanduser()
    directory.mkdir(parents=True, exist_ok=True)

    if announce:
        print(f"[e47-out] {directory}/", file=sys.stderr)

    return directory
