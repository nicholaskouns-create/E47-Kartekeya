#!/usr/bin/env python3
import numpy as np, json, math
from numpy.linalg import eigh, norm

j=2
m=np.array([2,1,0,-1,-2],dtype=float)
Jz=np.diag(m)
Jp=np.zeros((5,5),complex)
for col,mc in enumerate(m):
    mt=mc+1
    if mt<=j and mt in m:
        row=int(np.where(m==mt)[0][0])
        Jp[row,col]=math.sqrt(j*(j+1)-mc*(mc+1))
Jm=Jp.T.conj(); Jx=(Jp+Jm)/2; Jy=(Jp-Jm)/(2j)
I=np.eye(5)
kron3=lambda A,B,C: np.kron(np.kron(A,B),C)
Jtot=[]
for J in (Jx,Jy,Jz):
    Jtot.append(kron3(J,I,I)+kron3(I,J,I)+kron3(I,I,J))
C=sum(A@A for A in Jtot)
K=(C-6*np.eye(125))@(C-30*np.eye(125))
w,U=eigh(K)
mask=np.abs(w)<1e-9
P=U[:,mask]@U[:,mask].conj().T
K2=K@K
vals=np.linalg.eigvalsh(K2)
pos=vals[vals>1e-8]
Delta=float(pos.min()); M=float(pos.max())
eps=2/(Delta+M)
Gamma=np.eye(125)-eps*K2
rho=float(max(abs(1-eps*pos)))
X=np.eye(125,dtype=complex)
for _ in range(220): X=Gamma@X
err=float(norm(X-P,2))
checks={
 'su2_j2': bool(norm(Jx@Jy-Jy@Jx-1j*Jz)<1e-12),
 'rank_P47': bool(round(np.trace(P).real)==47),
 'projector': bool(norm(P@P-P)<1e-10),
 'kernel': bool(norm(K@P)<1e-9),
 'gap_11664': bool(abs(Delta-11664)<1e-6),
 'norm_186624': bool(abs(M-186624)<1e-6),
 'eps_1_99144': bool(abs(eps-1/99144)<1e-15),
 'rho_15_17': bool(abs(rho-15/17)<1e-12),
 'gamma_220_close': bool(err<1e-10)
}
out={'checks':checks,'passed':all(checks.values()),'rank':int(round(np.trace(P).real)),'Delta':Delta,'M':M,'epsilon':eps,'rho_star':rho,'gamma220_spectral_error':err}
print(json.dumps(out,indent=2))
