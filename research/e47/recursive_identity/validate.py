import numpy as np
from itertools import permutations
from fractions import Fraction
m=np.arange(-2,3)
Jz=np.diag(m)
Jp=np.diag(np.sqrt(6-m[:-1]*(m[:-1]+1)), -1)
Jx=(Jp+Jp.T)/2
Jy=(Jp-Jp.T)/(2j)
I=np.eye(5)
def total(j): return np.kron(np.kron(j,I),I)+np.kron(np.kron(I,j),I)+np.kron(np.kron(I,I),j)
C=sum(total(j)@total(j) for j in (Jx,Jy,Jz))
K=(C-6*np.eye(125))@(C-30*np.eye(125))
A=K@K
Pi=sum(np.eye(125)[np.arange(125).reshape(5,5,5).transpose(p).ravel()] for p in permutations(range(3)))/6
B=A+11664*(np.eye(125)-Pi)
rng=np.random.default_rng(47)
for op,rank in [(A,47),(B,5)]:
    w,V=np.linalg.eigh(op)
    mask=abs(w)<1e-6
    assert mask.sum()==rank
    assert np.isclose(w[~mask].min(),11664)
    assert np.isclose(w.max(),186624)
    P=V[:,mask]@V[:,mask].conj().T
    t=1-w/99144
    t[mask]=1
    T=(V*t)@V.conj().T
    assert np.linalg.norm(P@T-P)<1e-10
    assert np.isclose(max(abs(t[~mask])),15/17)
    x=rng.normal(size=125)+1j*rng.normal(size=125)
    y=P@x
    z=V@(t**220*(V.conj().T@x))
    assert np.linalg.norm(z-y)<2e-11
    D=(V*np.sqrt(np.maximum(0,1-t*t)))@V.conj().T
    U=np.block([[T,D],[D,-T]])
    U8=np.eye(256,dtype=complex); U8[:250,:250]=U
    err=np.linalg.norm(U8.conj().T@U8-np.eye(256))
    assert err<1e-9
    print(rank, 'convergence',np.linalg.norm(z-y),'unitarity',err)
