#!/usr/bin/env python3
"""Quadratic Golden-Root Convergence and Optimal E47 Spectral Projection.
Run: python validate_convergence.py --output results.json
Dependency: numpy. Exact arithmetic: fractions; scalar arithmetic: Decimal(100).
Numerical validation accompanies the analytic proof; finite samples do not prove
universal scalar convergence. The scalar and spectral constructions are distinct.
"""
import argparse
import hashlib
import json
import platform
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import numpy as np

TITLE = 'Quadratic Golden-Root Convergence and Optimal E47 Spectral Projection'
checks = []

def check(name, passed, residual=None, tolerance=None, evidence='numerical'):
    checks.append(dict(name=name, passed=bool(passed), residual=residual,
                       tolerance=tolerance, evidence=evidence))

def near(name, actual, expected=0, tol=1e-10):
    r = float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))
    check(name, r <= tol, r, tol)

# Exact bivariate polynomial arithmetic in x,a (no symbolic dependency).
def add(p, q):
    r = p.copy()
    for k,v in q.items(): r[k] = r.get(k, F(0)) + v
    return {k:v for k,v in r.items() if v}
def scale(p, c): return {k:v*c for k,v in p.items() if v*c}
def mul(p, q):
    r = {}
    for (i,j),v in p.items():
        for (k,l),w in q.items(): r[(i+k,j+l)] = r.get((i+k,j+l), F(0)) + v*w
    return {k:v for k,v in r.items() if v}
def sub(p,q): return add(p,scale(q,-1))
x,a = {(1,0):F(1)}, {(0,1):F(1)}
x2,a2 = mul(x,x),mul(a,a)
num = add(x2,a2)  # numerator of B = (x^2+a^2)/(2x)
check('Exact Newton update, cleared denominators', sub(scale(x2,2),sub(x2,a2)) == num, evidence='exact polynomial')
check('Exact error identity 2x(B-a)=(x-a)^2', sub(num,scale(mul(x,a),2)) == mul(sub(x,a),sub(x,a)), evidence='exact polynomial')
check('Exact monotonicity identity 2x(B-x)=a^2-x^2', sub(num,scale(x2,2)) == sub(a2,x2), evidence='exact polynomial')
check('Exact q conjugacy, cleared denominators',
      mul(sub(num,scale(mul(x,a),2)),mul(add(x,a),add(x,a))) ==
      mul(add(num,scale(mul(x,a),2)),mul(sub(x,a),sub(x,a))), evidence='exact polynomial')
# Q(sqrt(5)): r+t sqrt(5), including negative powers via inversion.
def qm(z,w): return (z[0]*w[0]+5*z[1]*w[1],z[0]*w[1]+z[1]*w[0])
phi_exact=(F(1,2),F(1,2)); inv_phi=(F(-1,2),F(1,2))
s_exact=(F(1),F(0))
for _ in range(5): s_exact=qm(s_exact,inv_phi)
check('Exact phi^-5=(5sqrt(5)-11)/2', s_exact==(F(-11,2),F(5,2)), evidence='exact algebraic')
check('Exact phi^2=phi+1', qm(phi_exact,phi_exact)==(F(3,2),F(1,2)), evidence='exact algebraic')

