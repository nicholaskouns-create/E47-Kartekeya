"""E47 quantum-channel check: seven-qubit (128-state) Halmos unitary dilation.
Statevector matrix simulation; not gate-compiled or executed on quantum hardware.
"""
import json
import numpy as np
from scipy.linalg import eigh, expm
I=np.eye(5);m=np.arange(-2,3,dtype=float);jp=np.zeros((5,5),complex)
for i,v in enumerate(m[:-1]):jp[i+1,i]=np.sqrt(6-v*(v+1))
jm=jp.conj().T;jx=(jp+jm)/2;jy=(jp-jm)/(2j);jz=np.diag(m)
def k(a,b,c):return np.kron(np.kron(a,b),c)
C=np.real(sum(z@z for z in [k(j,I,I)+k(I,j,I)+k(I,I,j) for j in (jx,jy,jz)]))
ev,V=eigh(C);Q=V[:,np.isclose(ev,6,atol=1e-8)|np.isclose(ev,30,atol=1e-8)]
S=np.roll(I,1,axis=0);l=2*I-S-S.T;d=(S-S.T)/2
L=k(l,I,I)+k(I,l,I)+k(I,I,l);D=k(d,I,I)+.7*k(I,d,I)-.4*k(I,I,d)
G=3*Q.T@D@Q-.2*Q.T@L@Q
T=expm(.1*G)
T64=np.eye(64);T64[:47,:47]=T
def root(Z):
 w,U=eigh((Z+Z.T)/2)
 assert w.min()>-1e-10
 return (U*np.sqrt(np.maximum(w,0)))@U.T
U=np.block([[T64,root(np.eye(64)-T64@T64.T)],
            [root(np.eye(64)-T64.T@T64),-T64.T]])
rng=np.random.default_rng(47);psi=rng.normal(size=47);psi/=np.linalg.norm(psi)
v=np.zeros(128);v[:47]=psi
final=U@v;expected=T@psi
metrics={
  "method":"7-qubit statevector matrix Halmos dilation; no hardware or gates",
  "qubits":7,"physical_dimension":128,"logical_dimension":47,
  "unitarity_residual":float(np.linalg.norm(U.T@U-np.eye(128))),
  "branch_evolution_error":float(np.linalg.norm(final[:47]-expected)),
  "idle_sector_leakage":float(np.linalg.norm(final[47:64])),
  "success_probability":float(np.linalg.norm(final[:64])**2),
  "failure_probability":float(np.linalg.norm(final[64:])**2),
  "probability_sum":float(np.linalg.norm(final)**2),
  "operator_contraction_norm":float(np.linalg.svd(T,compute_uv=False)[0])
}
assert metrics["unitarity_residual"]<1e-9
assert metrics["branch_evolution_error"]<1e-10
assert metrics["idle_sector_leakage"]<1e-10
with open("e47_quantum_dilation_results.json","w") as f:json.dump(metrics,f,indent=2)
print(json.dumps(metrics,indent=2))
