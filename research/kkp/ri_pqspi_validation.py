"""Canonical entrypoint for the user-supplied RI/PQSPI numerical validation sequence.

Implementation lives in src/coherence_runtime/ri_pqspi.py so the same code used
by the governance runtime is the code referenced by the research corpus.
"""
from dataclasses import asdict
import json
from coherence_runtime.ri_pqspi import *  # noqa: F401,F403

if __name__ == "__main__":
    print(json.dumps(asdict(run_validation()), indent=2, sort_keys=True))
