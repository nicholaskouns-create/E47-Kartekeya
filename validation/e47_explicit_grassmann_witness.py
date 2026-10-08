#!/usr/bin/env python3
"""E47 explicit Grassmann witness. Exact rational SymPy; no canonical promotion.

Run: python3 validation/e47_explicit_grassmann_witness.py
Produces e47_explicit_grassmann_witness.json alongside this file.
A and E are explicitly exported in sparse rational COO form.
"""
import json
from pathlib import Path
from itertools import product
import sympy as sp

d=5
I5=sp.eye(d)
Jz=sp.diag(-2,-1,0,1,2)
Jp=sp.zeros(d)
Jm=sp.zeros(d)
for i,m in enumerate(range(-2,3)):
    if i<4: Jp[i+1,i]=2-m
    if i>0: Jm[i-1,i]=2+m

def total(X):
    return (sp.kronecker_product(X,I5,I5)
            +sp.kronecker_product(I5,X,I5)
            +sp.kronecker_product(I5,I5,X))
Tz,Tp,Tm=map(total,(Jz,Jp,Jm))
I=sp.eye(125)
C=Tz*Tz+(Tp*Tm+Tm*Tp)/2
spectrum=(0,2,6,12,20,30,42)
def spectral_projector(c):
    R=I
    for z in spectrum:
        if z!=c: R=R*(C-z*I)/(c-z)
    return R
P=spectral_projector(6)+spectral_projector(30)
K=(C-6*I)*(C-30*I)
assert P*P==P and K*P==sp.zeros(125) and sp.trace(P)==47

# Deterministic exact column selection: SymPy columnspace picks pivot columns
# in the canonical lexicographic tensor basis (-2,-2,-2),..., (2,2,2).
U=sp.Matrix.hstack(*P.columnspace())           # 125 x 47
W=sp.Matrix.hstack(*(I-P).columnspace())       # 125 x 78
M=U.row_join(W)                                # 125 x 125
assert M.det()!=0
# Adapted coordinate ordering: [47 kernel | 43 W_E | 35 W_B].
E=M[:,:90]                                     # 125 x 90, explicit basis
Minv=M.inv()
A=Minv[47:90,:]                                # 43 x 125, explicit constraint
B=M[:,list(range(47))+list(range(90,125))]     # 125 x 82, basis of ker A
assert A*E[:,47:90]==sp.eye(43)
assert A*U==sp.zeros(43,47)
assert A*B==sp.zeros(43,82)
assert E.rank()==90 and A.rank()==43 and B.rank()==82
assert E.row_join(B).rank()==125
assert 90+82-125==47
assert E[:,:47]==U and B[:,:47]==U

def sparse(X):
    return dict(shape=list(X.shape),entries=[
        [int(i),int(j),str(X[i,j])]
        for i in range(X.rows) for j in range(X.cols) if X[i,j]!=0])
result={
    "status":"EXACT CONSTRUCTIVE WITNESS; not an identification of original unspecified constraints",
    "basis":"lexicographic tensor weights m1,m2,m3 in {-2,-1,0,1,2}",
    "selection":"SymPy columnspace pivot columns of P and I-P; E=M[:,0:90]; A=M.inv()[47:90,:]",
    "dimensions":{"V":125,"ker_K":47,"E":90,"rank_A":43,"ker_A":82,"intersection":47},
    "E":sparse(E),"A":sparse(A),"B":sparse(B),
    "claims":{"E_plus_ker_A_equals_V":True,"E_intersect_ker_A_equals_ker_K":True,
              "original_unprovided_E_A_identified":False,
              "cubic_closure_tested":False,"Einstein_map_tested":False,
              "hardware_trace_tested":False},
    "sympy_version":sp.__version__
}
out=Path(__file__).with_suffix(".json")
out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
print("PASS: exact 125x90 E, 43x125 A, 125x82 ker(A) basis; intersection=47")
print("EXPORTED",out)
