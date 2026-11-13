"""Reproducible E47 independent-target constrained exchange compilation."""
import numpy as np
import json
from scipy.linalg import expm
from scipy.optimize import minimize
from pathlib import Path

D=np.diag([-6.,-5.,-3.,0.,4.])
B=np.diag([0.,-.5,-1.5,-3.,-5.])
for j,v in enumerate(np.sqrt([12,147/20,144/35,9/7])):
    B[j,j+1]=B[j+1,j]=v
rng=np.random.default_rng(20261113)
def haar():
    z=rng.normal(size=(5,5))+1j*rng.normal(size=(5,5))
    q,r=np.linalg.qr(z)
    return q@np.diag(np.diag(r)/np.abs(np.diag(r)))
def compile_target(T,n,limit,restarts=2,maxiter=95):
    hs=[D if k%2==0 else B for k in range(n)]
    def objective(x):
        gs=[expm(-1j*t*h) for t,h in zip(x,hs)]
        prefix=[np.eye(5,dtype=complex)]
        for g in gs: prefix.append(g@prefix[-1])
        suffix=[None]*(n+1)
        suffix[n]=np.eye(5,dtype=complex)
        for k in range(n-1,-1,-1): suffix[k]=suffix[k+1]@gs[k]
        overlap=np.trace(T.conj().T@prefix[-1])
        value=1-abs(overlap)**2/25
        grad=np.empty(n)
        for k,h in enumerate(hs):
            derivative=suffix[k+1]@((-1j*h)@gs[k])@prefix[k]
            dv=np.trace(T.conj().T@derivative)
            grad[k]=-2*np.real(np.conj(overlap)*dv)/25
        return float(value),grad
    best=None
    for _ in range(restarts):
        start=rng.uniform(-limit,limit,n)
        fit=minimize(objective,start,jac=True,bounds=[(-limit,limit)]*n,method="L-BFGS-B",options={"maxiter":maxiter,"ftol":1e-10})
        if best is None or fit.fun<best.fun: best=fit
    return {"fidelity":float(1-best.fun),"infidelity":float(best.fun),"iterations":int(best.nit),"duration_l1":float(np.abs(best.x).sum()),"angles":best.x.tolist()}
if __name__=="__main__":
    targets=[haar() for _ in range(12)]
    rows=[]
    for ti,T in enumerate(targets):
        for limit in (0.5,1.5):
            for n in (8,16,24,32):
                rows.append({"target":ti,"split":"development" if ti<8 else "held_out","limit":limit,"pulses":n,**compile_target(T,n,limit)})
    Path("e47_pulse_resource_results.json").write_text(json.dumps({"seed":20261113,"rows":rows},indent=2))
    for limit in (0.5,1.5):
        for n in (8,16,24,32):
            v=[r["fidelity"] for r in rows if r["split"]=="held_out" and r["limit"]==limit and r["pulses"]==n]
            print(limit,n,np.median(v),min(v),max(v))
