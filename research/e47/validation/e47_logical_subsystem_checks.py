#!/usr/bin/env python3
"""E47 logical qubit in the J = 2 multiplicity: reproduction and gauge-aware collective-noise test.

Carrier H = V2 x V2 x V2 (dim 125). Its J = 2 sector factors as C^5 (multiplicity, one copy per
intermediate coupling j12 = 0..4) tensor V2 (gauge). Collective rotations act as I_5 x D2(g).

Logical qubit: copies j12 = 0, 1 of C^5, prepared in |+>; gauge state |M = 2>.
Channels: N_{theta,A}(rho) = (U rho U^+ + U^+ rho U)/2, U = exp(-i theta A), with
  collective A = J_x/2, J_y/2, J_z/2; local A = (S_z x I x I)/2;
  uniform collective rotation: exact twirl over the 60-element icosahedral group
  (spin 2 stays irreducible on it, so the twirl equals the Haar twirl on V2).
Decoders:
  fixed-gauge  L = B^+ rho B, B = the two code vectors at M = 2 (the decoder of the 16 October report)
  gauge-aware  L = restriction to copies {0, 1} of Tr_V2[W^+ rho W]
Bare control: one spin-2, |+> on m = 2, 1, under S_a/2.
Also: exact range of the report's local-noise numbers over every valid code basis.

Usage: python3 e47_logical_subsystem_checks.py [--json record.json]   Needs numpy, scipy, sympy.
Machine record: MC-E47-LOGICAL-SUBSYSTEM-20261016-001
"""
from __future__ import annotations

import itertools
import json
import sys

import numpy as np
from scipy.linalg import eigh, expm
from sympy import S
from sympy.physics.quantum.cg import CG

MS = [2, 1, 0, -1, -2]
PLUS = np.array([1, 1]) / np.sqrt(2)
REPORT_LOCAL = {0.1: (0.99480352, 0.99894534), 0.3: (0.95407752, 0.99057413),
                0.6: (0.82728631, 0.96317404), 1.0: (0.58541196, 0.90323760)}   # (F, E47 survival)
REPORT_BARE = {0.1: 0.99937513, 0.3: 0.99438554, 0.6: 0.97766824, 1.0: 0.93879128}


def spin2():
    j = 2
    m = np.arange(j, -j - 1, -1, dtype=float)
    z = np.diag(m).astype(complex)
    p = np.zeros((5, 5), complex)
    for c, mm in enumerate(m):
        if c:
            p[c - 1, c] = np.sqrt((j - mm) * (j + mm + 1))
    return (p + p.conj().T) / 2, (p - p.conj().T) / (2j), z


s = spin2()
I5 = np.eye(5)
k3 = lambda a, b, c: np.kron(np.kron(a, b), c)
J = [k3(a, I5, I5) + k3(I5, a, I5) + k3(I5, I5, a) for a in s]
C = sum(j @ j for j in J)
I = np.eye(125)
wC, UC = eigh(C)
P47 = UC[:, np.isclose(wC, 6) | np.isclose(wC, 30)]
P47 = P47 @ P47.conj().T


def coupled(j12, M):
    v = np.zeros(125, complex)
    for m1, m2, m3 in itertools.product(MS, MS, MS):
        m12 = m1 + m2
        if m1 + m2 + m3 != M or abs(m12) > j12:
            continue
        c = CG(S(2), S(m1), S(2), S(m2), S(j12), S(m12)).doit() * CG(S(j12), S(m12), S(2), S(m3), S(2), S(M)).doit()
        v[MS.index(m1) * 25 + MS.index(m2) * 5 + MS.index(m3)] += float(c)
    return v


W = np.column_stack([coupled(k, M) for k in range(5) for M in MS])     # column k*5 + index(M)
B = W[:, [0 * 5 + 0, 1 * 5 + 0]]                                        # copies 0, 1 at M = 2


def channel(rho, U):
    return 0.5 * (U @ rho @ U.conj().T + U.conj().T @ rho @ U)


def decode(rho):
    Lf = B.conj().T @ rho @ B
    R = (W.conj().T @ rho @ W).reshape(5, 5, 5, 5)
    Rm = np.einsum("aibi->ab", R)
    Lg = Rm[:2, :2]
    re = lambda L: (float(np.real(PLUS @ L @ PLUS)), float(np.real(np.trace(L))))
    (Ff, wf), (Fg, wg) = re(Lf), re(Lg)
    return {"fixed_gauge_F": Ff, "fixed_gauge_weight": wf, "gauge_aware_F": Fg, "gauge_aware_weight": wg,
            "E47_survival": float(np.real(np.trace(P47 @ rho)))}


