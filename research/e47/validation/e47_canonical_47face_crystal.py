#!/usr/bin/env python3
r"""
E47 Canonical Coupled-Basis -> 47-Face Dual Crystal
====================================================

This construction does exactly five things:

1. Builds the 47 coupled angular-momentum basis states
       |J, j12, m>
   in the coupling tree ((2 ⊗ 2) -> j12) ⊗ 2 -> J
   using the standard Condon-Shortley Clebsch-Gordan convention.

2. Maps each canonical label (J,j12,m) deterministically to a unique
   point on S^2.

3. Takes the polar dual of the convex hull of those 47 spherical points.

4. Verifies that the polar dual has exactly 47 facets, one facet for
   each canonical E47 basis state.

5. Renders the labeled crystal and writes the exact facet/channel map.

Important precision statement
-----------------------------
The coupled basis is canonical after fixing:
  - coupling tree ((1,2),3),
  - Condon-Shortley CG phases,
  - uncoupled basis ordering,
  - lexicographic facet ordering.

The 3D spherical embedding is a deterministic canonicalization rule,
not a claim that representation theory uniquely forces one Euclidean
3D embedding. The exact invariant content is the one-to-one mapping
between the 47 coupled basis channels and the 47 dual facets.

Label-derived spherical embedding
---------------------------------
Let μ_J be the multiplicity of spin J inside E47:
    μ_2 = 5, μ_5 = 2.
Let r(J,j12) be the zero-based copy index among allowed j12 values.

Set
    z = m/(J+1)

and
    phi = 2π [ r/μ_J + m/47 + offset_J ],

with
    offset_2 = 0,
    offset_5 = 1/94.

Then
    n(J,j12,m)
      = (sqrt(1-z²) cos phi,
         sqrt(1-z²) sin phi,
         z)
      ∈ S².

The 47 points are distinct and all lie on the unit sphere, hence each
is an exposed vertex of their convex hull. The origin lies strictly
inside that hull. The polar body

    C47 = { x ∈ R³ : n_a · x <= 1 for all a=1,...,47 }

is therefore bounded and has exactly one facet per spherical point.

Facet a corresponds exactly to the coupled channel |J,j12,m>_a.
"""

from pathlib import Path
import math, json
import numpy as np
import pandas as pd
import sympy as sp
from sympy.physics.wigner import clebsch_gordan
from scipy.spatial import ConvexHull, HalfspaceIntersection
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent
CERT = ROOT / "MC-E47-CANONICAL-47FACE-CRYSTAL-20260930-001.json"
CSV = ROOT / "e47_47facet_channel_map.csv"
NPZ = ROOT / "e47_47facet_crystal_data.npz"
OBJ = ROOT / "e47_47facet_crystal.obj"
PNG = ROOT / "e47_47facet_crystal_labeled.png"

# ------------------------------------------------------------------
# 1. Spin-2 operators on H = V2⊗V2⊗V2
# ------------------------------------------------------------------
mvals = [2, 1, 0, -1, -2]
marr = np.array(mvals, dtype=float)
j = 2
d = 5

Jz = np.diag(marr).astype(complex)
Jp = np.zeros((d,d), dtype=complex)

for col, m in enumerate(marr):
    mp = m + 1
    rows = np.where(np.isclose(marr, mp))[0]
    if len(rows):
        row = rows[0]
        Jp[row,col] = np.sqrt(j*(j+1) - m*(m+1))

Jm = Jp.conj().T
Jx = (Jp + Jm)/2
Jy = (Jp - Jm)/(2j)
I5 = np.eye(5, dtype=complex)

def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

Jxt = kron3(Jx,I5,I5) + kron3(I5,Jx,I5) + kron3(I5,I5,Jx)
Jyt = kron3(Jy,I5,I5) + kron3(I5,Jy,I5) + kron3(I5,I5,Jy)
Jzt = kron3(Jz,I5,I5) + kron3(I5,Jz,I5) + kron3(I5,I5,Jz)
C = Jxt@Jxt + Jyt@Jyt + Jzt@Jzt

