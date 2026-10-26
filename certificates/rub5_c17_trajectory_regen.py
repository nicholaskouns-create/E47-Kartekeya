import numpy as np
from fractions import Fraction as F

def spin_ops(j):
    d=int(round(2*j+1)); m=np.array([j-k for k in range(d)])
    Jz=np.diag(m).astype(complex); Jp=np.zeros((d,d),complex)
    for k in range(1,d):
        mm=m[k]; Jp[k-1,k]=np.sqrt(j*(j+1)-mm*(mm+1))
    Jm=Jp.conj().T
    return 0.5*(Jp+Jm), -0.5j*(Jp-Jm), Jz

jx,jy,jz=spin_ops(2); I5=np.eye(5,dtype=complex)
kr=lambda a,b,c: np.kron(np.kron(a,b),c)
Jx=kr(jx,I5,I5)+kr(I5,jx,I5)+kr(I5,I5,jx)
Jy=kr(jy,I5,I5)+kr(I5,jy,I5)+kr(I5,I5,jy)
Jz=kr(jz,I5,I5)+kr(I5,jz,I5)+kr(I5,I5,jz)
I=np.eye(125,dtype=complex)
C=Jx@Jx+Jy@Jy+Jz@Jz
K=(C-6*I)@(C-30*I)
ev,V=np.linalg.eigh(K); nul=np.abs(ev)<1e-8
P=V[:,nul]@V[:,nul].conj().T
NORM=99144; Gam=I-(K@K)/NORM
rho_c=F(15,17)**2
print("exact per-step odds factor (15/17)^2 =",rho_c,"=",float(rho_c))

rng=np.random.default_rng(17)
A=rng.standard_normal((125,125))+1j*rng.standard_normal((125,125))
r=A@A.conj().T; r/=np.trace(r).real

steps=[0,1,2,5,10,20,50,100,150]
rows=[]; R0=None
for k in range(151):
    if k in steps:
        Ck=float(np.trace(P@r).real); Rk=max(1.0-Ck,0.0)
        if R0 is None: R0=Rk; odds0=R0/(1-R0)
        odds=Rk/(1-Rk) if Rk<1 else float('inf')
        bound=odds0*float(rho_c)**k
        rows.append((k,Ck,Rk,odds,bound,odds<=bound*(1+1e-9)))
    r=Gam@r@Gam; t=np.trace(r).real
    if t>0: r/=t

print(f"{'k':>4} {'C_k':>18} {'R_k':>12} {'odds R/(1-R)':>14} {'bound':>12} {'holds':>6}")
allok=True
for k,Ck,Rk,od,bd,ok in rows:
    allok&=ok
    print(f"{k:4d} {Ck:18.15f} {Rk:12.3e} {od:14.3e} {bd:12.3e} {str(ok):>6}")
print("\nodds bound holds at every tabulated step:",allok)
print("naive (15/17)^(2k) bound on R_k itself holds everywhere:",
      all(Rk<=float(rho_c)**k*(1+1e-9) for k,_,Rk,_,_,_ in rows))
