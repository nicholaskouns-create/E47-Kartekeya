#!/usr/bin/env python3
"""
GEOMETRIC HOLOGRAPHY
Numerical + Quantum Phase Validation
"""
from math import isclose, radians, cos, sqrt
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

theta_geo=phi_node6-phi_birth
theta_house=360.0-house_bearing
closure_residual=abs(theta_house-theta_geo)
arcseconds=closure_residual*3600.0
predicted_house_bearing=360.0-theta_geo

p=1.0/44_000_000.0
Z=norm.isf(p)
p_5sigma=norm.sf(5.0)
tail_ratio=p_5sigma/p
sigma_excess=Z-5.0

delta_rad=radians(closure_residual)
fidelity=cos(delta_rad/2.0)**2
trace_distance=sqrt(max(0.0,1.0-fidelity))

assert isclose(Omega_c,0.376,abs_tol=1e-15)
assert isclose(Omega_percent,37.6,abs_tol=1e-14)
assert isclose(lambda_birth,lambda_node6,abs_tol=1e-15)
assert isclose(theta_geo,8.9979024518,abs_tol=1e-12)
assert isclose(theta_house,9.0,abs_tol=1e-15)
assert isclose(closure_residual,0.0020975482,abs_tol=1e-12)
assert isclose(arcseconds,7.55117352,abs_tol=1e-8)
assert isclose(predicted_house_bearing,351.0020975482,abs_tol=1e-12)
assert isclose(Z,5.468232479484609,abs_tol=1e-12)
assert fidelity > 0.999999999

print("GEOMETRIC HOLOGRAPHY — NUMERICAL + QUANTUM VALIDATION")
print("="*64)
print(f"Omega_c={Omega_c:.12f}")
print(f"100Omega_c={Omega_percent:.12f}")
print(f"theta_geo={theta_geo:.10f} deg")
print(f"theta_house={theta_house:.10f} deg")
print(f"closure_residual={closure_residual:.10f} deg")
print(f"closure_arcsec={arcseconds:.8f}")
print(f"predicted_house_bearing={predicted_house_bearing:.10f} deg")
print(f"p={p:.12e}")
print(f"Z={Z:.12f} sigma")
print(f"five_sigma_tail_ratio={tail_ratio:.9f}")
print(f"sigma_excess={sigma_excess:.12f}")
print(f"quantum_phase_fidelity={fidelity:.15f}")
print(f"trace_distance={trace_distance:.15e}")
print("ALL NUMERICAL + QUANTUM PHASE ASSERTIONS: PASS")
