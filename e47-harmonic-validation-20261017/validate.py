#!/usr/bin/env python3
"""E47 harmonic realization: exact rational algebra and numerical simulation.
Python standard library only. Run: python3 validate.py
E3 independent replication and E4 physical validation are not asserted.
"""
from fractions import Fraction as F
from collections import Counter
import itertools, json, math, random
from pathlib import Path

checks=[]
def check(level,name,ok,detail=None):
    checks.append(dict(level=level,name=name,status='PASS' if ok else 'FAIL',detail=detail))
    if not ok: raise AssertionError(name)
def monomials(n):
    return [(a,b,n-a-b) for a in range(n+1) for b in range(n-a+1)]
def add(p,q,scale=1):
    r=p.copy()
    for m,c in q.items(): r[m]=r.get(m,F(0))+scale*c
    return {m:c for m,c in r.items() if c}
def deriv(p,i):
    r={}
    for m,c in p.items():
        if m[i]:
            k=list(m);k[i]-=1;r[tuple(k)]=c*m[i]
    return r
def mulvar(p,i):
    r={}
    for m,c in p.items():
        k=list(m);k[i]+=1;r[tuple(k)]=c
    return r
def lap(p):
    r={}
    for i in range(3):r=add(r,deriv(deriv(p,i),i))
    return r
def rot(p,i):
    j,k=((1,2),(2,0),(0,1))[i]
    return add(mulvar(deriv(p,k),j),mulvar(deriv(p,j),k),-1)
def casimir(p):
    r={}
    for i in range(3):r=add(r,rot(rot(p,i),i),-1)
    return r
def rref(a):
    a=[[F(v) for v in row] for row in a]; piv=[]; row=0
    for col in range(len(a[0])):
        k=next((k for k in range(row,len(a)) if a[k][col]),None)
        if k is None:continue
        a[row],a[k]=a[k],a[row];v=a[row][col]
        a[row]=[x/v for x in a[row]]
        for k in range(len(a)):
            if k!=row:
                v=a[k][col];a[k]=[x-v*y for x,y in zip(a[k],a[row])]
        piv.append(col);row+=1
        if row==len(a):break
    return a,piv
def harmonic_basis(n):
    src,dst=monomials(n),monomials(n-2)
    cols=[lap({m:F(1)}) for m in src]
    a,piv=rref([[c.get(m,0) for c in cols] for m in dst])
    basis=[]
    for free in set(range(len(src)))-set(piv):
        v={src[free]:F(1)}
        for i,p in enumerate(piv):
            if a[i][free]:v[src[p]]=-a[i][free]
        basis.append(v)
    return basis,len(piv)
def serial(p):return [{'powers':list(m),'coefficient':str(c)} for m,c in sorted(p.items())]

bases={}
for n in (2,5):
    b,rank=harmonic_basis(n);bases[str(n)]=[serial(p) for p in b]
    check('E1',f'degree {n}: exact Laplacian nullity',len(b)==2*n+1,dict(rank=rank,nullity=len(b)))
    check('E1',f'degree {n}: all basis elements harmonic',all(not lap(p) for p in b))
    check('E1',f'degree {n}: Casimir eigenvalue {n*(n+1)}',all(not add(casimir(p),p,-n*(n+1)) for p in b))
    check('E1',f'degree {n}: rotations preserve harmonicity',all(not lap(rot(p,i)) for p in b for i in range(3)))
    check('E1',f'degree {n}: rotation Lie brackets',all(not add(add(rot(rot(p,1),0),rot(rot(p,0),1),-1),rot(p,2)) for p in b))

given=[{(0,1,1):F(1)},{(0,2,0):F(1),(0,0,2):F(-1)},
       {(1,0,1):F(1)},{(1,1,0):F(1)},{(2,0,0):F(1),(0,0,2):F(-1)}]
_,piv=rref([[p.get(m,0) for p in given] for m in monomials(2)])
check('E1','supplied quadratic basis: harmonic and independent',len(piv)==5 and all(not lap(p) for p in given))

# Weight enumeration of V_2 tensor V_2 tensor V_2; highest-weight subtraction.
weights=Counter(sum(t) for t in itertools.product(range(-2,3),repeat=3))
mult={j:weights[j]-weights[j+1] for j in range(7)}
census={j*(j+1):(2*j+1)*mult[j] for j in range(7)}
check('E1','125-dimensional tensor carrier census',list(census.values())==[1,9,25,28,27,22,13],census)
check('E1','E47 multiplicities',mult[2]==5 and mult[5]==2 and census[6]+census[30]==47,mult)
values=[(c-6)*(c-30) for c in census]
squares=sorted(set(k*k for k in values if k))
check('E1','exact nonzero K squared spectrum',squares==[11664,12544,19600,32400,186624],squares)
eps=F(2,squares[0]+squares[-1]);rho=max(abs(1-eps*s) for s in squares)
check('E1','exact minimax contraction',eps==F(1,99144) and rho==F(15,17),dict(epsilon=str(eps),rho=str(rho)))

# Diagonal spectral-basis simulation, not a quantum circuit or hardware execution.
rng=random.Random(47)
cs=[c for c,count in census.items() for _ in range(count)]
state=[complex(rng.gauss(0,1),rng.gauss(0,1)) for _ in cs]
norm=math.sqrt(sum(abs(z)**2 for z in state));state=[z/norm for z in state]
target=[z if c in (6,30) else 0j for c,z in zip(cs,state)]
evolved=state[:]
for _ in range(220):
    evolved=[z*(1-((c-6)*(c-30))**2/99144) for c,z in zip(cs,evolved)]
error=math.sqrt(sum(abs(a-b)**2 for a,b in zip(evolved,target)))
bound=(15/17)**220
check('E2','220-step complex state contraction',error<=bound*(1+1e-3),dict(error=error,operator_bound=bound))
check('E2','kernel amplitudes preserved',all(evolved[i]==state[i] for i,c in enumerate(cs) if c in (6,30)))

result=dict(title='E47 harmonic-polynomial realization',checks=checks,
            exact_bases=bases,seed=47,
            E0='PROVED: see validation.md for the mathematical argument',
            E1='PASS: exact rational and integer calculations',
            E2='PASS: numerical spectral-basis complex-state simulation',
            E3='NOT RUN: independent implementation or replication',
            E4='NOT TESTED: physical or experimental realization')
Path(__file__).with_name('results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='exact_bases'},indent=2))