with localcontext() as ctx:
    ctx.prec=100
    D=Decimal
    phi=(1+D(5).sqrt())/2; s=phi**(-5); root=s.sqrt()
    check('Golden seed numerical identity',abs(s-(5*phi-8))<D('1e-95'),str(abs(s-(5*phi-8))),'1e-95')
    scalar_rows=[]; worst_closed=D(0); worst_error=D(0); worst_q=D(0)
    starts=['1e-12','0.001','0.1',str(root),'0.5','1','2','100','1e12']
    for start in starts:
        z=D(start); q0=(z-root)/(z+root); converged=False; monotone=True
        for n in range(160):
            q=(z-root)/(z+root)
            if n<=8:  # restrict to well-resolved closed-form comparison
                qpow=q0**(2**n)
                closed=root*(1+qpow)/(1-qpow)
                worst_closed=max(worst_closed,abs(closed-z)/max(1,abs(z)))
            nxt=(z+s/z)/2
            worst_error=max(worst_error,abs((nxt-root)-(z-root)**2/(2*z))/max(1,abs(nxt)))
            worst_q=max(worst_q,abs((nxt-root)/(nxt+root)-q*q))
            if n>=1: monotone &= nxt >= root-D('1e-95') and nxt <= z+D('1e-95')
            z=nxt
            if abs(z-root)<D('1e-80'):
                converged=True; break
        scalar_rows.append(dict(x0=start,iterations=n+1,absolute_error=str(abs(z-root))))
        check('Scalar convergence and monotonicity: '+start,converged and monotone,str(abs(z-root)),'1e-80')
    check('Closed scalar solution vs direct iteration',worst_closed<D('1e-75'),str(worst_closed),'1e-75')
    check('Scalar error recurrence',worst_error<D('1e-85'),str(worst_error),'1e-85')
    check('Scalar q_(n+1)=q_n^2',worst_q<D('1e-85'),str(worst_q),'1e-85')
    # Error coefficient approaches 1/(2a), without dividing rounded errors.
    offset=D('1e-40'); coefficient=1/(2*(root+offset)); limit=1/(2*root)
    check('Quadratic asymptotic coefficient',abs(coefficient-limit)<D('1e-38'),str(abs(coefficient-limit)),'1e-38')
    constants=dict(phi=str(phi),s=str(s),golden_root=str(root),quadratic_coefficient=str(limit))

# Construct spin-2 generators, rather than supplying a precomputed Casimir.
m=np.arange(2,-3,-1,dtype=float)
Jz=np.diag(m).astype(complex); Jp=np.zeros((5,5),complex)
for i in range(4): Jp[i,i+1]=np.sqrt(6-m[i+1]*(m[i+1]+1))
Jx=(Jp+Jp.conj().T)/2; Jy=(Jp-Jp.conj().T)/(2j)
I5=np.eye(5); I=np.eye(125)
kron3=lambda u,v,w: np.kron(np.kron(u,v),w)
J=[kron3(t,I5,I5)+kron3(I5,t,I5)+kron3(I5,I5,t) for t in (Jx,Jy,Jz)]
near('Local spin-2 Casimir',Jx@Jx+Jy@Jy+Jz@Jz,6*I5)
for k in range(3): near('Total su(2) commutator '+str(k),J[k]@J[(k+1)%3]-J[(k+1)%3]@J[k],1j*J[(k+2)%3])
C=sum(t@t for t in J); near('Casimir Hermiticity',C,C.conj().T)
w,U=np.linalg.eigh(C)
expected_c={0:1,2:9,6:25,12:28,20:27,30:22,42:13}
near('Casimir eigenvalues',w,np.repeat(list(expected_c),list(expected_c.values())))
# Independent integer Clebsch-Gordan multiplicity construction.
mult=Counter({2:1})
for _ in range(2):
    nxt=Counter()
    for j,copies in mult.items():
        for ell in range(abs(j-2),j+3): nxt[ell]+=copies
    mult=nxt
check('Exact tensor multiplicities',dict(sorted(mult.items()))=={0:1,1:3,2:5,3:4,4:3,5:2,6:1},evidence='exact integer')
check('Exact carrier dimension',sum((2*j+1)*v for j,v in mult.items())==125,evidence='exact integer')
K=(C-6*I)@(C-30*I); A=K.conj().T@K
near('K Hermiticity',K,K.conj().T)
near('K^dagger K=K^2',A,K@K,tol=1e-8)
aw=np.linalg.eigvalsh(A)
expected_a=sorted([((c-6)*(c-30))**2 for c,count in expected_c.items() for _ in range(count)])
near('Full A spectrum with multiplicities',aw,expected_a,tol=1e-7)
check('A positive semidefinite to roundoff',float(aw.min())>=-1e-7,float(aw.min()),1e-7)
mask=(abs(w-6)<1e-8)|(abs(w-30)<1e-8)
P=U[:,mask]@U[:,mask].conj().T
check('Rank P=47',int(mask.sum())==47,int(mask.sum()),evidence='spectral rank')
check('Nullity K=nullity A=47',np.count_nonzero(abs(np.linalg.eigvalsh(K))<1e-7)==47 and np.count_nonzero(abs(aw)<1e-7)==47,evidence='spectral rank')
near('P idempotent',P@P,P)
near('P Hermitian',P,P.conj().T)
near('AP=0',A@P,tol=1e-7)
# Separate projector construction: exact Lagrange polynomial evaluated on C.
Ppoly=np.zeros_like(C)
for target in (6,30):
    part=I.astype(complex)
    for other in expected_c:
        if other!=target: part=part@(C-other*I)/(target-other)
    Ppoly+=part
