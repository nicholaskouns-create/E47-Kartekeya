#!/usr/bin/env python3
"""MC-E47-SIGNATURE-SYMMETRY/1.0 — K inertia, Krein form and its isometries, and the exact
SU(2) x S3 resolution of E47 (fermion exclusion, bosonic slice, mixed core).

Exact layer: the full SU(2) x S3 multiplicity table of V2⊗V2⊗V2 is derived from
cycle-type characters chi(q)^3, chi(q^2)chi(q), chi(q^3) with chi(q)=sum_{m=-2}^{2} q^m.
Machine layer: every exact statement is replayed on the 125x125 carrier.

Sharpens certificates/e47_joint_su2_s3_fingerprint_certificate.py, which asserts the
S3 dimensions (5,0,42) numerically and states the character resolution in a comment.
"""
from __future__ import annotations
import json, os
from itertools import permutations
from pathlib import Path
import numpy as np
import sympy as sp
from scipy.linalg import expm

ROOT=Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents)>3 else Path.cwd()
OUT=(ROOT/"artifacts"/"E47_SIGNATURE_SYMMETRY_CERTIFICATE.json") if (ROOT/"artifacts").exists() else Path(__file__).with_name("E47_SIGNATURE_SYMMETRY_CERTIFICATE.json")
if os.environ.get("E47_CERT_OUT"): OUT=Path(os.environ["E47_CERT_OUT"])

SPINS=range(7)
KERNEL_SPINS={2,5}                   # c=6 and c=30
IRREPS=("trivial","sign","standard")

def r(x):
    """Residuals are recorded to 3 significant figures so regeneration is byte-stable."""
    return float(f"{float(x):.2e}")

def exact():
    q=sp.symbols('q')
    chi=lambda t: sum(t**mm for mm in range(-2,3))
    cls={'id':sp.expand(chi(q)**3),'transposition':sp.expand(chi(q**2)*chi(q)),'three_cycle':sp.expand(chi(q**3))}
    def coeff(f,mm): return int(sp.expand(f*q**20).coeff(q,mm+20))
    n={c:{j:coeff(f,j)-coeff(f,j+1) for j in SPINS} for c,f in cls.items()}   # spin-j trace per class
    table={}
    for j in SPINS:
        a,t,z=n['id'][j],n['transposition'][j],n['three_cycle'][j]
        table[j]={'trivial':sp.Rational(a+3*t+2*z,6),'sign':sp.Rational(a-3*t+2*z,6),'standard':sp.Rational(2*a-2*z,6)}
    irrep_dim={'trivial':1,'sign':1,'standard':2}
    dim=lambda js,irr: sum(table[j][irr]*irrep_dim[irr]*(2*j+1) for j in js)
    casimir_mult={j:n['id'][j] for j in SPINS}
    e47={irr:dim(KERNEL_SPINS,irr) for irr in IRREPS}
    joint={j:{irr:table[j][irr] for irr in IRREPS if table[j][irr]} for j in KERNEL_SPINS}
    commutant=sum(v**2 for j in joint for v in joint[j].values())
    sign_k={j:sp.sign((j*(j+1)-6)*(j*(j+1)-30)) for j in SPINS}
    inertia=(sum(casimir_mult[j]*(2*j+1) for j in SPINS if sign_k[j]>0),
             sum(casimir_mult[j]*(2*j+1) for j in SPINS if sign_k[j]<0),
             sum(casimir_mult[j]*(2*j+1) for j in SPINS if sign_k[j]==0))
    # Gamma* = I - K^2/99144 acts on spin j by g_j; Gamma*^T eta Gamma* - eta = eta (Gamma*^2 - I)
    g={j:1-sp.Rational(((j*(j+1)-6)*(j*(j+1)-30))**2,99144) for j in SPINS}
    krein_defect=max(abs(1-g[j]**2) for j in SPINS)
    defect_spin=[j for j in SPINS if abs(1-g[j]**2)==krein_defect]
    return dict(table=table,casimir_mult=casimir_mult,e47=e47,joint=joint,commutant=commutant,inertia=inertia,
                g=g,krein_defect=krein_defect,defect_spin=defect_spin,
                sym=[j for j in SPINS if table[j]['trivial']],alt=[j for j in SPINS if table[j]['sign']],
                sym_dim=dim(SPINS,'trivial'),alt_dim=dim(SPINS,'sign'),
                integral=all(v.is_integer and v>=0 for row in table.values() for v in row.values()),
                total=sum(dim(SPINS,irr) for irr in IRREPS))

