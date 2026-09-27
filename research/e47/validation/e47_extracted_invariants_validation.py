#!/usr/bin/env python3
"""Reproducible checks for the ten supplied E47/Pip plates.

Run: python e47_extracted_invariants_validation.py
Only exact algebra is certified as a theorem. Chosen geometric data, image
measurements, physical interpretations, and unprovided hardware are separate.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction as F
from itertools import permutations, product
import json
import math
from pathlib import Path

import numpy as np

OUT = Path(__file__).with_suffix(".json")
checks: dict[str, bool] = {}
observations: dict[str, object] = {}


def check(name: str, condition: bool) -> None:
    checks[name] = bool(condition)
    if not condition:
        print(f"FAIL {name}")


def convolution(a: Counter[int], b: Counter[int]) -> Counter[int]:
    c: Counter[int] = Counter()
    for p, cp in a.items():
        for q, cq in b.items():
            c[p + q] += cp * cq
    return c


def spin_character(p: Counter[int]) -> dict[int, int]:
    return {j: p[j] - p[j + 1] for j in range(7)}


def exact_carrier() -> None:
    chi = Counter({m: 1 for m in range(-2, 3)})
    cyc = {
        "identity": convolution(convolution(chi, chi), chi),
        "transposition": convolution(chi, Counter({2 * m: 1 for m in range(-2, 3)})),
        "three_cycle": Counter({3 * m: 1 for m in range(-2, 3)}),
    }
    traces = {name: spin_character(p) for name, p in cyc.items()}
    table: dict[int, dict[str, int]] = {}
    for j in range(7):
        a, t, z = (traces[k][j] for k in ("identity", "transposition", "three_cycle"))
        numerators = (a + 3*t + 2*z, a - 3*t + 2*z, 2*a - 2*z)
        check(f"character_integrality_j{j}", all(n >= 0 and n % 6 == 0 for n in numerators))
        table[j] = dict(zip(("trivial", "sign", "standard"), (n // 6 for n in numerators)))
    expected = [(1,0,0),(0,1,1),(1,0,2),(1,1,1),(1,0,1),(0,0,1),(1,0,0)]
    check("joint_SU2_S3_table", [tuple(table[j].values()) for j in range(7)] == expected)
    m = [traces["identity"][j] for j in range(7)]
    d = [m[j] * (2*j+1) for j in range(7)]
    check("Casimir_sector_dimensions", d == [1,9,25,28,27,22,13] and sum(d) == 125)
    check("E47_dimension", d[2] + d[5] == 47)
    check("S3_5_0_42", (5, 0, 2*2*5 + 2*11) == (5,0,42))
    check("bosonic_irrep", table[2]["trivial"] == 1 and table[5]["trivial"] == 0)
    check("fermionic_exclusion", table[2]["sign"] == table[5]["sign"] == 0)
    check("joint_commutant_6", 1**2 + 2**2 + 1**2 == 6)
    check("SU2_commutant_29", m[2]**2 + m[5]**2 == 29)
    fp = (47, 5, 5-(2*5+11))
    check("permutation_fingerprint", fp == (47,5,-16))
    k = [(j*(j+1)-6)*(j*(j+1)-30) for j in range(7)]
    check("K_sector_values", k == [180,112,0,-108,-140,0,432])
    check("K_inertia", (sum(d[j] for j in range(7) if k[j]>0),
                        sum(d[j] for j in range(7) if k[j]<0),
                        sum(d[j] for j in range(7) if k[j]==0)) == (23,55,47))
    lam = sorted({v*v for v in k if v})
    check("K2_spectrum", lam == [11664,12544,19600,32400,186624])
    eps = F(1, 99144)
    gamma = [1-eps*v*v for v in k]
    check("optimal_Richardson", max(abs(1-eps*x) for x in lam) == F(15,17))
    check("five_factor_projector", all(math.prod(1-F(v*v,x) for x in lam) == (1 if v==0 else 0) for v in k))
    defect = max((1-g*g for v,g in zip(k,gamma) if v), default=F(0))
    check("Krein_nonisometry_defect", defect == F(12800,23409))
    observations.update(casimir_multiplicities=d, k_values=k,
                        gamma_eigenvalues=[str(v) for v in gamma],
                        krein_defect=str(defect), permutation_fingerprint=fp)
    # Enumerate nonempty selections of whole Casimir sectors, not arbitrary subspaces.
    selectors = [(tuple(s),sum(d[j] for j in s),sum(m[j]**2 for j in s))
                 for n in range(1,8) for s in __import__('itertools').combinations(range(7),n)]
    rank47 = [(list(s),c) for s,dim,c in selectors if dim==47]
    check("quadratic_selector_uniqueness", rank47 == [([2,5],29),([1,2,6],35)])
    observations["whole_sector_rank47_selectors"] = rank47


def matrix_reconstruction() -> None:
    m = np.arange(2,-3,-1)
    zp = np.diag(m).astype(complex)
    jp = np.zeros((5,5),complex)
    for i in range(4):
        jp[i,i+1] = np.sqrt(2*3 - m[i+1]*(m[i+1]+1))
    jx = (jp+jp.conj().T)/2
    jy = (jp-jp.conj().T)/(2j)
    ident = np.eye(5)
    def total(a: np.ndarray) -> np.ndarray:
        return (np.kron(np.kron(a,ident),ident)
              + np.kron(np.kron(ident,a),ident)
              + np.kron(np.kron(ident,ident),a))
    generators = [total(a) for a in (jx,jy,zp)]
    c = sum(a@a for a in generators)
    c = (c+c.conj().T)/2
    ev, v = np.linalg.eigh(c)
    expected = np.repeat([0,2,6,12,20,30,42],[1,9,25,28,27,22,13])
    check("matrix_Casimir_spectrum", np.max(np.abs(ev-expected)) < 1e-10)
    p = v[:,np.isclose(ev,6,atol=1e-10)|np.isclose(ev,30,atol=1e-10)]
    p = p@p.conj().T
    i = np.eye(125)
    check("matrix_projector_rank_idempotence", abs(np.trace(p).real-47)<1e-10
          and np.linalg.norm(p@p-p)<1e-10)
    eta = 2*p-i
    check("Krein_47_78", np.sum(np.linalg.eigvalsh(eta)>0)==47
          and np.sum(np.linalg.eigvalsh(eta)<0)==78)
    k = (c-6*i)@(c-30*i)
    gamma = i-k@k/99144
    check("matrix_contraction_error", abs(np.linalg.norm(gamma-p,2)-15/17)<1e-10)
    check("matrix_Gamma_not_eta_isometry", abs(np.linalg.norm(gamma.conj().T@eta@gamma-eta,2)
          - 12800/23409)<1e-10)
    # This is an explicitly chosen 4-frame, not a canonical spacetime metric.
    u = v[:,np.argmin(np.abs(ev))]
    w = v[:,np.where(np.isclose(ev,6,atol=1e-10))[0][:3]]
    b4 = np.column_stack((u,np.sqrt(2)*w[:,0],np.sqrt(8)*w[:,1],np.sqrt(2)*w[:,2]))
    p0 = np.outer(u,u.conj())
    p6 = v[:,np.isclose(ev,6,atol=1e-10)]
    p6 = p6@p6.conj().T
    lorentz = b4.conj().T@(p6-p0)@b4
    check("chosen_Lorentzian_pullback",np.allclose(lorentz,np.diag([-1,2,8,2]),atol=1e-10))
    check("two_eta_forms_distinct",np.linalg.norm((p6-p0)-eta)>1)
    # Exchange of factors, with the exact eigenspace projector reconstructed numerically.
    labels = list(product(range(5),repeat=3))
    idx = {x:i for i,x in enumerate(labels)}
    def exchange(t):
        u = np.zeros((125,125))
        for col,x in enumerate(labels):
            u[idx[tuple(x[t[a]] for a in range(3))],col]=1
        return u
    perms = [exchange(t) for t in permutations(range(3))]
    ps = sum(perms)/6
    pa = sum((-1)**sum(t[a]>t[b] for a in range(3) for b in range(a+1,3))*exchange(t)
             for t in permutations(range(3)))/6
    dims = [np.trace(p@q).real for q in (ps,pa,i-ps-pa)]
    check("matrix_S3_decomposition", np.allclose(dims,[5,0,42],atol=1e-10))
    observations["numeric_residuals"] = dict(casimir=float(np.max(np.abs(ev-expected))),
        projector=float(np.linalg.norm(p@p-p)), s3_dimensions=[float(x) for x in dims])


def independent_bridges() -> None:
    # These exact checks do not identify an ancient source, a particle mass law,
    # or an implemented FPGA. They test only the specified formulas.
    phi=(1+math.sqrt(5))/2
    s=phi**-5
    r=math.sqrt(s)
    # Elements (a,b) represent a+b*sqrt(5) over Q.
    mul=lambda x,y:(x[0]*y[0]+5*x[1]*y[1],x[0]*y[1]+x[1]*y[0])
    sq=(F(-11,2),F(5,2))
    s2=mul(sq,sq)
    check("golden_polynomial_exact",(s2[0]+11*sq[0]-1,s2[1]+11*sq[1])==(0,0))
    check("golden_irrational_extension", 5**2*5>11**2 and sq[0]<0<sq[1])
    check("golden_polynomial", abs(r**4+11*r*r-1)<1e-13)
    x=1.0
    q0=(x-r)/(x+r)
    for n in range(6):
        q=(x-r)/(x+r)
        check(f"Heron_double_exponent_{n}",abs(q-q0**(2**n))<2e-13)
        x=(x+s/x)/2
    check("cube_address_bijection",sorted(25*a+5*b+c for a,b,c in product(range(5),repeat=3))==list(range(125)))
    check("minimum_qubits",2**6<125<=2**7 and 128-125==3)
    check("sevenfold_rotation",all((i+7)%7==i and (i+1)%7 in range(7) for i in range(7)))
    check("Babylonian_linear_example",F(1200)+F(600)==1800 and
          F(2,3)*1200-F(1,2)*600==500)
    def terminating(v:F)->bool:
        d=v.denominator
        for prime in (2,5):
            while d%prime==0:d//=prime
        return d==1
    check("decimal_exactness",terminating(F(47,125)) and not terminating(F(1,99144))
          and not terminating(F(15,17)))
    q28=lambda x:F(round(x*2**28),2**28)
    inputs=[F(-1234567,1000000),F(47,125),F(1,99144),F(15,17)]
    check("Q4_28_rounding_bound",all(abs(q28(x)-x)<=F(1,2**29) for x in inputs))
    # The proposed half-integer mass lattice is a data projection, not a fit theorem.
    M=1.220890e19
    particle_input={"electron":(0.000511,107),"muon":(0.105658,96)}
    residuals={name:(M*phi**(-N)-mass)/mass for name,(mass,N) in particle_input.items()}
    check("electron_muon_plate_rounded", abs(residuals["electron"]-0.0389)<0.001
          and abs(residuals["muon"]+0.000091)<0.0002)
    observations["illustrative_mass_residuals"] = residuals
    observations["unvalidated_claims"] = [
        "physical particle-spectrum fit beyond the two displayed rounded inputs",
        "acoustic speed as a measured material constant",
        "FPGA implementation, resource counts, timing, and Q4.28 250-step error",
        "Lorentzian geometry, curvature, stress-energy, and flight from E47 alone",
        "Sevenfold historical interpretation and Turtle-Pace safety without a dynamical model",
        "Standard Model action, renormalization, cosmology, or consciousness claims",
    ]


def main() -> None:
    exact_carrier()
    matrix_reconstruction()
    independent_bridges()
    result={"title":"E47 Extracted Invariants: Exact and Machine Validation",
            "status":"PASS" if all(checks.values()) else "FAIL",
            "passed":sum(checks.values()),"total":len(checks),"checks":checks,
            "observations":observations}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="checks"},indent=2))
    if result["status"]!="PASS": raise SystemExit(1)

if __name__=="__main__":main()
