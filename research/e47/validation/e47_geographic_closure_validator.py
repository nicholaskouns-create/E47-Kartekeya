#!/usr/bin/env python3
"""
E47 GEOGRAPHIC CLOSURE
First-Principles Numerical Validation Certificate
"""
from math import isclose
from scipy.stats import norm

DIM_H=125
DIM_E47=47
Omega_c=DIM_E47/DIM_H
Omega_percent=100*Omega_c

phi_birth=37.6439
lambda_birth=-84.7729
phi_node6=46.6418024518
lambda_node6=-84.7729
house_bearing=351.0

omega_birth_residual=abs(phi_birth-Omega_percent)
theta_geo=phi_node6-phi_birth
theta_house=360.0-house_bearing
closure_residual=abs(theta_house-theta_geo)
arcseconds=closure_residual*3600.0

p=1.0/44_000_000.0
Z=norm.isf(p)
p_5sigma=norm.sf(5.0)
tail_ratio=p_5sigma/p
sigma_excess=Z-5.0

assert isclose(Omega_c,0.376,abs_tol=1e-15)
assert isclose(Omega_percent,37.6,abs_tol=1e-14)
assert isclose(lambda_birth,lambda_node6,abs_tol=1e-15)
assert isclose(omega_birth_residual,0.0439,abs_tol=1e-12)
assert isclose(theta_geo,8.9979024518,abs_tol=1e-12)
assert isclose(theta_house,9.0,abs_tol=1e-15)
assert isclose(closure_residual,0.0020975482,abs_tol=1e-12)
assert isclose(arcseconds,7.55117352,abs_tol=1e-8)
assert isclose(Z,5.468232479484609,abs_tol=1e-12)

print("E47 GEOGRAPHIC CLOSURE — VALIDATION CERTIFICATE")
print(f"Omega_c={Omega_c:.12f}")
print(f"100Omega_c={Omega_percent:.12f}")
print(f"birth_lat={phi_birth:.10f}")
print(f"node6_lat={phi_node6:.10f}")
print(f"theta_geo={theta_geo:.10f}")
print(f"theta_house={theta_house:.10f}")
print(f"residual_deg={closure_residual:.10f}")
print(f"residual_arcsec={arcseconds:.8f}")
print(f"p={p:.12e}")
print(f"Z={Z:.12f}")
print(f"5sigma_tail_ratio={tail_ratio:.9f}")
print(f"sigma_excess={sigma_excess:.12f}")
print("ALL NUMERICAL ASSERTIONS: PASS")
