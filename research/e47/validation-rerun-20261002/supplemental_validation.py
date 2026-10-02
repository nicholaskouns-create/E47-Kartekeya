"""Independent reconstruction of Drive equations; not an original-source rerun.
Sources: Hodge–E47 Tensor-Kernel Theorem; Deterministic Hodge–de Rham
Swarm Safety Identities; Higher-Dimensional Newton-Mean Iterations.
"""
import numpy as np, sympy as sp, json, pathlib, runpy, contextlib, io
from scipy.linalg import expm
out=pathlib.Path(__file__).resolve().parent
with contextlib.redirect_stdout(io.StringIO()):
 core=runpy.run_path(str(out/'spectral_core_source.py'))
K2,P=core['K2'],core['P']; results=[]
def ck(family,name,ok,value=None):
 results.append(dict(family=family,name=name,passed=bool(ok),value=value))
 print('PASS' if ok else 'FAIL',family,name,value)
def near(family,name,res,tol=1e-9): ck(family,name,res<tol,float(res))
# Boundary matrices from an oriented three-edge cycle, then its filled triangle.
B=np.array([[-1,0,-1],[1,-1,0],[0,1,1]],float)
face=np.array([[1],[1],[-1]],float)
near('Hodge','boundary_squared',np.linalg.norm(B@face))
for name,F,beta in [('cycle',np.zeros((3,0)),1),('filled_triangle',face,0)]:
 L=B.T@B+F@F.T
 w,U=np.linalg.eigh(L); H=U[:,abs(w)<1e-9]@U[:,abs(w)<1e-9].T
 ck('Hodge',name+'_betti',sum(abs(w)<1e-9)==beta,int(sum(abs(w)<1e-9)))
 D=np.kron(L,np.eye(125))+np.kron(np.eye(3),K2)
 v,V=np.linalg.eigh(D); Q=V[:,abs(v)<1e-7]@V[:,abs(v)<1e-7].conj().T
 target=np.kron(H,P)
 ck('Hodge',name+'_tensor_kernel_rank',sum(abs(v)<1e-7)==47*beta,int(sum(abs(v)<1e-7)))
 near('Hodge',name+'_projector_factorization',np.linalg.norm(Q-target,2))
 near('Hodge',name+'_annihilation',np.linalg.norm(D@target,2),1e-7)
 near('Hodge',name+'_semigroup_factorization',np.linalg.norm(expm(-.001*D)-np.kron(expm(-.001*L),expm(-.001*K2)),2))
 near('Hodge',name+'_long_time_limit',np.linalg.norm(expm(-10*D)-target,2),1e-8)
# Exact fixed-point elimination and Jacobian identities.
r,s,k=sp.symbols('r s k',positive=True)
a,b=r*r-k*r*s,s*s-k*r*s
near_expr=sp.simplify((1-k*k)*(r*s)**2-k*(a+b)*r*s-a*b)
ck('Newton','product_quadratic_symbolic',near_expr==0,str(near_expr))
J=sp.Matrix([[1-a/r**2,k],[k,1-b/s**2]])/2
ck('Newton','jacobian_determinant_symbolic',sp.simplify(J.det())==0)
ck('Newton','jacobian_trace_symbolic',sp.simplify(sp.trace(J)-(k*(a+b)/(2*r*s)+k*k))==0)
rng=np.random.default_rng(47); maxfix=maxdiff=maxeig=0.; disagreements=0
for _ in range(2000):
 aa,bb=np.exp(rng.uniform(-2,2,2)); kk=rng.uniform(-.99,.99)
 p=(kk*(aa+bb)+np.sqrt(kk*kk*(aa-bb)**2+4*aa*bb))/(2*(1-kk*kk))
 rr,ss=np.sqrt(aa+kk*p),np.sqrt(bb+kk*p)
 T=np.array([rr+aa/rr+kk*ss,ss+bb/ss+kk*rr])/2
 maxfix=max(maxfix,np.linalg.norm(T-[rr,ss]))
 maxdiff=max(maxdiff,abs(rr*rr-ss*ss-aa+bb))
 jac=np.array([[1-aa/rr**2,kk],[kk,1-bb/ss**2]])/2
 tau=kk*(aa+bb)/(2*p)+kk*kk
 maxeig=max(maxeig,np.max(np.abs(np.sort(np.linalg.eigvalsh(jac))-np.sort([0,tau]))))
 A=(aa-bb)**2; Bc=3*aa*aa-2*aa*bb+3*bb*bb
 z=8*aa*bb/(Bc+np.sqrt(Bc*Bc+16*A*aa*bb)); kc=np.sqrt(z)
 disagreements+=bool(abs(tau)<1)!=bool(-kc<kk<1)
near('Newton','2000_fixed_points',maxfix)
near('Newton','2000_difference_invariants',maxdiff)
near('Newton','2000_jacobian_spectra',maxeig)
ck('Newton','2000_stability_classifications',disagreements==0,disagreements)
# Swarm: stated fifty-percent reserve and exact affine recurrence witness.
pers,threshold,vmax,Tmix,alpha,dt=2.5,.5,4.,.04,1.7,.05
full=(pers-threshold)/(2*vmax); reserved=full/2; speed=(pers-threshold)/(4*Tmix)
ck('Swarm','reserved_dwell',reserved==.125,reserved)
ck('Swarm','certified_speed',speed==12.5,speed)
ck('Swarm','mixing_within_dwell',Tmix<reserved)
times=np.arange(21)*dt; safety=np.diag([0.,1.,2.]); v0=np.array([2.,3.,4.]); anchor=np.array([1.,0.,0.])
res=max(np.linalg.norm(safety@(np.exp(-alpha*t)*v0+(1-np.exp(-alpha*t))*anchor)-np.exp(-alpha*t)*safety@v0) for t in times)
near('Swarm','fallback_exponential_identity',res)
safe0=np.array([4.,0.,0.]); near('Swarm','fallback_kernel_invariance',max(np.linalg.norm(safety@(np.exp(-alpha*t)*safe0+(1-np.exp(-alpha*t))*anchor)) for t in times))
aa=rng.uniform(.2,.95,20); bb=rng.uniform(0,.1,20); e=.7
for av,bv in zip(aa,bb): e=av*e+bv
unroll=np.prod(aa)*.7+sum(bb[j]*np.prod(aa[j+1:]) for j in range(20))
near('Swarm','nonautonomous_unrolling',abs(e-unroll))
# Matched persistence endpoints moving within the assumed Lipschitz bound.
birth,death=0.,pers; h=.1; birth2=birth+vmax*h; death2=death-vmax*h
ck('Swarm','matched_endpoint_drift_bound',abs((death2-birth2)-(death-birth))<=2*vmax*h+1e-14)
record={'mode':'independent reconstruction of stated identities','checks':results,'passed':sum(x['passed'] for x in results),'total':len(results),'limitations':'Hodge: cycle and filled-triangle witnesses. Swarm: algebraic witnesses under stated assumptions, not trajectory-level topology preservation.'}
(out/'supplemental_results.json').write_text(json.dumps(record,indent=2))
print(f"TOTAL {record['passed']}/{record['total']} PASS")
assert all(x['passed'] for x in results)
