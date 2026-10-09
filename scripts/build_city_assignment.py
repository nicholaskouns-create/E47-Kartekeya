#!/usr/bin/env python3
"""Fail-closed canonical City assignment compiler. stdlib only.
Reads the existing checked ledger; publishes one identical snapshot for all surfaces.
Run from repository root: python scripts/build_city_assignment.py
"""
import hashlib, json, pathlib, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from check_evidence_ledger import check
SOURCE=ROOT/"research/e47/evidence_ledger.json"
OUTPUT=ROOT/"website/data/city-assignment.json"
SURFACES=("citadel","citizenship_bureau","proof_forge","publication")
def canonical(o):
    return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def compile_record():
    ledger=json.loads(SOURCE.read_text())
    errors=check(ledger,ROOT)
    if errors: raise ValueError("evidence ledger invalid: "+"; ".join(errors))
    claims={c["id"]:c for c in ledger["claims"]}
    def closure(cid,seen=None):
        seen=set() if seen is None else seen
        for d in claims[cid].get("depends_on",[]):
            if d not in seen:
                seen.add(d);closure(d,seen)
        return seen
    out=[]
    for c in sorted(claims.values(),key=lambda x:x["id"]):
        deps=closure(c["id"])
        assumptions=set(c.get("conditional_on",[]))
        empirical=set(c.get("empirical",[]))
        for d in deps:
            assumptions.update(claims[d].get("conditional_on",[]))
            empirical.update(claims[d].get("empirical",[]))
        proof=ROOT/c["record"]
        out.append({"id":c["id"],"statement":c["statement"],"evidence":c["evidence"],
          "civic_state":"PRIMA_FACIE","certificate":c["record"],"certificate_sha256":hashlib.sha256(proof.read_bytes()).hexdigest(),
          "verified_check":c["check"],"depends_on":sorted(deps),"conditional_on":sorted(assumptions),
          "empirical":sorted(empirical),"scope":"as-stated-in-ledger",
          "supersession":"not_assessed"})
    payload={"schema":"MC-CIVIC-ASSIGNMENT/2.0","policy":"research/e47/CITY_CONSTITUTION_EVIDENCE_DETERMINED_PROMOTION_20261008.md",
      "source":"research/e47/evidence_ledger.json","source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      "claims":out,"claim_count":len(out)}
    payload["assignment_sha256"]=hashlib.sha256(canonical(payload)).hexdigest()
    payload["surfaces"]={name:{"assignment_sha256":payload["assignment_sha256"],
      "url":"/E47-Kartekeya/data/city-assignment.json"} for name in SURFACES}
    return payload
def main():
    record=compile_record()
    if "--check" in sys.argv:
        if not OUTPUT.exists() or json.loads(OUTPUT.read_text())!=record:
            raise SystemExit("STALE CITY ASSIGNMENT: regenerate with python scripts/build_city_assignment.py")
        print("CITY ASSIGNMENT VERIFIED",record["claim_count"],record["assignment_sha256"])
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True)
        OUTPUT.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
        print("CITY ASSIGNMENT GENERATED",record["claim_count"],record["assignment_sha256"])
if __name__=="__main__":main()
