# natal_spectral_analysis.py
# Birth: 1965-12-08 21:53 EST, Danville KY
# Correct UT: 1965-12-09 02:53
# Requires: numpy, pandas, matplotlib, pyswisseph

import math
import numpy as np
import pandas as pd
import swisseph as swe

lat, lon = 37.645649, -84.772182
jd = swe.julday(1965, 12, 9, 2 + 53/60, swe.GREG_CAL)

body_ids = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY,
    "Venus": swe.VENUS, "Mars": swe.MARS, "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN, "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO, "North Node": swe.MEAN_NODE,
}

positions = {}
for name, body_id in body_ids.items():
    xx, _ = swe.calc_ut(jd, body_id, swe.FLG_SWIEPH | swe.FLG_SPEED)
    positions[name] = xx[0] % 360

cusps, ascmc = swe.houses_ex(jd, lat, lon, b"P", swe.FLG_SWIEPH)
positions["Asc"] = ascmc[0] % 360
positions["MC"] = ascmc[1] % 360

nodes = list(positions)
targets = {"conjunction":0.0, "sextile":60.0, "square":90.0,
           "trine":120.0, "opposition":180.0}
max_orb, sigma = 8.0, 4.0

def sep(a,b):
    d = abs(a-b) % 360
    return min(d, 360-d)

n = len(nodes)
A = np.zeros((n,n))
for i in range(n):
    for j in range(i+1,n):
        s = sep(positions[nodes[i]], positions[nodes[j]])
        name, target = min(targets.items(), key=lambda kv: abs(s-kv[1]))
        err = abs(s-target)
        if err <= max_orb:
            w = math.exp(-0.5*(err/sigma)**2)
            A[i,j] = A[j,i] = w

D = np.diag(A.sum(axis=1))
L = D-A
evals, evecs = np.linalg.eigh(L)

print("nodes =", nodes)
print("eigenvalues =", np.array2string(evals, precision=9))
print("spectral gaps =", np.array2string(np.diff(evals), precision=9))