def icosahedral_spin2():
    phi = (1 + 5 ** 0.5) / 2
    n5 = np.array([0, 1, phi]) / np.linalg.norm([0, 1, phi])
    n3 = np.ones(3) / 3 ** 0.5
    gens = [expm(-1j * 2 * np.pi / 5 * sum(c * a for c, a in zip(n5, s))),
            expm(-1j * 2 * np.pi / 3 * sum(c * a for c, a in zip(n3, s)))]
    key = lambda M: tuple(np.round(np.concatenate([M.real.ravel(), M.imag.ravel()]), 7))
    group, frontier = {key(np.eye(5)): np.eye(5, dtype=complex)}, [np.eye(5, dtype=complex)]
    while frontier:
        new = []
        for M in frontier:
            for g in gens:
                X = g @ M
                if key(X) not in group:
                    group[key(X)] = X
                    new.append(X)
        frontier = new
    return list(group.values())


def run():
    out, checks = {}, {}
    # structure
    fac = max(float(np.linalg.norm(W.conj().T @ Ja @ W - np.kron(I5, sa), 2)) for Ja, sa in zip(J, s))
    out["structure"] = {"isometry": float(np.linalg.norm(W.conj().T @ W - np.eye(25), 2)),
                        "casimir_6": float(np.linalg.norm(C @ W - 6 * W, 2)),
                        "inside_E47": float(np.linalg.norm(P47 @ W - W, 2)),
                        "factorization_I5_x_s": fac, "rank_P47": int(round(np.trace(P47).real))}
    st = out["structure"]
    checks["J2_sector_is_C5_x_V2_inside_E47"] = max(st["isometry"], st["casimir_6"], st["inside_E47"], fac) < 1e-12 and st["rank_P47"] == 47

    psiL = np.zeros(5)
    psiL[:2] = PLUS
    gauge = np.zeros(5)
    gauge[0] = 1
    v = W @ np.kron(psiL, gauge)
    rho0 = np.outer(v, v.conj())
    out["code_vector_equals_B_plus"] = float(np.linalg.norm(v - B @ PLUS))

    thetas = [0.0, 0.1, 0.3, 0.6, 1.0]
    table = {}
    for name, A in (("collective_Jx", J[0] / 2), ("collective_Jy", J[1] / 2), ("collective_Jz", J[2] / 2),
                    ("local_Sz_first_spin", k3(s[2], I5, I5) / 2)):
        table[name] = {str(t): decode(channel(rho0, expm(-1j * t * A))) for t in thetas}
    G60 = icosahedral_spin2()
    sig = np.random.default_rng(3).normal(size=(5, 5)) + 1j * np.random.default_rng(4).normal(size=(5, 5))
    sig = sig @ sig.conj().T
    twirl_err = float(np.linalg.norm(sum(D @ sig @ D.conj().T for D in G60) / len(G60) - np.trace(sig) * I5 / 5, 2))
    rho_tw = sum(k3(D, D, D) @ rho0 @ k3(D, D, D).conj().T for D in G60) / len(G60)
    table["uniform_collective_rotation"] = decode(rho_tw)
    out["channels"] = table
    out["icosahedral"] = {"order": len(G60), "twirl_minus_haar_on_V2": twirl_err}

    # bare control: single spin-2, |+> on m = 2, 1
    vb = np.zeros(5, complex)
    vb[:2] = PLUS
    rb = np.outer(vb, vb.conj())
    bare = {}
    for name, a in (("Sx", s[0]), ("Sy", s[1]), ("Sz", s[2])):
        bare[name] = {str(t): float(np.real(vb.conj() @ channel(rb, expm(-1j * t * a / 2)) @ vb)) for t in thetas}
    bare["uniform_rotation"] = float(np.real(vb.conj() @ (sum(D @ rb @ D.conj().T for D in G60) / len(G60)) @ vb))
    out["bare_control"] = bare

    # dense curves for the plate
    grid = np.linspace(0, np.pi, 61)
    out["curves_x"] = {"theta": grid.tolist(),
                       "fixed_gauge_F": [decode(channel(rho0, expm(-1j * t * J[0] / 2)))["fixed_gauge_F"] for t in grid],
                       "gauge_aware_F": [decode(channel(rho0, expm(-1j * t * J[0] / 2)))["gauge_aware_F"] for t in grid],
                       "bare_Sx_F": [float(np.real(vb.conj() @ channel(rb, expm(-1j * t * s[0] / 2)) @ vb)) for t in grid]}

    # exact range of the report's local-noise numbers over every code vector v in the J=2, M=2 space
    B5 = W[:, [k * 5 for k in range(5)]]
    Aloc = k3(s[2], I5, I5) / 2
    def ranges(t):
        U = expm(-1j * t * Aloc)
        M = B5.conj().T @ U @ B5                         # F = |v^+ M v|^2 over unit v in C^5
        lam = [np.linalg.eigvalsh((np.exp(1j * f) * M + np.exp(-1j * f) * M.conj().T) / 2) for f in np.linspace(0, 2 * np.pi, 7201)]
        rmax = max(l[-1] for l in lam)
        dmin = max(0.0, max(l[0] for l in lam))
        Q = B5.conj().T @ (0.5 * (U.conj().T @ P47 @ U + U @ P47 @ U.conj().T)) @ B5
        q = np.linalg.eigvalsh((Q + Q.conj().T) / 2)
        return {"F_min": float(dmin ** 2), "F_max": float(rmax ** 2), "survival_min": float(q[0]), "survival_max": float(q[-1])}
    lg = np.linspace(0, 1, 41)
    out["local_ranges"] = {"theta": lg.tolist(), "ranges": [ranges(t) for t in lg],
                           "coupled_basis_F": [decode(channel(rho0, expm(-1j * t * Aloc)))["fixed_gauge_F"] for t in lg]}
    rep = {str(t): ranges(t) for t in REPORT_LOCAL}
    out["report_local_inside_exact_range"] = {t: {"report": REPORT_LOCAL[float(t)], "range": r} for t, r in rep.items()}

    # a code vector that first-spin S_z noise cannot touch: |m1 = 2> x (spins 2, 3 in a singlet)
    e = lambda mm: np.eye(5)[MS.index(mm)]
    singlet = sum((-1) ** (2 - mm) * np.kron(e(mm), e(-mm)) for mm in MS) / np.sqrt(5)
    vs = np.kron(e(2), singlet)
    imm = [float(abs(vs.conj() @ expm(-1j * t * Aloc) @ vs) ** 2) for t in thetas]
    out["immune_code_vector"] = {"vector": "|m1=2> x singlet(spins 2,3)", "norm_inside_J2_M2_space": float(np.linalg.norm(B5.conj().T @ vs)), "F": imm}

    # the benchmark picks its code vectors as the first two left singular vectors of P_{J=2} restricted to
    # the M = 2 product states; all five nonzero singular values equal 1, so that choice is not unique
    wz = np.real(np.diag(J[2]))
    E2 = np.eye(125)[:, np.abs(wz - 2) < 1e-10]
    P2 = UC[:, np.isclose(wC, 6)] @ UC[:, np.isclose(wC, 6)].conj().T
    sv = np.linalg.svd(P2 @ E2, compute_uv=False)
    out["benchmark_svd_singular_values"] = [float(x) for x in sv[:6]]
    out["benchmark_rerun_note"] = ("e47_logical_benchmark.py (sha256 c5581dae...) run unchanged under PyTorch 2.14.1 gives local first-spin "
                                   "F = 0.58298921, w = 0.64828921, survival = 0.87306499 at theta = 1; the report (PyTorch 2.10.0) lists "
                                   "0.58541196, 0.72717416, 0.90323760")

    # gauge-aware decoding for random logical pairs in C^5 and random gauge states in V2
    rng, worst = np.random.default_rng(11), 0.0
    UJx = expm(-1j * 1.0 * J[0] / 2)
    for _ in range(40):
        EL, _r = np.linalg.qr(rng.normal(size=(5, 2)) + 1j * rng.normal(size=(5, 2)))
        g = rng.normal(size=5) + 1j * rng.normal(size=5)
        g /= np.linalg.norm(g)
        vv = W @ np.kron(EL @ PLUS, g)
        r0 = np.outer(vv, vv.conj())
        for r in (channel(r0, UJx), sum(k3(D, D, D) @ r0 @ k3(D, D, D).conj().T for D in G60) / len(G60)):
            Rm = np.einsum("aibi->ab", (W.conj().T @ r @ W).reshape(5, 5, 5, 5))
            worst = max(worst, abs(float(np.real(PLUS @ (EL.conj().T @ Rm @ EL) @ PLUS)) - 1))
    out["random_codes_gauge_aware_max_deviation"] = worst

    # checks
    coll = [table[c][str(t)] for c in ("collective_Jx", "collective_Jy", "collective_Jz") for t in thetas] + [table["uniform_collective_rotation"]]
    checks["gauge_aware_F_is_1_under_every_collective_channel"] = max(abs(d["gauge_aware_F"] - 1) for d in coll) < 1e-12
    checks["no_leakage_from_E47_under_collective_noise"] = max(abs(d["E47_survival"] - 1) for d in coll) < 1e-12
    checks["fixed_gauge_exact_under_Jz"] = max(abs(table["collective_Jz"][str(t)]["fixed_gauge_F"] - 1) for t in thetas) < 1e-12
    checks["fixed_gauge_F_equals_cos8_theta_over_4_under_Jx_Jy"] = max(
        abs(table[c][str(t)]["fixed_gauge_F"] - np.cos(t / 4) ** 8) for c in ("collective_Jx", "collective_Jy") for t in thetas) < 1e-12
    checks["fixed_gauge_conditional_F_is_1_under_collective"] = max(
        abs(d["fixed_gauge_F"] / d["fixed_gauge_weight"] - 1) for d in coll) < 1e-12
    checks["uniform_rotation_fixed_gauge_and_bare_give_one_fifth"] = (abs(table["uniform_collective_rotation"]["fixed_gauge_F"] - 0.2) < 1e-12
                                                                     and abs(bare["uniform_rotation"] - 0.2) < 1e-12 and twirl_err < 1e-12 and len(G60) == 60)
    checks["bare_Sz_matches_report_cos2_theta_over_4"] = all(abs(bare["Sz"][str(t)] - np.cos(t / 4) ** 2) < 1e-12 and abs(bare["Sz"][str(t)] - REPORT_BARE[t]) < 5e-9 for t in REPORT_BARE)
    checks["report_local_values_inside_exact_range"] = all(
        r["F_min"] - 1e-9 <= REPORT_LOCAL[float(t)][0] <= r["F_max"] + 1e-9 and r["survival_min"] - 1e-9 <= REPORT_LOCAL[float(t)][1] <= r["survival_max"] + 1e-9
        for t, r in rep.items())
    checks["encoding_follows_report_protocol"] = out["code_vector_equals_B_plus"] < 1e-14
    checks["first_spin_Sz_immune_code_vector_exists"] = (abs(out["immune_code_vector"]["norm_inside_J2_M2_space"] - 1) < 1e-12
                                                         and max(abs(x - 1) for x in imm) < 1e-12)
    checks["gauge_aware_F_is_1_for_random_codes_and_gauges"] = worst < 1e-12
    checks["benchmark_svd_code_basis_is_not_unique"] = bool(np.allclose(sv[:5], 1, atol=1e-12) and np.all(sv[5:] < 1e-12))
    return out, {k: bool(v) for k, v in checks.items()}


