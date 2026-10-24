#!/usr/bin/env python3
"""E47 Grassmann–Casimir Compatibility and Spectral Stabilization.
Exact SymPy arithmetic. Run: python3 e47_grassmann_validation.py
A PASS certifies the stated check, not every claim in the supplied narrative.
"""
import sympy as s
import json
from pathlib import Path
from collections import Counter
from itertools import product
checks=[]
def check(name, condition, detail=''):
    ok=bool(condition)
    checks.append(dict(name=name,passed=ok,detail=str(detail)))
    print(f"{'PASS' if ok else 'FAIL'} | {name} | {detail}", flush=True)
    if not ok: raise AssertionError(name)
I5=s.eye(5); Z=s.zeros(5)
# Unnormalized weight basis: m=-2,...,2; all entries rational.
Jz=s.diag(*range(-2,3)); Jp=Z.copy(); Jm=Z.copy()
for i,m in enumerate(range(-2,3)):
    if i<4: Jp[i+1,i]=2-m
    if i>0: Jm[i-1,i]=2+m
check('spin commutators',Jz*Jp-Jp*Jz==Jp and Jz*Jm-Jm*Jz==-Jm and Jp*Jm-Jm*Jp==2*Jz)
check('single-spin Casimir',Jz**2+(Jp*Jm+Jm*Jp)/2==6*I5)
# Positive metric makes this rational basis unitarily equivalent to standard spin 2.
G5=s.diag(1,s.Rational(1,4),s.Rational(1,6),s.Rational(1,4),1)
check('physical inner product',Jp.T*G5==G5*Jm and all(G5[i,i]>0 for i in range(5)))
def total(A):
    return s.kronecker_product(A,I5,I5)+s.kronecker_product(I5,A,I5)+s.kronecker_product(I5,I5,A)
Tz,Tp,Tm=map(total,(Jz,Jp,Jm)); I=s.eye(125)
C=Tz**2+(Tp*Tm+Tm*Tp)/2
check('carrier dimension',C.shape==(125,125))
check('total weight conserved',C*Tz==Tz*C)
# Independent exact characteristic-polynomial computation in conserved-weight blocks.
basis=list(product(range(-2,3),repeat=3)); census=Counter()
x=s.Symbol('x')
for weight in range(-6,7):
    idx=[i for i,b in enumerate(basis) if sum(b)==weight]
    cp=C.extract(idx,idx).charpoly(x).as_expr()
    roots=s.roots(cp,x)
    check(f'weight {weight:+d} polynomial splits',sum(roots.values())==len(idx))
    census.update({int(k):int(v) for k,v in roots.items()})
expected={0:1,2:9,6:25,12:28,20:27,30:22,42:13}
check('derived Casimir census',dict(census)==expected,dict(sorted(census.items())))
# Derive irreducible multiplicities independently from weight counts.
w=Counter(map(sum,basis)); mult={j:w[j]-w[j+1] for j in range(7)}
check('weight-character decomposition',{j*(j+1):(2*j+1)*n for j,n in mult.items()}==expected,mult)
K=(C-6*I)*(C-30*I)
# Verify square-free annihilating polynomial -> diagonalizability.
ann=I
for c in sorted(census): ann=ann*(C-c*I)
check('square-free Casimir annihilator',ann==s.zeros(125))
nullity=sum(n for c,n in census.items() if (c-6)*(c-30)==0)
check('Casimir selector nullity',nullity==47,f'nullity={nullity}; rank={125-nullity}; claimed 82 is incompatible with this operator')
def projector(c):
    out=I
    for d in sorted(census):
        if c!=d: out=out*(C-d*I)/(c-d)
    return out
P=projector(6)+projector(30)
check('exact projector',P*P==P and s.trace(P)==47 and K*P==s.zeros(125))
G=s.kronecker_product(G5,G5,G5)
check('orthogonal projector in physical metric',P.T*G==G*P)
nonzero=sorted({((c-6)*(c-30))**2 for c in census if c not in (6,30)})
a,b=min(nonzero),max(nonzero); eps=s.Rational(2,a+b)
rho=max(abs(1-eps*t) for t in nonzero)
check('optimal positive-step contraction',eps==s.Rational(1,99144) and rho==s.Rational(15,17),f'K^2 spectrum off kernel={nonzero}; epsilon={eps}; rho={rho}')
Gamma=I-eps*K*K
check('kernel fixed by propagator',Gamma*P==P)
check('complement strictly contracts',all(abs(1-eps*t)<1 for t in nonzero))
check('coherence ratio',s.Rational(nullity,125)==s.Rational(47,125),s.Rational(47,125))
# Construct actual subspaces of the computed carrier, without identifying A with K.
# Use column bases for ker K and im K; im K complements ker K.
U=s.Matrix.hstack(*P.columnspace()); W=s.Matrix.hstack(*(I-P).columnspace())
check('spectral complementary basis',U.cols==47 and W.cols==78 and s.Matrix.hstack(U,W).rank()==125)
E=s.Matrix.hstack(U,W[:,:43]); B=s.Matrix.hstack(U,W[:,43:])
check('constructed Grassmann dimensions',E.rank()==90 and B.rank()==82 and s.Matrix.hstack(E,B).rank()==125)
check('constructed intersection',E.cols+B.cols-s.Matrix.hstack(E,B).rank()==47)
# A in the adapted basis (U,W): extracts 43 coordinates; pullback gives A on V.
Acoord=s.zeros(43,125)
for i in range(43): Acoord[i,47+i]=1
check('constraint rank and restricted rank',Acoord.rank()==43 and Acoord[:,:90].rank()==43)
check('constraint kernel dimension',125-Acoord.rank()==82)
# Exact theorem: 90+82-dim(E+B) = 47 iff E+B=V.
check('Grassmann transversality arithmetic',90+82-125==47 and 90-43==47)
# Track supplied claims separately; these are not counted as passing theorem checks.
claims={
 'Casimir kernel equals 82':'FALSE for K=(C-6I)(C-30I); computed nullity 47',
 'Constraint kernel equals 82':'TRUE for a distinct rank-43 map A: V -> C^43',
 'Grassmann intersection equals 47':'TRUE when E+ker(A)=V; explicitly realized here',
 'Original E and 43 constraints':'Not supplied as matrices; construction here is an existence witness',
 'Cubic closure':'Polynomial not supplied; root and dynamical stability untested',
 'Einstein-to-spectral closure':'Metric/action/map and equivalence theorem not supplied; untested',
 'Repository bit-exact implementation':'Repository source unavailable through attempted retrieval; untested',
 'FPGA/ASIC realization':'Hardware description and execution evidence not supplied; untested',
 'Entropy decrease':'No entropy functional specified; spectral error contraction proved'
}
result={'title':__doc__.splitlines()[0], 'checks':checks,'passed':len(checks),'failed':0,'arithmetic':'exact rational SymPy; operator norm uses physical spin inner product','claim_status':claims,'sympy_version':s.__version__}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'\n{len(checks)}/{len(checks)} exact checks passed.',flush=True)
print(json.dumps(claims,indent=2))
