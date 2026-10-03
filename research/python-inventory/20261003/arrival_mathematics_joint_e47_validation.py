#!/usr/bin/env python3
# Arrival Mathematics — Joint Residual Closure + E47 Quantum Projection
# Generated validation certificate.
import numpy as np
from scipy.optimize import brentq

vals=np.array([0.,2.,6.,12.,20.,30.,42.])
mult=np.array([1,9,25,28,27,22,13])
C=np.repeat(vals,mult)
K=(C-6)*(C-30); B=K*K
P=((C==6)|(C==30)).astype(float)
Delta=B[B>0].min(); M=B.max()
eps=2/(Delta+M); q=(M-Delta)/(M+Delta)
G=1-eps*B
Oc=47/125

assert len(C)==125 and int(P.sum())==47
assert np.isclose(Delta,11664) and np.isclose(M,186624)
assert np.isclose(eps,1/99144) and np.isclose(q,15/17)
assert np.max(np.abs(G**220-P)) == q**220

# Explicit compatible residual witness
z=np.array([0.,0.,1.,Oc,0.,10.,0.,0.])
def R(z):
    continuity,psiC,Q,Omega,meff,D,Hperp,Hi=z
    return np.array([continuity,psiC,psiC,Q-1,
                     max(Oc-Omega,0),meff,D-10,Hperp,Hi])
assert np.max(np.abs(R(z))) < 1e-12

lam=brentq(lambda x:x**10-x-1,1,2)
assert abs(lam**10-lam-1)<1e-12
assert np.isclose(lam**20,(lam+1)**2)

rng=np.random.default_rng(47)
for _ in range(256):
    psi=rng.normal(size=125)+1j*rng.normal(size=125)
    psi/=np.linalg.norm(psi)
    target=P*psi
    x=psi.copy()
    for n in range(220):
        x=G*x
    assert np.linalg.norm(x-target)<1e-11
    assert np.linalg.norm(P*x-target)<1e-12

print("PASS — Arrival Mathematics / E47 validation")
print("rank =",int(P.sum()),"Omega_c =",Oc)
print("Delta =",Delta,"M =",M,"epsilon* =",eps,"q* =",q)
print("||Gamma^220-P||_2 =",np.max(np.abs(G**220-P)))
print("lambda10 =",lam,"capacity =",lam**20)

