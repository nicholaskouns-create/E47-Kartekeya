#!/usr/bin/env python3
"""Ω_c Coherence Algebra — one-pass spectral validation + infographic."""


import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


out_dir = "/home/workdir/artifacts"
os.makedirs(out_dir, exist_ok=True)


# =============================================================================
# 1. SPECTRA — one pass, all assertions
# =============================================================================


j_primitive = 2
d_primitive = 2 * j_primitive + 1          # 5
dim_H = d_primitive ** 3                    # 125
assert dim_H == 125


# Clebsch–Gordan: V2 ⊗ V2 ⊗ V2
spins          = np.array([0, 1, 2, 3, 4, 5, 6])
multiplicities = np.array([1, 3, 5, 4, 3, 2, 1])
subspace_dims  = 2 * spins + 1
sector_dims    = multiplicities * subspace_dims


assert np.array_equal(sector_dims, [1, 9, 25, 28, 27, 22, 13])
assert np.sum(sector_dims) == dim_H


# Casimir spectrum λ_J = J(J+1)
casimir = spins * (spins + 1)
assert np.array_equal(casimir, [0, 2, 6, 12, 20, 30, 42])


# Constraint operator K = (C − 6I)(C − 30I)
# Spectrum μ_J = (λ_J − 6)(λ_J − 30)
mu = (casimir - 6) * (casimir - 30)
assert np.array_equal(mu, [180, 112, 0, -108, -140, 0, 432])


# Dissipative spectrum of K²
mu2 = mu ** 2
assert np.array_equal(mu2, [32400, 12544, 0, 11664, 19600, 0, 186624])


# Kernel E47 = E6 ⊕ E30  (J = 2 and J = 5)
kernel_mask    = (mu == 0)
dim_kernel     = int(np.sum(sector_dims[kernel_mask]))
dim_complement = int(np.sum(sector_dims[~kernel_mask]))
assert dim_kernel == 47
assert dim_complement == 78


omega_c  = dim_kernel / dim_H          # 47/125 = 0.376
r_margin = dim_complement / dim_kernel # 78/47
assert omega_c == 47 / 125 == 0.376
assert r_margin == 78 / 47
assert np.isclose(1 / (1 + r_margin), omega_c)


# Spectral gap on E47^⊥ and condition number
spectral_gap = np.min(mu2[~kernel_mask])   # 11664  (J=3)
lambda_max   = np.max(mu2)                 # 186624 (J=6)
kappa        = lambda_max / spectral_gap   # 16
rho          = (kappa - 1) / (kappa + 1)   # 15/17
assert spectral_gap == 11664
assert lambda_max == 186624
assert kappa == 16
assert rho == 15 / 17


# Polynomial projector P47(C)
# zeros at {0, 2, 12, 20, 31, 42}; value 1 at {6, 30}
def P_47(C):
    return (C - 31) * C * (C - 2) * (C - 12) * (C - 20) * (C - 42) / 1814400.0


P_on_spectrum = P_47(casimir.astype(float))
assert np.allclose(P_on_spectrum, [0, 0, 1, 0, 0, 1, 0])
trace_P47 = float(np.sum(sector_dims * P_on_spectrum))
assert np.isclose(trace_P47, 47.0)


print("[✓] SPECTRA VALIDATED 100%")
print(" J   m_J  d_J  dim   λ=J(J+1)    μ=(λ-6)(λ-30)     μ²         P47")
for J, m, d, dim, lam, muj, mu2j, p in zip(
    spins, multiplicities, subspace_dims, sector_dims,
    casimir, mu, mu2, P_on_spectrum
):
    tag = "KER E47" if muj == 0 else "perp"
    print(f" {J}    {m}    {d:2d}   {dim:3d}    {lam:4d}     {muj:6d}         {mu2j:7d}    {p:3.0f}   {tag}")
