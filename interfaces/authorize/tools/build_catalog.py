#!/usr/bin/env python3
"""Build public ICD-10-CM catalog from CDC/CMS 2027 official order file.
No CPT descriptions. No PHI. Outputs a lazily delivered JSON pack.
Usage: python interfaces/authorize/tools/build_catalog.py
Or: python interfaces/authorize/tools/build_catalog.py --source path/to/icd10cm_order_2027.txt
"""
from __future__ import annotations
import argparse, datetime as dt, io, json, pathlib, re, urllib.request, zipfile

HERE = pathlib.Path(__file__).resolve().parents[1]
DEST = HERE / "data"
# Official code-set files are published on CDC/CMS; these pages contain current links.
CDC_PAGE = "https://www.cdc.gov/nchs/icd/icd-10-cm/files.html"
CMS_PAGE = "https://www.cms.gov/medicare/coding-billing/icd-10-codes"
# Official FY2027 CDC order-file endpoint; if CDC changes release paths, supply --source.
ZIP_URLS = (
    "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2027/icd10cm-order-2027.zip",
    "https://www.cms.gov/files/zip/2027-code-descriptions-tabular-order.zip",
)
USER_AGENT = "Authorize/0.1 (public ICD-10-CM import; no patient data)"

def download():
    errors = []
    for url in ZIP_URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=50) as r:
                data = r.read(35_000_001)
            if len(data) > 35_000_000:
                raise ValueError("Official file exceeds max size")
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                candidates = [n for n in z.namelist() if re.search(r"order.*\.txt$", n, re.I)]
                if not candidates:
                    raise ValueError("Order TXT not found in official ZIP")
                name = next((n for n in candidates if "2027" in n), candidates[0])
                return z.read(name).decode("utf-8-sig", "replace"), url
        except Exception as exc:
            errors.append(f"{url}: {exc}")
    raise RuntimeError("Official archive unavailable. Download the FY2027 order TXT from CDC/CMS and pass --source.\n"+"\n".join(errors))

def parse_order(text):
    codes = []
    for line in text.splitlines():
        # CDC fixed-width order file: seq(5), code(7), billable(1), short(60), long(rest).
        if len(line) < 15:
            continue
        match = re.match(r"^\s*(\d{1,5})\s+([A-TV-Z][0-9][A-Z0-9]{1,5})\s+([01])\s+(.+)$", line, re.I)
        if not match:
            continue
        _, code, billable, textpart = match.groups()
        code = code.upper()
        # For released fixed-width records, long description begins at character index 77.
        long_desc = line[77:].strip() if len(line)>77 else ""
        short_desc = textpart.strip()
        desc = long_desc or short_desc
        # ICD diagnosis dot after third character; original raw code is useful for un-dotted queries.
        display = code[:3]+("."+code[3:] if len(code)>3 else "")
        codes.append({"code": display, "description": desc, "system": "ICD-10-CM", "billable": billable == "1"})
    if len(codes) < 50000:
        raise ValueError(f"Only {len(codes)} rows parsed; official source/format needs review")
    unique={x["code"]:x for x in codes}
    return [unique[k] for k in sorted(unique)]

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--source", type=pathlib.Path, help="Locally downloaded official CDC/CMS order TXT or ZIP")
    args=a.parse_args()
    if args.source:
        raw=args.source.read_bytes()
        if zipfile.is_zipfile(io.BytesIO(raw)):
            with zipfile.ZipFile(io.BytesIO(raw)) as z:
                names=[n for n in z.namelist() if re.search(r"order.*\.txt$",n,re.I)]
                if not names: raise ValueError("No order TXT found")
                text=z.read(names[0]).decode("utf-8-sig","replace")
        else:
            text=raw.decode("utf-8-sig","replace")
        source=str(args.source)
    else:
        text,source=download()
    rows=parse_order(text)
    DEST.mkdir(parents=True,exist_ok=True)
    meta={"system":"ICD-10-CM","version":"FY2027","effectiveDate":"2026-10-01 to 2027-09-30","source":source,"generatedAt":dt.datetime.now(dt.timezone.utc).isoformat()}
    output={"metadata":meta,"codes":rows}
    (DEST/"icd10cm-2027.json").write_text(json.dumps(output,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
    manifest={"packs":[{"file":"icd10cm-2027.json","name":"Official ICD-10-CM FY2027","count":len(rows)}]}
    (DEST/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(f"Built {len(rows):,} ICD-10-CM entries from {source}")

if __name__=="__main__":
    main()
