#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LAB=ROOT/"lab-manifest.json"

def main()->None:
    ap=argparse.ArgumentParser()
    ap.add_argument("--benchmark",action="store_true")
    ap.add_argument("--receipt-dir",default="artifacts/instrument-receipts")
    args=ap.parse_args()
    receipt_dir=ROOT/args.receipt_dir
    receipt_dir.mkdir(parents=True,exist_ok=True)
    lab=json.loads(LAB.read_text())
    failures=[]
    for item in lab["components"]:
        contract=json.loads((ROOT/item["contract"]).read_text())
        command=contract["smoke"]["benchmark_command" if args.benchmark else "command"]
        env=os.environ.copy()
        env["PYTHONPATH"]=str(ROOT/"src")+os.pathsep+env.get("PYTHONPATH","")
        proc=subprocess.run(command,cwd=ROOT,env=env,shell=True,text=True,capture_output=True)
        lines=[line for line in proc.stdout.splitlines() if line.strip()]
        try:
            if not lines:
                raise json.JSONDecodeError("empty stdout","",0)
            receipt=json.loads(lines[-1])
        except json.JSONDecodeError:
            receipt={
                "schema":"CITY-INSTRUMENT-RECEIPT/1.0",
                "component_id":item["id"],
                "version":item["version"],
                "mode":"benchmark" if args.benchmark else "smoke",
                "status":"FAIL",
                "failure":{
                    "schema":"CITY-INSTRUMENT-FAILURE/1.0",
                    "component_id":item["id"],
                    "version":item["version"],
                    "phase":"receipt-parse",
                    "error_type":"InvalidReceipt",
                    "message":"smoke entrypoint did not emit valid JSON",
                    "recoverable":False,
                    "context":{"stdout":proc.stdout[-2000:],"stderr":proc.stderr[-2000:]}
                }
            }
        (receipt_dir/f"{item['id']}.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        ok=(proc.returncode==0 and receipt.get("status")=="PASS" and receipt.get("component_id")==item["id"] and receipt.get("version")==item["version"])
        print(f"{item['id']}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            failures.append({
                "id":item["id"],"returncode":proc.returncode,
                "receipt_status":receipt.get("status"),
                "stderr":proc.stderr[-1000:]
            })
    index={
        "schema":"CITY-INSTRUMENT-SMOKE-INDEX/1.0",
        "mode":"benchmark" if args.benchmark else "smoke",
        "components":[item["id"] for item in lab["components"]],
        "failures":failures
    }
    (receipt_dir/"index.json").write_text(json.dumps(index,indent=2,sort_keys=True)+"\n")
    if failures:
        raise SystemExit("instrument smoke failures: "+", ".join(x["id"] for x in failures))

if __name__=="__main__":
    main()