print(f"dim H={dim_H}  dim E47={dim_kernel}  rank K={dim_complement}")
print(f"Ωc={omega_c}=47/125   r={r_margin}=78/47")
print(f"Δ={spectral_gap}  Λmax={lambda_max}  κ={kappa}  ρ={rho}=15/17  Tr P47={trace_P47}")


# =============================================================================
# 2. RENDER
# =============================================================================


plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "mathtext.fontset": "dejavusans",
    "axes.unicode_minus": False,
    "figure.facecolor": "#0B0F19",
    "savefig.facecolor": "#0B0F19",
})


fig = plt.figure(figsize=(16.5, 13.2), facecolor="#0B0F19")
gs = gridspec.GridSpec(
    3, 2, figure=fig, height_ratios=[0.13, 1.0, 1.0],
    hspace=0.38, wspace=0.26, left=0.055, right=0.975, top=0.965, bottom=0.055,
)
title_style = {"color": "#E2E8F0", "fontsize": 12.5, "fontweight": "bold", "pad": 10}
label_style = {"color": "#94A3B8", "fontsize": 10}
grid_style  = {"color": "#1E293B", "linestyle": "--", "linewidth": 0.8}


ax_banner = fig.add_subplot(gs[0, :], facecolor="#0B0F19")
ax_banner.set_xlim(0, 1); ax_banner.set_ylim(0, 1); ax_banner.axis("off")
ax_banner.text(0.5, 0.72, r"$\Omega_c$  COHERENCE ALGEBRA  &  CONTRACTION FORMALISM",
               ha="center", va="center", color="#F8FAFC", fontsize=18, fontweight="bold")
ax_banner.text(0.5, 0.28,
               r"Spin-2 cube $V_2^{\otimes 3}$  $\cdot$  $\dim\mathcal{H}=125$  $\cdot$  $K=(C-6I)(C-30I)$  $\cdot$  $\ker K=E_{47}=E_6\oplus E_{30}$  $\cdot$  $\Omega_c=47/125=0.376$  $\cdot$  VERIFIED 100%",
               ha="center", va="center", color="#94A3B8", fontsize=9.2)
ax_banner.plot([0.08, 0.92], [0.02, 0.02], color="#10B981", lw=1.6, solid_capstyle="round")


# (A) isotypic decomposition
ax1 = fig.add_subplot(gs[1, 0], facecolor="#111827")
x = np.arange(len(spins))
ax1.bar(x, np.where(kernel_mask, sector_dims, 0), color="#10B981", width=0.55,
        edgecolor="#059669", linewidth=0.8, zorder=3, label=r"Invariant Kernel $E_{47}$ (dim = 47)")
ax1.bar(x, np.where(~kernel_mask, sector_dims, 0),
        bottom=np.where(kernel_mask, sector_dims, 0), color="#3B82F6", width=0.55,
        edgecolor="#2563EB", linewidth=0.8, zorder=3, label=r"Constrained $E_{47}^\perp$ (dim = 78)")
for i, total in enumerate(sector_dims):
    ax1.text(i, total + 1.15, f"{int(total)}\n({int(multiplicities[i])}×{int(subspace_dims[i])})",
             ha="center", va="bottom", color="#F8FAFC", fontsize=8.2, fontweight="bold")
ax1.set_title(r"(A) Carrier Space Isotypic Decomposition  ($\dim\mathcal{H}=125$)", **title_style)
ax1.set_xlabel(r"Total Spin Sector $J$", **label_style)
ax1.set_ylabel(r"Subspace Dimension $m_J\,(2J+1)$", **label_style)
ax1.set_xticks(x); ax1.set_xticklabels([f"$J={j}$" for j in spins], color="#CBD5E1")
ax1.tick_params(colors="#94A3B8"); ax1.set_ylim(0, 40)
ax1.grid(True, axis="y", **grid_style, zorder=0)
ax1.legend(facecolor="#1F2937", edgecolor="#374151", labelcolor="#F1F5F9", loc="upper left", fontsize=8.5)
for s in ax1.spines.values(): s.set_color("#334155")
ax1.text(0.985, 0.97, r"$\Omega_c=\dfrac{47}{125}=0.376$" + "\n" + r"$r=\dfrac{78}{47}\approx 1.660$",
         transform=ax1.transAxes, ha="right", va="top",
         bbox=dict(boxstyle="round,pad=0.45", facecolor="#064E3B", edgecolor="#10B981", alpha=0.95),
         color="#ECFDF5", fontsize=9.4, fontweight="bold")


