#!/usr/bin/env python3
"""Bi-SOC local-to-collective validator. Reduced-Hamiltonian quantum benchmark."""
import numpy as np
from scipy.linalg import eigh, expm
from scipy.optimize import linear_sum_assignment
ETAS=np.array([0.,.25,.50,.75,1.]); NB,NP=3,9; N=12
M=np.diag([209.]*NB+[12.,14.,16.,12.,14.,16.,12.,14.,16.]); Mi=np.diag(1/np.sqrt(np.diag(M)))
rng=np.random.default_rng(47); A=rng.normal(size=(N,N)); H0=A.T@A+4*np.eye(N)
B=rng.normal(size=(NB,NB)); dBB=B.T@B*.22; BP=rng.normal(size=(NB,NP))*.055
C=rng.normal(size=(NP,NP)); dPP=C.T@C*.008; dH=np.block([[dBB,BP],[BP.T,dPP]])
def H(e): return H0+e*dH
def D(e): return Mi@H(e)@Mi
def modes(e): w2,V=eigh(D(e)); return np.sqrt(np.clip(w2,0,None)),V
# BB/BP/PP, overlap tracking, participation, dω/dη and unitary quantum benchmark
delta=H(1)-H(0); norms=[np.linalg.norm(delta[:NB,:NB]),np.linalg.norm(delta[:NB,NB:]),np.linalg.norm(delta[NB:,NB:])]
w,V=modes(.5); h=1e-5; dD=(D(.5+h)-D(.5-h))/(2*h)
dw=np.array([(V[:,i]@dD@V[:,i])/(2*w[i]) for i in range(N)])
LB=np.sum(abs(V[:NB,:])**2,axis=0); LP=1-LB; PR=1/np.sum(abs(V)**4,axis=0)
U=expm(-1j*(D(.5)/np.linalg.norm(D(.5),2))*.7)
checks=[all(np.min(np.linalg.eigvalsh(D(e)))>0 for e in ETAS),all(x>0 for x in norms),
        np.max(abs(LB+LP-1))<1e-12,np.linalg.norm(U.conj().T@U-np.eye(N))<1e-12]
print("MC-BI-SOC-BIOPHYS-20261002-001", "PASS" if all(checks) else "FAIL")
print("BB/BP/PP",norms); print("mode omega domega/deta L_Bi L_bio PR")
for i in range(N): print(i,w[i],dw[i],LB[i],LP[i],PR[i])
assert all(checks)