J12x = np.kron(Jx,I5) + np.kron(I5,Jx)
J12y = np.kron(Jy,I5) + np.kron(I5,Jy)
J12z = np.kron(Jz,I5) + np.kron(I5,Jz)
J12sq = J12x@J12x + J12y@J12y + J12z@J12z
J12sq_125 = np.kron(J12sq, I5)

I125 = np.eye(125, dtype=complex)
K = (C - 6*I125) @ (C - 30*I125)

# Uncoupled product basis ordering:
# |m1,m2,m3>, with each m descending 2,1,0,-1,-2.
uncoupled = [(m1,m2,m3) for m1 in mvals for m2 in mvals for m3 in mvals]
uindex = {state:i for i,state in enumerate(uncoupled)}

# Canonical E47 labels:
# J=2 has j12=0..4 and m=-2..2 => 25 states
# J=5 has j12=3,4 and m=-5..5 => 22 states
labels = []
for J, j12_values in [(2, range(5)), (5, [3,4])]:
    for j12 in j12_values:
        for m in range(-J, J+1):
            labels.append((J,j12,m))

assert len(labels) == 47
assert len(set(labels)) == 47

# ------------------------------------------------------------------
# 2. Exact coupled basis from Clebsch-Gordan coefficients
# ------------------------------------------------------------------
B47 = np.zeros((125,47), dtype=complex)

for a,(J,j12,m) in enumerate(labels):
    for m1,m2,m3 in uncoupled:
        m12 = m1 + m2
        if abs(m12) > j12 or m12 + m3 != m:
            continue

        # Standard Condon-Shortley CG convention supplied by SymPy.
        c12 = clebsch_gordan(2, 2, j12, m1, m2, m12)
        cJ  = clebsch_gordan(j12, 2, J, m12, m3, m)
        coeff = complex(sp.N(c12*cJ, 30))

        if abs(coeff) > 0:
            B47[uindex[(m1,m2,m3)],a] = coeff

P47 = B47 @ B47.conj().T

DJ = np.diag([J*(J+1) for J,j12,m in labels])
Dj12 = np.diag([j12*(j12+1) for J,j12,m in labels])
Dm = np.diag([m for J,j12,m in labels])

basis_orth_resid = np.linalg.norm(B47.conj().T@B47 - np.eye(47))
C_eigen_resid = np.linalg.norm(C@B47 - B47@DJ)
J12_eigen_resid = np.linalg.norm(J12sq_125@B47 - B47@Dj12)
Jz_eigen_resid = np.linalg.norm(Jzt@B47 - B47@Dm)
kernel_resid = np.linalg.norm(K@B47)
projector_idem_resid = np.linalg.norm(P47@P47 - P47)

# ------------------------------------------------------------------
# 3. Deterministic label-derived spherical points
# ------------------------------------------------------------------
def copy_data(J,j12):
    if J == 2:
        allowed = [0,1,2,3,4]
        mu = 5
        offset = 0.0
    elif J == 5:
        allowed = [3,4]
        mu = 2
        offset = 1/94
    else:
        raise ValueError("Only J=2,5 belong to E47")
    return allowed.index(j12), mu, offset

points = []
for J,j12,m in labels:
    r,mu,offset = copy_data(J,j12)
    z = m/(J+1.0)
    phi = 2*np.pi*(r/mu + m/47 + offset)
    rr = np.sqrt(1-z*z)
    points.append([rr*np.cos(phi), rr*np.sin(phi), z])

points = np.asarray(points, dtype=float)

unit_resid = float(np.max(np.abs(np.linalg.norm(points,axis=1)-1)))
pair_d = np.linalg.norm(points[:,None,:]-points[None,:,:],axis=2)
pair_d[pair_d == 0] = np.inf
min_pair_distance = float(np.min(pair_d))