near('Polynomial projector vs eigenspace projector',Ppoly,P,tol=1e-10)
lo,hi=11664,186624
eps=F(2,lo+hi); q=F(hi-lo,hi+lo)
check('Exact optimal step',eps==F(1,99144),evidence='exact rational')
check('Exact optimal minimax contraction',q==F(15,17),evidence='exact rational')
check('Exact balanced spectral endpoints',1-eps*lo==q and 1-eps*hi==-q,evidence='exact rational')
check('Exact coherence fraction',F(int(mask.sum()),125)==F(47,125),evidence='exact rational')
positive=sorted(set(expected_a)-{0})
check('Exact contraction over positive spectrum',all(abs(1-eps*t)<=q<1 for t in positive),evidence='exact rational')
G=I-float(eps)*A
near('Gamma P=P',G@P,P)
rng=np.random.default_rng(470125)
v=rng.normal(size=125)+1j*rng.normal(size=125); v/=np.linalg.norm(v)
near('Quadratic form identity',np.vdot(v,A@v),np.vdot(K@v,K@v),tol=1e-8)
rows=[]
for n in (0,1,2,10,50,100,220):
    Gn=np.linalg.matrix_power(G,n)
    measured=float(np.linalg.norm(Gn-P,2)); target=float(q)**n
    check('Operator norm equality n='+str(n),abs(measured-target)<1e-10,abs(measured-target),1e-10)
    vn=Gn@v; error=float(np.linalg.norm(vn-P@v)); bound=target*float(np.linalg.norm((I-P)@v))
    check('Vector contraction bound n='+str(n),error<=bound+1e-10,max(0,error-bound),1e-10)
    near('Kernel component invariant n='+str(n),P@vn,P@v)
    rows.append(dict(n=n,operator_error=measured,theoretical_operator_error=target,vector_error=error,vector_bound=bound))

report=dict(title=TITLE,passed=sum(t['passed'] for t in checks),total=len(checks),
            environment=dict(python=platform.python_version(),numpy=np.__version__,scalar_precision=100,matrix_dtype='complex128',seed=470125),
            conventions=dict(matrix_identity_residual='maximum absolute entry unless explicitly operator norm',operator_norm='spectral 2-norm',rank_tolerance=1e-7),
            constants=constants,casimir_multiplicities=expected_c,tensor_multiplicities=dict(sorted(mult.items())),
            A_spectrum_multiplicities=dict(sorted(Counter(expected_a).items())),scalar_runs=scalar_rows,
            matrix_power_runs=rows,checks=checks,
            interpretation='Exact arithmetic verifies algebraic identities and constants. Numerical checks reconstruct the operators and validate finite iterations. Universal limits follow from the accompanying analytic identities and spectral theorem. The two mechanisms have distinct fixed objects and convergence rates; no identification of phi^(-5/2) with 47/125 is made.',
            source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
parser=argparse.ArgumentParser(); parser.add_argument('--output',default='results.json'); args=parser.parse_args()
Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
print(TITLE)
print(f"PASS {report['passed']}/{report['total']}")
print(json.dumps(dict(constants=constants,matrix_power_runs=rows),indent=2))
for t in checks:
    if not t['passed']: print('FAILED:',t)
raise SystemExit(0 if report['passed']==report['total'] else 1)
