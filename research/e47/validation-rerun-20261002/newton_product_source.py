#!/usr/bin/env python3
"""MC-E47-NEWTON-MEAN-PRODUCT-20260930-001: Newton–Mean x E47 validator."""
import numpy as np, math
from numpy.linalg import norm,eigvalsh,eigvals
j=2;m=np.array([2,1,0,-1,-2],float);Jz=np.diag(m).astype(complex);Jp=np.zeros((5,5),complex)
for c,mc in enumerate(m):
    mp=mc+1
    if mp<=j:
        r=np.where(m==mp)[0]
        if len(r): Jp[r[0],c]=math.sqrt(j*(j+1)-mc*(mc+1))
Jm=Jp.conj().T;Jx=(Jp+Jm)/2;Jy=(Jp-Jm)/(2j);I5=np.eye(5,dtype=complex)
k3=lambda A,B,C:np.kron(np.kron(A,B),C)
Js=[k3(A,I5,I5)+k3(I5,A,I5)+k3(I5,I5,A) for A in (Jx,Jy,Jz)]
C=sum(A@A for A in Js);I=np.eye(125,dtype=complex);K=(C-6*I)@(C-30*I);K2=K@K
w,U=np.linalg.eigh(C);s=np.isclose(w,6,atol=1e-9)|np.isclose(w,30,atol=1e-9);P=U[:,s]@U[:,s].conj().T;Q=I-P
G=I-K2/99144;q=15/17
a0=4.;rt=2.;Bn=lambda x:.5*(x+a0/x);x=3.1;quad=abs((Bn(x)-rt)-(x-rt)**2/(2*x))
a,b,k=4.,9.,.5;A=1-k*k;Bb=-k*(a+b);Cc=-a*b;p=(-Bb+math.sqrt(Bb*Bb-4*A*Cc))/(2*A)
r=math.sqrt(a+k*p);s0=math.sqrt(b+k*p);T=lambda r,s:np.array([.5*(r+a/r+k*s),.5*(s+b/s+k*r)])
J=.5*np.array([[1-a/r**2,k],[k,1-b/s0**2]]);ev=np.sort(np.real_if_close(eigvals(J)));tau=k*(a+b)/(2*p)+k*k
ge=eigvalsh((G+G.conj().T)/2);ones=np.sum(np.isclose(ge,1,atol=1e-10));rhoQ=np.max(np.abs(ge[~np.isclose(ge,1,atol=1e-10)]))
law=max(abs(norm(np.linalg.matrix_power(G,n)-P,2)-q**n) for n in [1,2,5,10,25,50])
rng=np.random.default_rng(47);psi=rng.normal(size=125)+1j*rng.normal(size=125);psi/=norm(psi);psiE=P@psi
fk=math.hypot(abs(rt*rt-a0),norm(K@psiE));fm=math.hypot(abs(Bn(rt)-rt),norm(G@psiE-psiE))
rq=np.outer(psi,psi.conj());rd=P@rq@P+Q@rq@Q;tp=norm(P@P+Q@Q-I);tr=abs(np.trace(rd)-1);herm=norm(rd-rd.conj().T);mine=np.min(eigvalsh((rd+rd.conj().T)/2));cross=norm(P@rd@Q)+norm(Q@rd@P)
pe=psiE/norm(psiE);re=np.outer(pe,pe.conj());inv=norm(P@re@P+Q@re@Q-re)
checks=[abs(np.trace(P).real-47)<1e-8,abs(np.trace(Q).real-78)<1e-8,norm(P@P-P)<1e-10,norm(K@P)<1e-8,norm(G@P-P)<1e-8,ones==47,abs(rhoQ-q)<1e-12,quad<1e-14,fk<1e-10,fm<1e-10,law<1e-10,norm(T(r,s0)-[r,s0])<1e-12,abs((r*r-s0*s0)-(a-b))<1e-12,abs((1-k*k)*p*p-k*(a+b)*p-a*b)<1e-12,abs(ev[0])<1e-12,abs(ev[1]-tau)<1e-12,abs(max(abs(tau),q)-q)<1e-15,tp<1e-12,tr<1e-12,herm<1e-12,mine>-1e-12,cross<1e-12,inv<1e-12]
print("MC-E47-NEWTON-MEAN-PRODUCT-20260930-001");print(f"rank(P),rank(Q)={np.trace(P).real:.0f},{np.trace(Q).real:.0f}");print(f"rho(Gamma|Q)={rhoQ:.15f}; 15/17={q:.15f}");print(f"tau={tau:.15f}; joint_rate={max(abs(tau),q):.15f}");print(f"TOTAL: {sum(checks)}/{len(checks)} PASS");assert all(checks)
