#!/usr/bin/env python3
"""
ARRIVAL MATHEMATICS / E47
First-Principles Spectral Projection Theorem + Quantum-State Validation

Constructs the 125-dimensional carrier V_2^{⊗3} directly from spin-2
SU(2) generators, builds C = J_tot^2, defines
K = (C-6I)(C-30I), and validates the E47 projector and optimal
Richardson/spectral contraction without typing in the Casimir spectrum.
"""
import numpy as np

TOL = 2e-10

def spin_j(j):
    m = np.arange(j, -j-1, -1, dtype=float)
    d = len(m)
    Jz = np.diag(m)
    Jp = np.zeros((d,d), complex)
    for col in range(1,d):
        mm = m[col]
        Jp[col-1,col] = np.sqrt(j*(j+1)-mm*(mm+1))
    Jm = Jp.conj().T
    Jx = (Jp+Jm)/2
    Jy = (Jp-Jm)/(2j)
    return Jx,Jy,Jz

def kron3(a,b,c): return np.kron(np.kron(a,b),c)

Jx,Jy,Jz = spin_j(2)
I5=np.eye(5)
JX=kron3(Jx,I5,I5)+kron3(I5,Jx,I5)+kron3(I5,I5,Jx)
JY=kron3(Jy,I5,I5)+kron3(I5,Jy,I5)+kron3(I5,I5,Jy)
JZ=kron3(Jz,I5,I5)+kron3(I5,Jz,I5)+kron3(I5,I5,Jz)
C=JX@JX+JY@JY+JZ@JZ
I=np.eye(125)
K=(C-6*I)@(C-30*I)
B=K@K

lam,U=np.linalg.eigh(C)
rounded=np.rint(lam).astype(int)
expected={0:1,2:9,6:25,12:28,20:27,30:22,42:13}
got={v:int(np.sum(rounded==v)) for v in sorted(set(rounded))}
mask=(rounded==6)|(rounded==30)
P=U[:,mask]@U[:,mask].conj().T

b=np.linalg.eigvalsh(B)
pos=b[b>1e-7]
Delta=float(pos.min()); M=float(pos.max())
eps=2/(Delta+M)
q=(M-Delta)/(M+Delta)
Gamma=I-eps*B

checks=[]
def check(name, ok, value=None):
    checks.append((name,bool(ok),value))

check("carrier_dimension", C.shape==(125,125), C.shape)
check("su2_commutator_xy", np.linalg.norm(JX@JY-JY@JX-1j*JZ)<TOL,
      np.linalg.norm(JX@JY-JY@JX-1j*JZ))
check("casimir_spectrum", got==expected, got)
check("E47_rank", np.linalg.matrix_rank(P,tol=1e-8)==47, np.linalg.matrix_rank(P,tol=1e-8))
check("P_idempotent", np.linalg.norm(P@P-P)<1e-10, np.linalg.norm(P@P-P))
check("KP_zero", np.linalg.norm(K@P)<2e-9, np.linalg.norm(K@P))
check("spectral_gap", abs(Delta-11664)<1e-6, Delta)
check("spectral_max", abs(M-186624)<1e-6, M)
check("optimal_step", abs(eps-1/99144)<1e-14, eps)
check("optimal_rate", abs(q-15/17)<1e-14, q)

n=220
Gn=np.linalg.matrix_power(Gamma,n)
operr=np.linalg.norm(Gn-P,2)
check("Gamma220_to_P47", abs(operr-(15/17)**n)<2e-11, operr)

rng=np.random.default_rng(20261003)
N=20000
weights=[]
max_state_err=0.0
max_kernel_drift=0.0
for _ in range(N):
    psi=rng.normal(size=125)+1j*rng.normal(size=125)
    psi/=np.linalg.norm(psi)
    target=P@psi
    out=Gn@psi
    max_state_err=max(max_state_err,np.linalg.norm(out-target))
    max_kernel_drift=max(max_kernel_drift,np.linalg.norm(P@(Gamma@psi)-P@psi))
    weights.append(float(np.vdot(target,target).real))
weights=np.array(weights)
mean=float(weights.mean())
se=float(weights.std(ddof=1)/np.sqrt(N))
theory=47/125
z=(mean-theory)/se
check("haar_mean_within_3SE", abs(z)<3, (mean,se,z))
check("random_state_projection_error", max_state_err<2e-12, max_state_err)
check("kernel_invariance", max_kernel_drift<2e-10, max_kernel_drift)

print("ARRIVAL MATHEMATICS / E47 — FIRST-PRINCIPLES QUANTUM VALIDATION")
print("="*72)
for name,ok,value in checks:
    print(("PASS" if ok else "FAIL"), name, value)
print("-"*72)
print("Delta =",Delta)
print("M =",M)
print("epsilon* =",eps," = 1/99144")
print("q* =",q," = 15/17")
print("||Gamma^220-P47||_2 =",operr)
print("Haar mean =",mean,"theory =",theory,"SE =",se,"z =",z)
print("max state projection error =",max_state_err)
print("RESULT:",sum(x[1] for x in checks),"/",len(checks),"PASS")
raise SystemExit(0 if all(x[1] for x in checks) else 1)
