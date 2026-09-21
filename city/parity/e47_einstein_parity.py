#!/usr/bin/env python3
"""Independent Mathematical City parity reconstruction.

This intentionally does NOT import the primary validator. It reconstructs the
spin decomposition from magnetic-weight counting, then compares its invariants
with the candidate certificate emitted by the primary route.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
from itertools import product

ROOTS=(6,30)

def magnetic_weight_reconstruction():
    # Count weight multiplicities N_M directly on the 5^3 product basis.
    weights={M:0 for M in range(-6,7)}
    for m1,m2,m3 in product(range(-2,3), repeat=3):
        weights[m1+m2+m3]+=1

    # For SU(2), N_M = sum_{J>=|M|} mu_J, hence mu_J=N_J-N_{J+1}.
    mu={}
    for J in range(7):
        mu[J]=weights[J]-(weights[J+1] if J<6 else 0)

    state_mult={J:(2*J+1)*mu[J] for J in mu}
    casimir={J:J*(J+1) for J in mu}
    k2={J:((casimir[J]-ROOTS[0])*(casimir[J]-ROOTS[1]))**2 for J in mu}
    carrier=sum(state_mult.values())
    kernel=sum(state_mult[J] for J in mu if k2[J]==0)
    pos=[v for v in k2.values() if v>0]
    return {
        "method":"magnetic_weight_counting",
        "weight_multiplicity":weights,
        "irrep_multiplicity":mu,
        "state_multiplicity":state_mult,
        "casimir":casimir,
        "k2_by_spin":k2,
        "carrier_dimension":carrier,
        "kernel_dimension":kernel,
        "kernel_fraction":[kernel,carrier],
        "positive_gap":min(pos),
        "positive_max":max(pos),
        "k2_annihilates_e47":all(k2[J]==0 for J in (2,5)),
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidate", required=True)
    p.add_argument("--theorem", default="research/e47/E47_Gauge_Inequivalent_Einstein_Conditional_Construction.md")
    p.add_argument("--out")
    a=p.parse_args()

    candidate=json.loads(Path(a.candidate).read_text())
    city=magnetic_weight_reconstruction()
    primary=candidate["finite_reconstruction"]

    parity_keys=[
        "irrep_multiplicity","state_multiplicity","casimir","k2_by_spin",
        "carrier_dimension","kernel_dimension","kernel_fraction",
        "positive_gap","positive_max","k2_annihilates_e47"
    ]
    parity={k:city[k]==primary[k] for k in parity_keys}

    theorem_text=Path(a.theorem).read_text()
    theorem_contract={
        "outcome_3_declared":"Outcome 3" in theorem_text,
        "linearization_stability_declared":"linearization stability" in theorem_text,
        "W47_declared":"W_{47}" in theorem_text,
        "curvature_nontriviality_declared":"R^{(1)}" in theorem_text,
        "failed_predecessor_retained":"pure-gauge construction remains" in theorem_text,
        "machine_scope_boundary_declared":"DECLARED" not in theorem_text and "machine-checkable" in theorem_text,
    }

    finite_pass=all(parity.values()) and city["kernel_dimension"]==47 and city["carrier_dimension"]==125
    contract_pass=all(theorem_contract.values())
    verdict="CONDITIONAL_PARITY_PASS" if finite_pass and contract_pass else "PARITY_FAIL"

    receipt={
        "schema":"CITY-E47-EINSTEIN-PARITY/1.0",
        "obligation":"E47-EIN-PHYS-001",
        "city_method":"magnetic_weight_counting",
        "candidate_method":primary["method"],
        "finite_parity":parity,
        "city_reconstruction":city,
        "theorem_contract":theorem_contract,
        "verdict":verdict,
        "scope":{
            "confirmed":"independent finite E47 reconstruction and conditional theorem typing",
            "not_claimed":"numerical proof of the nonlinear Einstein theorem gates",
        },
    }
    text=json.dumps(receipt,indent=2,sort_keys=True)
    if a.out:
        path=Path(a.out); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text+"\n")
    print(text)
    if verdict!="CONDITIONAL_PARITY_PASS":
        raise SystemExit(1)

if __name__=="__main__":
    main()
