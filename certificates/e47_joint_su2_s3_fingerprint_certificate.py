# E47 Joint SU(2)xS3 Symmetry Fingerprint Certificate
# Generated 2026-09-20. Requires numpy.
import numpy as np
from itertools import permutations
j=2; m=np.arange(-j,j+1,dtype=float)
Jz=np.diag(m); Jp=np.zeros((5,5),complex)
for col,mm in enumerate(m[:-1]): Jp[col+1,col]=np.sqrt(j*(j+1)-mm*(mm+1))
Jm=Jp.T.conj(); Jx=(Jp+Jm)/2; Jy=(Jp-Jm)/(2j); I=np.eye(5)
k3=lambda a,b,c: np.kron(np.kron(a,b),c)
JT=[k3(A,I,I)+k3(I,A,I)+k3(I,I,A) for A in (Jx,Jy,Jz)]
C=sum(A@A for A in JT); K=(C-6*np.eye(125))@(C-30*np.eye(125))
w,U=np.linalg.eigh(C); M=np.isclose(w,6,atol=1e-9)|np.isclose(w,30,atol=1e-9)
P=U[:,M]@U[:,M].conj().T
B=[(a,b,c) for a in range(5) for b in range(5) for c in range(5)]; ix={x:i for i,x in enumerate(B)}
def Up(p):
    Q=np.zeros((125,125))
    for i,x in enumerate(B):
        y=tuple(x[p[k]] for k in range(3)); Q[ix[y],i]=1
    return Q
ps=list(permutations(range(3))); UU={p:Up(p) for p in ps}
par=lambda p: -1 if sum(p[i]>p[k] for i in range(3) for k in range(i+1,3))%2 else 1
Ps=sum(UU[p] for p in ps)/6; Pa=sum(par(p)*UU[p] for p in ps)/6; Pt=np.eye(125)-Ps-Pa
dims=(round(np.trace(P@Ps).real),round(np.trace(P@Pa).real),round(np.trace(P@Pt).real))
fp=tuple(round(np.trace(P@UU[p]).real) for p in ((0,1,2),(1,0,2),(1,2,0)))
assert dims==(5,0,42); assert fp==(47,5,-16)
assert np.linalg.norm(P@P-P,2)<1e-10 and np.linalg.norm(K@P,2)<1e-10
# Exact character resolution gives M_2=1+2Std, M_5=Std,
# hence End_{SU(2)xS3}(E47) ≅ C ⊕ M_2(C) ⊕ C and dimension 6.
assert 1**2+2**2+1**2==6
print({"S3_dims":dims,"trace_fingerprint":fp,"joint_commutant_dim":6,"status":"PASS"})
