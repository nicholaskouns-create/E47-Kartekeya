#!/usr/bin/env python3
"""
E47 Noiseless-Subsystem + Convergence Certificate
=================================================
Certificate: MC-E47-NOISELESS-CONVERGENCE-20260928-001

Validates two remaining statements:

A. Uniform convergence:
   K=(C-6I)(C-30I), H=K^2,
   eps*=2/(lambda_min^+(H)+lambda_max(H))=1/99144,
   Gamma*=I-eps*H,
   ||Gamma*|_(ker K)^perp||_2 = 15/17.

   Because ||K||_2=432,
       ||K Gamma*^n (I-P)||_2 <= 432 (15/17)^n.
   n=270 is the first integer giving a uniform bound < 1e-12.

B. Noiseless multiplicity subsystems:
   E47 = E_6 (+) E_30
       ~= (C^5 tensor V_2) (+) (C^2 tensor V_5).

   For collective su(2) generators J_a,
       W_J^* J_a W_J = I_{m_J} tensor J_a^(J)
   for J=2,5.
   Hence the multiplicity factors C^5 and C^2 are noiseless subsystems
   for collective SU(2) noise. They are two protected multiplicity
   subsystems, not one 7-dimensional scalar Knill-Laflamme code.

Requires: numpy, scipy
"""

import numpy as np
import scipy.linalg as la
import math, json, hashlib
from pathlib import Path

TOL = 1e-10
TARGET = 1e-12

def su2_generators(j):
    m = np.arange(j, -j-1, -1, dtype=float)
    d = len(m)
    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((d,d), dtype=complex)
    for col, mm in enumerate(m):
        if mm < j:
            row = col - 1
            Jp[row,col] = np.sqrt(j*(j+1) - mm*(mm+1))
    Jm = Jp.conj().T
    Jx = (Jp + Jm)/2
    Jy = (Jp - Jm)/(2j)
    return Jx, Jy, Jz, Jp, Jm

def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

def build_carrier():
    jx,jy,jz,jp,jm = su2_generators(2)
    I5 = np.eye(5, dtype=complex)
    Jx = kron3(jx,I5,I5)+kron3(I5,jx,I5)+kron3(I5,I5,jx)
    Jy = kron3(jy,I5,I5)+kron3(I5,jy,I5)+kron3(I5,I5,jy)
    Jz = kron3(jz,I5,I5)+kron3(I5,jz,I5)+kron3(I5,I5,jz)
    Jp = Jx + 1j*Jy
    Jm = Jx - 1j*Jy
    C = Jx@Jx + Jy@Jy + Jz@Jz
    I = np.eye(125, dtype=complex)
    K = (C-6*I)@(C-30*I)
    H = K@K
    return Jx,Jy,Jz,Jp,Jm,C,K,H

def spectral_projector(C, lam, atol=1e-8):
    w,U = la.eigh(C)
    mask = np.isclose(w,lam,atol=atol)
    V = U[:,mask]
    return V@V.conj().T, w, U, V

def orthonormal_joint_eigenspace(C,Jz,lam,m,atol=1e-8):
    # First isolate C sector, then diagonalize Jz restricted to it.
    w,U = la.eigh(C)
    V = U[:,np.isclose(w,lam,atol=atol)]
    z,Z = la.eigh(V.conj().T@Jz@V)
    H = V@Z[:,np.isclose(z,m,atol=atol)]
    # QR suppresses accumulated floating noise.
    Q,_ = la.qr(H, mode="economic")
    return Q

def multiplicity_isometry(J, C, Jz, Jm):
    """
    Build W_J : C^{m_J} tensor V_J -> carrier.
    Choose an orthonormal highest-weight basis at m=J, then lower each chain.
    Ordering is multiplicity-major, then magnetic m=J,...,-J.
    """
    lam = J*(J+1)
    Htop = orthonormal_joint_eigenspace(C,Jz,lam,J)
    mult = Htop.shape[1]
    cols = []
    for a in range(mult):
        v = Htop[:,a].copy()
        v /= la.norm(v)
        cols.append(v.copy())
        m = J
        while m > -J:
            coeff = np.sqrt(J*(J+1) - m*(m-1))
            v = (Jm@v)/coeff
            # remove numerical contamination and normalize
            v /= la.norm(v)
            cols.append(v.copy())
            m -= 1
    W = np.column_stack(cols)
    return W, mult

