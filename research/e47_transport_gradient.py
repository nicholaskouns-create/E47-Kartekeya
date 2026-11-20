#!/usr/bin/env python3
"""E47 gradient plus skew transport; reproducible numerical experiment (2026-11-20)."""
import json, csv
from pathlib import Path
import numpy as np
from scipy.linalg import eigh, expm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path(__file__).resolve().parent
n = 5
I = np.eye(n)
m = np.arange(-2, 3, dtype=float)
Jp = np.zeros((n, n), dtype=complex)
for i, mi in enumerate(m[:-1]):
    Jp[i+1, i] = np.sqrt(6-mi*(mi+1))
Jm = Jp.conj().T
Jx, Jy, Jz = (Jp+Jm)/2, (Jp-Jm)/(2j), np.diag(m)
def k3(a,b,c):
    return np.kron(np.kron(a,b),c)
Js = [k3(j,I,I)+k3(I,j,I)+k3(I,I,j) for j in (Jx,Jy,Jz)]
C = np.real(sum(j@j for j in Js))
cvals,V = eigh(C)
mask = np.isclose(cvals,6,atol=1e-8) | np.isclose(cvals,30,atol=1e-8)
Q = V[:,mask]
assert Q.shape == (125,47)
P = Q@Q.T
S = np.roll(I,1,axis=0)
L5 = 2*I-S-S.T
D5 = (S-S.T)/2
L = k3(L5,I,I)+k3(I,L5,I)+k3(I,I,L5)
D = k3(D5,I,I)+.7*k3(I,D5,I)-.4*k3(I,I,D5)
B = Q.T@L@Q
A = 3*(Q.T@D@Q)
xx,yy,zz = np.meshgrid(np.arange(5),np.arange(5),np.arange(5),indexing="ij")
field = (.75*np.sin(2*np.pi*xx/5)+.48*np.cos(2*np.pi*yy/5)
         +.32*np.sin(2*np.pi*(xx+zz)/5)
         +.9*np.exp(-((xx-1)**2+(yy-3)**2+(zz-2)**2)/2.0))
field += .08*np.random.default_rng(47).normal(size=(5,5,5))
rho = field.reshape(-1)
rho /= np.linalg.norm(rho)
y0 = Q.T@rho
rate = .2
G = A-rate*B
ts = np.linspace(0,15,151)
records = []
for t in ts:
    yt = expm(t*G)@y0
    yn = expm(-rate*t*B)@y0
    energy = float(yt@B@yt)
    norm2 = float(yt@yt)
    comm = float(yt@(B@A-A@B)@yt)
    pred_deriv = comm-2*rate*float(yt@(B@B)@yt)
    direct_deriv = 2*float(yt@B@(G@yt))
    records.append({"t":float(t),"norm2":norm2,"gradient_energy":energy,
                    "energy_unmixed":float(yn@B@yn),
                    "energy_derivative":pred_deriv,
                    "derivative_residual":abs(pred_deriv-direct_deriv),
                    "e47_leakage":float(np.linalg.norm((np.eye(125)-P)@(Q@yt)))})
lam = eigh(B,eigvals_only=True)
comm_BA = B@A-A@B
report = {
  "dimension":int(Q.shape[1]),"gamma":rate,"transport_amplitude":3.,
  "directional_coefficients":[1.,.7,-.4],
  "lambda_min_B":float(lam.min()),"lambda_max_B":float(lam.max()),
  "A_skew_residual":float(np.linalg.norm(A+A.T)),
  "A_fro":float(np.linalg.norm(A)),
  "commutator_BA_fro":float(np.linalg.norm(comm_BA)),
  "projector_residual":float(np.linalg.norm(P@P-P)),
  "A_real_part_max":float(np.max(np.abs(np.real(np.linalg.eigvals(A))))),
  "G_spectral_abscissa":float(np.max(np.real(np.linalg.eigvals(G)))),
  "max_energy_derivative":float(max(r["energy_derivative"] for r in records)),
  "min_energy_derivative":float(min(r["energy_derivative"] for r in records)),
  "energy_increase_intervals":int(sum(records[i+1]["gradient_energy"]>records[i]["gradient_energy"]+1e-10 for i in range(len(records)-1))),
  "norm_monotone":bool(all(records[i+1]["norm2"]<=records[i]["norm2"]+1e-12 for i in range(len(records)-1))),
  "max_derivative_identity_residual":float(max(r["derivative_residual"] for r in records)),
  "max_complement_leakage":float(max(r["e47_leakage"] for r in records)),
  "init":records[0],"end":records[-1],
  "norm_bound_at_t15":float((y0@y0)*np.exp(-2*rate*lam.min()*15)),
  "stationary_dimension_gamma_positive":0,
  "exact_conclusions":["B=Q^T L Q positive definite",
                       "A=3 Q^T D Q skew symmetric",
                       "d||y||²/dt=-2 gamma y^T B y",
                       "d(y^T B y)/dt=y^T(BA-AB)y-2 gamma y^T B²y",
                       "stationary subspace of A-gamma B is {0} for gamma>0"]
}
(out/"e47_transport_gradient_results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
with (out/"e47_transport_gradient_timeseries.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,records[0].keys())
    w.writeheader()
    w.writerows(records)
fig,ax=plt.subplots(figsize=(9,5))
ax.semilogy(ts,[r["gradient_energy"] for r in records],label="Transport + dissipation")
ax.semilogy(ts,[r["energy_unmixed"] for r in records],label="Dissipation only",ls="--")
ax.set(xlabel="Time",ylabel="Spatial gradient energy",title="E47: skew transport coupled to dissipative gradients")
ax.legend()
ax.grid(alpha=.25)
fig.tight_layout()
fig.savefig(out/"e47_transport_gradient_plot.png",dpi=175)
plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5))
ax.plot(ts,[r["norm2"] for r in records])
ax.set(xlabel="Time",ylabel="Protected-sector squared norm",title="Exact monotone norm dissipation under skew transport")
ax.grid(alpha=.25)
fig.tight_layout()
fig.savefig(out/"e47_transport_norm_plot.png",dpi=175)
plt.close(fig)
print(json.dumps(report,indent=2))
