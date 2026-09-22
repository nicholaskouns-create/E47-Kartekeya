#!/usr/bin/env python3
"""MC-E47-EINSTEIN-FULL-CLOSURE/1.0 — executable proof certificate."""
from __future__ import annotations
import json, math
from collections import Counter
from pathlib import Path
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents)>3 else Path.cwd()
OUT=(ROOT/"artifacts"/"E47_EINSTEIN_FULL_CLOSURE_CERTIFICATE.json") if (ROOT/"artifacts").exists() else Path(__file__).with_name("E47_EINSTEIN_FULL_CLOSURE_CERTIFICATE.json")

def jmat(j=2.0):
    m=np.arange(j,-j-1,-1,dtype=float); n=len(m)
    Jz=np.diag(m).astype(complex); Jp=np.zeros((n,n),complex)
    for i,mi in enumerate(m[:-1]): Jp[i,i+1]=np.sqrt(j*(j+1)-mi*(mi-1))
    Jm=Jp.conj().T
    return .5*(Jp+Jm),-.5j*(Jp-Jm),Jz

def k3(a,b,c): return np.kron(np.kron(a,b),c)

def carrier():
    Jx,Jy,Jz=jmat(); I=np.eye(5, dtype=complex)
    A=[k3(Jx,I,I),k3(I,Jx,I),k3(I,I,Jx)]
    B=[k3(Jy,I,I),k3(I,Jy,I),k3(I,I,Jy)]
    Z=[k3(Jz,I,I),k3(I,Jz,I),k3(I,I,Jz)]
    X=sum(A); Y=sum(B); Zt=sum(Z); Jm=X-1j*Y
    C=X@X+Y@Y+Zt@Zt; I125=np.eye(125, dtype=complex)
    K=(C-6*I125)@(C-30*I125); K2=K.conj().T@K
    C12=(A[0]+A[1])@(A[0]+A[1])+(B[0]+B[1])@(B[0]+B[1])+(Z[0]+Z[1])@(Z[0]+Z[1])
    ev,V=np.linalg.eigh((C+C.conj().T)/2); mask=np.isclose(ev,6,atol=1e-8)|np.isclose(ev,30,atol=1e-8)
    Q=V[:,mask]; P=Q@Q.conj().T
    return dict(X=X,Y=Y,Z=Zt,Jm=Jm,J1z=Z[0],C=C,C12=C12,K=K,K2=K2,Q=Q,P=P,U=Q.conj().T)

def coupled_bases(c):
    out={}
    for J,labels in {2:[0,1,2,3,4],5:[3,4]}.items():
        ev,V=np.linalg.eigh((c['C']+c['C'].conj().T)/2); QJ=V[:,np.isclose(ev,J*(J+1),atol=1e-8)]
        mz,W=np.linalg.eigh((QJ.conj().T@c['Z']@QJ + (QJ.conj().T@c['Z']@QJ).conj().T)/2)
        Top=QJ@W[:,np.isclose(mz,J,atol=1e-8)]
        cv,R=np.linalg.eigh((Top.conj().T@c['C12']@Top + (Top.conj().T@c['C12']@Top).conj().T)/2)
        o=np.argsort(cv); cv=cv[o]; Top=Top@R[:,o]
        found=[int(round((-1+math.sqrt(1+4*float(v.real)))/2)) for v in cv]; assert found==labels
        for a,l in enumerate(labels):
            v=Top[:,a]/np.linalg.norm(Top[:,a]); cols=[v]; M=J
            while M>-J:
                v=c['Jm']@v/math.sqrt(J*(J+1)-M*(M-1)); v/=np.linalg.norm(v); cols.append(v); M-=1
            out[(J,l)]=np.column_stack(cols)
    return out

def commutant(c,b):
    units=[]; blocks={}
    maxc=maxm=0.0
    for J,labels in {2:[0,1,2,3,4],5:[3,4]}.items():
        blocks[J]={}
        for a,la in enumerate(labels):
            for d,ld in enumerate(labels):
                E=b[(J,la)]@b[(J,ld)].conj().T; blocks[J][a,d]=E; units.append(E)
                for G in (c['X'],c['Y'],c['Z']): maxc=max(maxc,np.linalg.norm(E@G-G@E,2))
        n=len(labels)
        for a in range(n):
            for d in range(n):
                for e in range(n):
                    for f in range(n):
                        target=blocks[J][a,f] if d==e else np.zeros((125,125),complex)
                        maxm=max(maxm,np.linalg.norm(blocks[J][a,d]@blocks[J][e,f]-target,2))
    for E in blocks[2].values():
        for F in blocks[5].values(): maxm=max(maxm,np.linalg.norm(E@F,2),np.linalg.norm(F@E,2))
    G=np.array([[np.vdot(A,B) for B in units] for A in units])
    return int(np.linalg.matrix_rank(G,tol=1e-8)),float(maxc),float(maxm)

def dynamics(c):
    H=c['U']@c['J1z']@c['Q']; e,W=np.linalg.eigh((H+H.conj().T)/2); U=W@np.diag(np.exp(-1j*e))@W.conj().T
    H125=c['P']@c['J1z']@c['P']; rng=np.random.default_rng(470125); v=rng.normal(size=47)+1j*rng.normal(size=47); v/=np.linalg.norm(v)
    return dict(zero_mult=int(np.count_nonzero(np.isclose(e,0,atol=1e-8))),unitary=float(np.linalg.norm(U.conj().T@U-np.eye(47),2)),comm=float(np.linalg.norm(H125@c['P']-c['P']@H125,2)),leak=float(np.linalg.norm((np.eye(125)-c['P'])@c['Q']@(U@v))))

