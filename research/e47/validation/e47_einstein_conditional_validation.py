#!/usr/bin/env python3
"""Primary first-principles validator for E47 -> Einstein conditional obligation.

Finite E47 data are reconstructed by successive SU(2) angular-momentum
coupling. The nonlinear Einstein statement is recorded as a conditional
theorem contract; this script does not pretend to solve the Einstein PDE.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOTS=(6,30)

def coupled_spin_multiplicities():
    # V_2 x V_2 = direct sum_{j12=0}^4 V_j12.
    mult={j:0 for j in range(7)}
    for j12 in range(5):
        for J in range(abs(j12-2), j12+2+1):
            mult[J]+=1
    return mult

def reconstruct():
    irrep_mult=coupled_spin_multiplicities()
    state_mult={J:(2*J+1)*m for J,m in irrep_mult.items()}
    carrier=sum(state_mult.values())
    casimir={J:J*(J+1) for J in irrep_mult}
    k2={J:((casimir[J]-ROOTS[0])*(casimir[J]-ROOTS[1]))**2 for J in irrep_mult}
    kernel=sum(state_mult[J] for J in irrep_mult if k2[J]==0)
    pos=[v for v in k2.values() if v>0]
    return {
        "method":"successive_su2_coupling",
        "irrep_multiplicity":irrep_mult,
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

def certificate():
    r=reconstruct()
    checks={
        "carrier_dim_125":r["carrier_dimension"]==125,
        "kernel_rank_47":r["kernel_dimension"]==47,
        "kernel_fraction_47_125":r["kernel_fraction"]==[47,125],
        "gap_11664":r["positive_gap"]==11664,
        "max_186624":r["positive_max"]==186624,
        "K2_zero_on_E47":r["k2_annihilates_e47"],
        "conditional_map_rank_possible":r["kernel_dimension"]==47,
        "intertwiner_reduces_to_zero_kernel":
            r["k2_annihilates_e47"],
    }
    return {
        "schema":"E47-EINSTEIN-CONDITIONAL-VALIDATION/1.0",
        "obligation":"E47-EIN-PHYS-001",
        "decision":"OUTCOME_3_CONDITIONAL_CONSTRUCTION",
        "finite_reconstruction":r,
        "checks":checks,
        "all_machine_checks_pass":all(checks.values()),
        "theorem_gates":{
            "exact_vacuum_background":"DECLARED_NOT_COMPUTED",
            "local_smoothness_or_linearization_stability":"DECLARED_NOT_COMPUTED",
            "physical_tangent_dimension_at_least_47":"DECLARED_NOT_COMPUTED",
            "curvature_map_injective_on_W47":"DECLARED_NOT_COMPUTED",
        },
        "machine_scope":
            "Finite E47 algebra and algebraic consequences only; nonlinear Einstein "
            "existence is conditional on the theorem gates.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out")
    a=p.parse_args()
    c=certificate()
    text=json.dumps(c,indent=2,sort_keys=True)
    if a.out:
        path=Path(a.out); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(text+"\n")
    print(text)
    if not c["all_machine_checks_pass"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
