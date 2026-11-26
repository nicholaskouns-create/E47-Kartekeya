import numpy as np
from numpy.linalg import eigvalsh, matrix_rank, norm
s,d=2,5
m=np.arange(s,-s-1,-1,dtype=float)
Jz=np.diag(m)
Jp=np.zeros((d,d),complex)
for i in range(d):
    v=s*(s+1)-m[i]*(m[i]+1)
    if v>0: Jp[i-1,i]=np.sqrt(v)
Jx,Jy=(Jp+Jp.conj().T)/2,(Jp-Jp.conj().T)/(2j)
I5=np.eye(d)
assert np.allclose(Jx@Jy-Jy@Jx,1j*Jz)
assert np.allclose(Jx@Jx+Jy@Jy+Jz@Jz,6*I5)
k3=lambda A,B,C: np.kron(np.kron(A,B),C)
J=[k3(P,I5,I5)+k3(I5,P,I5)+k3(I5,I5,P) for P in (Jx,Jy,Jz)]
C=sum(P@P for P in J)
ev,mult=np.unique(np.round(eigvalsh(C),6),return_counts=True)
assert np.allclose(ev,[0,2,6,12,20,30,42])
assert list(mult)==[1,9,25,28,27,22,13]
assert np.isclose(np.trace(C),2250)
assert np.isclose(np.trace(C@C),58500)
mu=np.trace(C).real/125
s2=np.trace(C@C).real/125-mu**2
assert np.isclose(mu,18) and np.isclose(s2,144)
I125=np.eye(125)
K=(C-6*I125)@(C-30*I125)
K2=K@K
assert matrix_rank(K,tol=1e-6)==78
specK2=np.unique(np.round(eigvalsh(K2)))
assert np.allclose(specK2,[0,11664,12544,19600,32400,186624])
sigma=[np.array([[0,1],[1,0]]),np.array([[0,-1j],[1j,0]]),np.diag([1,-1])]
O2,I2=np.zeros((2,2)),np.eye(2)
g0=np.block([[I2,O2],[O2,-I2]])
g=[g0]+[np.block([[O2,a],[-a,O2]]) for a in sigma]
g5=1j*g[0]@g[1]@g[2]@g[3]
eta=np.diag([1,-1,-1,-1])
I4=np.eye(4)
for a in range(4):
    for b in range(4):
        assert np.allclose(g[a]@g[b]+g[b]@g[a],2*eta[a,b]*I4)
    assert np.allclose(g5@g[a]+g[a]@g5,0)
assert np.allclose(g5@g5,I4)
alpha=[g0@g[i] for i in (1,2,3)]
beta=-1j*g0@g5
assert np.allclose(beta,beta.conj().T) and np.allclose(beta@beta,I4)
for a in alpha: assert np.allclose(a@beta+beta@a,0)
w,V=np.linalg.eigh(K2)
P47=V[:,w<1e-6]@V[:,w<1e-6].conj().T
assert np.isclose(np.trace(P47),47)
assert np.allclose(P47@P47,P47,atol=1e-8)
P=np.kron(I4,P47)
assert matrix_rank(P,tol=1e-6)==188
for Pi in ((I4+g5)/2,(I4-g5)/2):
    assert matrix_rank(np.kron(Pi,P47),tol=1e-6)==94
nz=specK2[specK2>1]
eps=2/(nz.min()+nz.max())
rho=(nz.max()-nz.min())/(nz.max()+nz.min())
assert np.isclose(eps,1/99144) and np.isclose(rho,15/17)
G=np.eye(500)-eps*np.kron(I4,K2)
for n in (10,50,100):
    actual=norm(np.linalg.matrix_power(G,n)-P,2)
    pred=rho**n
    assert np.isclose(actual,pred,rtol=1e-7,atol=1e-12)
    print(f"n={n:3d}  residual={actual:.3e}  predicted={pred:.3e}  ratio={actual/pred:.6f}")
assert np.isclose(np.trace(P)/500,0.376)
print("All implemented assertions passed")
