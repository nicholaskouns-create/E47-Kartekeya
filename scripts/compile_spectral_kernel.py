#!/usr/bin/env python3
"""Compile certified SU(2) spectral kernels and emit certificate artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from e47.spectral_compilation import (
    compile_spectral_kernel,
    parse_spin,
    write_spectral_compilation,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(
        description="Compile certified SU(2) spectral kernels."
    )
    parser.add_argument(
        "--spin",
        default="2",
        help="Single-factor spin, e.g. 2 or 3/2.",
    )
    parser.add_argument("--copies", type=int, default=3)
    parser.add_argument(
        "--select",
        nargs="+",
        default=["2", "5"],
        help="Selected total-spin sectors.",
    )
    parser.add_argument(
        "--certificate",
        type=Path,
        default=Path("artifacts/spectral_kernel_certificate.json"),
    )
    parser.add_argument(
        "--passport",
        type=Path,
        default=Path("artifacts/spectral_kernel_passport.md"),
    )
    parser.add_argument("--no-matrix-witness", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Execute the spectral compilation workflow."""

    args = parse_args(argv)
    compilation = compile_spectral_kernel(
        parse_spin(args.spin),
        args.copies,
        [parse_spin(value) for value in args.select],
        build_matrix_witness=not args.no_matrix_witness,
    )
    certificate, passport = write_spectral_compilation(
        compilation,
        args.certificate,
        args.passport,
    )

    print(json.dumps(compilation.to_json_dict(), indent=2))
    print(f"\nCertificate: {certificate}")
    print(f"Passport: {passport}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
