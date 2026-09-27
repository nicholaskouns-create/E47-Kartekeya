#!/usr/bin/env python3
"""MC-E47-CONDITION-LOCK/1.0 — condition-4 lock, equioscillation, five-factor projector,
five-step termination and Chebyshev rate for the E47 contraction.

Exact layer: every constant is derived in rational arithmetic from the seven Casimir
values alone. Machine layer: each exact statement is replayed on the 125x125 carrier.
"""
from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
import sympy as sp

ROOT=Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents)>3 else Path.cwd()
OUT=(ROOT/"artifacts"/"E47_CONDITION_LOCK_CERTIFICATE.json") if (ROOT/"artifacts").exists() else Path(__file__).with_name("E47_CONDITION_LOCK_CERTIFICATE.json")
if os.environ.get("E47_CERT_OUT"): OUT=Path(os.environ["E47_CERT_OUT"])

CASIMIR=[0,2,6,12,20,30,42]          # j(j+1), j=0..6, on V2⊗V2⊗V2
KERNEL={6,30}                        # E47 = ker (C-6I)(C-30I)
NMAX=8                               # Chebyshev degrees checked

def r(x):
    """Residuals are recorded to 3 significant figures so regeneration is byte-stable."""
    return float(f"{float(x):.2e}")

def exact():
    R=sp.Rational
    k={c:(c-6)*(c-30) for c in CASIMIR}
    comp=[c for c in CASIMIR if c not in KERNEL]
    absk=sorted({abs(k[c]) for c in comp})
    lam=[a*a for a in absk]
    kmin,kmax=absk[0],absk[-1]
    kappa_K=R(kmax,kmin); kappa=kappa_K**2
    gap,norm=R(lam[0]),R(lam[-1])
    eps=2/(gap+norm); rho=(norm-gap)/(norm+gap)
    gamma=[1-R(l)*eps for l in lam]
    x=sp.symbols('x')
    prod=sp.prod([1-x/l for l in lam])
    t=(sp.sqrt(kappa)+1)/(sp.sqrt(kappa)-1)   # 5/3
    cheb_rate=1/t
    arg=(norm+gap)/(norm-gap)                 # 17/15
    cheb=[1/sp.chebyshevt(n,arg) for n in range(1,NMAX+1)]
    return dict(
        k=k, absk=absk, lam=lam, kappa_K=kappa_K, kappa=kappa, eps=eps, rho=rho, gamma=gamma,
        prod_zero_on_complement=all(prod.subs(x,l)==0 for l in lam), prod_one_on_kernel=prod.subs(x,0)==1,
        cheb_rate=sp.nsimplify(cheb_rate), arg=arg, cheb=cheb,
        cheb_closed=all(sp.simplify(cheb[n-1]-2/(R(5,3)**n+R(3,5)**n))==0 for n in range(1,NMAX+1)),
        cheb_beats_richardson=all(cheb[n-1]<rho**n for n in range(2,NMAX+1)) and cheb[0]==rho,
    )

def carrier():
    j=2.0; m=np.arange(j,-j-1,-1); Jz=np.diag(m).astype(complex); Jp=np.zeros((5,5),complex)
    for i,mi in enumerate(m[:-1]): Jp[i,i+1]=np.sqrt(j*(j+1)-mi*(mi-1))
    Jx=.5*(Jp+Jp.conj().T); Jy=-.5j*(Jp-Jp.conj().T); I5=np.eye(5)
    def tot(A): return np.kron(np.kron(A,I5),I5)+np.kron(np.kron(I5,A),I5)+np.kron(np.kron(I5,I5),A)
    X,Y,Z=tot(Jx),tot(Jy),tot(Jz)
    C=((X@X+Y@Y+Z@Z)+(X@X+Y@Y+Z@Z).conj().T).real/2; I=np.eye(125)
    K=(C-6*I)@(C-30*I); K2=K@K
    ev,V=np.linalg.eigh(C); Q=V[:,np.isclose(ev,6,atol=1e-8)|np.isclose(ev,30,atol=1e-8)]
    return C,K,K2,Q@Q.T,I