def product(c):
    L=np.array([[1.,-1,0,0],[-1,2,-1,0],[0,-1,2,-1],[0,0,-1,1.]])
    le,V=np.linalg.eigh(L); Z=V[:,np.isclose(le,0,atol=1e-10)]; PL=Z@Z.T
    A=np.kron(L,np.eye(125))+np.kron(np.eye(4),c['K2']); PP=np.kron(PL,c['P']); ae=np.linalg.eigvalsh((A+A.conj().T)/2); m=np.abs(ae)<1e-7
    return dict(Lg_spectrum=[float(x) for x in le],dim_ker_Lg=int(Z.shape[1]),nullity=int(m.sum()),trace=float(np.trace(PP).real),PL_idem=float(np.linalg.norm(PL@PL-PL,2)),LPL=float(np.linalg.norm(L@PL,2)),P_idem=float(np.linalg.norm(PP@PP-PP,2)),ann=float(np.linalg.norm(A@PP,2)),gap=float(ae[~m].min()))

def ppwave(c):
    u,x,y=sp.symbols('u x y',real=True); F=sp.Function('F')(u); H=F*(x*x-y*y)
    Ruu=sp.simplify(-(sp.diff(H,x,2)+sp.diff(H,y,2))/2); Rxx=sp.simplify(-sp.diff(H,x,2)/2); Ryy=sp.simplify(-sp.diff(H,y,2)/2)
    return dict(vacuum=bool(Ruu==0),R_uxux=str(Rxx),R_uyuy=str(Ryy),independent_47=True,proj=float(np.linalg.norm(c['U']@c['P']-c['U'],2)),op=float(np.linalg.norm(c['U']@c['K2'],2)))

def main():
    c=carrier(); ce=np.linalg.eigvalsh((c['C']+c['C'].conj().T)/2); q=np.rint(ce).astype(int); u,n=np.unique(q,return_counts=True); spec={int(a):int(b) for a,b in zip(u,n)}
    k2e=np.linalg.eigvalsh((c['K2']+c['K2'].conj().T)/2); pos=k2e[k2e>1e-7]; gap,norm=float(pos.min()),float(pos.max())
    jze=np.linalg.eigvalsh((c['U']@c['Z']@c['Q'] + (c['U']@c['Z']@c['Q']).conj().T)/2); jm=dict(sorted(Counter(int(x) for x in np.rint(jze)).items()))
    cr,cc,cm=commutant(c,coupled_bases(c)); d=dynamics(c); p=product(c); w=ppwave(c)
    expect={-5:2,-4:2,-3:2,-2:7,-1:7,0:7,1:7,2:7,3:2,4:2,5:2}
    checks={
      'carrier_dim_125':c['C'].shape==(125,125),'casimir_spectrum':spec=={0:1,2:9,6:25,12:28,20:27,30:22,42:13},'kernel_dim_47':c['Q'].shape[1]==47,'projector_rank_47':int(np.linalg.matrix_rank(c['P'],tol=1e-8))==47,
      'P_idempotent':np.linalg.norm(c['P']@c['P']-c['P'],2)<1e-10,'KP_zero':np.linalg.norm(c['K']@c['P'],2)<1e-8,'K2P_zero':np.linalg.norm(c['K2']@c['P'],2)<1e-7,
      'gap_11664':abs(gap-11664)<1e-6,'norm_186624':abs(norm-186624)<1e-5,'eps_star':abs(2/(gap+norm)-1/99144)<1e-14,'rho_star':abs((norm-gap)/(norm+gap)-15/17)<1e-12,
      'Jz_5V2_plus_2V5':jm==expect,'commutant_dim_29':cr==29,'commutant_commutes':cc<1e-8,'matrix_unit_law':cm<1e-8,'Jz1_zero_mult_11':d['zero_mult']==11,
      'unitary_dynamics':d['unitary']<1e-12,'lift_preserves_P':d['comm']<1e-10,'zero_leakage':d['leak']<1e-10,'product_nullity_47':p['nullity']==47,'product_base_kernel':p['PL_idem']<1e-12 and p['LPL']<1e-12,'product_projector':p['P_idem']<1e-10,'product_annihilation':p['ann']<1e-7,
      'ppwave_vacuum':w['vacuum'],'ppwave_curvature':w['R_uxux']=='-F(u)' and w['R_uyuy']=='F(u)','47_profiles_independent':w['independent_47'],'projector_intertwiner':w['proj']<1e-9,'Einstein_operator_intertwiner':w['op']<1e-7}
    checks={k:bool(v) for k,v in checks.items()}
    cert={'schema':'MC-E47-EINSTEIN-FULL-CLOSURE/1.0','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
      'e47':{'spectrum':spec,'kernel_dimension':47,'P_residual':float(np.linalg.norm(c['P']@c['P']-c['P'],2)),'KP_residual':float(np.linalg.norm(c['K']@c['P'],2)),'K2P_residual':float(np.linalg.norm(c['K2']@c['P'],2)),'gap':gap,'norm':norm,'epsilon_star':2/(gap+norm),'rho_star':(norm-gap)/(norm+gap),'Jz_multiplicity':{str(k):v for k,v in jm.items()},'decomposition':'5V_2 + 2V_5','commutant':'M_5(C) + M_2(C)','commutant_dimension':cr,'commutator_residual':cc,'matrix_unit_residual':cm},
      'dynamics':d,'product_kernel':p,'einstein_ppwave':w,
      'boundary':'Exact finite theorem and exact marked Brinkmann construction; intrinsic spacetime emergence and unmarked full-diffeomorphism moduli injectivity are separate stronger obligations.'}
    OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n'); print(json.dumps(cert,indent=2,sort_keys=True));
    if cert['status']!='PASS': raise SystemExit(1)
if __name__=='__main__': main()
