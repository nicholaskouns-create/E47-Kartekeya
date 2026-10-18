#!/usr/bin/env python3
"""Run every E47 validator and report PASS/FAIL with no human judgment in the loop.

Validators come from two places in config/validators.json:
  * "discover": glob patterns. Every matching .py file runs with defaults, so a new
    validator is covered the moment it lands in one of those folders.
  * "validators": explicit entries that add args, a timeout, or a flag:
      - "known_failing": "<reason>"  runs, but a failure is reported as KNOWN-FAIL
        (visible, not fatal). If it starts passing it is reported as XPASS so the
        flag can be removed.
      - "needs_network": true        only runs with --allow-network; otherwise it is
        listed as NOT-RUN (network) - never dropped silently.
  * "exclude": [{"path", "reason"}] listed as EXCLUDED with the reason.

A validator passes when it exits 0 within its timeout. Exit status of this script is
nonzero if any validator FAILs, TIMEs OUT, or a manifest entry points at a missing file.

Usage:
  python scripts/run_all_validators.py [--allow-network] [--jobs N] [--only SUBSTR]
                                       [--log-dir DIR] [--json FILE]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import glob
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "config" / "validators.json"
TAIL_CHARS = 3000

# Single-threaded BLAS: with several validators in parallel, multi-threaded BLAS
# oversubscribes the CPU and can turn a 1 s script into a 10 min timeout.
BASE_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "MPLBACKEND": "Agg",
    "PYTHONHASHSEED": "0",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONUNBUFFERED": "1",
}


def load_entries(manifest: dict) -> list[dict]:
    default_timeout = int(manifest.get("default_timeout", 300))
    explicit = []
    for raw in manifest.get("validators", []):
        e = dict(raw)
        e.setdefault("id", e["path"])
        e.setdefault("args", [])
        e.setdefault("timeout", default_timeout)
        e["source"] = "manifest"
        explicit.append(e)
    claimed = {e["path"] for e in explicit}
    excluded = {x["path"]: x.get("reason", "no reason given") for x in manifest.get("exclude", [])}

    discovered = []
    for pattern in manifest.get("discover", []):
        for p in sorted(glob.glob(str(ROOT / pattern))):
            rel = Path(p).relative_to(ROOT).as_posix()
            if Path(p).name == "__init__.py" or rel in claimed:
                continue
            claimed.add(rel)
            discovered.append({"id": rel, "path": rel, "args": [], "timeout": default_timeout,
                               "source": "discovered"})

    entries = discovered + explicit
    for path, reason in excluded.items():
        entries = [e for e in entries if e["path"] != path]
        entries.append({"id": path, "path": path, "excluded": reason, "source": "exclude"})
    return sorted(entries, key=lambda e: e["id"])


def run_one(e: dict, allow_network: bool, log_dir: Path | None) -> dict:
    r = {"id": e["id"], "path": e["path"], "known_failing": e.get("known_failing"),
         "seconds": 0.0, "returncode": None, "tail": ""}
    if "excluded" in e:
        return {**r, "status": "EXCLUDED", "note": e["excluded"]}
    if not (ROOT / e["path"]).is_file():
        return {**r, "status": "MISSING", "note": "manifest entry points at a file that does not exist"}
    if e.get("needs_network") and not allow_network:
        return {**r, "status": "NOT-RUN", "note": "needs network; runs on nightly/manual sweeps (--allow-network)"}

    with tempfile.TemporaryDirectory(prefix="e47v-") as tmp:
        args = [a.replace("{tmp}", tmp) for a in e.get("args", [])]
        env = {**os.environ, **BASE_ENV, "E47_VALIDATOR_TMP": tmp}
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(ROOT / "src"), env.get("PYTHONPATH")]))
        t0 = time.monotonic()
        try:
            p = subprocess.run([sys.executable, e["path"], *args], cwd=ROOT, env=env,
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, timeout=e["timeout"])
            out, rc, timed_out = p.stdout.decode("utf-8", "replace"), p.returncode, False
        except subprocess.TimeoutExpired as ex:
            out = (ex.stdout or b"").decode("utf-8", "replace") if isinstance(ex.stdout, bytes) else (ex.stdout or "")
            rc, timed_out = None, True
        r["seconds"] = round(time.monotonic() - t0, 2)

    r["returncode"] = rc
    r["tail"] = out[-TAIL_CHARS:]
    if log_dir:
        (log_dir / (e["id"].replace("/", "__").replace(" ", "_") + ".log")).write_text(out, encoding="utf-8")
    ok = rc == 0 and not timed_out
    if e.get("known_failing"):
        r["status"] = "XPASS" if ok else "KNOWN-FAIL"
        r["note"] = e["known_failing"] if not ok else "passes now - remove its known_failing flag"
    elif timed_out:
        r["status"], r["note"] = "TIMEOUT", f"exceeded {e['timeout']} s"
    else:
        r["status"] = "PASS" if ok else "FAIL"
        r["note"] = "" if ok else f"exit code {rc}"
    return r


ICON = {"PASS": "✅", "FAIL": "❌", "TIMEOUT": "⏱️", "MISSING": "❓", "KNOWN-FAIL": "🟠",
        "XPASS": "🟡", "NOT-RUN": "🌐", "EXCLUDED": "⚪"}
FATAL = {"FAIL", "TIMEOUT", "MISSING"}


def summary_markdown(results: list[dict], elapsed: float) -> str:
    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    fatal = [r for r in results if r["status"] in FATAL]
    head = "❌ FAIL" if fatal else "✅ PASS"
    lines = [f"## E47 validators: {head}", "",
             " · ".join(f"{ICON[k]} {k} {v}" for k, v in sorted(counts.items())) + f" · {elapsed:.0f} s total", "",
             "| | Validator | Status | Time (s) | Note |", "|---|---|---|---:|---|"]
    order = {s: i for i, s in enumerate(["FAIL", "TIMEOUT", "MISSING", "XPASS", "KNOWN-FAIL", "NOT-RUN", "EXCLUDED", "PASS"])}
    for r in sorted(results, key=lambda r: (order[r["status"]], r["id"])):
        note = (r.get("note") or "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {ICON[r['status']]} | `{r['id']}` | {r['status']} | {r['seconds']:.1f} | {note} |")
    for r in results:
        if r["status"] in FATAL | {"KNOWN-FAIL"} and r["tail"]:
            tail = r["tail"][-1500:].replace("```", "'''")
            lines += ["", f"<details><summary>{r['status']}: <code>{r['id']}</code> output tail</summary>", "",
                      "```", tail, "```", "</details>"]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--allow-network", action="store_true", help="also run needs_network validators")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--only", help="run only validators whose id contains this substring")
    ap.add_argument("--log-dir", help="write each validator's full output here")
    ap.add_argument("--json", help="write a machine-readable receipt here")
    a = ap.parse_args()

    entries = load_entries(json.loads(Path(a.manifest).read_text(encoding="utf-8")))
    if a.only:
        entries = [e for e in entries if a.only in e["id"]]
    log_dir = Path(a.log_dir) if a.log_dir else None
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.monotonic()
    results = []
    with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        futs = {pool.submit(run_one, e, a.allow_network, log_dir): e for e in entries}
        for f in cf.as_completed(futs):
            r = f.result()
            results.append(r)
            print(f"{ICON[r['status']]} {r['status']:<10} {r['seconds']:>7.1f}s  {r['id']}"
                  + (f"  ({r['note']})" if r.get("note") else ""), flush=True)
    elapsed = time.monotonic() - t0

    md = summary_markdown(results, elapsed)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as fh:
            fh.write(md)
    if os.environ.get("GITHUB_ACTIONS"):
        for r in results:
            if r["status"] in FATAL:
                print(f"::error file={r['path']},title=Validator {r['status']}::{r['id']}: {r.get('note', '')}")
            elif r["status"] == "XPASS":
                print(f"::warning file={r['path']},title=Known-failing validator now passes::{r['id']}")
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps({"schema": "E47-VALIDATOR-RUN/1.0", "elapsed_seconds": round(elapsed, 2),
                                            "python": sys.version.split()[0], "results": sorted(results, key=lambda r: r["id"])},
                                           indent=2), encoding="utf-8")
    fatal = [r for r in results if r["status"] in FATAL]
    print(f"\n{len(results)} validators: {len(fatal)} unexpected failure(s).")
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
