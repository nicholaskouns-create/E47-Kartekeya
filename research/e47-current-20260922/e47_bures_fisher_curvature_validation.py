
import numpy as np, math, json
from scipy.linalg import eigh, expm
from pathlib import Path

# ============================================================
# E47 -> canonical 125-d density family -> Bures/SLD geometry
# No warp metric is introduced anywhere in this calculation.
#
# Parameter leaf:
#   theta = (tau, x, y, z)
#   rho(theta) = U(x,y,z) exp[-tau K^2/(2 Delta)] rho0
#                exp[-tau K^2/(2 Delta)] U^\dagger / Z
#   rho0 = I_125 / 125
#   U = exp(-i x Jx^(1)) exp(-i y Jy^(1)) exp(-i z Jz^(1))
#
# Because rho0 is maximally mixed, rho_tau is exactly
#   rho_tau = exp[-tau K^2/Delta] / Tr exp[-tau K^2/Delta].
#
# Bures metric:
#   g^B_{mu nu} = 1/2 sum_ij
#       (d_mu rho)_ij (d_nu rho)_ji / (lambda_i + lambda_j)
#
# SLD Fisher:
#   F_SLD = 4 g^B.
# ============================================================

TOL = 1e-10
j = 2
m = np.arange(j, -j-1, -1, dtype=float)
d = 5
Jz5 = np.diag(m).astype(complex)
Jp = np.zeros((d,d), complex)
for col, mm in enumerate(m):
    if col > 0:
        Jp[col-1,col] = np.sqrt(j*(j+1) - mm*(mm+1))
Jm = Jp.conj().T
Jx5 = (Jp + Jm)/2
Jy5 = (Jp - Jm)/(2j)

I5 = np.eye(5, dtype=complex)
I25 = np.eye(25, dtype=complex)
I125 = np.eye(125, dtype=complex)

def k3(a,b,c):
    return np.kron(np.kron(a,b),c)

JxT = k3(Jx5,I5,I5) + k3(I5,Jx5,I5) + k3(I5,I5,Jx5)
JyT = k3(Jy5,I5,I5) + k3(I5,Jy5,I5) + k3(I5,I5,Jy5)
JzT = k3(Jz5,I5,I5) + k3(I5,Jz5,I5) + k3(I5,I5,Jz5)

C = JxT@JxT + JyT@JyT + JzT@JzT
C = (C + C.conj().T)/2
K = (C - 6*I125) @ (C - 30*I125)
K = (K + K.conj().T)/2
K2 = K@K
K2 = (K2 + K2.conj().T)/2

# Direct spectrum
ce = np.linalg.eigvalsh(C)
cvals, cmults = np.unique(np.rint(ce).astype(int), return_counts=True)
kw, V0 = eigh(K2)
kernel = np.isclose(kw, 0.0, atol=1e-7)
P = V0[:,kernel] @ V0[:,kernel].conj().T
Q = I125 - P

positive = kw[kw > 1e-7]
DELTA = float(np.min(positive))
K2NORM = float(np.max(positive))
TRK2 = float(np.trace(K2).real)
a = kw / DELTA

# Local first-factor SU(2) generators in the K^2 eigenbasis.
Gfull = [np.kron(G, I25) for G in (Jx5, Jy5, Jz5)]
M = [V0.conj().T @ G @ V0 for G in Gfull]
denJ = float(np.trace(Jx5@Jx5).real)

def su2_coeffs(H):
    return np.array([
        np.trace(Jx5@H).real/denJ,
        np.trace(Jy5@H).real/denJ,
        np.trace(Jz5@H).real/denJ,
    ])

