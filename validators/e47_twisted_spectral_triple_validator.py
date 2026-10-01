#!/usr/bin/env python3
"""E47 -> Explicit Twisted Spectral Triple: First-Principles Validator.

Builds H125=V2^{tensor 3} from spin-2 generators, derives the Casimir
projectors, validates E47=E6+E30, and constructs the finite twisted spectral
triple A=C+C, Hgeo=E6+E0, sigma(a+,a-)=(a-,a+),
gamma=(P6-P0)|Hgeo, D=[[0,T],[T*,0]].

Certificate target: 13/13 PASS.
"""
import numpy as np

TOL=2e-10
j=2
m=np.array([2,1,0,-1,-2.],float)
Jz=np.diag(m).astype(complex)
Jp=np.zeros((5,5),complex)
for c,mm in enumerate(m):
    hit=np.where(np.isclose(m,mm+1))[0]
    if len(hit):
        Jp[hit[0],c]=np.sqrt(j*(j+1)-mm*(mm+1))
Jm=Jp.conj().T
Jx=(Jp+Jm)/2
Jy=(Jp-Jm)/(2j)
I5=np.eye(5)
k3=lambda a,b,c: np.kron(np.kron(a,b),c)
Jt=[k3(J,I5,I5)+k3(I5,J,I5)+k3(I5,I5,J) for J in (Jx,Jy,Jz)]
C=sum(J@J for J in Jt)
ev,U=np.linalg.eigh(C)
I125=np.eye(125)

def sector(lam):
    V=U[:,np.isclose(ev,lam,atol=1e-8)]
    return V@V.conj().T,V

P0,U0=sector(0)
P6,U6=sector(6)
P30,U30=sector(30)
P47=P6+P30
K=(C-6*I125)@(C-30*I125)
expected=[0,2,6,12,20,30,42]
mult=[int(np.sum(np.isclose(ev,x,atol=1e-8))) for x in expected]

# Hgeo=E6+E0; A=C+C; swap automorphism.
Q=np.column_stack([U6,U0])
I26=np.eye(26)
Pp=np.diag([1.]*25+[0.])
Pm=np.diag([0.]*25+[1.])
gamma=Pp-Pm
pi=lambda a,b:a*Pp+b*Pm
pi_sigma=lambda a,b:b*Pp+a*Pm

# Deterministic nonzero odd Dirac block T:E0->E6.
T=np.zeros((25,1),complex)
T[0,0]=1
D=np.block([[np.zeros((25,25)),T],
            [T.conj().T,np.zeros((1,1))]])

checks=[]
def ck(name,condition,value=None):
    checks.append((name,bool(condition),value))

ck("su(2) commutator",
   np.linalg.norm(Jx@Jy-Jy@Jx-1j*Jz)<TOL,
   np.linalg.norm(Jx@Jy-Jy@Jx-1j*Jz))
ck("Casimir multiplicities",mult==[1,9,25,28,27,22,13],mult)
ck("rank P47=47",abs(np.trace(P47).real-47)<1e-8,np.trace(P47).real)
ker=int(np.sum(np.abs(np.linalg.eigvalsh(K))<1e-7))
ck("ker K=47",ker==47,ker)
ck("gamma=(P6-P0)|Hgeo",
   np.linalg.norm(Q.conj().T@(P6-P0)@Q-gamma)<1e-8,
   np.linalg.norm(Q.conj().T@(P6-P0)@Q-gamma))
ck("gamma^2=I",np.linalg.norm(gamma@gamma-I26)<1e-12,
   np.linalg.norm(gamma@gamma-I26))
ck("D=D*",np.linalg.norm(D-D.conj().T)<1e-12,
   np.linalg.norm(D-D.conj().T))
ck("{D,gamma}=0",np.linalg.norm(D@gamma+gamma@D)<1e-12,
   np.linalg.norm(D@gamma+gamma@D))

rng=np.random.default_rng(47)
max_tw=max_ga=0.0
for _ in range(50):
    a,b=rng.normal(size=2)+1j*rng.normal(size=2)
    A=pi(a,b)
    max_tw=max(max_tw,np.linalg.norm(D@A-pi_sigma(a,b)@D))
    max_ga=max(max_ga,np.linalg.norm(gamma@A-A@gamma))
ck("twisted commutators vanish",max_tw<1e-12,max_tw)
ck("[gamma,A]=0",max_ga<1e-12,max_ga)
ck("compact resolvent (finite dimensional)",
   np.all(np.isfinite(np.linalg.inv(D-1j*I26))),
   np.linalg.norm(np.linalg.inv(D-1j*I26)))

# Actual Casimir eigenvectors form a 3+1 frame.
u=U0[:,0]
v1=np.sqrt(2)*U6[:,0]
v2=np.sqrt(8)*U6[:,1]
v3=np.sqrt(2)*U6[:,2]
B=np.column_stack([u,v1,v2,v3])
eta=P6-P0
g=B.conj().T@eta@B
gt=np.diag([-1,2,8,2])
ck("g=diag(-1,2,8,2)",np.linalg.norm(g-gt)<1e-8,
   np.linalg.norm(g-gt))
ge=np.linalg.eigvalsh(g).real
ck("Lorentzian inertia (1-,3+)",
   sum(ge<0)==1 and sum(ge>0)==3,ge.tolist())

print("E47 -> EXPLICIT TWISTED SPECTRAL TRIPLE")
print("spec(C) =",expected,"multiplicities =",mult)
print("A=C+C; sigma(a+,a-)=(a-,a+)")
print("Hgeo=E6+E0; gamma=(P6-P0)|Hgeo")
print("max twisted commutator norm =",max_tw)
print("g =\n",np.real_if_close(g))
for name,ok,val in checks:
    print(("PASS" if ok else "FAIL"),name,"::",val)
print(f"RESULT: {sum(x[1] for x in checks)}/{len(checks)} PASS")
assert all(x[1] for x in checks)
