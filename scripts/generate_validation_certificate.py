#!/usr/bin/env python3
"""Generate the canonical E47 validation certificate.

This script orchestrates all five validation layers, aggregates results,
and writes a JSON certificate to disk with reproducible formatting.

Exit codes:
    0 - Certificate generated and validation passed
    1 - Certificate generated but validation failed (with --allow-invalid)
    2 - Validation failed and --allow-invalid not set
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from e47.serialization import write_validation_certificate
from e47.validation_results import (
    require_all_validations,
    run_all_validations,
)


DEFAULT_OUTPUT = Path("artifacts/e47_validation_certificate.json")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate the canonical E47 validation certificate.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Exit codes:
  0 - Certificate generated and all validations passed
  1 - Certificate generated but validation failed (only with --allow-invalid)
  2 - Validation failed and certificate not written
""",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Destination JSON path (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--allow-invalid",
        action="store_true",
        help="Write the certificate even when validation fails.",
    )
    return parser.parse_args()


def main() -> int:
    """Execute the certificate generation workflow.

    Returns
    -------
    int
        Exit code: 0 for valid, 1 for invalid with --allow-invalid, 2 for failure.
    """
    args = parse_args()

    try:
        results = run_all_validations()
    except Exception as exc:
        print(f"FATAL: Validation orchestration failed: {exc}", file=sys.stderr)
        return 2

    if not results.valid and not args.allow_invalid:
        print(
            "VALIDATION FAILED: Certificate not written.",
            file=sys.stderr,
        )
        print(
            "Use --allow-invalid to write an invalid certificate.",
            file=sys.stderr,
        )
        return 2

    try:
        destination = write_validation_certificate(results, args.output)
    except Exception as exc:
        print(f"FATAL: Failed to write certificate: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote E47 validation certificate to {destination}")
    print(f"Overall status: {'✓ PASS' if results.valid else '✗ FAIL'}")

    return 0 if results.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
