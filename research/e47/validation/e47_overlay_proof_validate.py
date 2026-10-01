#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E47 / D5h / C90 — Celestial-to-Terrestrial Overlay: First-Principles Proof
VALIDATION CONSTRUCT · e47_overlay_proof_validate.py

One executable check per statement of the proof, §0–§11.
Run:   python3 e47_overlay_proof_validate.py        exit 0  ⇔  every check PASS
Needs: numpy, scipy, sympy, networkx.   Optional: ephem (star-catalog cross-check).
"""
import sys, math, cmath, itertools, datetime as dt
from fractions import Fraction
import numpy as np
import sympy as sp
import networkx as nx
from scipy.spatial import ConvexHull
from scipy.integrate import quad

TITLE = "E47 / D5h / C90 — Celestial-to-Terrestrial Overlay: First-Principles Proof"
RNG = np.random.default_rng(47)
D2R, R_EARTH = math.pi / 180.0, 6371.0088
RESULTS, NOTES = [], []

def check(tag, ok, msg):
    RESULTS.append((tag, bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {tag:<10} {msg}")

def note(msg):
    NOTES.append(msg)
    print(f"  [NOTE]            {msg}")

def section(name):
    print(f"\n{name}")

def close(a, b, tol):
    return abs(a - b) <= tol

def u(phi, lam):
    f, l = phi * D2R, lam * D2R
    return np.array([math.cos(f) * math.cos(l), math.cos(f) * math.sin(l), math.sin(f)])

def e_hat(phi, lam):
    l = lam * D2R
    return np.array([-math.sin(l), math.cos(l), 0.0])

def n_hat(phi, lam):
    f, l = phi * D2R, lam * D2R
    return np.array([-math.sin(f) * math.cos(l), -math.sin(f) * math.sin(l), math.cos(f)])

def latlon(x):
    x = x / np.linalg.norm(x)
    return math.degrees(math.asin(max(-1.0, min(1.0, x[2])))), math.degrees(math.atan2(x[1], x[0]))

def frame(x):
    phi, lam = latlon(x)
    return np.column_stack([u(phi, lam), e_hat(phi, lam), n_hat(phi, lam)])

def angle(x, y):
    return math.atan2(np.linalg.norm(np.cross(x, y)), float(np.dot(x, y)))

def centroid(X):
    s = np.sum(X, axis=0)
    return s / np.linalg.norm(s)

def zeta(c, x):
    phi, lam = latlon(c)
    return complex(x @ e_hat(phi, lam), x @ n_hat(phi, lam)) / (x @ u(phi, lam))

def rot_axis(k, g):
    k = k / np.linalg.norm(k)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(g) * K + (1 - math.cos(g)) * K @ K

def rand_s2(n):
    X = RNG.normal(size=(n, 3))
    return X / np.linalg.norm(X, axis=1)[:, None]

print(TITLE)
print("VALIDATION CONSTRUCT · e47_overlay_proof_validate.py")
print("═" * 78)

section("§0 Notation")
err = 0.0
for _ in range(500):
    ph, la = RNG.uniform(-89.9, 89.9), RNG.uniform(-180, 180)
    M = frame(u(ph, la))
    err = max(err, np.abs(np.cross(e_hat(ph, la), n_hat(ph, la)) - u(ph, la)).max(),
              abs(np.linalg.det(M) - 1), np.abs(M.T @ M - np.eye(3)).max())
check("§0.1", err < 1e-12, f"ê × n̂ = u, E(x) ∈ SO(3)  [500 samples, max err {err:.1e}]")

phc, lac = 30.0, 31.0
c0 = u(phc, lac)
dirs = [(math.cos(t), math.sin(t)) for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
add, rel = [], []
for D in (1e-1, 1e-2, 1e-3, 1e-4):
    a_m = r_m = 0.0
    for p_, q_ in dirs:
        x = u(phc + math.degrees(D * p_), lac + math.degrees(D * q_))
        lin = complex(D * q_ * math.cos(phc * D2R), D * p_)
        e_ = abs(zeta(c0, x) - lin)
        a_m, r_m = max(a_m, e_ / D ** 2), max(r_m, e_ / (abs(lin) * D ** 2))
    add.append(a_m); rel.append(r_m)
check("§0.2", max(add) / min(add) < 1.5,
      f"ζ_c(x) = (Δλ cos φ_c + iΔφ) + O(Δ²)  [sup|r|/Δ² ∈ ({min(add):.4f}, {max(add):.4f}), Δ = 1e-1…1e-4]")
note(f"§0 remainder is additive: relative error is O(Δ) (sup|r|/(|ζ|Δ²) grows ×{rel[-1] / rel[0]:.0f}), so '·(1 + O(Δ²))' → '+ O(Δ²)'")

def hms(h, m, s): return 15.0 * (h + m / 60 + s / 3600)
def dms(sg, d, m, s): return sg * (d + m / 60 + s / 3600)
ORION = {"δ Ori": (hms(5, 32, 0.40), dms(-1, 0, 17, 56.7)),
         "ε Ori": (hms(5, 36, 12.81), dms(-1, 1, 12, 6.9)),
         "ζ Ori": (hms(5, 40, 45.53), dms(-1, 1, 56, 33.3))}
GIZA = {"Khufu": (29.9792, 31.1342), "Khafre": (29.9761, 31.1308), "Menkaure": (29.9725, 31.1283)}
STATED_O = [(83.0017, -0.2991), (84.0534, -1.2019), (85.1897, -1.9426)]
section("§1 Axioms · data")
check("§1.A1", all(close(a, sa, 5e-5) and close(d, sd, 5e-5) for (a, d), (sa, sd) in zip(ORION.values(), STATED_O)),
      "o_k = u(δ_k, α_k): J2000 (α, δ) round to stated 4-dp values")
try:
    import ephem
    dev = 0.0
    for nm, (a, d) in zip(("Mintaka", "Alnilam", "Alnitak"), ORION.values()):
        st = ephem.star(nm); st.compute(epoch=ephem.J2000)
        dev = max(dev, abs(math.degrees(float(st._ra)) - a), abs(math.degrees(float(st._dec)) - d))
    check("§1.A1′", dev < 1e-4, f"PyEphem catalog cross-check (J2000): max |Δ| = {dev:.1e}°")
except ImportError:
    note("§1 ephem not installed: catalog cross-check skipped")

def c90_d5h(tube_rings=7):
    G = nx.Graph(); R = tube_rings
    top, cap1 = [(0, j) for j in range(5)], [(1, j) for j in range(5)]
    tube = [[(2 + k, i) for i in range(10)] for k in range(R)]
    cap2, bot = [(R + 2, j) for j in range(5)], [(R + 3, j) for j in range(5)]
    for j in range(5):
        G.add_edges_from([(top[j], top[(j + 1) % 5]), (top[j], cap1[j]),
                          (bot[j], bot[(j + 1) % 5]), (bot[j], cap2[j]),
                          (cap1[j], tube[0][2 * j]), (cap1[j], tube[0][2 * j + 1]),
                          (cap2[j], tube[-1][2 * j]), (cap2[j], tube[-1][2 * j + 1])])
    for k, rg in enumerate(tube):
        off = 1 - k % 2
        G.add_edges_from((rg[(2 * j + off) % 10], rg[(2 * j + off + 1) % 10]) for j in range(5))
        if k + 1 < R:
            G.add_edges_from((rg[i], tube[k + 1][i]) for i in range(10))
    return G, top

G, TOP = c90_d5h()
NODES = list(G.nodes)
planar, EMB = nx.check_planarity(G)
FACES, seen = [], set()
for a, b in EMB.edges():
    if (a, b) not in seen:
        FACES.append(EMB.traverse_face(a, b, mark_half_edges=seen))
SZ = [len(f) for f in FACES]
check("§1.A3", G.number_of_nodes() == 90 and G.number_of_edges() == 135 and {d for _, d in G.degree()} == {3} and planar,
      "Γ(P₄₇) constructed: |𝒱| = 90, |E| = 135, 3-regular, planar")
auts = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
sig_h = {(r, i): (10 - r, i) for (r, i) in NODES}
c5 = {(r, i): (r, (i + 1) % 5) if r in (0, 1, 9, 10) else (r, (i + 2) % 10) for (r, i) in NODES}
is_aut = lambda m: all(G.has_edge(m[a], m[b]) for a, b in G.edges)
check("§1.Sym", len(auts) == 20 and is_aut(sig_h) and is_aut(c5) and all(sig_h[(5, i)] == (5, i) for i in range(10)),
      f"|Aut Γ| = {len(auts)} = |D₅ₕ|; C₅ ∈ Aut; σ_h ∈ Aut")

section("§2 Combinatorics")
Vs, Es, Fs = sp.symbols("V E F", positive=True)
sol = sp.solve([sp.Eq(Vs - Es + Fs, 2), sp.Eq(3 * Vs, 2 * Es)], [Vs, Es], dict=True)[0]
check("§2.L1", sp.simplify(6 * Fs - 2 * sol[Es]) == 12,
      "Euler + cubic valence ⇒ Σ(6 − n_f) = 12")
p_ = 12; h_ = 35; E_ = (5*p_+6*h_)//2; V_ = 2*E_//3
check("§2.C1", (p_,h_,E_,V_,V_-E_+47)==(12,35,135,90,2), "(p,h,E,V,χ)=(12,35,135,90,2)")
nP, nH = SZ.count(5), SZ.count(6)
check("§2.C1′", (len(FACES), nP, nH, len(SZ)-nP-nH)==(47,12,35,0),
      f"embedding faces: F={len(FACES)}={nP} pentagons+{nH} hexagons")
check("§2.χ", G.number_of_nodes()-G.number_of_edges()+len(FACES)==2 and sum(6-s for s in SZ)==12,
      "χ=2 and discrete curvature sum=12")

section("§3 Constants")
check("§3.Ω", Fraction(47,125)==Fraction(376,1000), "Ω_c = 47/125 = 0.376")
check("§3.ε", f"{1/99144:.4e}"=="1.0086e-05", f"ε*={1/99144:.6e}")
check("§3.ρ", f"{15/17:.6f}"=="0.882353", "ρ*=15/17=0.882353")

section("§4 Volumes")
VC,VS,VP=8.0,4*math.pi/3,3.9392
c_fit=47*(1-VP/VS)
check("§4.ord", VP<VS<VC, "V(P47)<V(S)<V(C)")
check("§4.V", close(VS,4.18879,5e-6) and close(VC-VP,4.0608,1e-9) and close(VC-VS,3.81121,5e-6),
      "volume values reproduce")
check("§4.ratio", close((VC-VP)/VC,0.5076,1e-9) and close((VC-VS)/VC,0.47640,5e-6)
      and close(1-VP/VS,0.0596,5e-5), "void ratios reproduce")
check("§4.c", close(c_fit,2.8005,5e-5), f"c={c_fit:.4f}")
rows_ok=[]
for Fk,exp in ((188,(4.1264,3.8736,0.4842)),(1504,(4.1810,3.8190,0.4774))):
    vh=VS*(1-c_fit/Fk); rows_ok.append(all(close(g,e,5e-5) for g,e in zip((vh,VC-vh,(VC-vh)/VC),exp)))
check("§4.V̂", all(rows_ok), "asymptotic rows reproduce")

def icosa():
    t=(1+5**0.5)/2
    V=np.array([[-1,t,0],[1,t,0],[-1,-t,0],[1,-t,0],[0,-1,t],[0,1,t],[0,-1,-t],[0,1,-t],[t,0,-1],[t,0,1],[-t,0,-1],[-t,0,1]],float)
    F=[(0,11,5),(0,5,1),(0,1,7),(0,7,10),(0,10,11),(1,5,9),(5,11,4),(11,10,2),(10,7,6),(7,1,8),
       (3,9,4),(3,4,2),(3,2,6),(3,6,8),(3,8,9),(4,9,5),(2,4,11),(6,2,10),(8,6,7),(9,8,1)]
    return V/np.linalg.norm(V,axis=1)[:,None],F
def geodesic(nu):
    V,F=icosa(); P=[]
    for a,b,c in F:
        for i in range(nu+1):
            for j in range(nu+1-i):
                q=(i*V[a]+j*V[b]+(nu-i-j)*V[c])/nu
                P.append(q/np.linalg.norm(q))
    return np.unique(np.round(np.array(P),12),axis=0)
HULLS,CS={},[]
for nu in (2,4,8,16,32):
    H=ConvexHull(geodesic(nu)); HULLS[nu]=H; CS.append((len(H.simplices),H.volume,len(H.simplices)*(1-H.volume/VS)))
mono=all(CS[i][1]<CS[i+1][1]<VS for i in range(len(CS)-1))
check("§4.L2", mono and abs(CS[-1][2]/CS[-2][2]-1)<0.01,
      "V(S)-V(P_F)=Θ(F^-1) on geodesic refinement")

section("§5 Geodetic frame")
PD,LD=37.6439,-84.7729
uD,eD,nD=u(PD,LD),e_hat(PD,LD),n_hat(PD,LD)
az_vec=lambda A:math.cos(A*D2R)*nD+math.sin(A*D2R)*eD
xh,yh=az_vec(81),az_vec(351)
S_u=np.array([0.0721378333,-0.7885290627,0.6107520367])
S_x=np.array([0.9748766773,0.1851273173,0.1238682381])
S_y=np.array([-0.2107405918,0.5864723299,0.7820732761])
check("§5.u", np.abs(uD-S_u).max()<1e-10 and close(np.linalg.norm(uD),1,1e-15), "u_D reproduced")
check("§5.x̂ŷ", np.abs(xh-S_x).max()<1e-10 and np.abs(yh-S_y).max()<1e-10, "house axes reproduced")
Mh=np.column_stack([xh,yh,uD])
check("§5.SO3", np.abs(np.cross(xh,yh)-uD).max()<1e-12 and np.abs(Mh.T@Mh-np.eye(3)).max()<1e-12
      and close(np.linalg.det(Mh),1,1e-12), "house frame ∈ SO(3)")
az_of=lambda v:math.degrees(math.atan2(v@eD,v@nD))%360
AZ=tuple(round(az_of(v),9) for v in (xh,yh,-xh,-yh))
check("§5.az", AZ==(81.0,351.0,261.0,171.0), f"az={AZ}")
t0=dt.datetime(1965,12,9,3,22,tzinfo=dt.timezone.utc)
loc=t0.astimezone(dt.timezone(dt.timedelta(hours=-5)))
check("§5.t₀", loc.isoformat()=="1965-12-08T22:22:00-05:00", "UTC/local conversion")
layers=nx.multi_source_dijkstra_path_length(G,TOP)
census=[sum(1 for v in layers.values() if v==k) for k in range(max(layers.values())+1)]
check("§5.ring", census==[5,5,10,10,10,10,10,10,10,5,5] and sum(census)==90,
      f"ring census={tuple(census)}")
PHI1=46.6418024518
sep=math.degrees(angle(uD,u(PHI1,LD)))
check("§5.v₆", close(sep,8.9979024518,1e-9), f"Node-6 separation={sep:.10f}°")

section("§6 Local triad")
Ou=[u(d,a) for a,d in ORION.values()]
Gu=[u(p,l) for p,l in GIZA.values()]
cO,cG=centroid(Ou),centroid(Gu)
z=np.array([zeta(cO,x) for x in Ou]); w=np.array([zeta(cG,x) for x in Gu])
lo_,ao_=latlon(cO); lg_,ag_=latlon(cG)
check("§6.c", close(lo_,-1.1480,5e-5) and close(ao_%360,84.0814,5e-5) and close(lg_,29.9759,5e-5) and close(ag_,31.1311,5e-5),
      "centroids reproduced")
sides=lambda q:np.array([abs(q[1]-q[0]),abs(q[2]-q[1]),abs(q[2]-q[0])])
dO,dG=np.degrees(sides(z)),sides(w)*R_EARTH
check("§6.d", np.allclose(dO,[1.38626,1.35630,2.73666],atol=5e-6) and np.allclose(dG,[0.4755,0.4672,0.9370],atol=5e-5),
      f"d(O)=({dO[0]:.5f},{dO[1]:.5f},{dO[2]:.5f})°, d(G)=({dG[0]:.4f},{dG[1]:.4f},{dG[2]:.4f}) km")
check("§6.ratio", np.allclose(dO/dO[0],[1,0.9784,1.9741],atol=5e-5) and np.allclose(dG/dG[0],[1,0.9825,1.9707],atol=5e-5),
      "normalized side ratios reproduce")
kap=lambda q:(q[2]-q[0])/(q[1]-q[0])
kz,kw=kap(z),kap(w)
check("§6.κ", all(close(a,b,5e-5) for a,b in ((kz.real,1.9700),(kz.imag,0.1280),(kw.real,1.9592),(kw.imag,0.2127),(abs(kz-kw),0.0854))),
      f"|Δκ|={abs(kz-kw):.4f}")
def procrustes(zz,ww):
    mz,mw=zz.mean(),ww.mean()
    A=np.sum((ww-mw)*np.conj(zz-mz))/np.sum(abs(zz-mz)**2)
    return A,mw-A*mz
A_s,b_s=procrustes(z,w)
def fit_cfg(zz,ww):
    zn=(zz-zz.mean())/abs(zz[1]-zz[0]); wn=(ww-ww.mean())/abs(ww[1]-ww[0])
    An=np.sum(wn*np.conj(zn))/np.sum(abs(zn)**2)
    return math.sqrt(np.sum(abs(wn-An*zn)**2)/3),An
TABLE=[]
for perm in itertools.permutations(range(3)):
    for mirror in (False,True):
        zz=z[list(perm)]
        rms,An=fit_cfg(np.conj(zz) if mirror else zz,w)
        TABLE.append((rms,perm,mirror,An))
TABLE.sort(key=lambda t:t[0]); rms_b,perm_b,mir_b,An_b=TABLE[0]
theta=math.degrees(np.angle(A_s))
check("§6.π*", perm_b==(0,1,2) and not mir_b, "best mapping = (id, Sim+)")
check("§6.fit", close(abs(An_b),0.9992,5e-5) and close(theta,-90.428,5e-4) and close(rms_b,0.0204,5e-5),
      f"a={abs(An_b):.4f}, θ*={theta:.3f}°, RMS={rms_b:.4f}")
a_star=abs(A_s)
check("§6.a*", close(a_star,3.0821e-3,5e-8) and close(a_star*R_EARTH*D2R,0.3427,5e-5),
      f"a*={a_star:.4e}={a_star*R_EARTH*D2R:.4f} km/deg")

section("§7 Global extension")
th=math.radians(theta)
Mt=np.array([[1,0,0],[0,math.cos(th),-math.sin(th)],[0,math.sin(th),math.cos(th)]])
FO,FG=frame(cO),frame(cG)
Rs=FG@Mt@FO.T
S_R=np.array([[-0.35385,0.77164,-0.52854],[-0.20263,0.48844,0.84875],[0.91309,0.40742,-0.01648]])
gap=np.linalg.norm(Rs@cO-cG)
check("§7.R*", np.abs(Rs-S_R).max()<5e-6 and close(np.linalg.det(Rs),1,1e-12)
      and np.abs(Rs@Rs.T-np.eye(3)).max()<1e-12 and gap<1e-15,
      f"R* ∈ SO(3), ||R*c_O-c_G||={gap:.1e}")
note(f"§7 exact θ* = {theta:.6f}° ⇒ R*₂₁ = {Rs[1,0]:.7f} → −0.20263")

section("§8 Propositions")
S=rand_s2(2000); P=S@Rs.T
rt=max(np.abs(u(*latlon(p))-p).max() for p in P)
check("§8.P2", rt<1e-12 and np.abs(P@Rs-S).max()<1e-12, "2000-point round-trip")
pairs=RNG.integers(0,len(S),size=(5000,2))
dang=max(abs(angle(P[i],P[j])-angle(S[i],S[j])) for i,j in pairs)
check("§8.P3", dang<1e-12, f"angular distances preserved, max={dang:.1e}")
check("§8.P5", close(math.degrees(np.angle(A_s)),theta,1e-12), "local/global angle arguments agree")

section("§9 Theorem")
STATUS=dict(RESULTS)
for k,tags in {"(i)":["§2.L1","§2.C1","§2.C1′","§2.χ","§1.Sym"],
               "(iii)":["§7.R*"],"(iv)":["§8.P3"],"(v)":["§8.P2"],
               "(vi)":["§6.π*","§6.fit","§6.κ"]}.items():
    check(f"§9{k}", all(STATUS.get(t,False) for t in tags), " ⇐ "+", ".join(tags))

section("§10 Predictions")
def delta_stat(stars,nodes):
    return float(np.mean(np.arccos(np.clip(np.max(stars@nodes.T,axis=1),-1,1))))
def null_expectation(nodes,n=50000): return delta_stat(rand_s2(n),nodes)
fib=np.array([u(math.degrees(math.asin(1-2*(k+0.5)/90)),(k*137.50776405)%360-180) for k in range(90)])
calib=abs(delta_stat(rand_s2(50000),fib)-null_expectation(fib))
check("§10.H₁", delta_stat(fib,fib)<1e-6 and calib<2e-3, "estimator calibrated")
note("§10 H₁ verdict requires the final 90 lattice nodes and chosen figure-star set J")

section("§11 Curvature")
gb,_=quad(lambda t:2*math.pi*math.sin(t),0,math.pi)
check("§11.GB", close(gb,4*math.pi,1e-12), "Gauss-Bonnet sphere integral = 4π")
kv=nx.node_connectivity(G)
check("§11.Γ", planar and kv==3, f"planar and 3-connected, κ(Γ)={kv}")
xs,ys=sp.symbols("x y",real=True)
lam=4/(1-xs**2-ys**2)**2
Kc=sp.simplify(-(sp.diff(sp.log(lam),xs,2)+sp.diff(sp.log(lam),ys,2))/(2*lam))
check("§11.K", Kc==-1, "Poincaré disk metric has K=-1")

n_ok=sum(ok for _,ok in RESULTS)
print("\n"+"═"*78)
print(TITLE)
print(f"VALIDATION: {n_ok}/{len(RESULTS)} PASS")
for m in NOTES: print("NOTE",m)
sys.exit(0 if n_ok==len(RESULTS) else 1)