if __name__ == "__main__":
    out, checks = run()
    if "--json" in sys.argv:
        import hashlib
        rec = {"certificate": "MC-E47-LOGICAL-SUBSYSTEM-20261016-001", "status": "PASS" if all(checks.values()) else "FAIL",
               "evidence": "E0 exact (J=2 sector = C^5 x V2, closed forms cos^2(theta/4), cos^8(theta/4), 1/5); E1 machine reconstruction (NumPy, SciPy, SymPy, complex128)",
               "subject": "E47 logical qubit in the J=2 multiplicity: reproduction of the 16 October logical-qubit report and gauge-aware collective-noise test",
               "source_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
               "checks": checks, "check_count": len(checks), "pass_count": sum(checks.values()), "results": out}
        json.dump(rec, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    t = out["channels"]
    print("structure:", out["structure"])
    print("icosahedral:", out["icosahedral"])
    for c in ("collective_Jz", "collective_Jx", "collective_Jy", "local_Sz_first_spin"):
        d = t[c]["1.0"]
        print(f"{c:22s} theta=1: fixed-gauge F {d['fixed_gauge_F']:.8f} (w {d['fixed_gauge_weight']:.8f}) | gauge-aware F {d['gauge_aware_F']:.8f} (w {d['gauge_aware_weight']:.8f}) | E47 {d['E47_survival']:.8f}")
    d = t["uniform_collective_rotation"]
    print(f"{'uniform rotation':22s}          fixed-gauge F {d['fixed_gauge_F']:.8f} | gauge-aware F {d['gauge_aware_F']:.8f} | E47 {d['E47_survival']:.8f}")
    print("bare control theta=1:", {k: (v["1.0"] if isinstance(v, dict) else v) for k, v in out["bare_control"].items()})
    for th, r in out["report_local_inside_exact_range"].items():
        print(f"local theta={th}: report F {r['report'][0]} in [{r['range']['F_min']:.6f}, {r['range']['F_max']:.6f}]; survival {r['report'][1]} in [{r['range']['survival_min']:.6f}, {r['range']['survival_max']:.6f}]")
    print("\n".join(f"[{'PASS' if ok else 'FAIL'}] {k}" for k, ok in checks.items()))
    sys.exit(0 if all(checks.values()) else 1)
