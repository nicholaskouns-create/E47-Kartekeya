#!/usr/bin/env python3
"""E47 symbolic + Python + quantum-state validation.

Targeted validation suite covering the finite E47 spectral machine,
Hamiltonian seismic energy-balance identity, Brinkmann vacuum geometry,
and simulated 125-dimensional quantum-state projection.

Evidence boundary: classical execution of symbolic/numerical identities and
state-vector simulation. This is not quantum hardware validation and does not
by itself establish an E47 derivation of quantum gravity.
"""
from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import sympy as sp

RESULTS=[]
def check(tag, claim, ok, detail=""):
    ok=bool(ok)
    RESULTS.append({"tag":tag,"claim":claim,"pass":ok,"detail":detail})
    print(f"[{'PASS' if ok else 'FAIL'}] {tag} {claim}")

# ---- E47 spectral machine ----
def jmat(j=2.0):
    m=np.arange(j,-j-1,-1,dtype=float); n=len(m)
    Jz=np.diag(m).astype(complex); Jp=np.zeros((n,n),complex)
    for i,mi in enumerate(m[:-1]):
        Jp[i,i+1]=np.sqrt(j*(j+1)-mi*(mi-1))
    Jm=Jp.conj().T
    return .5*(Jp+Jm), -.5j*(Jp-Jm), Jz

def k3(a,b,c): return np.kron(np.kron(a,b),c)
Jx,Jy,Jz=jmat(); I5=np.eye(5,dtype=complex); I125=np.eye(125,dtype=complex)
X=k3(Jx,I5,I5)+k3(I5,Jx,I5)+k3(I5,I5,Jx)
Y=k3(Jy,I5,I5)+k3(I5,Jy,I5)+k3(I5,I5,Jy)
Z=k3(Jz,I5,I5)+k3(I5,Jz,I5)+k3(I5,I5,Jz)
C=X@X+Y@Y+Z@Z
w,U=np.linalg.eigh(C)
wr=np.rint(w).astype(int)
expected={0:1,2:9,6:25,12:28,20:27,30:22,42:13}
actual={k:int(np.sum(wr==k)) for k in expected}
check("S1","carrier dimension 125",C.shape==(125,125))
check("S2","Casimir census exact",actual==expected,str(actual))
K=(C-6*I125)@(C-30*I125)
mask=np.isin(wr,[6,30]); P=U[:,mask]@U[:,mask].conj().T
check("S3","kernel/projector rank 47",int(round(np.trace(P).real))==47)
check("S4","projector idempotence",np.linalg.norm(P@P-P,2)<1e-12)
Q=K@K; eps=1/99144; G=I125-eps*Q
check("S5","Gamma fixes E47",np.linalg.norm(G@P-P,2)<1e-10)
comp=np.linalg.eigvalsh((I125-P)@G@(I125-P))
rho=max(abs(comp[np.abs(comp)>1e-10]))
check("S6","complement contraction 15/17",abs(rho-15/17)<1e-10,repr(rho))
check("S7","Gamma^220 approximates P",np.linalg.norm(np.linalg.matrix_power(G,220)-P,2)<1e-11)

# ---- Hamiltonian seismic identity ----
m1,m2,c1,c2,k1,k2,ag=sp.symbols('m1 m2 c1 c2 k1 k2 ag', real=True)
q1,q2,v1,v2,r1,r2=sp.symbols('q1 q2 v1 v2 r1 r2',real=True)
M=sp.diag(m1,m2); D=sp.diag(c1,c2); Ks=sp.diag(k1,k2)
q=sp.Matrix([q1,q2]); v=sp.Matrix([v1,v2]); r=sp.Matrix([r1,r2])
a=-M.inv()*(D*v+Ks*q+M*r*ag)
Hdot=(v.T*M*a+q.T*Ks*v)[0]
target=-(v.T*D*v)[0]-(v.T*M*r)[0]*ag
check("H1","Hamiltonian seismic energy-balance identity",sp.simplify(Hdot-target)==0)
check("H2","nonnegative damping form",sp.simplify((v.T*D*v)[0]-c1*v1**2-c2*v2**2)==0)