def machine(e):
    C,K,K2,P,I=carrier(); Pc=I-P
    ce=np.rint(np.linalg.eigvalsh(C)).astype(int); u,n=np.unique(ce,return_counts=True); spec={int(a):int(b) for a,b in zip(u,n)}
    # K on each Casimir sector, and its inertia
    ev,V=np.linalg.eigh(C); sector={}
    for c in CASIMIR:
        Qc=V[:,np.isclose(ev,c,atol=1e-8)]; sector[c]=float(np.mean(np.diag(Qc.T@K@Qc)))
    ke=np.linalg.eigvalsh(K); inertia=(int((ke>.5).sum()),int((ke<-.5).sum()),int((abs(ke)<.5).sum()))
    # condition numbers on the complement
    sv=np.abs(ke[abs(ke)>.5]); kK=sv.max()/sv.min()
    # Gamma* spectrum on the complement: equioscillation
    G=I-float(e['eps'])*K2; W=V[:,~(np.isclose(ev,6,atol=1e-8)|np.isclose(ev,30,atol=1e-8))]
    ge_c=np.linalg.eigvalsh(W.T@G@W)
    # five-factor exact projector
    Pp=I.copy()
    for l in e['lam']: Pp=Pp@(I-K2/l)
    # five-step termination, constructively: five variable-step Richardson steps from a random start
    rng=np.random.default_rng(47); b=rng.standard_normal(125); x=b.copy()
    for l in e['lam']: x=x-(K2@x)/l
    kr=np.column_stack([np.linalg.matrix_power(K2,i)@(Pc@b) for i in range(7)])
    kr_rank=int(np.linalg.matrix_rank(kr/np.linalg.norm(kr,axis=0),tol=1e-9))
    # Chebyshev: p_n(K2) = T_n((L+d-2K2)/(L-d)) / T_n((L+d)/(L-d)), p_n(0)=1
    d,L=float(e['lam'][0]),float(e['lam'][-1]); A=((L+d)*I-2*K2)/(L-d)
    cheb=[]; T0,T1=I.copy(),A.copy()
    for n in range(1,NMAX+1):
        Tn=T1 if n==1 else 2*A@T1-T0
        if n>1: T0,T1=T1,Tn
        pn=Tn/float(sp.chebyshevt(n,e['arg']))
        cheb.append(float(np.linalg.norm(pn@Pc,2)))
    return dict(spec=spec,sector=sector,inertia=inertia,kK=kK,ge_c=ge_c,
                prod_res=np.linalg.norm(Pp-P,2),rich_res=np.linalg.norm(x-P@b),kr_rank=kr_rank,cheb=cheb,
                eta_comm=np.linalg.norm(G@(2*P-I)-(2*P-I)@G,2))

