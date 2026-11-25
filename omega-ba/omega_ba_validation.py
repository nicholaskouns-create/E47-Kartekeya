#!/usr/bin/env python3
"""ΩBA first-principles 5D contraction + exact E47 spectral check. NumPy."""
import numpy as np
from fractions import Fraction as F
rng=np.random.default_rng(47)
mu,lam,tau,gap=2.,.5,.3,1.
beta=1/(1+lam*mu); alpha=np.exp(-tau*gap); gamma=alpha*beta
U=np.linalg.qr(rng.normal(size=(5,5)))[0]
Q=np.linalg.qr(rng.normal(size=(5,5)))[0]
A=(Q*np.exp(-tau*np.arange(1,6)))@Q.T
M=A@(beta*U); b=A@np.arange(5.)*(1-beta)
xstar=np.linalg.solve(np.eye(5)-M,b)
x=rng.normal(size=5); e0=np.linalg.norm(x-xstar); prev=e0
for n in range(1,101):
 x=M@x+b; e=np.linalg.norm(x-xstar)
 assert e<=gamma**n*e0+1e-13 and e<=prev+1e-13
 prev=e
X=rng.normal(size=(10000,5)); Y=rng.normal(size=(10000,5)); D=X-Y
ratios=np.linalg.norm(D@M.T,axis=1)/np.linalg.norm(D,axis=1)
assert max(ratios)<=gamma+1e-13
assert np.linalg.norm(M@xstar+b-xstar)<1e-13
j=np.arange(7); mult=np.array([1,3,5,4,3,2,1]); c=j*(j+1); k=(c-6)*(c-30); dims=mult*(2*j+1); a=k*k
assert sum(dims)==125 and sum(dims[k==0])==47
nonzero=a[a>0]; eps=F(2,int(min(nonzero)+max(nonzero))); rho=max(abs(1-eps*int(v)) for v in nonzero)
assert eps==F(1,99144) and rho==F(15,17)
print('gamma',gamma,'max sampled ratio',max(ratios),'fixed point residual',np.linalg.norm(M@xstar+b-xstar),'iteration 100 residual',prev)
print('E47 dimension',sum(dims[k==0]),'gap',min(nonzero),'norm',max(nonzero),'epsilon',eps,'rho',rho,'trace K',sum(k*dims))
print('phi^-5',((1+np.sqrt(5))/2)**-5)
