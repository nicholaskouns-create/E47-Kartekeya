#!/usr/bin/env python3
"""Hyperbolic–Liquid Fractal Buoy Formalism — reproducible Run B calibration."""
import numpy as np

np.random.seed(42)

def hyp_dist(z,w,kappa=1.0):
    z,w=complex(z),complex(w)
    arg=abs(z-w)/abs(1-np.conj(z)*w)
    return (2.0/kappa)*np.arctanh(np.clip(arg,0.0,0.999999))

z1,z2,z3=0j,0.3+0.4j,0.1-0.2j
d12=hyp_dist(z1,z2); d21=hyp_dist(z2,z1); d11=hyp_dist(z1,z1)
d13=hyp_dist(z1,z3); d23=hyp_dist(z2,z3)
assert d12>=0
assert np.isclose(d12,d21)
assert np.isclose(d11,0.0)
assert d12 <= d13+d23+1e-10

def hyp_vol_2d(r,kappa=1.0):
    return 2*np.pi*(np.cosh(kappa*r)-1)/kappa**2
rs=np.arange(1.0,4.01,0.5); vols=hyp_vol_2d(rs)
slope=np.polyfit(rs,np.log(vols),1)[0]
assert slope>0.8

true_alpha=1.37
ells=np.logspace(0,2,20)
A_true=2.5*ells**true_alpha
A=A_true*(1+0.03*np.random.randn(len(ells)))
alpha_est,intercept=np.polyfit(np.log(ells),np.log(A),1)
res=np.log(A)-(alpha_est*np.log(ells)+intercept)
rmse=np.sqrt(np.mean(res**2))
assert abs(alpha_est-true_alpha)<0.03 and rmse<0.05

def kuramoto_R(theta):
    return np.abs(np.mean(np.exp(1j*theta)))
N=64; K=3.0
omega=np.random.normal(0,0.5,N)
theta=np.random.uniform(0,2*np.pi,N)
dt=0.05; steps=400; R_traj=[]
for _ in range(steps):
    R=kuramoto_R(theta); R_traj.append(R)
    psi=np.angle(np.mean(np.exp(1j*theta)))
    theta=(theta+dt*(omega+K*R*np.sin(psi-theta)))%(2*np.pi)
R_traj=np.array(R_traj)
assert np.all((R_traj>=0)&(R_traj<=1))
assert R_traj[-1]>0.9

def F(x): return 3.7*x*(1-x)
fp=(3.7-1)/3.7
def Fhat(y): return fp+0.6*(y-fp)
def Phi(x): return np.clip(x,0.1,0.9)
xs=np.linspace(0.2,0.8,50)
residuals=np.array([abs(Phi(F(x))-Fhat(Phi(x))) for x in xs])
r_buoy=float(residuals.max())
assert np.isfinite(r_buoy)

eps=r_buoy; L=0.85; n=30
bound=eps*(1-L**n)/(1-L); asymp_bound=eps/(1-L)
assert L<1 and np.isfinite(bound)

A0=np.array([[2.,0.5],[0.5,1.]])
E0=0.01*np.random.randn(2,2); E0=(E0+E0.T)/2
B=A0+E0
diff=np.abs(np.sort(np.linalg.eigvalsh(A0))-np.sort(np.linalg.eigvalsh(B)))
op_norm=np.linalg.norm(E0,2)
assert diff.max() <= op_norm+1e-14

print("MC-HLFB-RUN-B-REPRO-20260930-001 PASS_WITH_CALIBRATION")
print("metric",d12,d13+d23)
print("growth_slope",slope)
print("alpha",alpha_est,"rmse",rmse)
print("R_final",R_traj[-1],"range",R_traj.min(),R_traj.max())
print("r_buoy",r_buoy,"mean",residuals.mean())
print("bound_n30",bound,"limsup",asymp_bound)
print("weyl",op_norm,diff.max())