# (B) spec(K²)
ax2 = fig.add_subplot(gs[1, 1], facecolor="#111827")
ax2.bar(x, np.where(mu2 == 0, 1.0, mu2),
        color=["#10B981" if k else "#F59E0B" for k in kernel_mask],
        width=0.55, edgecolor="#4B5563", linewidth=0.8, zorder=3)
ax2.set_yscale("log")
ax2.axhline(11664,  color="#EF4444", linestyle=":", linewidth=1.6, label=r"Spectral Gap $\Delta=11{,}664$ ($J=3$)")
ax2.axhline(186624, color="#8B5CF6", linestyle=":", linewidth=1.6, label=r"$\Lambda_{\max}=186{,}624$ ($J=6$)")
for i, val in enumerate(mu2):
    ax2.text(i, 1.7 if val == 0 else val * 1.28,
             r"$0$ ($E_{47}$)" if val == 0 else f"{int(val):,}",
             ha="center", va="bottom", color="#F8FAFC", fontsize=7.8, rotation=22)
ax2.set_title(r"(B) Spectrum of $K^2$  &  Spectral Gap $\Delta=11{,}664$", **title_style)
ax2.set_xlabel(r"Total Spin Sector $J$", **label_style)
ax2.set_ylabel(r"Eigenvalue $\mu_J^2$  (log scale)", **label_style)
ax2.set_xticks(x); ax2.set_xticklabels([f"$J={j}$" for j in spins], color="#CBD5E1")
ax2.tick_params(colors="#94A3B8"); ax2.set_ylim(0.5, 1.1e6)
ax2.grid(True, which="both", **grid_style, zorder=0)
ax2.legend(facecolor="#1F2937", edgecolor="#374151", labelcolor="#F1F5F9", loc="upper left", fontsize=8.2)
for s in ax2.spines.values(): s.set_color("#334155")
ax2.text(0.97, 0.42, r"$\kappa=\Lambda_{\max}/\Delta=16$" + "\n" + r"$\rho=(\kappa-1)/(\kappa+1)=15/17$",
         transform=ax2.transAxes, ha="right", va="center",
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#1E1B4B", edgecolor="#8B5CF6", alpha=0.95),
         color="#EDE9FE", fontsize=9.2, fontweight="bold")


# (C) P47 filter
ax3 = fig.add_subplot(gs[2, 0], facecolor="#111827")
c_dense = np.linspace(-1, 45, 2400)
p_clip  = np.ma.masked_where(np.abs(P_47(c_dense)) > 1.55, P_47(c_dense))
ax3.plot(c_dense, p_clip, color="#38BDF8", linewidth=2.15, label=r"Filter curve $P_{47}(C)$", zorder=3)
ax3.scatter(casimir[~kernel_mask], np.zeros(np.sum(~kernel_mask)),
            color="#EF4444", s=78, zorder=5, label=r"Annihilated modes ($P=0$)")
ax3.scatter(casimir[kernel_mask], np.ones(np.sum(kernel_mask)),
            color="#10B981", s=110, zorder=5, edgecolor="#FFFFFF", linewidth=0.8,
            label=r"Invariant modes $\lambda\in\{6,30\}$ ($P=1$)")
