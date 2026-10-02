import numpy as np

TOL = 1e-10

def su2(j=2):
    m=np.arange(j,-j-1,-1,dtype=float); d=len(m)
    Jz=np.diag(m).astype(complex); Jp=np.zeros((d,d),complex)
    for i in range(d-1):
        mm=m[i+1]
        Jp[i,i+1]=np.sqrt(j*(j+1)-mm*(mm+1))
    Jm=Jp.conj().T
    return (Jp+Jm)/2,(Jp-Jm)/(2j),Jz,Jp,Jm

def k3(A,B,C): return np.kron(np.kron(A,B),C)

jx,jy,jz,_,_=su2(2); I5=np.eye(5); I125=np.eye(125)
Jx=k3(jx,I5,I5)+k3(I5,jx,I5)+k3(I5,I5,jx)
Jy=k3(jy,I5,I5)+k3(I5,jy,I5)+k3(I5,I5,jy)
Jz=k3(jz,I5,I5)+k3(I5,jz,I5)+k3(I5,I5,jz)
Jm=Jx-1j*Jy
C=Jx@Jx+Jy@Jy+Jz@Jz
K=(C-6*I125)@(C-30*I125)

j12x=np.kron(jx,I5)+np.kron(I5,jx)
j12y=np.kron(jy,I5)+np.kron(I5,jy)
j12z=np.kron(jz,I5)+np.kron(I5,jz)
C12=np.kron(j12x@j12x+j12y@j12y+j12z@j12z,I5)

cew,cev=np.linalg.eigh(C)
V6=cev[:,np.isclose(cew,6,atol=1e-8)]
V30=cev[:,np.isclose(cew,30,atol=1e-8)]
assert V6.shape[1]==25 and V30.shape[1]==22
assert np.sum(np.isclose(np.linalg.eigvalsh(K),0,atol=1e-8))==47

Jz6=V6.conj().T@Jz@V6
mz,U=np.linalg.eigh(Jz6)
Wm2=V6@U[:,np.isclose(mz,2,atol=1e-8)]
c12,U12=np.linalg.eigh(Wm2.conj().T@C12@Wm2)
o=np.argsort(c12); c12=c12[o]; highest=Wm2@U12[:,o]
assert np.max(np.abs(c12-np.array([0,2,6,12,20])))<TOL

psi={}
for k in range(5):
    v=highest[:,k]/np.linalg.norm(highest[:,k]); psi[(k,2)]=v
    for m in [2,1,0,-1]:
        a=np.sqrt(6-m*(m-1))
        v=(Jm@v)/a; v/=np.linalg.norm(v); psi[(k,m-1)]=v

W=np.column_stack([psi[(k,m)] for k in range(5) for m in [2,1,0,-1,-2]])
P=W@W.conj().T
omega=np.exp(2j*np.pi/5)
X=np.zeros((125,125),complex); Z=np.zeros((125,125),complex)
for m in range(-2,3):
    for k in range(5):
        vk=psi[(k,m)][:,None]; vn=psi[((k+1)%5,m)][:,None]
        X+=vn@vk.conj().T
        Z+=(omega**k)*(vk@vk.conj().T)

lams=[0.,2.,6.,12.,20.]
Zpoly=np.zeros((125,125),complex)
for k,lk in enumerate(lams):
    L=I125.copy()
    for j,lj in enumerate(lams):
        if j!=k: L=L@((C12-lj*I125)/(lk-lj))
    Zpoly+=(omega**k)*L
Zpoly=P@Zpoly@P

gx,gy,gz,_,_=su2(2)
factor=max(
    np.linalg.norm(W.conj().T@A@W-np.kron(np.eye(5),B),2)
    for A,B in [(Jx,gx),(Jy,gy),(Jz,gz)]
)

Code=np.column_stack([psi[(k,2)] for k in range(5)])
errs=[I125,Jx,Jy,Jz]; kl=0.
for Ea in errs:
    for Eb in errs:
        M=Code.conj().T@(Ea.conj().T@Eb)@Code
        kl=max(kl,np.linalg.norm(M-(np.trace(M)/5)*np.eye(5),2))

poly=np.linalg.norm(Z-Zpoly,2)
weyl=np.linalg.norm(Z@X-omega*(X@Z),2)
x5=np.linalg.norm(np.linalg.matrix_power(X,5)-P,2)
z5=np.linalg.norm(np.linalg.matrix_power(Z,5)-P,2)
comm=max(np.linalg.norm(L@J-J@L,2) for L in [X,Z] for J in [Jx,Jy,Jz])

rng=np.random.default_rng(137)
c=rng.normal(size=5)+1j*rng.normal(size=5); c/=np.linalg.norm(c)
g=np.array([1,0,0,0,0],complex)
psi0=W@np.kron(c,g)

X5=np.roll(np.eye(5),1,axis=0)
Z5=np.diag([omega**k for k in range(5)])
G5=X5@np.linalg.matrix_power(Z5,2)@np.linalg.matrix_power(X5,3)
G=X@np.linalg.matrix_power(Z,2)@np.linalg.matrix_power(X,3)
ct=G5@c

theta=np.array([2.4,-1.7,3.1])
H=theta[0]*Jx+theta[1]*Jy+theta[2]*Jz
ew,U=np.linalg.eigh(H); Unoise=U@np.diag(np.exp(-1j*ew))@U.conj().T
psin=Unoise@G@psi0
A=(W.conj().T@psin).reshape(5,5)
rho=A@A.conj().T; target=np.outer(ct,ct.conj())
rho_res=np.linalg.norm(rho-target,2)
fid=float(np.real(np.vdot(ct,rho@ct)))
ret=float(np.real(np.vdot(psin,P@psin)))

checks={
"dim_kernel_47": True,
"decomposition_5V2_2V5": V6.shape[1]//5==5 and V30.shape[1]//11==2,
"c12_spectrum": np.max(np.abs(c12-np.array(lams)))<TOL,
"factorization": factor<TOL,
"knill_laflamme": kl<TOL,
"z_polynomial": poly<TOL,
"weyl_relation": weyl<TOL,
"x5": x5<TOL,
"z5": z5<TOL,
"collective_commutation": comm<1e-10,
"sector_retention": abs(ret-1)<1e-10,
"logical_density_invariance": rho_res<TOL,
"logical_fidelity": abs(fid-1)<1e-10,
}
assert all(checks.values())

print("=== E47 NOISELESS + HEISENBERG-WEYL CERTIFICATE ===")
for k,v in checks.items(): print(("PASS" if v else "FAIL"),k)
print("factorization_residual",factor)
print("knill_laflamme_residual",kl)
print("z_polynomial_residual",poly)
print("weyl_residual",weyl)
print("x5_residual",x5)
print("z5_residual",z5)
print("max_collective_commutator",comm)
print("sector_retention",ret)
print("logical_density_residual",rho_res)
print("logical_fidelity",fid)
