"""Corrected Stargate formalism validation v1.1.
Validates corrected mathematical identities and exposes old contradictions.
Not experimental evidence for a physical wormhole.
"""
import numpy as np
import sympy as sp

omega_c = sp.Rational(47,125)
l, ell, eps = sp.symbols("l ell eps", positive=True, real=True)
rho = omega_c + eps*sp.tanh(l/ell)
assert sp.simplify(sp.diff(rho,l) - eps/ell*sp.sech(l/ell)**2) == 0
assert sp.simplify(sp.diff(rho,l)**2 - eps**2/ell**2*sp.sech(l/ell)**4) == 0

# t = tanh(u) -> sech^4(u) du = (1-t^2) dt
t = sp.symbols("t", real=True)
assert sp.integrate(1-t**2,(t,-1,1)) == sp.Rational(4,3)

time,tau,tau_ref,c0 = sp.symbols("time tau tau_ref c0", positive=True)
chi_avg = sp.simplify(sp.integrate(c0,(time,0,tau))/tau)
chi_acc = sp.simplify(sp.integrate(c0,(time,0,tau))/tau_ref)
assert chi_avg == c0
assert chi_acc == c0*tau/tau_ref

Z,V,rp = sp.symbols("Z V rp", real=True)
energy = sp.Rational(1,2)*Z*rp**2 + V
p_radial = sp.Rational(1,2)*Z*rp**2 - V
assert sp.simplify(energy+p_radial-Z*rp**2) == 0

m2,alpha = sp.symbols("m2 alpha", positive=True)
Zneg = sp.symbols("Zneg", negative=True)
x = sp.symbols("x", nonnegative=True)
lam = m2 + Zneg*x + alpha*x**2
xstar = -Zneg/(2*alpha)
assert sp.simplify(lam.subs(x,xstar) - (m2-Zneg**2/(4*alpha))) == 0

Znum,m2num,anum = -0.5,1.0,0.10
ks=np.linspace(0,100,10001)
assert (m2num+Znum*ks**2).min() < 0
assert (m2num+Znum*ks**2+anum*ks**4).min() > 0

x1,T0=sp.symbols("x1 T0", real=True)
Om=sp.Function("Omega")(x1)
div_eff=sp.diff((1-Om)*T0,x1)
assert sp.simplify(div_eff + T0*sp.diff(Om,x1)) == 0

c_si=299792458.0
t_planck=5.391247e-44
assert 3.0/c_si > t_planck

print("PASS: corrected mathematical identities and contradiction checks.")
print("BOUNDARY: no physical-wormhole, ghost-free QFT, or hardware-realization claim.")