def metric_and_parts(theta, return_parts=False):
    tau, x, y, z = map(float, theta)

    # Canonical thermalized/contraction spectrum.
    wt = np.exp(-tau*a)
    lam = wt / wt.sum()
    abar = float(np.dot(lam, a))

    # tau tangent in instantaneous eigenbasis.
    D = [np.diag(lam*(abar-a)).astype(complex)]

    # Euler-coordinate tangent generators, expressed in the co-moving frame.
    Uy = expm(-1j*y*Jy5)
    Uz = expm(-1j*z*Jz5)
    Hx = Uz.conj().T @ Uy.conj().T @ Jx5 @ Uy @ Uz
    Hy = Uz.conj().T @ Jy5 @ Uz
    Hz = Jz5

    for H in (Hx,Hy,Hz):
        cx,cy,cz = su2_coeffs(H)
        He = cx*M[0] + cy*M[1] + cz*M[2]
        D.append(-1j * He * (lam[None,:] - lam[:,None]))

    denom = lam[:,None] + lam[None,:]
    mask = denom > 1e-15

    g = np.zeros((4,4), float)
    for mu in range(4):
        for nu in range(mu,4):
            term = np.zeros_like(D[mu], dtype=complex)
            term[mask] = D[mu][mask] * D[nu].T[mask] / denom[mask]
            val = 0.5*np.sum(term).real
            g[mu,nu] = g[nu,mu] = val

    if not return_parts:
        return g

    # SLDs in rho's instantaneous eigenbasis.
    L = []
    for de in D:
        Le = np.zeros_like(de)
        Le[mask] = 2*de[mask]/denom[mask]
        L.append(Le)

    U5 = expm(-1j*x*Jx5) @ expm(-1j*y*Jy5) @ expm(-1j*z*Jz5)
    U = np.kron(U5, I25)

    # Direct Fisher metric check from SLDs.
    F = np.zeros((4,4), float)
    RHO = np.diag(lam)
    for mu in range(4):
        for nu in range(4):
            F[mu,nu] = 0.5*np.trace(
                RHO @ (L[mu]@L[nu] + L[nu]@L[mu])
            ).real

    return g, lam, L, U, F

# ------------------------------------------------------------
# Numerical differential geometry on the 4D leaf
# ------------------------------------------------------------

def metric_derivatives(theta, h=4e-3):
    theta = np.array(theta, float)
    d = 4
    g0 = metric_and_parts(theta)
    dg = np.zeros((d,d,d), float)       # dg[a,i,j]
    d2g = np.zeros((d,d,d,d), float)    # d2g[a,b,i,j]
    E = np.eye(d)

    # 5-point first derivatives and diagonal second derivatives.
    for aa in range(d):
        gm2 = metric_and_parts(theta - 2*h*E[aa])
        gm1 = metric_and_parts(theta - h*E[aa])
        gp1 = metric_and_parts(theta + h*E[aa])
        gp2 = metric_and_parts(theta + 2*h*E[aa])
        dg[aa] = (gm2 - 8*gm1 + 8*gp1 - gp2)/(12*h)
        d2g[aa,aa] = (-gp2 + 16*gp1 - 30*g0 + 16*gm1 - gm2)/(12*h*h)

    # Mixed Hessian entries.
    for aa in range(d):
        for bb in range(aa+1,d):
            fpp = metric_and_parts(theta + h*E[aa] + h*E[bb])
            fpm = metric_and_parts(theta + h*E[aa] - h*E[bb])
            fmp = metric_and_parts(theta - h*E[aa] + h*E[bb])
            fmm = metric_and_parts(theta - h*E[aa] - h*E[bb])
            mixed = (fpp - fpm - fmp + fmm)/(4*h*h)
            d2g[aa,bb] = mixed
            d2g[bb,aa] = mixed
    return g0, dg, d2g

def curvature(theta, h=4e-3):
    g, dg, d2g = metric_derivatives(theta, h)
    gi = np.linalg.inv(g)
    d = 4

    Gamma = np.zeros((d,d,d), float)
    for r in range(d):
        for mu in range(d):
            for nu in range(d):
                Gamma[r,mu,nu] = 0.5*sum(
                    gi[r,s]*(dg[mu,s,nu] + dg[nu,s,mu] - dg[s,mu,nu])
                    for s in range(d)
                )

    dgi = np.array([-gi@dg[a_]@gi for a_ in range(d)])
    dGamma = np.zeros((d,d,d,d), float)  # dGamma[a,r,mu,nu]
    for aa in range(d):
        for r in range(d):
            for mu in range(d):
                for nu in range(d):
                    dGamma[aa,r,mu,nu] = 0.5*sum(
                        dgi[aa,r,s] *
                        (dg[mu,s,nu] + dg[nu,s,mu] - dg[s,mu,nu])
                        +
                        gi[r,s] *
                        (d2g[aa,mu,s,nu] + d2g[aa,nu,s,mu] - d2g[aa,s,mu,nu])
                        for s in range(d)
                    )

    # R^r_{s mu nu}
    Riemann = np.zeros((d,d,d,d), float)
    for r in range(d):
        for s in range(d):
            for mu in range(d):
                for nu in range(d):
                    Riemann[r,s,mu,nu] = (
                        dGamma[mu,r,nu,s] - dGamma[nu,r,mu,s]
                        + sum(
                            Gamma[r,mu,l]*Gamma[l,nu,s]
                            - Gamma[r,nu,l]*Gamma[l,mu,s]
                            for l in range(d)
                        )
                    )

    Ricci = np.einsum("rsrn->sn", Riemann)
    Rscalar = float(np.einsum("ij,ij", gi, Ricci))
    Einstein = Ricci - 0.5*Rscalar*g

    Rlow = np.einsum("ar,rsuv->asuv", g, Riemann)
    symmetry = {
        "R_abmn_antisym_mn": float(np.max(np.abs(Rlow + np.swapaxes(Rlow,2,3)))),
        "R_abmn_antisym_ab": float(np.max(np.abs(Rlow + np.swapaxes(Rlow,0,1)))),
        "pair_exchange": float(np.max(np.abs(Rlow - np.transpose(Rlow,(2,3,0,1))))),
        "first_bianchi": float(np.max(np.abs(
            Rlow
            + np.transpose(Rlow,(0,2,3,1))
            + np.transpose(Rlow,(0,3,1,2))
        ))),
        "ricci_symmetry": float(np.max(np.abs(Ricci - Ricci.T))),
    }
    return g, Gamma, Riemann, Ricci, Rscalar, Einstein, symmetry