ax3.axhline(0, color="#475569", lw=0.8)
ax3.axhline(1, color="#10B981", ls="--", lw=0.85, alpha=0.55)
j_off = {0: (-1.4, 1.28), 1: (1.5, 1.28)}
for lam, J in zip(casimir, spins):
    ax3.axvline(lam, color="#1E293B", ls=":", lw=0.75)
    dx, yj = j_off.get(int(J), (0.0, 1.28))
    ax3.text(lam + dx, yj, f"$J={J}$", ha="center", va="bottom", color="#64748B", fontsize=7.2)
ax3.set_title(r"(C) Spectral Projector $P_{47}(C)$  —  $\operatorname{Tr}P_{47}=47$", **title_style)
ax3.set_xlabel(r"Casimir Eigenvalue $\lambda=J(J+1)$", **label_style)
ax3.set_ylabel(r"Transmission $P_{47}(\lambda)$", **label_style)
ax3.tick_params(colors="#94A3B8"); ax3.set_ylim(-0.45, 1.48); ax3.set_xlim(-2, 44)
ax3.grid(True, **grid_style, zorder=0)
ax3.legend(facecolor="#1F2937", edgecolor="#374151", labelcolor="#F1F5F9", loc="lower center", fontsize=8.2)
for s in ax3.spines.values(): s.set_color("#334155")


# (D) contraction
ax4 = fig.add_subplot(gs[2, 1], facecolor="#111827")
steps = np.arange(0, 31)
ax4.plot(np.linspace(0, 30, 400), np.exp(-np.linspace(0, 30, 400)),
         color="#F59E0B", lw=2.3, label=r"Continuous: $\exp(-\gamma\Delta t)$", zorder=3)
ax4.step(steps, (15 / 17) ** steps, where="mid", color="#06B6D4", lw=1.85, ls="--",
         label=r"Discrete: $(15/17)^k$  ($\kappa=16$)", zorder=3)
k_half = np.log(0.5) / np.log(15 / 17)
ax4.axhline(0.5, color="#475569", ls=":", lw=0.7, alpha=0.8)
ax4.axvline(k_half, color="#475569", ls=":", lw=0.7, alpha=0.8)
ax4.text(k_half + 0.4, 0.58, rf"$k_{{1/2}}\approx{k_half:.2f}$", color="#CBD5E1", fontsize=8)
ax4.set_title(r"(D) State Contraction into Invariant Subspace $E_{47}$", **title_style)
ax4.set_xlabel(r"Relaxation Time / Step Index $k$", **label_style)
ax4.set_ylabel(r"Relative Error  $\mathrm{dist}(\mathbf{v},E_{47})/\|\mathbf{v}_\perp(0)\|$", **label_style)
ax4.set_yscale("log"); ax4.set_ylim(1e-4, 1.6); ax4.set_xlim(0, 30)
ax4.tick_params(colors="#94A3B8")
ax4.grid(True, which="both", **grid_style, zorder=0)
ax4.legend(facecolor="#1F2937", edgecolor="#374151", labelcolor="#F1F5F9", loc="upper right", fontsize=8.4)
for s in ax4.spines.values(): s.set_color("#334155")


fig.text(0.5, 0.012,
         r"$K=(C-6I)(C-30I)$   ·   $\mu_J=(\lambda_J-6)(\lambda_J-30)$   ·   $P_{47}(C)=\frac{C(C-2)(C-12)(C-20)(C-31)(C-42)}{1{,}814{,}400}$   ·   $\dot\rho=-K^2\rho$",
         ha="center", va="bottom", color="#64748B", fontsize=8.0)


png = os.path.join(out_dir, "Omega_c_Coherence_Algebra_Contraction_Formalism.png")
pdf = os.path.join(out_dir, "Omega_c_Coherence_Algebra_Contraction_Formalism.pdf")
fig.savefig(png, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
fig.savefig(pdf, dpi=220, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close(fig)
print(f"[✓] {png}")
print(f"[✓] {pdf}")

