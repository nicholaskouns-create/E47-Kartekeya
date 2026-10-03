import numpy as np, itertools
from collections import Counter
np.set_printoptions(precision=12, suppress=True)

# ---------- spin-2 (dim 5) generators, basis x=0..4 <-> m=2-x ----------
j=2; d=5
ms=[j-x for x in range(d)]
Jz=np.diag(ms).astype(float)
Jp=np.zeros((d,d)); Jm=np.zeros((d,d))
for x,m in enumerate(ms):
    if m+1<=j:
        Jp[x-1,x]=np.sqrt(j*(j+1)-m*(m+1)) # raises m -> m+1 (index x-1)
    if m-1>=-j:
        Jm[x+1,x]=np.sqrt(j*(j+1)-m*(m-1))
assert np.allclose(Jp, Jm.T)
assert np.allclose(Jp@Jm - Jm@Jp, 2*Jz)

I5=np.eye(5)
def slot(M,i):
    ops=[I5,I5,I5]; ops[i]=M
    return np.kron(np.kron(ops[0],ops[1]),ops[2])

JZ=sum(slot(Jz,i) for i in range(3))
JP=sum(slot(Jp,i) for i in range(3))
JM=sum(slot(Jm,i) for i in range(3))
C = JZ@JZ + 0.5*(JP@JM + JM@JP)
print("C symmetric residual:", np.abs(C-C.T).max())

w,V=np.linalg.eigh(C)
wr=np.round(w,9)
print("Casimir spectrum & multiplicities:", sorted(Counter(wr).items()))
print("expected j(j+1) for j=0..6:", [jj*(jj+1) for jj in range(7)])

# ---------- K and P47 ----------
K=(C-6*np.eye(125))@(C-30*np.eye(125))
print("dim ker K:", int(np.sum(np.abs(np.linalg.eigvalsh(K))<1e-8)))
sel=(np.abs(wr-6)<1e-9)|(np.abs(wr-30)<1e-9)
P=V[:,sel]@V[:,sel].T
print("P idempotent residual:", np.abs(P@P-P).max(), "| trace P =", round(np.trace(P),10))
print("P K residual (P projects into ker K):", np.abs(K@P).max())

# ---------- S3 acting by permuting tensor slots ----------
pts=list(itertools.product(range(5),repeat=3)); idx={p:i for i,p in enumerate(pts)}
def perm_mat(sig):
    M=np.zeros((125,125))
    for p in pts:
        q=tuple(p[sig[k]] for k in range(3)) # (sigma.v)_k = v_{sigma(k)}
        M[idx[q],idx[p]]=1
    return M
S3=[perm_mat(s) for s in itertools.permutations(range(3))]
sig_par=[(-1)**(sum(1 for a in range(3) for b in range(a+1,3) if s[a]>s[b])) for s in itertools.permutations(range(3))]
print("\n[S3 test] max ||P.sigma - sigma.P|| over S3:",
      max(np.abs(P@M-M@P).max() for M in S3))
print("[S3 test] max ||C.sigma - sigma.C||:", max(np.abs(C@M-M@C).max() for M in S3))

# ---------- (Z/5)^3 index shifts ----------
def shift_mat(axis):
    M=np.zeros((125,125))
    for p in pts:
        q=list(p); q[axis]=(q[axis]+1)%5
        M[idx[tuple(q)],idx[p]]=1
    return M
Z5=[shift_mat(a) for a in range(3)]
print("\n[Z/5 test] max ||P.T_a - T_a.P||:", round(max(np.abs(P@M-M@P).max() for M in Z5),10))
print("[Z/5 test] max ||C.T_a - T_a.C||:", round(max(np.abs(C@M-M@C).max() for M in Z5),10))

# ---------- Schur-Weyl block content of ker K ----------
Sym=sum(S3)/6.0
Alt=sum(s*M for s,M in zip(sig_par,S3))/6.0
print("\ndim Sym^3 =", round(np.trace(Sym),8), " dim Lambda^3 =", round(np.trace(Alt),8),
      " dim mixed =", round(125-np.trace(Sym)-np.trace(Alt),8))
a=np.trace(P@Sym); c=np.trace(P@Alt); b=47-a-c
print("ker K ∩ Sym^3 :", round(a,10))
print("ker K ∩ Lambda^3:", round(c,10))
print("ker K ∩ mixed :", round(b,10), "(must be even = 2 x S_(2,1) copies)")

# ---------- per-j multiplicity spaces as S3 reps ----------
print("\n j | dim V_j | mult | S3 character on mult space (e, transposition, 3-cycle) | decomposition")
classes={'e':S3[0],'transp':perm_mat((1,0,2)),'3cyc':perm_mat((1,2,0))}
for jj in range(7):
    lam=jj*(jj+1); s=(np.abs(wr-lam)<1e-9)
    if not s.any(): continue
    Pj=V[:,s]@V[:,s].T
    chi={k: np.trace(Pj@M)/(2*jj+1) for k,M in classes.items()}
    e,t,c3=chi['e'],chi['transp'],chi['3cyc']
    n_triv=(e+3*t+2*c3)/6; n_sgn=(e-3*t+2*c3)/6; n_std=(2*e-2*c3)/6
    print(f" {jj} | {2*jj+1:2d} | {int(round(e))} | ({e:.6f}, {t:.6f}, {c3:.6f}) |"
          f" triv x{round(n_triv,6)}, sgn x{round(n_sgn,6)}, std x{round(n_std,6)}")