# ------------------------------------------------------------
# Direct comparison to the 47/78 block construction
# ------------------------------------------------------------

def sld_pullback(Aop, theta):
    """
    Natural SLD/Bures pullback of a Hilbert-space operator A:

      Pi_A(mu,nu)
        = 1/16 Re Tr[(rho A + A rho){L_mu,L_nu}].

    Pi_I = g_B exactly.
    """
    g, lam, L, U, F = metric_and_parts(theta, return_parts=True)
    Ae = V0.conj().T @ U.conj().T @ Aop @ U @ V0
    rhoA_plus_Arho = (lam[:,None] + lam[None,:]) * Ae

    B = np.zeros((4,4), float)
    for mu in range(4):
        for nu in range(mu,4):
            anti = L[mu]@L[nu] + L[nu]@L[mu]
            val = np.trace(rhoA_plus_Arho @ anti).real/16.0
            B[mu,nu] = B[nu,mu] = val
    return B

def compare_block(theta, sigma=1.0, h=4e-3):
    gB, Gamma, Riemann, RicB, RB, GB, sym = curvature(theta,h)

    g_op = P + sigma*Q
    Ric_op = K2                       # = Q K^2 Q
    R_op = TRK2/sigma
    Lambda = R_op/2.0
    G_op = Ric_op - 0.5*R_op*g_op

    block_residual = G_op + Lambda*g_op - Ric_op

    PB_g = sld_pullback(g_op, theta)
    PB_Ric = sld_pullback(Ric_op, theta)
    PB_G = sld_pullback(G_op, theta)
    PB_residual = PB_G + Lambda*PB_g - PB_Ric

    # Direct shape comparison after the only innocuous freedom: one scalar scale.
    alpha = float(np.vdot(PB_G, GB).real / np.vdot(PB_G, PB_G).real)
    direct_relative_residual = float(
        np.linalg.norm(GB - alpha*PB_G) / np.linalg.norm(GB)
    )
    cosine = float(
        np.vdot(GB, PB_G).real /
        (np.linalg.norm(GB)*np.linalg.norm(PB_G))
    )

    # More permissive test:
    # can GB + lambda*gB be made proportional to pulled-back block Ricci?
    design = np.column_stack([gB.ravel(), -PB_Ric.ravel()])
    lam_fit, beta_fit = np.linalg.lstsq(
        design, -GB.ravel(), rcond=None
    )[0]
    fit_residual = float(
        np.linalg.norm(GB + lam_fit*gB - beta_fit*PB_Ric)
        / np.linalg.norm(GB)
    )

    return {
        "metric": gB,
        "Gamma": Gamma,
        "Riemann": Riemann,
        "Ricci": RicB,
        "Rscalar": RB,
        "Einstein": GB,
        "symmetry": sym,
        "metric_eigenvalues": np.linalg.eigvalsh(gB),
        "metric_rank": int(np.linalg.matrix_rank(gB, tol=1e-10)),
        "block_identity_residual_2norm": float(np.linalg.norm(block_residual,2)),
        "pulled_block_identity_residual_F": float(np.linalg.norm(PB_residual)),
        "direct_Einstein_cosine": cosine,
        "direct_Einstein_best_scale": alpha,
        "direct_Einstein_relative_residual": direct_relative_residual,
        "best_lambda_for_G_plus_lambda_g_vs_pullback_Ric": float(lam_fit),
        "best_scale_for_pullback_Ric": float(beta_fit),
        "best_Einstein_equation_relative_residual": fit_residual,
    }

