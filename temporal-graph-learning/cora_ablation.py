"""E47 matched-rank Cora ablation. Provenance: tower/noesis/cora_e47_benchmark.py.
Run from repository root; downloads tkipf/pygcn Cora content/cites.
This is NODE CLASSIFICATION ACCURACY, not the historical Cora link-AUC claim.
"""
import json, hashlib, urllib.request
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.linalg import eigh
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
ROOT=Path(__file__).resolve().parent
CACHE=ROOT/"data"; CACHE.mkdir(exist_ok=True)
BASE="https://raw.githubusercontent.com/tkipf/pygcn/master/data/cora/"
def get(name):
 p=CACHE/name
 if not p.exists(): urllib.request.urlretrieve(BASE+name,p)
 return p
def projector():
 m=np.array([2,1,0,-1,-2]); z=np.diag(m); up=np.zeros((5,5))
 for i in range(1,5): up[i-1,i]=np.sqrt(6-m[i]*(m[i]+1))
 x=(up+up.T)/2; y=(up-up.T)/(2j); I=np.eye(5)
 ops=[np.kron(np.kron(a,I),I)+np.kron(np.kron(I,a),I)+np.kron(np.kron(I,I),a) for a in (x,y,z)]
 C=sum(a@a for a in ops); w,v=eigh(C)
 U=v[:,(abs(w-6)<1e-7)|(abs(w-30)<1e-7)]
 P=np.real(U@U.conj().T)
 assert U.shape==(125,47) and np.linalg.norm(P@P-P)<1e-8
 return P, {"rank":47,"idempotence_fro":float(np.linalg.norm(P@P-P)),"commutator_fro":float(np.linalg.norm(P@C-C@P))}
def main():
 raw=np.loadtxt(get("cora.content"),dtype=str)
 X=raw[:,1:-1].astype(float); _,y=np.unique(raw[:,-1],return_inverse=True)
 assert X.shape==(2708,1433)
 edges=np.loadtxt(get("cora.cites"),dtype=str); ids={s:i for i,s in enumerate(raw[:,0])}
 pairs=np.array([(ids[a],ids[b]) for a,b in edges if a in ids and b in ids])
 A=sparse.coo_matrix((np.ones(2*len(pairs)),(np.r_[pairs[:,0],pairs[:,1]],np.r_[pairs[:,1],pairs[:,0]])),shape=(2708,2708)).tocsr()
 A.data[:]=1; A.setdiag(1); d=np.asarray(A.sum(1)).ravel()
 G=sparse.diags(1/np.sqrt(d))@A@sparse.diags(1/np.sqrt(d))
 Q,_=np.linalg.qr(np.random.default_rng(47).standard_normal((1433,125)))
 Z=X@Q
 P,checks=projector()
 # Reuse the exact fixed split and scoring function of tower/noesis/cora_e47_benchmark.py.
 rng=np.random.default_rng(2026)
 tr=np.concatenate([rng.choice(np.where(y==k)[0],20,replace=False) for k in range(7)])
 remain=np.setdiff1d(np.arange(2708),tr);rng.shuffle(remain)
 val=remain[:500];test=remain[500:1500]
 split_hash=hashlib.sha256(np.r_[tr,val,test].astype("<i8").tobytes()).hexdigest()
 def evaluate(H):
  H=G@H;H=H/(np.linalg.norm(H,axis=1,keepdims=True)+1e-12)
  clf=LogisticRegression(max_iter=1500,random_state=0).fit(H[tr],y[tr])
  return {"validation_accuracy":float(accuracy_score(y[val],clf.predict(H[val]))),"test_accuracy":float(accuracy_score(y[test],clf.predict(H[test]))),"test_indices":test.tolist(),"test_truth":y[test].tolist(),"test_predictions":clf.predict(H[test]).tolist(),"test_probabilities":clf.predict_proba(H[test]).tolist()}
 arms={"baseline_125d":evaluate(Z),"E47_rank47":evaluate(Z@P)}
 random_seeds=[11,23,47,89,137,2026,2047,2112,3141,4242]
 for seed in random_seeds:
  V,_=np.linalg.qr(np.random.default_rng(seed).standard_normal((125,47)))
  arms["random_rank47_seed_"+str(seed)]=evaluate(Z@(V@V.T))
 scores=np.array([arms["random_rank47_seed_"+str(s)]["test_accuracy"] for s in random_seeds])
 delta=arms["E47_rank47"]["test_accuracy"]-scores
 summary={"baseline_test_accuracy":arms["baseline_125d"]["test_accuracy"],"E47_test_accuracy":arms["E47_rank47"]["test_accuracy"],"random_mean_test_accuracy":float(scores.mean()),"random_sd":float(scores.std(ddof=1)),"E47_minus_random_mean":float(delta.mean()),"E47_minus_random_95pct_t_interval":[float(delta.mean()-2.262*delta.std(ddof=1)/np.sqrt(len(delta))),float(delta.mean()+2.262*delta.std(ddof=1)/np.sqrt(len(delta)))],"random_seeds":random_seeds}
 out={"scope":"Cora node classification; custom split, NOT Planetoid public masks or link AUC","source":"tower/noesis/cora_e47_benchmark.py","feature_map":"cora.content 1433 bag-of-words -> Gaussian QR seed 47 -> 125d","split":"stratified 20/class seed 2026, next 500 validation and 1000 test","split_sha256":split_hash,"dataset_sha256":{p:hashlib.sha256(get(p).read_bytes()).hexdigest() for p in ("cora.content","cora.cites")},"projector":checks,"arms":arms,"summary":summary}
 (ROOT/"cora-ablation-results.json").write_text(json.dumps(out,indent=2))
 (ROOT/"cora-ablation-summary.json").write_text(json.dumps({k:v for k,v in out.items() if k!="arms"},indent=2))
 print(json.dumps(out["summary"],indent=2))
if __name__=="__main__":main()
