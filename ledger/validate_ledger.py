#!/usr/bin/env python3
"""Validator for the KKP-E47 failure ledger. Standard library only.
Run: python3 -I validate_ledger.py [FAILURE_LEDGER.json]   Exits non-zero on any violation."""
import json, sys, re
from collections import Counter

path = sys.argv[1] if len(sys.argv) > 1 else "FAILURE_LEDGER.json"
d = json.load(open(path))
errs = []

STATES, TYPES = set(d["states"]), set(d["types"])
seen = set()

for e in d["entries"]:
    i = e.get("id", "<no id>")
    if not re.fullmatch(r"F-\d{3}", i):          errs.append(f"{i}: malformed id")
    if i in seen:                                 errs.append(f"{i}: duplicate id")
    seen.add(i)
    for k in ("claim", "state", "type", "found_by"):
        if not e.get(k):                          errs.append(f"{i}: missing '{k}'")
    if e.get("state") not in STATES:              errs.append(f"{i}: unknown state {e.get('state')!r}")
    if e.get("type")  not in TYPES:               errs.append(f"{i}: unknown type {e.get('type')!r}")
    if e.get("found_by") not in {"author","collaborator","both"}:
                                                  errs.append(f"{i}: found_by must be author/collaborator/both")
    # a CORRECTED or SUPERSEDED entry must say what replaced it
    if e.get("state") in {"CORRECTED","SUPERSEDED"} and not e.get("correction"):
        errs.append(f"{i}: {e['state']} requires a 'correction' field")
    # a FALSIFIED entry must say how it was tested
    if e.get("state") == "FALSIFIED" and not (e.get("method") or e.get("note")):
        errs.append(f"{i}: FALSIFIED requires 'method' or 'note' recording the test")
    # a BLOCKED entry must say what blocks it
    if e.get("state") == "BLOCKED" and not e.get("note"):
        errs.append(f"{i}: BLOCKED requires a 'note' naming the obstruction")

for s in d["standing"]:
    if s.get("type") not in TYPES:                errs.append(f"{s.get('id')}: unknown type")

print(f"ledger  : {path}")
print(f"entries : {len(d['entries'])}   standing: {len(d['standing'])}")
print(f"states  : {dict(Counter(e['state'] for e in d['entries']))}")
print(f"types   : {dict(Counter(e['type'] for e in d['entries']))}")
print(f"found by: {dict(Counter(e['found_by'] for e in d['entries']))}")
if errs:
    print("\nFAIL"); [print("  -", x) for x in errs]; sys.exit(1)
print("\nPASS  every entry typed, every correction carries its replacement,")
print("      every falsification carries its test, every block names its obstruction.")
