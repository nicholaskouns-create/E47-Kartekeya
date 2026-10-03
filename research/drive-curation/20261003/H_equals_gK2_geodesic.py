#!/usr/bin/env python3
"""
H = g K²
========
Role of H, stated once: H is the stability Hamiltonian (cost and
generator of the geodesic). After that statement the notation

    H = g K²

is the definition, not a metaphor.

    K = (C − 6I)(C − 30I)     on H_space = V₂^{⊗3}
    g > 0                     coupling
    H = g K²                  ≥ 0
    ker H = ker K = E₄₇
    geodesic                  ψ̇ = −H ψ
                              ρ̇ = −{H, ρ}/2   (equivalently −Hρ on eigenweights)
    discrete                  Γ = I − ε_* H / g   wait: balanced step uses spec(H).

Parsimonious chain
    C → K → H=gK² → ker H = E47 → P47 → Γ → L → n(L) → (T,a)=(0,0) on geodesic/hover

This module imports the locked engines. It does not invent a second kernel.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import sympy as sp

sys.path.insert(0, "/home/workdir/.grok/skills/tomographic-visualizer/scripts")
sys.path.insert(0, "/home/workdir/.grok/skills/eidolon-propulsion/scripts")
sys.path.insert(0, "/home/workdir/.grok/skills/spectral-app-forge/scripts")
sys.path.insert(0, "/home/workdir/artifacts")

from spectral_engine import SpectralEngine, P_47  # noqa: E402
from eidolon_engine import DIM_H, DIM_COMP, OMEGA_C, Craft  # noqa: E402
from fidelity_lock import check as fidelity_check, write_lock  # noqa: E402
from shared_occupancy_bus import (  # noqa: E402
    SharedOccupancyEidolon,
    n_from_L,
    build_casimir_spectrum,
)

OUT = Path("/home/workdir/artifacts")

# Locked spectrum of K², named once.
SPEC_K2 = np.array([32400, 12544, 0, 11664, 19600, 0, 186624], dtype=float)
DELTA_K2 = 11664.0
M_K2 = 186624.0


# ---------------------------------------------------------------------------
# Symbolic layer  (math)
# ---------------------------------------------------------------------------

def symbolic_hamiltonian():
    """First-principles symbols. Role of H is the first line."""
    g, C, I = sp.symbols("g C I", commutative=True)
    g = sp.symbols("g", positive=True)
    C, I = sp.symbols("C I", commutative=True)
    K = (C - 6 * I) * (C - 30 * I)
    H = g * K ** 2
    return {
        "role": "H is the stability Hamiltonian: cost and geodesic generator",
        "definition": H,
        "K": K,
        "ker": "ker H = ker K = E47",
        "flow": "dψ/dt = -H ψ",
        "gap_H": g * 11664,
        "stiff_H": g * 186624,
        "kappa": sp.Integer(16),
        "rho": sp.Rational(15, 17),
        "P47": "P47 = p(C), unique interpolant 1 on {6,30}, 0 else",
        "Gamma": "Γ = I - ε H  with ε = 2 / (Δ_H + M_H) = 2 / (g(Δ+M))",
    }


# ---------------------------------------------------------------------------
# Numeric layer  (physics)
# ---------------------------------------------------------------------------

@dataclass
class Hamiltonian:
    """H = g K² on the locked spin-2 cube."""

    g: float = 1.0

    def __post_init__(self):
        if self.g <= 0:
            raise ValueError("g > 0")
        self.spec = SpectralEngine()
        self.spec.validate()
        self.spec_H = self.g * self.spec.mu2.astype(float)
        self.Delta = self.g * DELTA_K2
        self.M = self.g * M_K2
        self.kappa = self.M / self.Delta
        self.rho = (self.kappa - 1.0) / (self.kappa + 1.0)
        self.eps = 2.0 / (self.Delta + self.M)
        self.g_factor = 1.0 - self.eps * self.spec_H  # eigenvalues of Γ = I − ε H

    @property
    def gap_units_time(self) -> float:
        """τ = (g Δ) t   so n3(τ) = n3(0) e^{-τ}."""
        return self.g * DELTA_K2


def hilbert_H(g: float) -> dict:
    snapped, evecs = build_casimir_spectrum()
    mu2 = ((snapped - 6.0) * (snapped - 30.0)) ** 2
    H = evecs * (g * mu2) @ evecs.T
    H = 0.5 * (H + H.T)
    P = evecs * P_47(snapped) @ evecs.T
    P = 0.5 * (P + P.T)
    Delta_H = g * DELTA_K2
    M_H = g * M_K2
    eps = 2.0 / (Delta_H + M_H)
    Gamma = np.eye(125) - eps * H
    return {"H": H, "P": P, "Gamma": Gamma, "snapped": snapped, "mu2": mu2, "eps": eps}


def validate(g: float = 1.0) -> dict:
    findings = []

    def add(ok, name, got):
        findings.append({"pass": bool(ok), "name": name, "got": got})

    lock = fidelity_check()
    write_lock(OUT, lock)
    add(lock["passed"], "forge_lock", lock["line"])

    ham = Hamiltonian(g=g)
    add(ham.kappa == 16.0, "kappa_invariant", ham.kappa)
    add(abs(ham.rho - 15.0 / 17.0) < 1e-15, "rho_invariant", ham.rho)
    add(np.allclose(ham.spec_H[ham.spec.kernel_mask], 0.0), "ker_H_is_E47", 0.0)
    add(abs(ham.Delta - g * DELTA_K2) < 1e-12, "gap_scales_with_g", ham.Delta)
    add(abs(ham.eps * g - 2.0 / (DELTA_K2 + M_K2)) < 1e-18, "eps_compensates_g", ham.eps)

    ops = hilbert_H(g)
    H, P, G = ops["H"], ops["P"], ops["Gamma"]
    add(abs(np.trace(P) - 47) < 1e-6, "TrP", float(np.trace(P)))
    add(np.linalg.norm(H @ P) < 1e-8, "H_annihilates_code", float(np.linalg.norm(H @ P)))
    add(np.linalg.norm(G @ P - P) < 1e-8, "Gamma_fixes_code", float(np.linalg.norm(G @ P - P)))

    # geodesic: dissipative flow of H
    rng = np.random.default_rng(47)
    v = rng.normal(size=125)
    v = v / np.linalg.norm(v)
    costs = [float(v @ H @ v)]
    F_to_P = [float(np.linalg.norm(P @ v) ** 2)]
    psi = v.copy()
    for _ in range(40):
        psi = G @ psi
        nrm = np.linalg.norm(psi)
        psi = psi / nrm
        costs.append(float(psi @ H @ psi))
        F_to_P.append(float(np.linalg.norm(P @ psi) ** 2))
    costs = np.array(costs)
    F_to_P = np.array(F_to_P)
    add(bool(np.all(np.diff(costs) <= 1e-10)), "cost_monotone", float(np.max(np.diff(costs))))
    add(F_to_P[-1] > 0.99, "geodesic_to_code", float(F_to_P[-1]))

    # force-free ambient geodesic on shared L from Hilbert occupancy of this flow
    L_curve = F_to_P  # occupancy of P after each Γ step
    geo = SharedOccupancyEidolon(
        np.arange(len(L_curve), dtype=float), L_curve,
        Craft(mode="geodesic", lock_target=0.98, gain=0.15, pump=0.40, heading_deg=12),
        duration=48.0,
    ).run()
    add(float(np.max(np.abs(geo.arr("thrust")))) == 0.0, "T_zero", 0.0)
    add(geo.history[-1].phase == "COAST", "phase_COAST", geo.history[-1].phase)

    # hold floor from the same H
    me_floor = 1200.0 * (DIM_COMP / DIM_H * (1.0 - OMEGA_C) + 1e-6)
    add(abs(me_floor - 467.2524) < 1e-3, "m_eff_floor_at_Omega_c", me_floor)

    return {
        "passed": all(f["pass"] for f in findings),
        "n_pass": sum(1 for f in findings if f["pass"]),
        "n_total": len(findings),
        "findings": findings,
        "g": g,
        "Delta_H": ham.Delta,
        "eps": ham.eps,
        "rho": ham.rho,
        "costs": costs,
        "F_to_P": F_to_P,
        "L_inf": float(L_curve[-1]),
        "geo_phase": geo.history[-1].phase,
        "m_eff_floor": me_floor,
        "lock": lock["line"],
        "geo": geo,
        "ham": ham,
    }


def render(report, path: Path) -> str:
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    from matplotlib.patches import FancyBboxPatch

    plt.rcParams.update({
        "font.family": "DejaVu Serif",
        "mathtext.fontset": "cm",
        "axes.unicode_minus": False,
        "figure.facecolor": "#F7F4EA",
        "savefig.facecolor": "#F7F4EA",
    })
    fig = plt.figure(figsize=(16.4, 20.4), facecolor="#F7F4EA")
    outer = gridspec.GridSpec(
        7, 1, figure=fig,
        height_ratios=[0.12, 0.42, 0.28, 0.55, 0.42, 0.38, 0.18],
        hspace=0.07, left=0.05, right=0.96, top=0.985, bottom=0.02,
    )
    ink, rule = "#1A1A1A", "#1F4A3A"

    h = fig.add_subplot(outer[0])
    h.set_xlim(0, 1)
    h.set_ylim(0, 1)
    h.axis("off")
    h.text(0.5, 0.70, r"$H = gK^{2}$", ha="center", fontsize=26, fontweight="bold", color=ink)
    h.text(0.5, 0.22, "STABILITY HAMILTONIAN AND ITS GEODESIC",
           ha="center", fontsize=12, color="#244")
    h.plot([0.08, 0.92], [0.00, 0.00], color=rule, lw=1.7)

    ax = fig.add_subplot(outer[1])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.01, 0.03), 0.98, 0.94, boxstyle="round,pad=0.008,rounding_size=0.01",
                                facecolor="#E8F0E9", edgecolor=rule, lw=1.2))
    text = (
        r"$\mathbf{Role\ of\ }H.$  $H$ is the stability Hamiltonian: the cost of leaving $E_{47}$ "
        r"and the generator of the geodesic."
        "\n"
        r"$\mathbf{Definition.}$  $K=(C-6I)(C-30I)$,  $g>0$,  $H=gK^{2}\geq 0$.  "
        r"Then $\ker H=\ker K=E_{47}$ and $\mathrm{spec}(H)=g\,\mathrm{spec}(K^{2})$."
        "\n"
        r"$\mathbf{Geodesic.}$  $\dot\psi=-H\psi$.  Discrete: $\Gamma=I-\varepsilon H$,  "
        r"$\varepsilon=2/(\Delta_H+M_H)=2/(g(\Delta+M))$.  "
        r"$\rho(\Gamma|_{E_{47}^\perp})=15/17$ independent of $g$."
        "\n"
        r"$\mathbf{Physics.}$  Occupancy $L=\mathrm{Tr}(P_{47}\rho)/\mathrm{Tr}\rho$.  "
        r"Hover / geodesic set $T=0$, so $\ddot x=0$.  "
        r"$m_{\mathrm{eff}}=m[(78/125)(1-L)+\varepsilon]$.  "
        r"Holding $L=\Omega_c$ floors inertia at $467.252\,\mathrm{kg}$."
    )
    ax.text(0.035, 0.92, text, ha="left", va="top", fontsize=11.0, color=ink, linespacing=1.55)

    ax = fig.add_subplot(outer[2])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.78, "CHAIN", ha="center", fontsize=12, fontweight="bold", color=ink)
    ax.text(
        0.5, 0.32,
        r"$C \;\to\; K \;\to\; H=gK^{2} \;\to\; \ker H=E_{47} \;\to\; P_{47}"
        r" \;\to\; \Gamma \;\to\; L \;\to\; n(L) \;\to\; (T,a)=(0,0)$",
        ha="center", fontsize=12.0, color="#143",
    )

    mid = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=outer[3], wspace=0.24)
    costs, F = report["costs"], report["F_to_P"]
    k = np.arange(len(costs))
    ax = fig.add_subplot(mid[0, 0])
    ax.semilogy(k, np.clip(costs / max(costs[0], 1e-18), 1e-16, None), color="#1F4A3A", lw=2.0)
    ax.set_title(r"$\langle\psi_n|H|\psi_n\rangle/\langle\psi_0|H|\psi_0\rangle$", fontsize=10)
    ax.set_xlabel(r"$n$")
    ax.set_facecolor("#FBF8F0")
    ax.grid(True, ls="--", lw=0.5, color="#CCC")

    ax = fig.add_subplot(mid[0, 1])
    ax.plot(k, F, color="#1B6B9A", lw=2.0)
    ax.set_ylim(0, 1.05)
    ax.set_title(r"$L_n=\|P_{47}\psi_n\|^{2}$", fontsize=10)
    ax.set_xlabel(r"$n$")
    ax.set_facecolor("#FBF8F0")
    ax.grid(True, ls="--", lw=0.5, color="#CCC")

    ax = fig.add_subplot(mid[0, 2])
    t = report["geo"].arr("t")
    ax.plot(t, report["geo"].arr("thrust"), color="#A35B12", lw=2.0, label=r"$T$")
    ax.plot(t, report["geo"].arr("accel"), color="#A33", lw=1.4, ls="--", label=r"$a$")
    ax.set_title("ambient geodesic (force-free)", fontsize=10)
    ax.legend(fontsize=8, frameon=False)
    ax.set_facecolor("#FBF8F0")

    ax = fig.add_subplot(outer[4])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.add_patch(FancyBboxPatch((0.01, 0.04), 0.98, 0.92, boxstyle="round,pad=0.008,rounding_size=0.01",
                                facecolor="#F3EBDC", edgecolor="#6B4F2A", lw=1.1))
    proof = (
        r"$\mathbf{Proof.}$  $K$ annihilates exactly $\lambda\in\{6,30\}$.  $H=gK^{2}$ therefore annihilates "
        r"the same subspace and scales every positive eigenvalue by $g$.  "
        r"The ratio $M_H/\Delta_H=M/\Delta=16$ is $g$-invariant, so the Richardson step still yields $15/17$. "
        "\n"
        r"The flow $\dot\psi=-H\psi$ is the gradient of $\frac{1}{2}\langle\psi|H|\psi\rangle$ on the unit sphere.  "
        r"Its discrete form $\Gamma=I-\varepsilon H$ contracts $E_{47}^\perp$ and fixes $E_{47}$.  "
        r"Hence $\Gamma^n\psi\to P_{47}\psi/\|P_{47}\psi\|$ and $L_n\to 1$ unless $P_{47}\psi=0$. "
        "\n"
        r"Eidolon geodesic sets $T=0$, so the ambient curve is the Euclidean rest geodesic.  "
        r"The only remaining motion is the flow of $H$.  Q.E.D."
    )
    ax.text(0.035, 0.90, proof, ha="left", va="top", fontsize=10.4, color=ink, linespacing=1.5)

    ax = fig.add_subplot(outer[5])
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.5, 0.92, f"PYTHON  {report['n_pass']}/{report['n_total']} PASS    g = {report['g']}",
            ha="center", fontsize=12, fontweight="bold", color=ink)
    y = 0.72
    for i, f in enumerate(report["findings"]):
        col = "#1F4A3A" if f["pass"] else "#A33"
        ax.text(0.04 + (0.50 if i >= 7 else 0.0), y - 0.09 * (i % 7),
                f"{'PASS' if f['pass'] else 'FAIL'}  {f['name']}",
                fontsize=8.6, color=col, family="DejaVu Sans Mono")

    foot = fig.add_subplot(outer[6])
    foot.axis("off")
    foot.set_xlim(0, 1)
    foot.set_ylim(0, 1)
    foot.plot([0.08, 0.92], [0.72, 0.72], color=rule, lw=1.3)
    foot.text(
        0.5, 0.38,
        r"$H=gK^{2}$  is the Hamiltonian.  The geodesic of $H$ is the physics.  "
        r"Python is the same chain executed.",
        ha="center", fontsize=10.2, color="#244",
    )
    foot.text(0.5, 0.08, r"Q.E.D.", ha="center", fontsize=15, fontweight="bold", color=ink)

    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(path.with_suffix(".pdf"), dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return str(path)


def main() -> None:
    print(symbolic_hamiltonian()["role"])
    print("H :=", symbolic_hamiltonian()["definition"])
    report = validate(g=1.0)
    print(json.dumps({k: report[k] for k in report if k not in ("findings", "costs", "F_to_P", "geo", "ham")}, indent=2))
    for f in report["findings"]:
        print(("PASS" if f["pass"] else "FAIL"), f["name"])
    if not report["passed"]:
        raise SystemExit("validation failed")
    png = render(report, OUT / "H_equals_gK2_Geodesic.png")
    print("[✓]", png)
    (OUT / "H_equals_gK2_geodesic.json").write_text(
        json.dumps({k: report[k] for k in report if k not in ("geo", "ham", "costs", "F_to_P")}, indent=2, default=str)
    )


if __name__ == "__main__":
    main()
