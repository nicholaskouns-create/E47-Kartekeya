#!/usr/bin/env python3
"""Relativistic QMD of Bismuth — Summed-Force Theorem Validator
Symbolic identities + finite quantum SOC lattice realization.
The finite model is a Bi-like effective Hamiltonian, not ab-initio DFT.
"""
import numpy as np
import sympy as sp

R=sp.symbols("R", real=True)
names=["kin","ion","H","xc","SO","NN"]
Es=[sp.Function("E_"+n)(R) for n in names]
Etot=sp.Add(*Es)
assert sp.simplify(-sp.diff(Etot,R)-sp.Add(*[-sp.diff(E,R) for E in Es]))==0
assert sp.simplify(sp.diff(Etot,R,2)-sp.Add(*[sp.diff(E,R,2) for E in Es]))==0
print("PASS symbolic summed-force and Hessian identities")

sx=np.array([[0,1],[1,0]],complex); sz=np.array([[1,0],[0,-1]],complex); I=np.eye(2)
Delta0,a,lam,Kion,M=0.65,0.80,1.10,2.40,1.0
def H(u,L=lam): return (Delta0+a*u)*np.kron(sz,I)+L*np.kron(sx,sz)
def E(u,L=lam):
    q=np.linalg.eigvalsh(H(u,L))
    return q[0]+q[1]+0.5*Kion*u*u
def Ea(u,L=lam):
    return -2*np.sqrt((Delta0+a*u)**2+L**2)+0.5*Kion*u*u
assert max(abs(E(x)-Ea(x)) for x in np.linspace(-.25,.25,51))<1e-12
h=1e-5
Ffd=-(E(h)-E(-h))/(2*h)
s=np.sqrt(Delta0**2+lam**2)
Fan=2*a*Delta0/s
assert abs(Ffd-Fan)<1e-7
vals,vecs=np.linalg.eigh(H(0)); occ=vecs[:,:2]; dH=a*np.kron(sz,I)
Fhf=-sum(np.vdot(occ[:,j],dH@occ[:,j]).real for j in range(2))
assert abs(Fhf-Fan)<1e-12
phi=Kion-2*a*a*lam**2/s**3
phi0=Kion
assert phi>0 and abs(phi-phi0)>1e-6
omega=np.sqrt(phi/M)
assert abs(phi/M-omega**2)<1e-14
print("PASS quantum spectrum")
print("PASS Hellmann-Feynman force")
print("PASS SOC changes force constant")
print("PASS dynamical matrix -> phonon frequency")
# quantum nuclear propagation
N=512; box=16.; dx=box/N
x=(np.arange(N)-N//2)*dx
p=2*np.pi*np.fft.fftfreq(N,d=dx)
dt=.002; steps=1000
V=np.array([Ea(q) for q in x]); V-=V.min()
psi=np.exp(-.5*((x-.6)/.45)**2).astype(complex)
psi/=np.sqrt(np.sum(abs(psi)**2)*dx)
n0=np.sum(abs(psi)**2)*dx
pv=np.exp(-.5j*V*dt); pt=np.exp(-.5j*(p**2/M)*dt)
for _ in range(steps):
    psi*=pv
    z=np.fft.fft(psi); z*=pt
    psi=np.fft.ifft(z); psi*=pv
n1=np.sum(abs(psi)**2)*dx
assert abs(n1-n0)<1e-10
print("PASS quantum nuclear propagation / unitarity",abs(n1-n0))
print("ALL CHECKS PASS")