# ------------------------------------------------------------------
# 4. Primal convex hull and polar dual
# ------------------------------------------------------------------
primal = ConvexHull(points)
origin_slacks = primal.equations[:,-1]  # A*0 + b = b, interior means b<0
origin_margin = float(-np.max(origin_slacks))

# Polar dual C47 = {x : n_a·x <= 1}
halfspaces = np.c_[points, -np.ones(47)]
dual = HalfspaceIntersection(halfspaces, np.zeros(3))
dual_vertices = np.asarray(dual.intersections, dtype=float)

def order_face(vertices, ids, normal):
    ids = np.asarray(ids, dtype=int)
    p = vertices[ids]
    c = p.mean(axis=0)

    trial = np.array([1.0,0.0,0.0])
    if abs(np.dot(trial, normal)) > 0.9:
        trial = np.array([0.0,1.0,0.0])

    u = trial - np.dot(trial,normal)*normal
    u /= np.linalg.norm(u)
    v = np.cross(normal,u)

    angles = np.arctan2((p-c)@v, (p-c)@u)
    return ids[np.argsort(angles)]

faces = []
facet_plane_resid = 0.0

for a,n in enumerate(points):
    ids = np.where(np.isclose(dual_vertices@n, 1.0, atol=1e-9))[0]
    ordered = order_face(dual_vertices, ids, n)
    faces.append(ordered)
    facet_plane_resid = max(
        facet_plane_resid,
        float(np.max(np.abs(dual_vertices[ordered]@n - 1.0)))
    )

# Unique dual edges from cyclic facet boundaries.
edges = set()
for face in faces:
    f = list(map(int,face))
    for p,q in zip(f, f[1:] + f[:1]):
        edges.add(tuple(sorted((p,q))))

V = len(dual_vertices)
E = len(edges)
F = len(faces)
euler = V-E+F
face_sizes = [len(f) for f in faces]

# ------------------------------------------------------------------
# 5. Exact facet/channel mapping
# ------------------------------------------------------------------
rows = []
for a,((J,j12,m),n,face) in enumerate(zip(labels,points,faces), start=1):
    centroid = dual_vertices[face].mean(axis=0)
    rows.append({
        "facet": f"F{a:02d}",
        "basis_state": f"|J={J}, j12={j12}, m={m}>",
        "J": J,
        "j12": j12,
        "m": m,
        "Casimir_C": J*(J+1),
        "sector_dimension": 25 if J==2 else 22,
        "normal_x": n[0],
        "normal_y": n[1],
        "normal_z": n[2],
        "face_vertices": len(face),
        "centroid_x": centroid[0],
        "centroid_y": centroid[1],
        "centroid_z": centroid[2],
    })

mapping = pd.DataFrame(rows)
mapping.to_csv(CSV, index=False)

# Save full numerical model.
np.savez_compressed(
    NPZ,
    B47=B47,
    P47=P47,
    labels=np.array(labels, dtype=int),
    spherical_points=points,
    dual_vertices=dual_vertices,
    face_sizes=np.array(face_sizes, dtype=int),
)

# Save OBJ mesh with facet comments carrying exact channel labels.
with OBJ.open("w") as f:
    f.write("# E47 canonical 47-face polar-dual crystal\n")
    f.write("# Coupled basis convention: ((2⊗2)->j12)⊗2->J, Condon-Shortley\n")
    for v in dual_vertices:
        f.write(f"v {v[0]:.16e} {v[1]:.16e} {v[2]:.16e}\n")
    for a,(face,label) in enumerate(zip(faces,labels),start=1):
        J,j12,m = label
        f.write(f"# F{a:02d} <-> |J={J},j12={j12},m={m}>\n")
        f.write("f " + " ".join(str(int(i)+1) for i in face) + "\n")

# ------------------------------------------------------------------
# 6. Validation certificate
# ------------------------------------------------------------------
checks = []

