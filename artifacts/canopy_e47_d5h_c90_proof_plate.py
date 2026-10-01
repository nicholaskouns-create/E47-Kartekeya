#!/usr/bin/env python3
"""CANOPY / E47-D5h-C90 — Academic Proof Plate renderer.
Nicholas Kouns · KKP-R / CANOPY · 2026-09-30
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def box(ax,x,y,w,h,title,lines,fs=9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.008,rounding_size=0.008",
        linewidth=1.15,edgecolor="#2b3440",facecolor="#f8fafc"))
    ax.text(x+.018,y+h-.035,title,fontsize=11.3,fontweight="bold",va="top",color="#111827")
    ax.text(x+.018,y+h-.078,"\n".join(lines),fontsize=fs,va="top",
        family="DejaVu Sans Mono",linespacing=1.38,color="#243040")

fig=plt.figure(figsize=(16,20),dpi=220,facecolor="white")
ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
ax.text(.05,.966,"CANOPY / E47–D5h–C90",fontsize=27,fontweight="bold",color="#0b1220")
ax.text(.05,.938,"COMPILED CORRECTED VALIDATION CERTIFICATE · ACADEMIC PROOF PLATE",
        fontsize=13.5,fontweight="bold",color="#334155")
ax.text(.05,.916,"Explicit graph invariants · celestial/terrestrial geometry · E47 constants · toy mechanical stability",
        fontsize=10.8,color="#475569")
ax.plot([.05,.95],[.900,.900],lw=1.4,color="#111827")

box(ax,.05,.715,.43,.165,"I. C90 COMBINATORIAL CERTIFICATE",[
"V = 90     E = 135     F = 47","degree(v) = 3  for every vertex",
"face census: 12 pentagons + 35 hexagons","χ = V − E + F = 2",
"Σ_f (6 − n_f) = 12","planar = TRUE     κ_vertex = 3","|Aut(G)| = 20",
"dual: (V*,E*,F*) = (47,135,90)","all dual faces triangular"],8.9)
box(ax,.52,.715,.43,.165,"II. SCALE-FREE SKY ↔ GROUND GEOMETRY",[
"Orion: r_O = 0.978364589002175","middle bend = 7.517142902261°",
"Giza: r_G = 0.982510022894732","middle bend = 12.501649438494°",
"segments ≈ 475.5 m, 467.2 m, 937.0 m","log(r_G/r_O) = 0.004228154154441",
"relative ratio gap ≈ 0.423711%"],8.75)
box(ax,.05,.545,.43,.145,"III. TANGENT-PLANE SHAPE TEST",[
"Gnomonic projection about each triplet centroid","Normalize translation and Frobenius scale",
"Orientation-preserving Procrustes: d ≈ 0.0253","θ ≈ 90.43°     det(R) > 0",
"Giza rounding sensitivity (95%):","r_G ∈ [0.9530,1.0131], median ≈ 0.9825"],8.9)
box(ax,.52,.545,.43,.145,"IV. DANVILLE LOCAL TANGENT FRAME",[
"φ = 37.6439°     λ = −84.7729°","h_x · h_y ≈ 0","h_x × h_y ≈ local up",
"az(h_x) = 81.000°","az(h_y) = 351.000°"],8.8)
box(ax,.05,.395,.43,.125,"V. E47 LOCKED CONSTANTS",[
"dim(H)=125     dim(E47)=47","Ω_c = 47/125 = 0.376",
"ε* = 1/99144 ≈ 1.008634×10⁻⁵","ρ* = 15/17 ≈ 0.882352941176"],9.25)
box(ax,.52,.395,.43,.125,"VI. TOY sp²-LIKE MECHANICAL TEST",[
"E = E_bond + E_angle + E_repulsion","bond target: l = 1",
"angle target: cos θ = −1/2 ⇔ θ = 120°","L-BFGS-B relaxation on 90 vertices",
"Hessian conditions: N₋=0, N₀=6, λ_min,int>0"],8.75)

ax.text(.05,.348,"FORMAL DEDUCTION CHAIN",fontsize=12,fontweight="bold",color="#111827")
ax.text(.05,.304,"G → {V,E,F,faces,Aut(G)} → dual census\n"
"J2000 Orion + stated Giza coordinates → angular sides → ratios/bends → Procrustes\n"
"Danville basis → orthonormal local frame + azimuth axes\n"
"C90 Laplacian embedding → local relaxation → Hessian inertia test",
fontsize=10.2,family="DejaVu Sans Mono",linespacing=1.55,color="#1f2937")
ax.plot([.05,.95],[.255,.255],lw=1,color="#94a3b8")
ax.text(.05,.225,"SCOPE BOUNDARY",fontsize=11.5,fontweight="bold")
ax.text(.05,.186,"Automorphism order 20 alone is not used as a proof of D5h; stated Giza coordinates are explicit numerical inputs; the mechanical model is a toy local force field, not ab-initio chemistry; no natural-mineral realization is asserted.",fontsize=9.6,wrap=True,color="#334155")
ax.text(.05,.128,"VALIDATION TARGET",fontsize=11.5,fontweight="bold")
ax.text(.05,.097,"python3 canopy_c90_corrected_validator.py → all check(...) propositions PASS → machine-readable JSON summary",fontsize=10.1,family="DejaVu Sans Mono")
ax.text(.05,.055,"Nicholas Kouns · KKP-R / CANOPY · 2026-09-30",fontsize=9.4,color="#64748b")
ax.text(.95,.055,"Proof plate generated in Python / Matplotlib",fontsize=9.4,color="#64748b",ha="right")
plt.savefig("CANOPY_E47_D5h_C90_Academic_Proof_Plate.png",bbox_inches="tight",pad_inches=.15,dpi=300)
plt.savefig("CANOPY_E47_D5h_C90_Academic_Proof_Plate.pdf",bbox_inches="tight",pad_inches=.15)
