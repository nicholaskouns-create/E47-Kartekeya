#!/usr/bin/env python3
"""E47 spacetime execution plate.

Source mirror for the 2026-09-22 executable. This module keeps the runtime
entrypoint discoverable in the repository while the full uploaded execution
source is mirrored in Google Drive and indexed in the Mathematical City corpus.
"""

from pathlib import Path

FULL_SOURCE_DRIVE_ID = "1B6HvDiP9qTAWm6laeresnLEsqFpmDEaX"
CHAIN_SOURCE = Path(__file__).with_name("e47_spacetime_chain.py")

def main() -> None:
    namespace = {"__name__": "__main__"}
    exec(CHAIN_SOURCE.read_text(), namespace)

if __name__ == "__main__":
    main()
