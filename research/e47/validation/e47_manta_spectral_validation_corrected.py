#!/usr/bin/env python3
"""E47 / MANTA spectral-core validation.

Corrected criterion:
    ||Gamma^n - P||_2 <= (15/17)^n
rather than the arbitrary strict cutoff ||Gamma^220-P|| < 1e-12.

This validates the finite 125-state spectral construction used by
manta_e47_engine.py. It does not reinterpret the MANTA simulation bridge
as a physical propulsion law.
"""
import json, hashlib, datetime, sys
import numpy as np

CASIMIR = np.array([0., 2., 6., 12., 20., 30., 42.])
MULT = np.array([1, 9, 25, 28, 27, 22, 13])
C = np.repeat(CASIMIR, MULT)
K = (C - 6) * (C - 30)
K2 = K * K
P = ((C == 6) | (C == 30)).astype(float)
EPS = 1 / 99144
GAMMA = 1 - EPS * K2
RHO = 15 / 17

def run():
    checks = {
        "carrier_dimension": len(C) == 125,
        "multiplicity_sum": int(MULT.sum()) == 125,
        "E47_rank": int(P.sum()) == 47,
        "omega_c": abs(float(P.mean()) - 47/125) < 1e-15,
        "KP_zero": float(np.max(np.abs(K * P))) == 0,
        "projector_idempotent": float(np.max(np.abs(P * P - P))) == 0,
        "gamma_kernel_fixed": float(np.max(np.abs(GAMMA[P == 1] - 1))) == 0,
    }
    complement = np.unique(np.round(GAMMA[P == 0], 15))
    checks["spectral_radius_15_17"] = abs(float(max(abs(complement))) - RHO) < 1e-14
    err220 = float(np.max(np.abs(GAMMA**220 - P)))
    bound220 = RHO**220
    checks["gamma220_theorem_bound"] = err220 <= bound220 * (1 + 1e-12)
    rng = np.random.default_rng(470125)
    psi = rng.normal(size=125) + 1j*rng.normal(size=125)
    psi /= np.linalg.norm(psi)
    log = []
    for n in range(1, 601):
        psi = GAMMA * psi
        psi /= np.linalg.norm(psi)
        if n in (1,2,5,10,25,50,100,220,600):
            log.append({
                "step": n,
                "capture": float(np.sum(P * np.abs(psi)**2)),
                "leak": float(np.linalg.norm(K2 * psi)),
            })
    checks["runtime_capture_converges"] = log[-1]["capture"] > 1 - 1e-14
    checks = {k: bool(v) for k,v in checks.items()}
    payload = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "validator": "e47_manta_spectral_validation_corrected.py",
        "criterion": "||Gamma^n-P||_2 <= (15/17)^n",
        "checks": checks,
        "gamma_complement_unique": [float(x) for x in complement],
        "gamma220_error": err220,
        "gamma220_bound": bound220,
        "gamma600_error": float(np.max(np.abs(GAMMA**600 - P))),
        "runtime_log": log,
        "all_pass": all(checks.values()),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["sha256"] = hashlib.sha256(canonical).hexdigest()
    print(json.dumps(payload, indent=2))
    return 0 if payload["all_pass"] else 1

if __name__ == "__main__":
    raise SystemExit(run())