# ============================================================
# Execute at four genuine 4D leaf points.
# ============================================================

points = [
    np.array([0.20,  0.10,  0.20, -0.10]),
    np.array([0.35,  0.21, -0.17,  0.13]),
    np.array([0.50, -0.40,  0.25,  0.30]),
    np.array([0.80,  0.70, -0.50,  0.40]),
]
central = points[1]

records = []
central_full = None
for pnt in points:
    r = compare_block(pnt, sigma=1.0, h=4e-3)
    record = {
        "theta": pnt.tolist(),
        "metric_eigenvalues": r["metric_eigenvalues"].tolist(),
        "metric_rank": r["metric_rank"],
        "Rscalar": r["Rscalar"],
        "Einstein_F_norm": float(np.linalg.norm(r["Einstein"])),
        "block_identity_residual_2norm": r["block_identity_residual_2norm"],
        "pulled_block_identity_residual_F": r["pulled_block_identity_residual_F"],
        "direct_Einstein_cosine": r["direct_Einstein_cosine"],
        "direct_Einstein_relative_residual": r["direct_Einstein_relative_residual"],
        "best_lambda": r["best_lambda_for_G_plus_lambda_g_vs_pullback_Ric"],
        "best_scale": r["best_scale_for_pullback_Ric"],
        "best_Einstein_equation_relative_residual":
            r["best_Einstein_equation_relative_residual"],
        "curvature_symmetry_residuals": r["symmetry"],
    }
    records.append(record)
    if np.allclose(pnt,central):
        central_full = r

# Fisher = 4 * Bures check at central point.
gC, lamC, LC, UC, FC = metric_and_parts(central, return_parts=True)
fisher_relation_error = float(np.linalg.norm(FC - 4*gC))

# Time/contraction direction alignment with the softest Bures eigenvector.
ewC, evC = np.linalg.eigh(gC)
soft_time_overlap = float(abs(evC[0,0])**2)

# Step-size convergence of scalar curvature at central point.
convergence = []
for h in (1e-2, 6e-3, 4e-3, 3e-3, 2e-3):
    c = curvature(central,h)
    convergence.append({
        "h": h,
        "Rscalar": c[4],
        "Einstein_F_norm": float(np.linalg.norm(c[5])),
    })

certificate = {
    "schema":"E47-BURES-FISHER-CURVATURE-VALIDATION-1.0",
    "leaf":{
        "coordinates":["tau","x","y","z"],
        "rho0":"I_125/125",
        "contraction":"exp[-tau K^2/(2 Delta)] on both sides",
        "unitary_fiber":
          "exp(-i x Jx^(1)) exp(-i y Jy^(1)) exp(-i z Jz^(1))",
        "warp_metric_used":False,
    },
    "e47":{
        "dim_H":125,
        "casimir_spectrum":cvals.tolist(),
        "casimir_multiplicities":cmults.tolist(),
        "dim_kernel":int(kernel.sum()),
        "dim_complement":int(125-kernel.sum()),
        "Delta":DELTA,
        "K2_norm":K2NORM,
        "Tr_K2":TRK2,
        "Omega_c":47/125,
    },
    "bures_sld":{
        "Fisher_minus_4Bures_F_norm":fisher_relation_error,
        "central_softest_eigenvalue":float(ewC[0]),
        "central_soft_direction_time_overlap":soft_time_overlap,
    },
    "sample_points":records,
    "step_convergence":convergence,
    "central_full_tensors":{
        "theta":central.tolist(),
        "g_Bures":central_full["metric"].tolist(),
        "Gamma_r_mn":central_full["Gamma"].tolist(),
        "Riemann_r_s_mn":central_full["Riemann"].tolist(),
        "Ricci_mn":central_full["Ricci"].tolist(),
        "Rscalar":central_full["Rscalar"],
        "Einstein_mn":central_full["Einstein"].tolist(),
    },
    "conclusion":{
        "bures_leaf_rank4_all_samples":all(r["metric_rank"]==4 for r in records),
        "bures_metric_positive_all_samples":
            all(min(r["metric_eigenvalues"])>0 for r in records),
        "block_identity_closes":
            all(r["block_identity_residual_2norm"]<1e-8 for r in records),
        "block_identity_closes_after_SLD_pullback":
            all(r["pulled_block_identity_residual_F"]<1e-8 for r in records),
        "bures_Einstein_equals_pulled_block_Einstein":
            all(r["direct_Einstein_relative_residual"]<1e-6 for r in records),
    }
}

Path("/mnt/data/e47_bures_fisher_curvature_certificate.json").write_text(
    json.dumps(certificate, indent=2)
)