def ck(name, condition, value, expected):
    checks.append({
        "name": name,
        "pass": bool(condition),
        "value": float(value) if isinstance(value,(np.floating,float)) else int(value) if isinstance(value,(np.integer,int)) else str(value),
        "expected": str(expected),
    })

ck("47 unique coupled labels", len(labels)==47 and len(set(labels))==47, len(labels), 47)
ck("J=2 state count", sum(J==2 for J,_,_ in labels)==25, sum(J==2 for J,_,_ in labels), 25)
ck("J=5 state count", sum(J==5 for J,_,_ in labels)==22, sum(J==5 for J,_,_ in labels), 22)
ck("coupled basis orthonormal", basis_orth_resid < 1e-12, basis_orth_resid, "<1e-12")
ck("C eigenlabels J(J+1)", C_eigen_resid < 1e-11, C_eigen_resid, "<1e-11")
ck("J12^2 eigenlabels j12(j12+1)", J12_eigen_resid < 1e-11, J12_eigen_resid, "<1e-11")
ck("Jz eigenlabels m", Jz_eigen_resid < 1e-12, Jz_eigen_resid, "<1e-12")
ck("K annihilates coupled E47 basis", kernel_resid < 1e-10, kernel_resid, "<1e-10")
ck("rank P47 = 47", np.linalg.matrix_rank(P47,tol=1e-9)==47, np.linalg.matrix_rank(P47,tol=1e-9), 47)
ck("P47 idempotent", projector_idem_resid < 1e-12, projector_idem_resid, "<1e-12")
ck("47 spherical points", len(points)==47, len(points), 47)
ck("all spherical points have unit norm", unit_resid < 1e-12, unit_resid, "<1e-12")
ck("all spherical points distinct", min_pair_distance > 1e-3, min_pair_distance, ">1e-3")
ck("all 47 are primal hull vertices", len(primal.vertices)==47, len(primal.vertices), 47)
ck("origin strictly inside primal hull", origin_margin > 1e-6, origin_margin, ">1e-6")
ck("dual has exactly 47 facets", sum(len(f)>=3 for f in faces)==47, sum(len(f)>=3 for f in faces), 47)
ck("one facet per coupled channel", len(faces)==len(labels)==47, len(faces), 47)
ck("facet planes n_a·x=1", facet_plane_resid < 1e-9, facet_plane_resid, "<1e-9")
ck("dual Euler characteristic", euler==2, euler, 2)
ck("dual topology vertex count", V==90, V, 90)
ck("dual topology edge count", E==135, E, 135)

status = "PASS" if all(c["pass"] for c in checks) else "FAIL"

cert = {
    "certificate": "MC-E47-CANONICAL-47FACE-CRYSTAL-20260930-001",
    "status": status,
    "checks_passed": sum(c["pass"] for c in checks),
    "checks_total": len(checks),
    "basis_convention": {
        "coupling_tree": "((V2 tensor V2) -> j12) tensor V2 -> J",
        "phase_convention": "Condon-Shortley Clebsch-Gordan",
        "uncoupled_order": "m1,m2,m3 each in [2,1,0,-1,-2]",
        "facet_order": "J ascending, j12 ascending, m ascending"
    },
    "basis": {
        "J2_channels": 25,
        "J5_channels": 22,
        "total": 47,
        "orthonormality_residual": float(basis_orth_resid),
        "C_eigen_residual": float(C_eigen_resid),
        "J12_eigen_residual": float(J12_eigen_resid),
        "Jz_eigen_residual": float(Jz_eigen_resid),
        "kernel_residual": float(kernel_resid),
    },
    "spherical_embedding": {
        "rule": "z=m/(J+1); phi=2pi[r/mu_J + m/47 + offset_J], offset_2=0, offset_5=1/94",
        "unit_norm_residual": unit_resid,
        "minimum_pair_distance": min_pair_distance,
        "primal_hull_vertices": int(len(primal.vertices)),
        "origin_interior_margin": origin_margin,
    },
    "dual_crystal": {
        "V": V,
        "E": E,
        "F": F,
        "Euler": euler,
        "face_size_histogram": {str(k): face_sizes.count(k) for k in sorted(set(face_sizes))},
        "facet_plane_residual": facet_plane_resid,
    },
    "precision_note": (
        "The coupled basis is canonical after fixing coupling tree, CG phase, and ordering. "
        "The 3D point rule is an explicit deterministic label-derived embedding convention; "
        "it is not claimed to be the unique Euclidean embedding forced by SU(2). "
        "The exact invariant correspondence is one canonical E47 channel per dual facet."
    ),
    "checks": checks,
}
CERT.write_text(json.dumps(cert, indent=2))

