#!/usr/bin/env python3
"""
E47 First-Principles Proof
Spectral Selection, Projector, and Recursive Contraction from the Spin-2 Carrier

Primary framework: Nicholas Shane Kouns
Certificate: MC-E47-SPECTRAL-EXPLICATION-20261001-001

This certificate derives the finite-dimensional E47 core from the spin-2
generators. The optional "implicit -> explicit" language is interpretive;
the executable theorem is the spectral construction below.
"""
import json, math, numpy as np

TOL=1e-10
checks={}
def check(name, condition, value=None):
    checks[name]={"pass":bool(condition),"value":value}
    assert condition, f"FAIL: {name}: {value}"

# 1. Spin-2 irrep
j=2
m=np.array([2,1,0,-1,-2.],dtype=float)
Jz=np.diag(m).astype(complex)
Jp=np.zeros((5,5),dtype=complex)
for col,mc in enumerate(m):
    row=np.where(np.isclose(m,mc+1))[0]
    if len(row):
        Jp[row[0],col]=math.sqrt(j*(j+1)-mc*(mc+1))
Jm=Jp.conj().T
Jx=(Jp+Jm)/2
Jy=(Jp-Jm)/(2j)
I5=np.eye(5,dtype=complex)
comm=[
    np.linalg.norm(Jx@Jy-Jy@Jx-1j*Jz,2),
    np.linalg.norm(Jy@Jz-Jz@Jy-1j*Jx,2),
    np.linalg.norm(Jz@Jx-Jx@Jz-1j*Jy,2),
]
check("spin2_su2_commutators",max(comm)<TOL,comm)
check("spin2_casimir",np.linalg.norm(Jx@Jx+Jy@Jy+Jz@Jz-6*I5,2)<TOL)

# 2. Triple carrier and total Casimir
k3=lambda A,B,C: np.kron(np.kron(A,B),C)
Jtot=[k3(A,I5,I5)+k3(I5,A,I5)+k3(I5,I5,A) for A in (Jx,Jy,Jz)]
I=np.eye(125,dtype=complex)
C=sum(A@A for A in Jtot)
check("carrier_dimension",C.shape==(125,125),C.shape)
check("C_hermitian",np.linalg.norm(C-C.conj().T,2)<TOL)

w,U=np.linalg.eigh(C)
eigs=[0,2,6,12,20,30,42]
expected=[1,9,25,28,27,22,13]
mult=[int(np.sum(np.isclose(w,x,atol=1e-9))) for x in eigs]
check("casimir_spectrum_multiplicities",mult==expected,dict(zip(eigs,mult)))
check("multiplicity_sum",sum(mult)==125,sum(mult))

# 3. E47 selector and orthogonal projector
K=(C-6*I)@(C-30*I)
K2=K@K
mask=np.isclose(w,6,atol=1e-9)|np.isclose(w,30,atol=1e-9)
P=U[:,mask]@U[:,mask].conj().T
rank=int(np.linalg.matrix_rank(P,tol=1e-9))
check("E47_rank",rank==47,rank)
check("P_idempotent",np.linalg.norm(P@P-P,2)<TOL,float(np.linalg.norm(P@P-P,2)))
check("P_hermitian",np.linalg.norm(P-P.conj().T,2)<TOL)
check("KP_zero",np.linalg.norm(K@P,2)<1e-8,float(np.linalg.norm(K@P,2)))
check("Omega_c",abs(np.trace(P).real/125-47/125)<1e-12,float(np.trace(P).real/125))

# 4. K^2 spectrum and contraction
kw=np.linalg.eigvalsh((K2+K2.conj().T)/2)
positive=sorted({int(round(x)) for x in kw if x>1e-7})
expected_positive=[11664,12544,19600,32400,186624]
check("K2_positive_spectrum",positive==expected_positive,positive)
Delta,M=min(positive),max(positive)
eps=2/(Delta+M)
check("epsilon_star",abs(eps-1/99144)<1e-18,eps)
Gamma=I-eps*K2
gw=np.linalg.eigvalsh((Gamma+Gamma.conj().T)/2)
comp=gw[~np.isclose(gw,1,atol=1e-9)]
rho=float(np.max(np.abs(comp)))
check("rho_star",abs(rho-15/17)<1e-12,rho)
check("Gamma_fixes_E47",np.linalg.norm(Gamma@P-P,2)<1e-8)

# 5. Explicit convergence and state decomposition
G220=np.linalg.matrix_power(Gamma,220)
err220=float(np.linalg.norm(G220-P,2))
check("Gamma220_to_P",err220<2e-12,err220)
rng=np.random.default_rng(47)
psi=rng.normal(size=125)+1j*rng.normal(size=125)
psi/=np.linalg.norm(psi)
psiP=P@psi
psiQ=(I-P)@psi
check("state_decomposition",np.linalg.norm(psi-(psiP+psiQ))<TOL)
check("preserved_component",np.linalg.norm(G220@psiP-psiP)<1e-8)
check("contracted_component",np.linalg.norm(G220@psiQ)<2e-12)

result={
 "title":"E47 First-Principles Proof: Spectral Selection, Projector, and Recursive Contraction",
 "certificate":"MC-E47-SPECTRAL-EXPLICATION-20261001-001",
 "evidence_class":"E0/E1",
 "carrier_dimension":125,
 "casimir_spectrum":eigs,
 "multiplicities":mult,
 "E47_dimension":rank,
 "Omega_c":47/125,
 "K2_positive_spectrum":positive,
 "epsilon_star":eps,
 "rho_star":rho,
 "Gamma220_projector_spectral_norm":err220,
 "checks":checks,
 "status":"PASS",
 "scope":"Finite-dimensional spectral theorem only. Bohmian implicate/explicate language is an interpretive analogy, not used in the proof."
}
print(json.dumps(result,indent=2))
print(f"\n{sum(v['pass'] for v in checks.values())}/{len(checks)} CHECKS PASS")