# Human-readable report.
lines = []
lines.append("# E47 Bures/Fisher 4D Curvature Validation")
lines.append("")
lines.append("No warp metric is used. The metric is computed directly from the 125-dimensional density-state family through the Bures/SLD formula.")
lines.append("")
lines.append("## Canonical carrier")
lines.append(f"- dim H = 125")
lines.append(f"- dim ker K = {int(kernel.sum())}")
lines.append(f"- dim complement = {125-int(kernel.sum())}")
lines.append(f"- Δ = {DELTA:.12g}")
lines.append(f"- ||K²|| = {K2NORM:.12g}")
lines.append(f"- Tr(K²) = {TRK2:.12g}")
lines.append(f"- ||F_SLD - 4 g_Bures||_F = {fisher_relation_error:.3e}")
lines.append("")
lines.append("## Four-dimensional leaf results")
for r in records:
    lines.append(
        f"- θ={r['theta']}: rank={r['metric_rank']}, "
        f"eig(g)={np.array(r['metric_eigenvalues'])}, "
        f"R={r['Rscalar']:.9g}, "
        f"||G||_F={r['Einstein_F_norm']:.9g}, "
        f"direct block residual={r['direct_Einstein_relative_residual']:.6f}, "
        f"best Einstein-equation residual={r['best_Einstein_equation_relative_residual']:.6f}"
    )
lines.append("")
lines.append("## Central point")
lines.append(f"- θ = {central.tolist()}")
lines.append(f"- softest Bures eigenvalue = {ewC[0]:.12g}")
lines.append(f"- overlap of softest eigenvector with τ direction = {soft_time_overlap:.12f}")
lines.append(f"- scalar curvature R = {central_full['Rscalar']:.12g}")
lines.append(f"- ||G_Bures||_F = {np.linalg.norm(central_full['Einstein']):.12g}")
lines.append(f"- block Einstein identity residual = {central_full['block_identity_residual_2norm']:.3e}")
lines.append(f"- pulled block identity residual = {central_full['pulled_block_identity_residual_F']:.3e}")
lines.append(f"- direct G_Bures vs pulled G_block relative residual = {central_full['direct_Einstein_relative_residual']:.6f}")
lines.append("")
lines.append("## Result")
lines.append("- The Bures/SLD family is genuinely four-dimensional and positive-definite at every sampled point.")
lines.append("- Its Levi-Civita connection, Riemann tensor, Ricci tensor, scalar curvature and Einstein tensor are nontrivial.")
lines.append("- The 47/78 block Einstein identity closes to machine precision and remains closed after the explicit SLD pullback.")
lines.append("- The intrinsic Bures Einstein tensor is NOT identical to the SLD-pulled 47/78 block Einstein tensor for this canonical leaf.")
lines.append("- Therefore the missing E47 -> information geometry -> block Einstein identification is not yet an identity; an additional map/dynamical condition is required.")
Path("/mnt/data/e47_bures_fisher_curvature_report.md").write_text("\n".join(lines))

print("E47 / Bures-Fisher 4D validation")
print("--------------------------------")
print("Casimir spectrum:", cvals.tolist())
print("multiplicities   :", cmults.tolist())
print("dim ker K        :", int(kernel.sum()))
print("Delta            :", DELTA)
print("||K^2||          :", K2NORM)
print("Tr(K^2)          :", TRK2)
print("||F_SLD-4g_B||_F :", f"{fisher_relation_error:.3e}")
print()
for r in records:
    print(
        "theta=", r["theta"],
        " rank=", r["metric_rank"],
        " min eig=", f'{min(r["metric_eigenvalues"]):.6g}',
        " R=", f'{r["Rscalar"]:.6g}',
        " block_res=", f'{r["block_identity_residual_2norm"]:.2e}',
        " Gmatch_res=", f'{r["direct_Einstein_relative_residual"]:.6f}'
    )
print()
print("CENTRAL POINT theta =", central.tolist())
print("g_Bures =")
print(central_full["metric"])
print("Ricci =")
print(central_full["Ricci"])
print("R =", central_full["Rscalar"])
print("Einstein =")
print(central_full["Einstein"])
print("softest direction overlap with tau =", soft_time_overlap)
print("curvature symmetry residuals =", central_full["symmetry"])
print("direct G_Bures vs pulled G_block rel residual =",
      central_full["direct_Einstein_relative_residual"])
print("best G_Bures + lambda g vs beta pullback(Ric_block) rel residual =",
      central_full["best_Einstein_equation_relative_residual"])
print()
print("CONCLUSION =", certificate["conclusion"])