def carrier():
    j=2.0; m=np.arange(j,-j-1,-1); Jz=np.diag(m).astype(complex); Jp=np.zeros((5,5),complex)
    for i,mi in enumerate(m[:-1]): Jp[i,i+1]=np.sqrt(j*(j+1)-mi*(mi-1))
    Jx=.5*(Jp+Jp.conj().T); Jy=-.5j*(Jp-Jp.conj().T); I5=np.eye(5)
    def tot(A): return np.kron(np.kron(A,I5),I5)+np.kron(np.kron(I5,A),I5)+np.kron(np.kron(I5,I5),A)
    J=[tot(Jx),tot(Jy),tot(Jz)]; I=np.eye(125)
    C=sum(A@A for A in J); C=((C+C.conj().T)/2).real
    K=(C-6*I)@(C-30*I)
    ev,V=np.linalg.eigh(C); Q=V[:,np.isclose(ev,6,atol=1e-8)|np.isclose(ev,30,atol=1e-8)]
    B=[(a,b,c) for a in range(5) for b in range(5) for c in range(5)]; ix={x:i for i,x in enumerate(B)}
    def perm(p):
        M=np.zeros((125,125))
        for i,x in enumerate(B): M[ix[tuple(x[p[k]] for k in range(3))],i]=1
        return M
    ps=list(permutations(range(3))); S={p:perm(p) for p in ps}
    sgn={p:(-1 if sum(p[a]>p[b] for a in range(3) for b in range(a+1,3))%2 else 1) for p in ps}
    return J,C,K,Q@Q.T,S,sgn,I

def machine():
    J,C,K,P,S,sgn,I=carrier()
    Ps=sum(S.values())/6; Pa=sum(sgn[p]*S[p] for p in S)/6; Pm=I-Ps-Pa
    tr=lambda A: int(round(np.trace(A).real))
    dims=(tr(P@Ps),tr(P@Pa),tr(P@Pm))
    fp=tuple(tr(P@S[p]) for p in ((0,1,2),(1,0,2),(1,2,0)))
    # bosonic slice: range of P Ps is one spin-2 irrep
    w,V=np.linalg.eigh(P@Ps@P); Bs=V[:,w>.5]
    cas_slice=np.linalg.eigvalsh(Bs.T@C@Bs)
    # Krein form. Commuting with eta makes a Hermitian operator eta-self-adjoint and
    # reduces E47 + E47^perp; only unitaries that commute with eta are isometries.
    eta=2*P-I; G=I-K@K/99144
    ev_eta=np.linalg.eigvalsh(eta)
    esa=lambda A: np.linalg.norm(A.conj().T@eta-eta@A,2)
    eta_sa_ops=max([esa(A) for A in J]+[esa(C),esa(K),esa(G)])
    reduces=max(np.linalg.norm(P@A@(I-P),2) for A in J+[C,K,G])
    rng=np.random.default_rng(47); rot=[]
    for _ in range(4):
        n=rng.standard_normal(3); n/=np.linalg.norm(n); th=rng.uniform(0,2*np.pi)
        rot.append(expm(-1j*th*(n[0]*J[0]+n[1]*J[1]+n[2]*J[2])))
    iso=lambda U: np.linalg.norm(U.conj().T@eta@U-eta,2)
    rot_unitary=max(np.linalg.norm(U.conj().T@U-I,2) for U in rot)
    rot_iso=max(iso(U) for U in rot); perm_iso=max(iso(M) for M in S.values())
    gamma_identity=np.linalg.norm(G.T@eta@G-eta@G@G,2)
    gamma_defect=iso(G); gamma_fix=np.linalg.norm(G@P-P,2)
    ke=np.linalg.eigvalsh(K)
    # eta-positive definite on E47, eta-negative definite on its complement
    Qp=np.linalg.eigh(P)[1][:,-47:]; Qn=np.linalg.eigh(I-P)[1][:,-78:]
    return dict(dims=dims,fp=fp,slice_dim=Bs.shape[1],cas_slice=cas_slice,
                eta_inv=np.linalg.norm(eta@eta-I,2),eta_sa=np.linalg.norm(eta-eta.T,2),
                eta_sig=(int((ev_eta>.5).sum()),int((ev_eta<-.5).sum())),eta_sa_ops=eta_sa_ops,reduces=reduces,
                rot_unitary=rot_unitary,rot_iso=rot_iso,perm_iso=perm_iso,gamma_identity=gamma_identity,
                gamma_defect=gamma_defect,gamma_fix=gamma_fix,
                eta_pos=np.linalg.eigvalsh(Qp.T@eta@Qp).min(),eta_neg=np.linalg.eigvalsh(Qn.T@eta@Qn).max(),
                inertia=(int((ke>.5).sum()),int((ke<-.5).sum()),int((abs(ke)<.5).sum())),
                sym_trace=tr(Ps),alt_trace=tr(Pa))

