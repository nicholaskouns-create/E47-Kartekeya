#!/usr/bin/env python3
"""MC-E47-CASIMIR-CENSUS/1.0 — the Casimir census of V2⊗V2⊗V2 as a named object.

Census: m = (m_0,...,m_6) = (1,3,5,4,3,2,1), the spin multiplicities of the cube.
Every selection S of spins defines ker prod_{j in S}(C - j(j+1)I), of dimension
sum_S m_j(2j+1) with SU(2) commutant of dimension sum_S m_j^2. E47 is S = {2,5}.

Exact layer: the census is read off the character chi(q)^3, chi(q)=q^-2+...+q^2,
and all 127 selections are enumerated. Machine layer: replay on the 125x125 carrier.
"""
from __future__ import annotations
import json, os
from itertools import combinations
from pathlib import Path
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents)>3 else Path.cwd()
OUT=(ROOT/"artifacts"/"E47_CASIMIR_CENSUS_CERTIFICATE.json") if (ROOT/"artifacts").exists() else Path(__file__).with_name("E47_CASIMIR_CENSUS_CERTIFICATE.json")
if os.environ.get("E47_CERT_OUT"): OUT=Path(os.environ["E47_CERT_OUT"])

SPINS=list(range(7))
E47=(2,5)

def exact():
    q=sp.symbols('q')
    f=sp.expand(sum(q**k for k in range(-2,3))**3*q**6)       # shift to a polynomial
    w=lambda mm: int(f.coeff(q,mm+6))
    census=[w(j)-w(j+1) for j in SPINS]
    dim=lambda S: sum(census[j]*(2*j+1) for j in S)
    com=lambda S: sum(census[j]**2 for j in S)
    selections=[S for r in range(1,8) for S in combinations(SPINS,r)]
    hits47=[S for S in selections if dim(S)==47]
    pairs47=[S for S in hits47 if len(S)==2]
    return dict(census=census,sector_dims=[census[j]*(2*j+1) for j in SPINS],
                casimir=[j*(j+1) for j in SPINS],total=dim(SPINS),full_commutant=com(SPINS),
                e47_dim=dim(E47),e47_commutant=com(E47),n_selections=len(selections),
                hits47=hits47,hits47_commutants=[com(S) for S in hits47],pairs47=pairs47,
                pair_dims=sorted({dim(S) for S in selections if len(S)==2}))

def machine(e):
    j=2.0; m=np.arange(j,-j-1,-1); Jz=np.diag(m).astype(complex); Jp=np.zeros((5,5),complex)
    for i,mi in enumerate(m[:-1]): Jp[i,i+1]=np.sqrt(j*(j+1)-mi*(mi-1))
    Jx=.5*(Jp+Jp.conj().T); Jy=-.5j*(Jp-Jp.conj().T); I5=np.eye(5); I=np.eye(125)
    def tot(A): return np.kron(np.kron(A,I5),I5)+np.kron(np.kron(I5,A),I5)+np.kron(np.kron(I5,I5),A)
    J=[tot(Jx),tot(Jy),tot(Jz)]; C=sum(A@A for A in J); C=((C+C.conj().T)/2).real
    ev=np.rint(np.linalg.eigvalsh(C)).astype(int)
    mult={c:int((ev==c).sum()) for c in e['casimir']}
    def nullity(S):
        M=I.copy()
        for jj in S: M=M@(C-jj*(jj+1)*I)
        return 125-int(np.linalg.matrix_rank(M,tol=1e-6*max(1.0,np.linalg.norm(M,2))))
    return dict(mult=mult,nullity={S:nullity(S) for S in e['hits47']})

def main():
    e=exact(); m=machine(e)
    checks={
      'census_1_3_5_4_3_2_1':e['census']==[1,3,5,4,3,2,1],
      'sector_dims':e['sector_dims']==[1,9,25,28,27,22,13],
      'census_total_125':e['total']==125,
      'casimir_multiplicities_machine':[m['mult'][c] for c in e['casimir']]==e['sector_dims'],
      'full_su2_commutant_65':e['full_commutant']==65,
      'e47_dim_47':e['e47_dim']==47,'e47_commutant_29':e['e47_commutant']==29,
      'all_127_selections_enumerated':e['n_selections']==127,
      'dim47_selections_exactly_two':e['hits47']==[(2,5),(1,2,6)],
      'dim47_commutants_29_35':e['hits47_commutants']==[29,35],
      'e47_unique_quadratic_selector':e['pairs47']==[(2,5)],
      'dim47_selections_machine':all(m['nullity'][S]==47 for S in e['hits47']),
    }
    checks={k:bool(v) for k,v in checks.items()}
    cert={'schema':'MC-E47-CASIMIR-CENSUS/1.0','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
      'exact':{
        'evidence':'exact character arithmetic: chi(q)^3, chi(q)=q^-2+...+q^2',
        'census':{'spins':SPINS,'multiplicity':e['census'],'casimir':e['casimir'],'sector_dimension':e['sector_dims']},
        'decomposition':'V2⊗V2⊗V2 = V0 + 3V1 + 5V2 + 4V3 + 3V4 + 2V5 + V6',
        'selector_rule':'dim ker prod_S (C - j(j+1)I) = sum_S m_j(2j+1); SU(2) commutant dim = sum_S m_j^2',
        'full_su2_commutant':e['full_commutant'],
        'e47':{'selection':list(E47),'dimension':e['e47_dim'],'commutant':e['e47_commutant']},
        'dimension_47_selections':[{'spins':list(S),'commutant':c} for S,c in zip(e['hits47'],e['hits47_commutants'])],
        'two_sector_dimensions':e['pair_dims'],
      },
      'machine':{'evidence':'float64 replay on the 125x125 carrier',
                 'casimir_multiplicities':{str(c):v for c,v in m['mult'].items()},
                 'nullity_of_dimension_47_selectors':{",".join(map(str,S)):v for S,v in m['nullity'].items()}},
      'boundary':'Finite census of the fixed 125-dimensional carrier. The uniqueness statement is about selections of whole Casimir sectors; other 47-dimensional subspaces exist.'}
    OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n'); print(json.dumps(cert,indent=2,sort_keys=True))
    if cert['status']!='PASS': raise SystemExit(1)
if __name__=='__main__': main()
