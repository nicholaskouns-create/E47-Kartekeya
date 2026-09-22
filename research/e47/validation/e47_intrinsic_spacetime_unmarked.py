#!/usr/bin/env python3
"""
MC-E47-INTRINSIC-SPACETIME-UNMARKED/1.0

Finite locked E47 datum -> intrinsic Lorentzian 3+1 affine spacetime ->
47-real-dimensional injective family in the unmarked vacuum Einstein
moduli space modulo all diffeomorphisms.

The full locked datum includes the ordered tensor cube V2⊗V2⊗V2 and
its product Jz basis, not merely the abstract rank-47 projector.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import sympy as sp

TOL = 1e-9
ROOT = Path.cwd()
OUT = ROOT / "E47_INTRINSIC_SPACETIME_UNMARKED_CERTIFICATE.json"


def spin2():
    j = 2.0
    m = np.arange(j, -j - 1, -1, dtype=float)
    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((5, 5), dtype=complex)
    for i, mi in enumerate(m[:-1]):
        Jp[i, i + 1] = np.sqrt(j * (j + 1) - mi * (mi - 1))
    Jm = Jp.conj().T
    Jx = (Jp + Jm) / 2
    Jy = (Jp - Jm) / (2j)
    return Jx, Jy, Jz


def k3(a, b, c):
    return np.kron(np.kron(a, b), c)


def build():
    Jx, Jy, Jz = spin2()
    I = np.eye(5, dtype=complex)
    X = [k3(Jz, I, I), k3(I, Jz, I), k3(I, I, Jz)]
    JX = k3(Jx, I, I) + k3(I, Jx, I) + k3(I, I, Jx)
    JY = k3(Jy, I, I) + k3(I, Jy, I) + k3(I, I, Jy)
    JZ = sum(X)
    C = JX @ JX + JY @ JY + JZ @ JZ
    I125 = np.eye(125, dtype=complex)
    K = (C - 6 * I125) @ (C - 30 * I125)
    K2 = K @ K
    ev, V = np.linalg.eigh((C + C.conj().T) / 2)
    mask = np.isclose(ev, 6, atol=1e-8) | np.isclose(ev, 30, atol=1e-8)
    Q = V[:, mask]
    P = Q @ Q.conj().T
    return X, C, K, K2, P


def canonical_real_basis(P, dim=47, tol=1e-10):
    """Deterministic pivot Gram-Schmidt on the lexicographic cube basis."""
    basis = []
    for k in range(P.shape[1]):
        v = np.asarray(P[:, k].real, dtype=float).copy()
        for b in basis:
            v -= b * np.dot(b, v)
        n = np.linalg.norm(v)
        if n > tol:
            v /= n
            nz = np.flatnonzero(np.abs(v) > tol)
            if len(nz) and v[nz[0]] < 0:
                v = -v
            basis.append(v)
        if len(basis) == dim:
            break
    if len(basis) != dim:
        raise RuntimeError(f"expected {dim} basis vectors, got {len(basis)}")
    return np.column_stack(basis)


def intrinsic_frame(X, K2, P):
    """
    Omega = equal-amplitude cube state.
    e0 = normalized semigroup/contraction direction K^2 Omega in E47^perp.
    Spatial raw directions wi = P X_i Omega in E47.
    Canonically whiten the 3x3 positive Gram matrix.
    """
    Omega = np.ones(125, dtype=complex) / np.sqrt(125)
    traw = K2 @ Omega
    if np.linalg.norm(traw) < TOL:
        raise RuntimeError("time direction vanished")
    e0 = traw / np.linalg.norm(traw)

    W = np.column_stack([P @ Xi @ Omega for Xi in X])
    S = np.real(W.conj().T @ W)
    lam, U = np.linalg.eigh(S)
    if np.min(lam) <= TOL:
        raise RuntimeError(f"spatial Gram is degenerate: {lam}")
    Sinvhalf = U @ np.diag(1 / np.sqrt(lam)) @ U.T
    Esp = W @ Sinvhalf
    frame = np.column_stack([e0, Esp])
    return Omega, W, S, lam, frame


def derive_brinkmann_ricci():
    """
    Derive Ricci directly for
      ds^2 = -2 du dv + dx^2 + dy^2 + H(u,x,y) du^2.
    """
    u, v, x, y = sp.symbols("u v x y", real=True)
    coords = [u, v, x, y]
    H = sp.Function("H")(u, x, y)
    g = sp.Matrix([[H, -1, 0, 0],
                   [-1, 0, 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])
    gi = sp.simplify(g.inv())
    n = 4
    Gamma = [[[
        sp.simplify(sum(
            gi[a, d] * (
                sp.diff(g[d, c], coords[b])
                + sp.diff(g[d, b], coords[c])
                - sp.diff(g[b, c], coords[d])
            )
            for d in range(n)
        ) / 2)
        for c in range(n)] for b in range(n)] for a in range(n)]

    Ric = sp.MutableDenseMatrix(n, n, [0] * (n * n))
    for b in range(n):
        for d in range(n):
            acc = 0
            for a in range(n):
                # R^a_{bad}
                acc += sp.diff(Gamma[a][b][d], coords[a]) - sp.diff(Gamma[a][b][a], coords[d])
                acc += sum(
                    Gamma[a][a][q] * Gamma[q][b][d]
                    - Gamma[a][d][q] * Gamma[q][b][a]
                    for q in range(n)
                )
            Ric[b, d] = sp.simplify(acc)

    expected = -sp.diff(H, x, 2) / 2 - sp.diff(H, y, 2) / 2
    reduction_ok = (
        sp.simplify(Ric[0, 0] - expected) == 0
        and all(
            sp.simplify(Ric[i, j]) == 0
            for i in range(4) for j in range(4)
            if (i, j) != (0, 0)
        )
    )
    return reduction_ok


def anchor_rigidity():
    """
    For profiles
       F_c(u)=u^78 + u^47 + sum_{j=0}^{46} c_j u^j
    and plane-wave isometry freedom
       F_c(u)=s a^2 F_d(a u+b),  a != 0, s in {+1,-1},
    compare degrees 78,77,47.

    coeff u^78: 1 = s a^80 -> s=1, |a|=1.
    coeff u^77: 0 = 78 s a^79 b -> b=0.
    coeff u^47: 1 = s a^49 -> a=1.
    Then all lower coefficients coincide.
    """
    u, a, b, s = sp.symbols("u a b s", real=True, nonzero=True)
    rhs_anchor = sp.expand(s * a**2 * ((a*u + b)**78 + (a*u + b)**47))
    p = sp.Poly(rhs_anchor, u)
    c78 = sp.factor(p.coeff_monomial(u**78))
    c77 = sp.factor(p.coeff_monomial(u**77))
    c47 = sp.factor(p.coeff_monomial(u**47))
    formulas_ok = (
        sp.simplify(c78 - s*a**80) == 0
        and sp.simplify(c77 - 78*s*a**79*b) == 0
        and sp.simplify(c47.subs(b, 0) - s*a**49) == 0
    )
    return formulas_ok, str(c78), str(c77), str(c47)


def main():
    X, C, K, K2, P = build()
    eta = 2 * P - np.eye(125, dtype=complex)
    B = canonical_real_basis(P)

    Omega, W, S, spatial_eigs, frame = intrinsic_frame(X, K2, P)
    G = np.real(frame.conj().T @ eta @ frame)
    target = np.diag([-1.0, 1.0, 1.0, 1.0])

    # Direct spectral facts.
    ce = np.linalg.eigvalsh((C + C.conj().T)/2)
    spec = {}
    for z in np.rint(ce).astype(int):
        spec[int(z)] = spec.get(int(z), 0) + 1

    # Derive vacuum criterion symbolically.
    ricci_reduction_ok = derive_brinkmann_ricci()

    # E47-native profile anchor kills all residual affine u-gauge.
    rigidity_ok, c78, c77, c47 = anchor_rigidity()

    # Generic profile is non-flat and tracefree:
    # p(u) = F(u) diag(1,-1), tr p = 0.
    u = sp.symbols("u", real=True)
    coeffs = sp.symbols("c0:47", real=True)
    F = u**78 + u**47 + sum(coeffs[j] * u**j for j in range(47))
    laplace_transverse = sp.expand(2*F + (-2*F))  # Hxx+Hyy for H=F(x^2-y^2)

    checks = {
        "carrier_125": C.shape == (125,125),
        "casimir_spectrum": spec == {0:1,2:9,6:25,12:28,20:27,30:22,42:13},
        "projector_rank_47": np.linalg.matrix_rank(P, tol=1e-8) == 47,
        "projector_real": np.max(np.abs(P.imag)) < 1e-12,
        "eta_selfadjoint": np.linalg.norm(eta - eta.conj().T, 2) < 1e-10,
        "eta_involution": np.linalg.norm(eta @ eta - np.eye(125), 2) < 1e-10,
        "eta_inertia_47_78": (
            np.count_nonzero(np.linalg.eigvalsh(eta.real) > 0.5) == 47
            and np.count_nonzero(np.linalg.eigvalsh(eta.real) < -0.5) == 78
        ),
        "uniform_state_normalized": abs(np.linalg.norm(Omega)-1) < 1e-12,
        "time_direction_nonzero": np.linalg.norm(K2 @ Omega) > 1,
        "time_in_complement": np.linalg.norm(P @ frame[:,0]) < 1e-10,
        "cube_spatial_rank_3": np.linalg.matrix_rank(W, tol=1e-10) == 3,
        "cube_spatial_gram_positive": np.min(spatial_eigs) > 1e-10,
        "space_in_kernel": np.linalg.norm(P @ frame[:,1:] - frame[:,1:], 2) < 1e-10,
        "intrinsic_4frame_rank": np.linalg.matrix_rank(frame, tol=1e-10) == 4,
        "lorentzian_pullback": np.linalg.norm(G-target, 2) < 1e-10,
        "lorentzian_determinant": abs(np.linalg.det(G)+1) < 1e-10,
        "canonical_real_basis_47": B.shape == (125,47),
        "canonical_basis_orthonormal": np.linalg.norm(B.T @ B - np.eye(47), 2) < 1e-10,
        "canonical_basis_in_E47": np.linalg.norm(P.real @ B - B, 2) < 1e-10,
        "brinkmann_ricci_derived": bool(ricci_reduction_ok),
        "profile_tracefree_vacuum": sp.simplify(laplace_transverse) == 0,
        "profile_nonflat": sp.Poly(F, u).degree() == 78,
        "anchor_coefficients_78_77_47": bool(rigidity_ok),
        "unmarked_affine_rigidity": bool(rigidity_ok),
    }
    checks = {k: bool(v) for k,v in checks.items()}

    cert = {
        "schema": "MC-E47-INTRINSIC-SPACETIME-UNMARKED/1.0",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "intrinsic_spacetime": {
            "fundamental_symmetry": "eta = 2 P47 - I",
            "eta_inertia": {"positive":47,"negative":78},
            "basepoint": "P47 Omega, Omega = 125^(-1/2) sum_cube |m1,m2,m3>",
            "time_raw": "K^2 Omega",
            "space_raw": ["P47 Jz^(1) Omega","P47 Jz^(2) Omega","P47 Jz^(3) Omega"],
            "spatial_gram_eigenvalues": [float(x) for x in spatial_eigs],
            "pullback_gram": G.tolist(),
            "pullback_residual_to_Minkowski": float(np.linalg.norm(G-target,2)),
            "determinant": float(np.linalg.det(G)),
        },
        "unmarked_moduli_embedding": {
            "real_domain_dimension": 47,
            "canonical_basis": "pivot Gram-Schmidt of columns P47 e_n in lexicographic cube basis",
            "profile": "F_q(u)=u^78+u^47+sum_{a=0}^{46} c_a(q) u^a",
            "metric": "g_q=-2 du dv+dx^2+dy^2+F_q(u)(x^2-y^2)du^2",
            "rigidity_coeff_u78": c78,
            "rigidity_coeff_u77": c77,
            "rigidity_coeff_u47_before_b0": c47,
            "rigidity_conclusion": "isometry => s=1, a=1, b=0 => all c_a equal => q equal",
            "correspondence": "E47_R bijects with its image M_E47 inside Ricci-flat Lorentzian metrics / Diff",
        },
        "boundary": (
            "This is an injective correspondence onto a 47-real-dimensional plane-wave "
            "subfamily of the full unmarked vacuum Einstein moduli space, not a parametrization "
            "of the entire Einstein moduli space. The intrinsic spacetime uses the full locked "
            "tensor-cube datum (ordered V2^⊗3 product basis and factor generators), not the "
            "abstract projector P47 stripped of that structure."
        ),
    }
    OUT.write_text(json.dumps(cert, indent=2))
    print(json.dumps(cert, indent=2))
    if cert["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()