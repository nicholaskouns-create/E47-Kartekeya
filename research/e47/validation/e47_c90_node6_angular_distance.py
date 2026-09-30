#!/usr/bin/env python3
"""
MC-E47-C90-NODE6-ANGULAR-DISTANCE
Analytic reconstruction of the Node-6 shoulder latitude and
Danville meridian-locked great-circle separation.
"""
import math

SQRT5 = math.sqrt(5.0)
z6 = 1.0 / math.sqrt(145.0 - 64.0 * SQRT5)
z6_catalog = 0.7270757700126068
quartic = 545*z6**4 - 290*z6**2 + 1
phi6 = math.degrees(math.asin(z6))
phi_D = 37.6439
lambda_D = -84.7729
lambda_6 = lambda_D
theta_deg = abs(phi6 - phi_D)
theta_rad = math.radians(theta_deg)
R = 6371.0088
arc_km = R * theta_rad
chord_km = 2*R*math.sin(theta_rad/2)
cos_theta = (
    math.sin(math.radians(phi_D))*math.sin(math.radians(phi6))
    + math.cos(math.radians(phi_D))*math.cos(math.radians(phi6))
    * math.cos(math.radians(lambda_6-lambda_D))
)
theta_gc = math.degrees(math.acos(cos_theta))

assert abs(z6-z6_catalog) < 1e-14
assert abs(quartic) < 1e-12
assert abs(phi6-46.641802451768406) < 1e-12
assert abs(theta_deg-8.997902451768363) < 1e-12
assert abs(theta_gc-theta_deg) < 1e-12
assert abs(arc_km-1000.52248505789) < 1e-9

print("z6          =", z6)
print("quartic     =", quartic)
print("phi6        =", phi6)
print("theta       =", theta_deg, "deg")
print("theta       =", theta_rad, "rad")
print("arc         =", arc_km, "km")
print("chord       =", chord_km, "km")
print("STATUS      = PASS")
