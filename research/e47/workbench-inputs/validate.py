import numpy as np, json
from pathlib import Path
out=Path(__file__).resolve().parent
j=2; m=np.arange(j,-j-1,-1); z=np.diag(m.astype(float)); plus=np.zeros((5,5),complex)
for i,mi in enumerate(m):
 if i>0: plus[i-1,i]=np.sqrt((j-mi)*(j+mi+1))
x=(plus+plus.conj().T)/2;y=(plus-plus.conj().T)/(2j); eye=np.eye(5)
def lift(a):return sum((np.kron(np.kron(a if k==0 else eye,a if k==1 else eye),a if k==2 else eye) for k in []),np.zeros((125,125)))
def total(a):return np.kron(np.kron(a,eye),eye)+np.kron(np.kron(eye,a),eye)+np.kron(np.kron(eye,eye),a)
X,Y,Z=map(total,(x,y,z));C=X@X+Y@Y+Z@Z;I=np.eye(125);K=(C-6*I)@(C-30*I);K2=K@K
lam,U=np.linalg.eigh(C); mask=np.abs(lam-6)<1e-7; mask|=np.abs(lam-30)<1e-7;P=(U[:,mask]@U[:,mask].conj().T);G=I-K2/99144
rng=np.random.default_rng(47);v=rng.normal(size=125)+1j*rng.normal(size=125);v/=np.linalg.norm(v);target=P@v
records=[];cur=v.copy()
for n in range(221):
 if n in [0,1,5,10,20,50,100,220]:records.append(dict(n=n,error=float(np.linalg.norm(cur-target)),bound=float((15/17)**n*np.linalg.norm(v-target)),kernel_weight=float(np.linalg.norm(P@cur)**2)))
 cur=G@cur
counts=[int(np.count_nonzero(abs(lam-q)<1e-7)) for q in [0,2,6,12,20,30,42]]
res=dict(counts=counts,rankK=int(np.linalg.matrix_rank(K,tol=1e-6)),rankP=int(np.linalg.matrix_rank(P,tol=1e-7)),traceP=float(np.trace(P).real),hermiticityC=float(np.linalg.norm(C-C.conj().T,2)),casimir_commutator=float(max(np.linalg.norm(C@a-a@C,2) for a in (X,Y,Z))),projector_idempotence=float(np.linalg.norm(P@P-P,2)),KP=float(np.linalg.norm(K@P,2)),projector_polynomial=float(np.linalg.norm(P-(C@(C-2*I)@(C-12*I)@(C-20*I)@(C-31*I)@(C-42*I))/1814400,2)),spectral_rho=float(max(abs(np.linalg.eigvalsh(G-P)))),seed=47,records=records)
assert counts==[1,9,25,28,27,22,13] and res['rankK']==78 and res['rankP']==47
assert res['projector_idempotence']<1e-10 and res['projector_polynomial']<1e-8
assert abs(res['spectral_rho']-15/17)<1e-9
np.savez_compressed(out/'operators.npz',C=C,K=K,P=P,G=G)
(out/'results.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
