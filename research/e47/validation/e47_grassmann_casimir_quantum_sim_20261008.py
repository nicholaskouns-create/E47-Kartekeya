#!/usr/bin/env python3
import numpy as np
from numpy.linalg import eigh, norm

# 125-dimensional classical state-vector simulation of the finite quantum Hilbert space.
d=5
m=np.arange(-2,3,dtype=float)
Jz=np.diag(m)
Jp=np.zeros((d,d)); Jm=np.zeros((d,d))
for i,mi in enumerate(range(-2,3)):
    if i<4: Jp[i+1,i]=2-mi
    if i>0: Jm[i-1,i]=2+mi
G5=np.diag([1,.25,1/6,.25,1.])
I5=np.eye(5)
kron3=lambda A,B,C: np.kron(np.kron(A,B),C)
def total(X):
    return kron3(X,I5,I5)+kron3(I5,X,I5)+kron3(I5,I5,X)
Tz,Tp,Tm=map(total,(Jz,Jp,Jm))
G=kron3(G5,G5,G5)
C=Tz@Tz+.5*(Tp@Tm+Tm@Tp)
I=np.eye(125)
K=(C-6*I)@(C-30*I)
# G-orthonormalize via S=G^(1/2), where transformed C is Euclidean Hermitian.
gdiag=np.diag(G)
S=np.diag(np.sqrt(gdiag)); Sinv=np.diag(1/np.sqrt(gdiag))
Ct=S@C@Sinv
w,U=eigh((Ct+Ct.T)/2)
sel=(np.isclose(w,6,atol=1e-9)|np.isclose(w,30,atol=1e-9))
Pt=U[:,sel]@U[:,sel].T
P=Sinv@Pt@S
assert np.linalg.matrix_rank(P,tol=1e-8)==47
assert norm(P@P-P)<1e-10
assert norm(P.T@G-G@P)<1e-10
assert norm(K@P)<1e-9
print('PASS 125-dimensional complex quantum state simulation')
print('PASS G-orthogonal projector rank 47 and metric adjoint')

# Seeded complex state and G normalization.
rng=np.random.default_rng(47)
psi=rng.normal(size=125)+1j*rng.normal(size=125)
gnorm=lambda x: np.sqrt(np.real(np.conjugate(x)@(G@x)))
psi/=gnorm(psi)
pp=np.real(np.conjugate(psi)@(G@(P@psi)))
proj_norm=gnorm(P@psi)**2
assert abs(pp-proj_norm)<1e-11
print('PASS Born probability <psi,Ppsi>_G = ||Ppsi||_G^2')

eps=1/99144
Gamma=I-eps*(K@K)
assert norm(Gamma@P-P)<1e-9
assert norm(K@P)<1e-9
print('PASS fixed-point Gamma P = P and K P = 0')
# Compute complementary eigenvalues from exact Casimir sectors.
cs=np.array([0,2,12,20,42],dtype=float)
kvals=(cs-6)*(cs-30)
gvals=1-eps*kvals*kvals
rho=np.max(np.abs(gvals))
assert abs(rho-15/17)<1e-14
print('PASS complementary spectral radius 15/17')

n=220
state_n=np.linalg.matrix_power(Gamma,n)@psi
state_p=P@psi
err=gnorm(state_n-state_p)
bound=(15/17)**n
# State error <= operator norm bound times complement norm <= bound.
assert err <= bound*(1+1e-6)
print('PASS state convergence at n=220')
print(f'probability={pp:.12f}; exact_norm_bound={bound:.12e}; state_error={err:.12e}')
