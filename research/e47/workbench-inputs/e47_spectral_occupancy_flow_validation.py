#!/usr/bin/env python3
"""
E47 Spectral Occupancy Flow Theorem.

For Q=K^2 >= 0, P=proj ker(Q), H=I-P, and dx/dt=-Qx,
define Omega=||Px||^2/||x||^2 and

    lambda_eff = <Hx,QHx>/||Hx||^2.

Then exactly:

    dOmega/dt = 2 lambda_eff Omega(1-Omega),
    d/dt logit(Omega) = 2 lambda_eff,

with lambda_gap <= lambda_eff <= lambda_max.

For E47:
    lambda_gap = 11664,
    lambda_max = 186624,
    rank(P)/N = 47/125 = 0.376.
"""
import numpy as np

rng=np.random.default_rng(47125)
spectrum={0:1,2:9,6:25,12:28,20:27,30:22,42:13}
c=np.concatenate([np.full(m,l,float) for l,m in spectrum.items()])
q=((c-6)*(c-30))**2
ker=q==0
comp=~ker
gap=q[comp].min()
qmax=q[comp].max()

x0=rng.normal(size=len(c))+1j*rng.normal(size=len(c))
x0/=np.linalg.norm(x0)
w0=np.abs(x0)**2
a=w0[ker].sum()

tau=np.linspace(0,15,15001)
t=tau/gap
W=w0[None,:]*np.exp(-2*t[:,None]*q[None,:])
b=W[:,comp].sum(axis=1)
Omega=a/(a+b)
lam=(W[:,comp]*q[comp]).sum(axis=1)/b

Omega_dot=2*a*(W[:,comp]*q[comp]).sum(axis=1)/(a+b)**2
assert np.max(np.abs(Omega_dot-2*lam*Omega*(1-Omega)))<1e-10
assert np.all(lam>=gap-1e-10)
assert np.all(lam<=qmax+1e-10)
assert np.all(np.diff(Omega)>=-1e-12)

logit=np.log(a/b)
dlogit_dtau=(logit[2:]-logit[:-2])/(tau[2:]-tau[:-2])
rhs=2*lam[1:-1]/gap
assert np.max(np.abs(dlogit_dtau-rhs)/rhs)<1e-4

assert ker.sum()==47
assert gap==11664
assert qmax==186624
assert abs(ker.sum()/len(c)-47/125)<1e-15

print("PASS")
