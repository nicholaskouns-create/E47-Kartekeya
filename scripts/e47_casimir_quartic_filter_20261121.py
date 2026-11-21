#!/usr/bin/env python3
"""E47 authoritative spin-2 Casimir quartic filter: self-contained NumPy certificate."""
import numpy as np
j=2
ms=np.arange(-2,3)
Jz=np.diag(ms).astype(complex)
Jp=np.zeros((5,5),complex)
for col,m in enumerate(ms[:-1]): Jp[col+1,col]=np.sqrt(j*(j+1)-m*(m+1))
Jm=Jp.conj().T; Jx=(Jp+Jm)/2; Jy=(Jp-Jm)/(2j)
I5=np.eye(5,dtype=complex)
def lift(B): return np.kron(np.kron(B,I5),I5)+np.kron(np.kron(I5,B),I5)+np.kron(np.kron(I5,I5),B)
X,Y,Z=map(lift,(Jx,Jy,Jz))
C=X@X+Y@Y+Z@Z
I=np.eye(125,dtype=complex);K=(C-6*I)@(C-30*I);A=K/432
A2=A@A;Q=I-2176/353*A2+2048/353*A2@A2
P=Q+1j*(272/353)*A2
cs=np.array([0,2,6,12,20,30,42]);mult=np.array([1,9,25,28,27,22,13])
ks=(cs-6)*(cs-30);s=ks/432
q=1-2176/353*s*s+2048/353*s**4
Proj=np.eye(125,dtype=complex)
for lam in (11664,12544,19600,32400,186624):Proj=Proj@(I-(K@K)/lam)
r=225/353
print('J mult C K normalized_signal Q4')
for jj,nn,c,k,ss,qq in zip(range(7),mult,cs,ks,s,q):print(jj,nn,c,k,ss,qq)
print('Casimir spectrum error',max(abs(np.sort(np.linalg.eigvalsh(C))-np.repeat(cs,mult))))
print('projector defect',np.linalg.norm(Proj@Proj-Proj,2))
print('retention defect',np.linalg.norm(Q@Proj-Proj,2))
print('one-stage error',np.linalg.norm(Q-Proj,2))
print('dilation contraction min eigenvalue',np.linalg.eigvalsh(I-P.conj().T@P).min())
assert np.max(abs(np.sort(np.linalg.eigvalsh(C))-np.repeat(cs,mult)))<1e-10
assert np.linalg.norm(Proj@Proj-Proj,2)<1e-9
assert np.linalg.norm(Q@Proj-Proj,2)<1e-9
assert np.isclose(np.linalg.norm(Q-Proj,2),r,atol=1e-9)
assert np.linalg.eigvalsh(I-P.conj().T@P).min()>-1e-9
print('PASS: exact sector limit ||Q^n-P47||2=(225/353)^n')
