#!/usr/bin/env python3
"""Fun With Einstein — E47 fivefold spectral/quantum certificate. NumPy + SymPy."""
import json
import numpy as np
import sympy as sp
from pathlib import Path
checks={}
def ck(k,v):
    checks[k]=bool(v)
    if not checks[k]: raise AssertionError(k)
s=sp.sqrt(5); phi=(1+s)/2
lo=(5-s)/2; hi=(5+s)/2; Om=sp.Rational(47,125)
alpha=sp.simplify(Om/phi**2)
ck("Fibonacci root",sp.simplify(phi**2-phi-1)==0)
ck("fivefold ratio",sp.simplify(lo/hi-phi**-2)==0)
ck("attenuation radical",sp.simplify(phi**-2-(3-s)/2)==0)
ck("alpha radical",sp.simplify(alpha-(141-47*s)/250)==0)
ck("alpha positive",bool(alpha>0))
L5=sp.zeros(5)
for i in range(5):
    L5[i,i]=2
    L5[i,(i+1)%5]=-1
    L5[i,(i-1)%5]=-1
ck("five cycle exact census",L5.eigenvals()=={sp.Integer(0):1,lo:2,hi:2})
l5=np.array(L5,dtype=float)
ck("cycle numeric spectrum",np.allclose(np.linalg.eigvalsh(l5),[0,float(lo),float(lo),float(hi),float(hi)],atol=1e-12))
I5=np.eye(5)
L=np.kron(np.kron(l5,I5),I5)+np.kron(np.kron(I5,l5),I5)+np.kron(np.kron(I5,I5),l5)
ck("125D graph symmetry",np.allclose(L,L.T))
ck("125D graph positivity",np.linalg.eigvalsh(L).min()>-1e-10)
ck("125D graph row sums",abs(L.sum(axis=1)).max()<1e-12)
m=np.arange(-2,3,dtype=float); Jz=np.diag(m).astype(complex)
Jp=np.zeros((5,5),dtype=complex)
for i,v in enumerate(m[:-1]): Jp[i+1,i]=np.sqrt(6-v*(v+1))
Jm=Jp.conj().T; Jx=(Jp+Jm)/2; Jy=(Jp-Jm)/(2j)
def total(X):return np.kron(np.kron(X,I5),I5)+np.kron(np.kron(I5,X),I5)+np.kron(np.kron(I5,I5),X)
X,Y,Z=map(total,[Jx,Jy,Jz])
C=X@X+Y@Y+Z@Z
ck("Casimir Hermitian",np.linalg.norm(C-C.conj().T)<1e-11)
evals,U=np.linalg.eigh(C); labels=[0,2,6,12,20,30,42]
counts=[int(np.sum(abs(evals-v)<1e-8)) for v in labels]
ck("spin sector census",counts==[1,9,25,28,27,22,13])
mask=(abs(evals-6)<1e-8)|(abs(evals-30)<1e-8)
P=U[:,mask]@U[:,mask].conj().T
ck("projector rank and trace",mask.sum()==47 and abs(np.trace(P)-47)<1e-9)
ck("projector idempotency",np.linalg.norm(P@P-P)<1e-10)
K=(C-6*np.eye(125))@(C-30*np.eye(125))
ck("kernel annihilation",np.linalg.norm(K@P)<1e-8)
ck("Casimir/projector commutator",np.linalg.norm(C@P-P@C)<1e-9)
w=float(phi**-2); B=np.sqrt(w)*P; A=np.eye(125)-(1-np.sqrt(1-w))*P
Uanc=np.block([[A,-B],[B,A]])
ck("250D quantum unitary",np.linalg.norm(Uanc.conj().T@Uanc-np.eye(250))<1e-10)
rho=np.eye(125)/125
prob=float(np.trace(B@rho@B.conj().T).real)
ck("Born probability equals alpha",abs(prob-float(alpha))<1e-12)
E=w*P
ck("POVM effect positive",np.linalg.eigvalsh(E).min()>-1e-10)
ck("POVM effect bounded",np.linalg.eigvalsh(np.eye(125)-E).min()>-1e-10)
ck("alternate coefficient exists",sp.simplify(Om*phi**-4-alpha)!=0)
result={"status":"PASS","passed":sum(checks.values()),"total":len(checks),"checks":checks,"alpha_exact":str(alpha),"alpha_decimal":str(sp.N(alpha,65)),"quantum_probability":prob,"projector_rank":int(mask.sum()),"sector_multiplicities":counts,"ancilla_unitary_defect":float(np.linalg.norm(Uanc.conj().T@Uanc-np.eye(250))),"boundary":"Quantum simulation and finite spectral theorem; no measured GR deviation established; Lean/Coq separate compilation required."}
Path(__file__).with_name("results.json").write_text(json.dumps(result,indent=2))
print("PASS",result["passed"],"/",result["total"])
print("alpha =",sp.N(alpha,50))
print("quantum probability =",prob)