def main():
    e=exact(); m=machine(e)
    R=sp.Rational
    comp=[c for c in CASIMIR if c not in KERNEL]
    # K inertia: sector signs (exact) weighted by Casimir multiplicities
    pos=sum(m['spec'][c] for c in comp if e['k'][c]>0); neg=sum(m['spec'][c] for c in comp if e['k'][c]<0)
    checks={
      'casimir_spectrum':m['spec']=={0:1,2:9,6:25,12:28,20:27,30:22,42:13},
      'K_sector_values_exact':{c:e['k'][c] for c in comp}=={0:180,2:112,12:-108,20:-140,42:432},
      'K_sector_values_machine':all(abs(m['sector'][c]-e['k'][c])<1e-8 for c in CASIMIR),
      'abs_K_set':e['absk']==[108,112,140,180,432],
      'condition_K_4':e['kappa_K']==4,'condition_K_machine':abs(m['kK']-4)<1e-10,
      'condition_K2_16':e['kappa']==16,
      'gap_108sq':e['lam'][0]==108**2==11664,'norm_16x108sq':e['lam'][-1]==16*108**2==186624,
      'eps_1_over_99144':e['eps']==R(1,99144),'99144_eq_108sq_17_over_2':R(108**2*17,2)==99144,
      'rho_15_17':e['rho']==R(15,17),'rho_from_kappa':e['rho']==(e['kappa']-1)/(e['kappa']+1),
      'equioscillation_exact':min(e['gamma'])==-R(15,17) and max(e['gamma'])==R(15,17),
      'equioscillation_machine':abs(m['ge_c'].min()+15/17)<1e-12 and abs(m['ge_c'].max()-15/17)<1e-12,
      'five_factor_scalar_identity':e['prod_zero_on_complement'] and e['prod_one_on_kernel'],
      'five_factor_projector_machine':m['prod_res']<1e-9,
      'krylov_dimension_5':m['kr_rank']==5,'five_step_richardson_exact':m['rich_res']<1e-9,
      'chebyshev_rate_3_5':e['cheb_rate']==R(3,5),
      'chebyshev_closed_form':e['cheb_closed'],'chebyshev_beats_richardson':e['cheb_beats_richardson'],
      'chebyshev_machine_bound':all(m['cheb'][n]<=float(e['cheb'][n])*(1+1e-8)+1e-10 for n in range(NMAX)),
      'K_inertia_23_55_47':(pos,neg)==(23,55) and m['inertia']==(23,55,47),
      'gamma_commutes_eta':m['eta_comm']<1e-10,
    }
    checks={k:bool(v) for k,v in checks.items()}
    cert={'schema':'MC-E47-CONDITION-LOCK/1.0','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
      'exact':{
        'evidence':'exact rational arithmetic from the Casimir values {0,2,6,12,20,30,42}',
        'K_on_sectors':{str(c):e['k'][c] for c in CASIMIR},
        'abs_K_on_complement':e['absk'],'K2_eigenvalues_on_complement':e['lam'],
        'condition_number_K':str(e['kappa_K']),'condition_number_K2':str(e['kappa']),
        'epsilon_star':str(e['eps']),'rho_star':str(e['rho']),
        'constants_from_two_integers':'11664=108^2, 186624=16*108^2, 99144=108^2*17/2, 15/17=(16-1)/(16+1)',
        'gamma_on_complement':[str(g) for g in e['gamma']],
        'five_factor_projector':'P47 = prod_{lam in {108^2,112^2,140^2,180^2,432^2}} (I - K^2/lam)',
        'chebyshev_rate':str(e['cheb_rate']),
        'chebyshev_bound':{str(n+1):str(e['cheb'][n]) for n in range(NMAX)},
        'chebyshev_closed_form':'1/T_n(17/15) = 2/((5/3)^n + (3/5)^n)',
      },
      'machine':{
        'evidence':'float64 replay on the 125x125 carrier',
        'K_inertia':{'positive':m['inertia'][0],'negative':m['inertia'][1],'zero':m['inertia'][2]},
        'condition_number_K':r(m['kK']),
        'gamma_complement_min':r(m['ge_c'].min()),'gamma_complement_max':r(m['ge_c'].max()),
        'five_factor_projector_residual':r(m['prod_res']),'five_step_richardson_residual':r(m['rich_res']),
        'krylov_dimension':m['kr_rank'],'chebyshev_norms':[r(x) for x in m['cheb']],
        'gamma_eta_commutator':r(m['eta_comm']),
      },
      'boundary':'Finite spectral statements about the fixed 125-dimensional carrier. They sharpen the existing contraction theorem (rate 15/17 at step 1/99144) and add no physical claim.'}
    OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n'); print(json.dumps(cert,indent=2,sort_keys=True))
    if cert['status']!='PASS': raise SystemExit(1)
if __name__=='__main__': main()