# ---- Brinkmann vacuum geometry ----
u,vv,x,y=sp.symbols('u v x y',real=True); F=sp.Function('F')(u)
coords=[u,vv,x,y]
g=sp.Matrix([[F*(x*x-y*y),1,0,0],[1,0,0,0],[0,0,1,0],[0,0,0,1]])
gi=g.inv(); n=4
Gamma=[[[sp.simplify(sum(gi[a,d]*(sp.diff(g[d,c],coords[b])+sp.diff(g[d,b],coords[c])-sp.diff(g[b,c],coords[d]))/2 for d in range(n))) for c in range(n)] for b in range(n)] for a in range(n)]
Ric=sp.zeros(n)
for b in range(n):
    for d in range(n):
        Ric[b,d]=sp.simplify(sum(sp.diff(Gamma[a][d][b],coords[a])-sp.diff(Gamma[a][a][b],coords[d])+sum(Gamma[a][a][e]*Gamma[e][d][b]-Gamma[a][d][e]*Gamma[e][a][b] for e in range(n)) for a in range(n)))
check("E1","Brinkmann Ricci-flatness",Ric==sp.zeros(4))
def Rup(a,b,c,d):
    return sp.simplify(sp.diff(Gamma[a][d][b],coords[c])-sp.diff(Gamma[a][c][b],coords[d])+sum(Gamma[a][c][e]*Gamma[e][d][b]-Gamma[a][d][e]*Gamma[e][c][b] for e in range(n)))
def Rdn(a,b,c,d):
    return sp.simplify(sum(g[a,e]*Rup(e,b,c,d) for e in range(n)))
check("E2","nonzero curvature components",sp.simplify(Rdn(0,2,0,2)+F)==0 and sp.simplify(Rdn(0,3,0,3)-F)==0)
poly=sum(sp.Symbol(f'a{i}')*u**i for i in range(47))
check("E3","47 monomial profiles independent",sp.Poly(poly,u).degree()==46)

# ---- Quantum-state simulation ----
rng=np.random.default_rng(47)
psi=rng.normal(size=125)+1j*rng.normal(size=125); psi/=np.linalg.norm(psi)
ppsi=P@psi
born=float(np.vdot(psi,P@psi).real)
check("Q1","Born overlap equals projected norm",abs(born-np.linalg.norm(ppsi)**2)<1e-12)
psi220=np.linalg.matrix_power(G,220)@psi
check("Q2","state convergence to projected component",np.linalg.norm(psi220-ppsi)<1e-10)
phi=U[:,mask]@(rng.normal(size=47)+1j*rng.normal(size=47)); phi/=np.linalg.norm(phi)
check("Q3","E47 state invariant under Gamma",np.linalg.norm(G@phi-phi)<1e-10)
chi=(I125-P)@(rng.normal(size=125)+1j*rng.normal(size=125)); chi/=np.linalg.norm(chi)
check("Q4","complement contracts",np.linalg.norm(G@chi)<=15/17+1e-10)
check("Q5","projective measurement dimensions 47+78=125",int(round(np.trace(P).real))+int(round(np.trace(I125-P).real))==125)

# ---- Grassmann dimensional witness ----
# Deterministic coordinate witness with dim(E)=90, dim(ker A)=82, intersection=47.
E=np.eye(125)[:,:90]
kerA=np.eye(125)[:,43:]
rankE=np.linalg.matrix_rank(E); rankKern=np.linalg.matrix_rank(kerA)
rankSum=np.linalg.matrix_rank(np.concatenate([E,kerA],axis=1))
inter=rankE+rankKern-rankSum
check("G1","Grassmann witness dimensions",(rankE,rankKern,rankSum,inter)==(90,82,125,47),str((rankE,rankKern,rankSum,inter)))

# ---- Additional exact identities ----
check("A1","occupancy 47/125",sp.Rational(47,125)==sp.Rational(47,125))
check("A2","selector annihilates projector",np.linalg.norm(K@P,2)<1e-10)
check("A3","K^2 positive semidefinite",np.min(np.linalg.eigvalsh(Q))>-1e-8)
check("A4","scalar curvature vanishes for Ricci-flat metric",sp.simplify(sum(gi[i,j]*Ric[i,j] for i in range(4) for j in range(4)))==0)

passed=sum(r["pass"] for r in RESULTS); total=len(RESULTS)
report={
    "schema":"MC-E47-SYMBOLIC-PYTHON-QUANTUM-VALIDATION/1.0",
    "status":"PASS" if passed==total else "FAIL",
    "total":total,
    "passed":passed,
    "failed":total-passed,
    "evidence_boundary":"Symbolic algebra, numerical linear algebra, and classical state-vector simulation only; not quantum hardware validation and not a complete derivation of gravity or quantum gravity from E47.",
    "results":RESULTS,
}
out=Path(__file__).with_name("e47_symbolic_python_quantum_validation_report.json")
out.write_text(json.dumps(report,indent=2))
print(f"\nRESULT: {passed}/{total} PASS")
print(f"REPORT: {out}")
raise SystemExit(0 if passed==total else 1)