# ------------------------------------------------------------------
# 7. Precise labeled Python render
# ------------------------------------------------------------------
# Continuity convention from the E47 work:
# J=2 / C=6 -> green family
# J=5 / C=30 -> magenta family
green = (0.18, 0.72, 0.36, 0.68)
magenta = (0.88, 0.20, 0.58, 0.68)
edge_color = (0.12,0.16,0.22,0.70)

polys = [dual_vertices[f] for f in faces]
face_colors = [green if labels[i][0]==2 else magenta for i in range(47)]

fig = plt.figure(figsize=(11,11))
ax = fig.add_subplot(111, projection="3d")
pc = Poly3DCollection(
    polys,
    facecolors=face_colors,
    edgecolors=edge_color,
    linewidths=0.65
)
ax.add_collection3d(pc)

# Exact facet IDs. The CSV gives the full |J,j12,m> map.
for a,(face,(J,j12,m)) in enumerate(zip(faces,labels),start=1):
    c = dual_vertices[face].mean(axis=0)
    p = 1.025*c
    ax.text(
        p[0],p[1],p[2],
        f"F{a:02d}",
        fontsize=6.4,
        ha="center",
        va="center"
    )

lim = np.max(np.abs(dual_vertices))*1.08
ax.set_xlim(-lim,lim)
ax.set_ylim(-lim,lim)
ax.set_zlim(-lim,lim)
ax.set_box_aspect((1,1,1))
ax.view_init(elev=20, azim=33)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_title(
    "E47 Canonical 47-Face Dual Crystal\n"
    "one facet per coupled state |J, j12, m>"
)

handles = [
    Patch(facecolor=green, edgecolor=edge_color, label="J=2, C=6: 25 canonical channels"),
    Patch(facecolor=magenta, edgecolor=edge_color, label="J=5, C=30: 22 canonical channels"),
]
ax.legend(handles=handles, loc="upper left")
fig.tight_layout()
fig.savefig(PNG, dpi=240, bbox_inches="tight")
plt.close(fig)

print(f"{cert['certificate']}: {status}")
print(f"{cert['checks_passed']}/{cert['checks_total']} checks PASS")
print(f"Basis orthonormality residual : {basis_orth_resid:.3e}")
print(f"C eigenlabel residual         : {C_eigen_resid:.3e}")
print(f"J12 eigenlabel residual       : {J12_eigen_resid:.3e}")
print(f"K annihilation residual       : {kernel_resid:.3e}")
print(f"Minimum spherical separation  : {min_pair_distance:.6f}")
print(f"Primal hull vertices          : {len(primal.vertices)}")
print(f"Dual topology                 : V={V}, E={E}, F={F}, Euler={euler}")
print(f"Facet plane residual          : {facet_plane_resid:.3e}")
print(f"Face-size histogram           : {cert['dual_crystal']['face_size_histogram']}")
print(f"Render                        : {PNG}")
print(f"Mapping CSV                   : {CSV}")
print(f"Numerical model               : {NPZ}")
print(f"OBJ mesh                      : {OBJ}")
print(f"Certificate                   : {CERT}")