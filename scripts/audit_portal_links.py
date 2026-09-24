#!/usr/bin/env python3
"""
audit_portal_links.py

Audit the live Mathematical City instrument portal against the repository.

Default catalog:
    website/interfaces/instruments/instruments.js

Typical use, from the repository root:
    python scripts/audit_portal_links.py --site-root website
    python scripts/audit_portal_links.py --site-root website --json

External URLs are recorded but not network-checked.

Exit codes:
  0  every internal public route and source path resolves
  1  one or more internal routes/source paths are missing
  2  catalog/site/repository input is malformed or missing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


def _isatty() -> bool:
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


class C:
    _tty = _isatty()
    RESET = "\033[0m" if _tty else ""
    DIM = "\033[2m" if _tty else ""
    BOLD = "\033[1m" if _tty else ""
    CYAN = "\033[36m" if _tty else ""
    BRONZE = "\033[33m" if _tty else ""
    MINT = "\033[32m" if _tty else ""
    RED = "\033[31m" if _tty else ""
    GRAY = "\033[90m" if _tty else ""


CATALOG_START = "const INSTRUMENTS = ["
CATALOG_END_RE = re.compile(r"^\s*\];", re.MULTILINE)


def _field(block: str, key: str) -> str | None:
    match = re.search(
        rf"\b{re.escape(key)}\s*:\s*'((?:\\.|[^'])*)'",
        block,
        re.DOTALL,
    )
    if not match:
        return None
    return match.group(1).replace(r"\'", "'").replace(r"\\", "\\")


def extract_catalog(catalog_path: Path) -> list[dict]:
    text = catalog_path.read_text(encoding="utf-8")
    start = text.find(CATALOG_START)
    if start < 0:
        raise ValueError(f"Could not find {CATALOG_START!r} in {catalog_path}")
    start += len(CATALOG_START)

    end_match = CATALOG_END_RE.search(text, start)
    if not end_match:
        raise ValueError("Unterminated INSTRUMENTS array")

    literal = text[start:end_match.start()]
    blocks = re.findall(r"\{(.*?)\}", literal, re.DOTALL)
    if not blocks:
        raise ValueError("No instrument records found")

    rows: list[dict] = []
    for block in blocks:
        row = {
            "n": _field(block, "n"),
            "name": _field(block, "name"),
            "sector": _field(block, "sector"),
            "evidence": _field(block, "evidence"),
            "open": _field(block, "open"),
            "source": _field(block, "source"),
            "external": bool(re.search(r"\bexternal\s*:\s*true\b", block)),
        }
        required = ("name", "sector", "evidence", "open", "source")
        missing = [k for k in required if not row.get(k)]
        if missing:
            raise ValueError(
                f"Malformed instrument record; missing {', '.join(missing)}: {block[:180]}"
            )
        rows.append(row)
    return rows


def is_external(route: str) -> bool:
    return route.startswith(("http://", "https://", "mailto:", "tel:"))


def strip_query_fragment(route: str) -> str:
    return route.split("?", 1)[0].split("#", 1)[0]


def inside(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_public_route(route: str, site_root: Path) -> Path | None:
    if is_external(route):
        return None
    clean = strip_query_fragment(route)
    clean = clean[2:] if clean.startswith("./") else clean.lstrip("/")
    target = (site_root / clean).resolve()
    if not inside(site_root, target):
        raise ValueError(f"Public route escapes site root: {route}")
    return target


def resolve_source(source: str, repo_root: Path) -> Path | None:
    if is_external(source):
        return None
    clean = strip_query_fragment(source).lstrip("/")
    target = (repo_root / clean).resolve()
    if not inside(repo_root, target):
        raise ValueError(f"Source path escapes repository root: {source}")
    return target


def target_exists(target: Path) -> tuple[bool, str]:
    if not target.exists():
        return False, "missing"
    if target.is_dir():
        index = target / "index.html"
        if index.exists():
            return True, "directory + index.html"
        return True, "directory present"
    return True, "file present"


def rel(target: Path | None, root: Path) -> str | None:
    if target is None:
        return None
    try:
        return str(target.relative_to(root))
    except ValueError:
        return str(target)


def audit(catalog_path: Path, repo_root: Path, site_root: Path) -> dict:
    catalog = extract_catalog(catalog_path)
    results = {
        "schema": "E47-PORTAL-AUDIT-1.0",
        "catalog": str(catalog_path.relative_to(repo_root)),
        "site_root": str(site_root.relative_to(repo_root)),
        "items": [],
        "summary": {
            "instruments": len(catalog),
            "ok": 0,
            "missing": 0,
            "external": 0,
            "checks": 0,
        },
    }

    for item in catalog:
        entry = {
            "n": item["n"],
            "name": item["name"],
            "sector": item["sector"],
            "evidence": item["evidence"],
            "checks": [],
        }

        public_route = item["open"]
        results["summary"]["checks"] += 1
        if is_external(public_route):
            results["summary"]["external"] += 1
            entry["checks"].append({
                "kind": "open",
                "route": public_route,
                "status": "external",
                "note": "not network-checked",
            })
        else:
            target = resolve_public_route(public_route, site_root)
            ok, note = target_exists(target)
            results["summary"]["ok" if ok else "missing"] += 1
            entry["checks"].append({
                "kind": "open",
                "route": public_route,
                "resolved": rel(target, repo_root),
                "status": "ok" if ok else "missing",
                "note": note,
            })

        source = item["source"]
        results["summary"]["checks"] += 1
        if is_external(source):
            results["summary"]["external"] += 1
            entry["checks"].append({
                "kind": "source",
                "route": source,
                "status": "external",
                "note": "not network-checked",
            })
        else:
            target = resolve_source(source, repo_root)
            ok, note = target_exists(target)
            results["summary"]["ok" if ok else "missing"] += 1
            entry["checks"].append({
                "kind": "source",
                "route": source,
                "resolved": rel(target, repo_root),
                "status": "ok" if ok else "missing",
                "note": note,
            })

        results["items"].append(entry)

    return results


def print_human(results: dict) -> None:
    print(
        f"{C.BOLD}Portal audit{C.RESET}  "
        f"{C.DIM}{results['catalog']} → {results['site_root']}{C.RESET}\n"
    )

    current_sector = None
    for item in results["items"]:
        if item["sector"] != current_sector:
            current_sector = item["sector"]
            print(f"{C.BRONZE}{current_sector.upper()}{C.RESET}")

        ev = item["evidence"]
        ev_color = {
            "e0": C.MINT,
            "e1": C.CYAN,
            "e2": C.BRONZE,
            "e3": "",
        }.get(ev, "")

        print(f"  {ev_color}[{ev.upper()}]{C.RESET} {item['name']}")
        for check in item["checks"]:
            status = check["status"]
            if status == "ok":
                mark = f"{C.MINT}✓{C.RESET}"
            elif status == "external":
                mark = f"{C.GRAY}·{C.RESET}"
            else:
                mark = f"{C.RED}✗{C.RESET}"

            print(
                f"     {mark} {check['kind']:<6} "
                f"{C.DIM}{check['route']}{C.RESET}"
            )
            if status == "missing":
                print(
                    f"       {C.RED}→ {check.get('resolved')} "
                    f"({check['note']}){C.RESET}"
                )
        print()

    s = results["summary"]
    print(
        f"{C.BOLD}Summary{C.RESET}  "
        f"{s['instruments']} instruments · "
        f"{C.MINT}{s['ok']} ok{C.RESET} · "
        f"{C.RED}{s['missing']} missing{C.RESET} · "
        f"{C.GRAY}{s['external']} external{C.RESET} · "
        f"{s['checks']} checks"
    )


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    ap.add_argument(
        "--catalog",
        default="website/interfaces/instruments/instruments.js",
        help="Portal catalog JS (default: website/interfaces/instruments/instruments.js)",
    )
    ap.add_argument(
        "--repo-root",
        default=".",
        help="Repository root (default: current directory)",
    )
    ap.add_argument(
        "--site-root",
        default="website",
        help="Published site root (default: website)",
    )
    ap.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON",
    )
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.exists():
        print(f"repo root not found: {repo_root}", file=sys.stderr)
        return 2

    catalog_path = (repo_root / args.catalog).resolve()
    if not catalog_path.exists():
        print(f"catalog not found: {catalog_path}", file=sys.stderr)
        return 2

    site_root = (repo_root / args.site_root).resolve()
    if not site_root.exists():
        print(f"site root not found: {site_root}", file=sys.stderr)
        return 2

    try:
        results = audit(catalog_path, repo_root, site_root)
    except (ValueError, OSError) as exc:
        print(f"portal audit error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_human(results)

    return 0 if results["summary"]["missing"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
