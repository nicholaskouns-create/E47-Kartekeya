#!/usr/bin/env python3
"""E47 convergence + noiseless-subsystem closure.
Certificate: MC-E47-CONVERGENCE-NOISELESS-20260928-001
"""
import json, numpy as np
from numpy.linalg import eigh, norm, svd
from scipy.linalg import expm

TOL=1e-10; THRESHOLD=1e-12; EPS=1/99144
CERT="MC-E47-CONVERGENCE-NOISELESS-20260928-001"

def spin(j):
    m=np.arange(j,-j-1,-1,dtype=float); d=len(m)
    Jz=np.diag(m).astype(complex); Jp=np.zeros((d,d),complex)
    for c in range(1,d):
        mm=m[c]; Jp[c-1,c]=np.sqrt(j*(j+1)-mm*(mm+1))
    Jm=Jp.conj().T
    return (Jp+Jm)/2,(Jp-Jm)/(2j),Jz,Jp,Jm

def k3(A,B,C): return np.kron(np.kron(A,B),C)
def total(A):
    I=np.eye(5,dtype=complex)
    return k3(A,I,I)+k3(I,A,I)+k3(I,I,A)

jx,jy,jz,jp,jm=spin(2)
Jx,Jy,Jz,Jp,Jm=map(total,(jx,jy,jz,jp,jm))
C=Jx@Jx+Jy@Jy+Jz@Jz; I=np.eye(125,dtype=complex)
K=(C-6*I)@(C-30*I); K2=K@K; Gamma=I-EPS*K2
w,V=eigh(C)

def sector(lam):
    Q=V[:,np.isclose(w,lam,atol=1e-9)]
    return Q@Q.conj().T,Q
P6,Q6=sector(6); P30,Q30=sector(30); P=P6+P30

shells=[(0,180),(2,112),(6,0),(12,-108),(20,-140),(30,0),(42,432)]
def bound(n): return max(abs(k)*abs(1-EPS*k*k)**n for _,k in shells if k)
n=0
while bound(n)>=THRESHOLD: n+=1
direct=norm(K@np.linalg.matrix_power(Gamma,n)@(I-P),2)

def null(A,tol=1e-10):
    _,s,Vh=svd(A,full_matrices=True); r=(s>tol).sum()
    return Vh.conj().T[:,r:]

def basis(J,Q):
    H=Q@null(Jp@Q); H,_=np.linalg.qr(H); mult=H.shape[1]; cols=[]
    for a in range(mult):
        v=H[:,a]; cols.append(v/norm(v)); m=J
        while m>-J:
            v=(Jm@v)/np.sqrt((J+m)*(J-m+1)); v=v/norm(v)
            cols.append(v); m-=1
    return np.column_stack(cols),mult

def test(J,Q):
    U,m=basis(J,Q); x,y,z,_,_=spin(J)
    E={"Jx":np.kron(np.eye(m),x),"Jy":np.kron(np.eye(m),y),"Jz":np.kron(np.eye(m),z)}
    A={"Jx":U.conj().T@Jx@U,"Jy":U.conj().T@Jy@U,"Jz":U.conj().T@Jz@U}
    res={k:float(norm(A[k]-E[k],2)) for k in A}
    th=(.371,-.219,.487); G=th[0]*Jx+th[1]*Jy+th[2]*Jz; g=th[0]*x+th[1]*y+th[2]*z
    rr=float(norm(U.conj().T@expm(-1j*G)@U-np.kron(np.eye(m),expm(-1j*g)),2))
    ort=float(norm(U.conj().T@U-np.eye(U.shape[1]),2))
    return {"J":J,"multiplicity":m,"sector_dimension":U.shape[1],
      "orthonormality_residual":ort,"generator_factorization_residuals":res,
      "finite_rotation_residual":rr,"pass":bool(ort<TOL and max(res.values())<TOL and rr<TOL)}

s2=test(2,Q6); s5=test(5,Q30)
comm={a:float(norm(P@A-A@P,2)) for a,A in (("Jx",Jx),("Jy",Jy),("Jz",Jz))}
checks={
 "rank_P47":round(np.trace(P).real)==47,
 "uniform_threshold_crossed":bound(n)<THRESHOLD,
 "uniform_threshold_minimal":bound(n-1)>=THRESHOLD,
 "direct_matrix_bound":direct<THRESHOLD,
 "multiplicity_J2_is_5":s2["multiplicity"]==5,
 "multiplicity_J5_is_2":s5["multiplicity"]==2,
 "J2_noiseless_subsystem":s2["pass"],"J5_noiseless_subsystem":s5["pass"],
 "P47_collective_SU2_invariant":max(comm.values())<TOL}
checks={k:bool(v) for k,v in checks.items()}
out={"certificate":CERT,"status":"PASS" if all(checks.values()) else "FAIL",
 "evidence":"E1 numerical machine certificate; finite-dimensional representation identities",
 "kernel":{"K":"(C-6I)(C-30I)","rank_P47":int(round(np.trace(P).real)),
 "epsilon_star":EPS,"rho_star":15/17},
 "uniform_convergence":{"criterion":"||K Gamma^n (I-P47)||_2 < 1e-12",
 "first_passing_n":n,"bound_n_minus_1":bound(n-1),"bound_n":bound(n),"direct_matrix_norm":direct},
 "noiseless_subsystems":{"decomposition":"E47 ~= (C^5 tensor V_2) direct_sum (C^2 tensor V_5)",
 "J2":s2,"J5":s5,
 "interpretation":"Under collective SU(2), C^5 and C^2 are noiseless multiplicity subsystems; V_2 and V_5 carry the collective action."},
 "commutators_P47":comm,"checks":checks}
print(json.dumps(out,indent=2)); assert out["status"]=="PASS"