def main():
    e=exact(); m=machine()
    T=e['table']
    checks={
      'character_table_integral':e['integral'],
      'character_total_125':e['total']==125,
      'casimir_multiplicities':e['casimir_mult']=={0:1,1:3,2:5,3:4,4:3,5:2,6:1},
      'su2_s3_table':{j:tuple(int(T[j][i]) for i in IRREPS) for j in SPINS}=={0:(1,0,0),1:(0,1,1),2:(1,0,2),3:(1,1,1),4:(1,0,1),5:(0,0,1),6:(1,0,0)},
      'sym3_is_V0_V2_V3_V4_V6':e['sym']==[0,2,3,4,6] and e['sym_dim']==35,
      'alt3_is_V1_V3':e['alt']==[1,3] and e['alt_dim']==10,
      'fermion_exclusion_exact':e['e47']['sign']==0,
      'fermion_exclusion_machine':m['dims'][1]==0,
      'bosonic_slice_exact':e['joint'][2].get('trivial')==1 and 'trivial' not in e['joint'][5] and e['e47']['trivial']==5,
      'bosonic_slice_machine':m['dims'][0]==5 and m['slice_dim']==5 and np.allclose(m['cas_slice'],6,atol=1e-9),
      'mixed_core_exact':e['e47']['standard']==42,
      'mixed_core_machine':m['dims'][2]==42,
      'trace_fingerprint_47_5_m16':m['fp']==(47,5,-16),
      'joint_commutant_C_M2_C':e['joint']=={2:{'trivial':1,'standard':2},5:{'standard':1}} and e['commutant']==6,
      'sym_alt_traces':m['sym_trace']==35 and m['alt_trace']==10,
      'K_inertia_exact_23_55_47':e['inertia']==(23,55,47),
      'K_inertia_machine':m['inertia']==(23,55,47),
      'eta_involution':m['eta_inv']<1e-10 and m['eta_sa']<1e-10,
      'eta_signature_47_78':m['eta_sig']==(47,78),
      'eta_definite_split':m['eta_pos']>1-1e-10 and m['eta_neg']<-1+1e-10,
      'eta_selfadjoint_J_C_K_Gamma':m['eta_sa_ops']<1e-9,
      'J_C_K_Gamma_reduce_E47_split':m['reduces']<1e-9,
      'krein_isometry_su2_rotations':m['rot_unitary']<1e-10 and m['rot_iso']<1e-9,
      'krein_isometry_s3_permutations':m['perm_iso']<1e-12,
      'gamma_identity_on_E47':m['gamma_fix']<1e-9,
      'gamma_krein_identity_eta_gamma2':m['gamma_identity']<1e-10,
      'gamma_not_krein_isometry_exact':e['krein_defect']==sp.Rational(12800,23409) and e['defect_spin']==[0],
      'gamma_not_krein_isometry_machine':abs(m['gamma_defect']-12800/23409)<1e-10,
    }
    checks={k:bool(v) for k,v in checks.items()}
    cert={'schema':'MC-E47-SIGNATURE-SYMMETRY/1.0','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
      'exact':{
        'evidence':'exact character arithmetic: chi(q)^3, chi(q^2)chi(q), chi(q^3), chi(q)=q^-2+...+q^2',
        'su2_s3_multiplicities':{str(j):{i:int(T[j][i]) for i in IRREPS} for j in SPINS},
        'sym3_V2':'V0 + V2 + V3 + V4 + V6 (dim 35)','alt3_V2':'V1 + V3 (dim 10)',
        'e47_resolution':'(trivial x V2) + 2(standard x V2) + (standard x V5)',
        'e47_s3_dimensions':{i:int(e['e47'][i]) for i in IRREPS},
        'joint_commutant':'C + M_2(C) + C, dimension 6',
        'K_inertia':{'positive':e['inertia'][0],'negative':e['inertia'][1],'zero':e['inertia'][2],
                     'positive_spins':[0,1,6],'negative_spins':[3,4]},
        'krein_isometries':'U^dagger eta U = eta for SU(2) rotations and S3 permutations (unitary and commuting with eta)',
        'gamma_krein_relation':'Gamma*^dagger eta Gamma* = eta Gamma*^2 != eta',
        'gamma_krein_defect':str(e['krein_defect']),
        'gamma_krein_defect_origin':'1-(103/153)^2 on the spin-0 sector, where Gamma* = 103/153',
      },
      'machine':{
        'evidence':'float64 replay on the 125x125 carrier',
        'e47_s3_dimensions':dict(zip(IRREPS,m['dims'])),'trace_fingerprint':list(m['fp']),
        'bosonic_slice_casimir':r(float(np.mean(m['cas_slice']))),
        'eta_signature':{'positive':m['eta_sig'][0],'negative':m['eta_sig'][1]},
        'eta_involution_residual':r(m['eta_inv']),'eta_selfadjoint_residual':r(m['eta_sa_ops']),
        'krein_isometry_residual_rotations':r(m['rot_iso']),'krein_isometry_residual_permutations':r(m['perm_iso']),
        'gamma_krein_defect':r(m['gamma_defect']),
        'K_inertia':{'positive':m['inertia'][0],'negative':m['inertia'][1],'zero':m['inertia'][2]},
      },
      'boundary':'Finite representation-theoretic statements about the fixed 125-dimensional carrier. The Krein structure is the indefinite form eta = 2P - I. Its isometries here are the unitary symmetries (SU(2) rotations, S3 permutations); J_a, C, K and Gamma* are eta-self-adjoint and preserve E47 and its complement, but are not isometries. No physical interpretation is claimed.'}
    OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n'); print(json.dumps(cert,indent=2,sort_keys=True))
    if cert['status']!='PASS': raise SystemExit(1)
if __name__=='__main__': main()