def partial_trace_gauge(rho, m, d):
    # rho on C^m tensor C^d, multiplicity-major basis.
    R = rho.reshape(m,d,m,d)
    return np.einsum("agbg->ab", R)

def random_density(d, rng):
    A = rng.normal(size=(d,d)) + 1j*rng.normal(size=(d,d))
    rho = A@A.conj().T
    return rho/np.trace(rho)

def main():
    Jx,Jy,Jz,Jp,Jm,C,K,H = build_carrier()
    w,U = la.eigh(C)
    vals, counts = np.unique(np.rint(w).astype(int), return_counts=True)

    k = (w-6)*(w-30)
    h = k*k
    ker = np.isclose(k,0,atol=1e-8)
    P = U[:,ker]@U[:,ker].conj().T

    positive = h[h>1e-8]
    gap = float(positive.min())
    top = float(positive.max())
    eps = 2.0/(gap+top)
    rho_star = (top-gap)/(top+gap)
    K_norm = float(np.max(np.abs(k)))

    Gamma = np.eye(125) - eps*H
    complement = np.eye(125) - P
    complement_norm = la.norm(complement@Gamma@complement,2)

    n_uniform = math.ceil(math.log(TARGET/K_norm)/math.log(rho_star))
    prev_bound = K_norm*(rho_star**(n_uniform-1))
    cert_bound = K_norm*(rho_star**n_uniform)

    gamma_n = np.linalg.matrix_power(Gamma, n_uniform)
    actual_operator_residual = la.norm(K@gamma_n@complement, 2)

    # Direct factorization/noiseless-subsystem audits.
    rng = np.random.default_rng(20260928)
    sector_results = {}
    for J, expected_mult in [(2,5),(5,2)]:
        W,mult = multiplicity_isometry(J,C,Jz,Jm)
        jx,jy,jz,_,_ = su2_generators(J)
        d = 2*J+1

        iso_resid = la.norm(W.conj().T@W - np.eye(mult*d), 2)
        factor_resids = {
            "Jx": float(la.norm(W.conj().T@Jx@W - np.kron(np.eye(mult),jx),2)),
            "Jy": float(la.norm(W.conj().T@Jy@W - np.kron(np.eye(mult),jy),2)),
            "Jz": float(la.norm(W.conj().T@Jz@W - np.kron(np.eye(mult),jz),2)),
        }

        # Test a nontrivial collective rotation.
        theta = np.array([0.37,-0.51,0.29])
        A_full = theta[0]*Jx + theta[1]*Jy + theta[2]*Jz
        A_gauge = theta[0]*jx + theta[1]*jy + theta[2]*jz
        Ufull = la.expm(-1j*A_full)
        Ug = la.expm(-1j*A_gauge)
        rotation_factor_resid = float(
            la.norm(W.conj().T@Ufull@W - np.kron(np.eye(mult),Ug),2)
        )

        # Reduced logical state invariance under a random-unitary collective channel.
        rhoL = random_density(mult,rng)
        rhoG = random_density(d,rng)
        rho0 = np.kron(rhoL,rhoG)

        angles = [
            np.array([0.11,-0.07,0.23]),
            np.array([-0.31,0.19,0.05]),
            np.array([0.17,0.13,-0.29]),
        ]
        probs = np.array([0.2,0.35,0.45])
        rho1 = np.zeros_like(rho0)
        channel_factor_resids = []
        for p,t in zip(probs,angles):
            Af = t[0]*Jx+t[1]*Jy+t[2]*Jz
            Ag = t[0]*jx+t[1]*jy+t[2]*jz
            Uf = la.expm(-1j*Af)
            Ugg = la.expm(-1j*Ag)
            F = W.conj().T@Uf@W
            target = np.kron(np.eye(mult),Ugg)
            channel_factor_resids.append(float(la.norm(F-target,2)))
            rho1 += p*(F@rho0@F.conj().T)

        logical_before = partial_trace_gauge(rho0,mult,d)
        logical_after = partial_trace_gauge(rho1,mult,d)
        logical_invariance = float(la.norm(logical_after-logical_before,'fro'))

        sector_results[str(J)] = {
            "multiplicity": int(mult),
            "expected_multiplicity": int(expected_mult),
            "factor_dimension": [int(mult), int(d)],
            "isometry_residual": float(iso_resid),
            "generator_factorization_residuals": factor_resids,
            "rotation_factorization_residual": rotation_factor_resid,
            "random_unitary_channel_factorization_max_residual": max(channel_factor_resids),
            "logical_reduced_state_invariance_residual": logical_invariance,
            "pass": bool(
                mult==expected_mult and
                iso_resid<TOL and
                max(factor_resids.values())<TOL and
                rotation_factor_resid<TOL and
                max(channel_factor_resids)<TOL and
                logical_invariance<TOL
            )
        }

    P6,_,_,_ = spectral_projector(C,6)
    P30,_,_,_ = spectral_projector(C,30)
    cross_block = max(
        float(la.norm(P6@A@P30,2)) for A in (Jx,Jy,Jz)
    )

    result = {
        "certificate": "MC-E47-NOISELESS-CONVERGENCE-20260928-001",
        "status": "PASS",
        "carrier_dim": 125,
        "casimir_spectrum": vals.tolist(),
        "sector_dimensions": counts.tolist(),
        "kernel_dim": int(np.count_nonzero(ker)),
        "omega_c": float(np.count_nonzero(ker)/125),
        "K2_gap": gap,
        "K2_norm": top,
        "K_norm": K_norm,
        "epsilon_star": eps,
        "rho_star": rho_star,
        "uniform_threshold": {
            "target": TARGET,
            "first_guaranteed_step": int(n_uniform),
            "step_minus_1_bound": float(prev_bound),
            "step_bound": float(cert_bound),
            "direct_operator_norm_at_step": float(actual_operator_residual),
            "pass": bool(prev_bound>=TARGET and cert_bound<TARGET and actual_operator_residual<TARGET)
        },
        "collective_cross_block_residual": cross_block,
        "noiseless_subsystems": sector_results,
        "interpretation": (
            "E47 decomposes as (C^5 tensor V2) direct-sum "
            "(C^2 tensor V5). The multiplicity factors C^5 and C^2 "
            "are noiseless subsystems for collective SU(2) noise."
        )
    }

    if not result["uniform_threshold"]["pass"]:
        result["status"] = "FAIL"
    if cross_block >= TOL:
        result["status"] = "FAIL"
    if not all(v["pass"] for v in sector_results.values()):
        result["status"] = "FAIL"

    print("="*72)
    print("MC-E47-NOISELESS-CONVERGENCE-20260928-001")
    print("="*72)
    print("STATUS:", result["status"])
    print("Spec(C):", result["casimir_spectrum"])
    print("Sector dimensions:", result["sector_dimensions"])
    print("dim ker(K):", result["kernel_dim"])
    print("Omega_c:", result["omega_c"])
    print("K^2 gap / norm:", gap, "/", top)
    print("eps*:", eps, " rho*:", rho_star)
    print()
    print("UNIFORM <1e-12 CONVERGENCE CERTIFICATE")
    print("first guaranteed n:", n_uniform)
    print("bound at n-1:", f"{prev_bound:.16e}")
    print("bound at n  :", f"{cert_bound:.16e}")
    print("direct ||K Gamma^n (I-P)||_2:", f"{actual_operator_residual:.16e}")
    print()
    print("NOISELESS MULTIPLICITY SUBSYSTEMS")
    for J, r in sector_results.items():
        print(f"J={J}: C^{r['multiplicity']} tensor V_{J} ->",
              "PASS" if r["pass"] else "FAIL")
        print("  isometry residual:", f"{r['isometry_residual']:.3e}")
        print("  generator max residual:",
              f"{max(r['generator_factorization_residuals'].values()):.3e}")
        print("  rotation residual:", f"{r['rotation_factorization_residual']:.3e}")
        print("  channel factor residual:",
              f"{r['random_unitary_channel_factorization_max_residual']:.3e}")
        print("  reduced logical-state residual:",
              f"{r['logical_reduced_state_invariance_residual']:.3e}")
    print("cross-block collective residual:", f"{cross_block:.3e}")

    here = Path(__file__).resolve()
    repo_root = here.parents[3] if len(here.parents) >= 4 else here.parent
    certificate_dir = repo_root / "certificates"
    out = (certificate_dir if certificate_dir.is_dir() else here.parent) / "MC-E47-NOISELESS-CONVERGENCE-20260928-001.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print("\nJSON:", out)

if __name__ == "__main__":
    main()
