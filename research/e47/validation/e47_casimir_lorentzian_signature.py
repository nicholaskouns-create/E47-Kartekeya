#!/usr/bin/env python3
import numpy as np

TOL=1e-10
checks={}
def ck(name,ok):
    checks[name]=bool(ok)
    print(("PASS" if ok else "FAIL"),name)

j=2
m=np.arange(j,-j-1,-1,dtype=float)
Jz=np.diag(m).astype(complex)
Jp=np.zeros((5,5),complex)
for i in range(4):
    mm=m[i+1]
    Jp[i,i+1]=np.sqrt(j*(j+1)-mm*(mm+1))
Jm=Jp.conj().T
Jx=(Jp+Jm)/2
Jy=(Jp-Jm)/(2j)
I5=np.eye(5,dtype=complex)
def k3(A,B,C): return np.kron(np.kron(A,B),C)

Jxt=k3(Jx,I5,I5)+k3(I5,Jx,I5)+k3(I5,I5,Jx)
Jyt=k3(Jy,I5,I5)+k3(I5,Jy,I5)+k3(I5,I5,Jy)
Jzt=k3(Jz,I5,I5)+k3(I5,Jz,I5)+k3(I5,I5,Jz)
C=Jxt@Jxt+Jyt@Jyt+Jzt@Jzt
I125=np.eye(125,dtype=complex)
spec=[0,2,6,12,20,30,42]

def projector(lam):
    P=np.eye(125,dtype=complex)
    den=1.0
    for mu in spec:
        if mu!=lam:
            P=P@(C-mu*I125)
            den*=lam-mu
    return P/den,int(round(den))

P0,d0=projector(0)
P6,d6=projector(6)
eta=P6-P0

evals,evecs=np.linalg.eigh(C)
u=evecs[:,np.argmin(np.abs(evals))]
u/=np.linalg.norm(u)

Jx12=np.kron(Jx,I5)+np.kron(I5,Jx)
Jy12=np.kron(Jy,I5)+np.kron(I5,Jy)
Jz12=np.kron(Jz,I5)+np.kron(I5,Jz)
C12=Jx12@Jx12+Jy12@Jy12+Jz12@Jz12
e12,v12=np.linalg.eigh(C12)
s=v12[:,np.argmin(np.abs(e12))]
s/=np.linalg.norm(s)
W=np.column_stack([np.kron(s,I5[:,k]) for k in range(5)])

Q=np.diag([1.,0.,-1.])
A=[
 np.array([[0,0,0],[0,0,-1],[0,1,0]],float),
 np.array([[0,0,1],[0,0,0],[-1,0,0]],float),
 np.array([[0,-1,0],[1,0,0],[0,0,0]],float),
]
D=[a@Q-Q@a for a in A]
Sb=[
 np.diag([1.,-1.,0.])/np.sqrt(2),
 np.diag([1.,1.,-2.])/np.sqrt(6),
 np.array([[0,1,0],[1,0,0],[0,0,0]],float)/np.sqrt(2),
 np.array([[0,0,1],[0,0,0],[1,0,0]],float)/np.sqrt(2),
 np.array([[0,0,0],[0,0,1],[0,1,0]],float)/np.sqrt(2),
]
coords=np.column_stack([[np.trace(B.T@Di) for B in Sb] for Di in D]).astype(complex)
S125=W@coords
G3=np.real_if_close(S125.conj().T@S125).astype(float)
B4=np.column_stack([u,S125])
g4=np.real_if_close(B4.conj().T@eta@B4).astype(float)
eg=np.linalg.eigvalsh(g4)

ck("P0 projector",np.linalg.norm(P0@P0-P0)<TOL)
ck("P6 projector",np.linalg.norm(P6@P6-P6)<TOL)
ck("P0 P6 orthogonal",np.linalg.norm(P0@P6)<TOL)
ck("rank P0 = 1",np.sum(np.linalg.eigvalsh((P0+P0.conj().T)/2)>.5)==1)
ck("rank P6 = 25",np.sum(np.linalg.eigvalsh((P6+P6.conj().T)/2)>.5)==25)
ck("P0 u = u",np.linalg.norm(P0@u-u)<TOL)
ck("P6 u = 0",np.linalg.norm(P6@u)<TOL)
ck("W in E6",np.linalg.norm(P6@W-W)<1e-9)
ck("P0 W = 0",np.linalg.norm(P0@W)<1e-9)
ck("G3 = diag(2,8,2)",np.allclose(G3,np.diag([2.,8.,2.]),atol=TOL))
ck("g4 = diag(-1,2,8,2)",np.allclose(g4,np.diag([-1.,2.,8.,2.]),atol=TOL))
ck("signature (-,+,+,+)",np.sum(eg<-TOL)==1 and np.sum(eg>TOL)==3)

print("P0 denominator =",d0)
print("P6 denominator =",d6)
print("G3 =",G3)
print("g4 =",g4)
print("eigenvalues =",eg)
print(f"TOTAL: {sum(checks.values())}/{len(checks)} PASS")
