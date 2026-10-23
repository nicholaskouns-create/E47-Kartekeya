import json, urllib.request
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.linalg import eigh
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

base="https://raw.githubusercontent.com/tkipf/pygcn/master/data/cora/"
cache=Path("/tmp/noesis-cora"); cache.mkdir(exist_ok=True)
def get(name):
 p=cache/name
 if not p.exists(): urllib.request.urlretrieve(base+name,p)
 return p
def projector():
 m=np.array([2,1,0,-1,-2]); z=np.diag(m); up=np.zeros((5,5))
 for i in range(1,5):up[i-1,i]=np.sqrt(6-m[i]*(m[i]+1))
 x=(up+up.T)/2; y=(up-up.T)/(2j); eye=np.eye(5)
 ops=[np.kron(np.kron(a,eye),eye)+np.kron(np.kron(eye,a),eye)+np.kron(np.kron(eye,eye),a) for a in (x,y,z)]
 c=sum(a@a for a in ops)
 w,v=eigh(c); selected=(abs(w-6)<1e-7)|(abs(w-30)<1e-7)
 assert selected.sum()==47
 return np.asarray(v[:,selected], dtype=np.complex128)
def main():
 raw=np.loadtxt(get("cora.content"),dtype=str)
 X=raw[:,1:-1].astype(float); _,y=np.unique(raw[:,-1],return_inverse=True)
 assert X.shape==(2708,1433)
 edges=np.loadtxt(get("cora.cites"),dtype=str); ids={s:i for i,s in enumerate(raw[:,0])}
 pairs=np.array([(ids[a],ids[b]) for a,b in edges if a in ids and b in ids])
 A=sparse.coo_matrix((np.ones(2*len(pairs)),(np.r_[pairs[:,0],pairs[:,1]],np.r_[pairs[:,1],pairs[:,0]])),shape=(2708,2708)).tocsr()
 A.data[:]=1; A.setdiag(1); d=np.asarray(A.sum(1)).ravel()
 G=sparse.diags(1/np.sqrt(d))@A@sparse.diags(1/np.sqrt(d))
 rng=np.random.default_rng(47)
 Q,_=np.linalg.qr(rng.standard_normal((1433,125)))
 Z=X@Q; U=projector(); E=Z@U
 pca=PCA(n_components=47,svd_solver="full").fit(Z); P=pca.transform(Z)
 # Fixed label-stratified 140/500/1000 split; not official Planetoid masks.
 rng=np.random.default_rng(2026)
 tr=np.concatenate([rng.choice(np.where(y==k)[0],20,replace=False) for k in range(7)])
 remain=np.setdiff1d(np.arange(2708),tr);rng.shuffle(remain);val=remain[:500];test=remain[500:1500]
 def score(H):
  H=np.column_stack((H.real,H.imag)) if np.iscomplexobj(H) else H
  H=G@H; H=H/(np.linalg.norm(H,axis=1,keepdims=True)+1e-12)
  clf=LogisticRegression(max_iter=1500,random_state=0).fit(H[tr],y[tr])
  return {"validation_accuracy":float(accuracy_score(y[val],clf.predict(H[val]))),"test_accuracy":float(accuracy_score(y[test],clf.predict(H[test])))}
 result={"dataset":"Cora","nodes":2708,"input_features":1433,"carrier_dimension":125,"compressed_dimension":47,"embedding":"Gaussian QR seed 47","split":"stratified seed 2026, 140 train / 500 val / 1000 test, not official Planetoid","E47":{"mse":float(np.mean(np.abs(Z-E@U.conj().T)**2)),**score(E)},"PCA":{"mse":float(np.mean((Z-pca.inverse_transform(P))**2)),**score(P)}}
 print(json.dumps(result,indent=2));Path("cora-e47-results.json").write_text(json.dumps(result,indent=2))

def graph_aware_study():
 """Graph-aware, unsupervised E47 alignment. No labels enter embedding fit."""
 raw=np.loadtxt(get("cora.content"),dtype=str)
 X=raw[:,1:-1].astype(float); _,y=np.unique(raw[:,-1],return_inverse=True)
 edges=np.loadtxt(get("cora.cites"),dtype=str)
 ids={s:i for i,s in enumerate(raw[:,0])}
 pairs=np.array([(ids[a],ids[b]) for a,b in edges if a in ids and b in ids])
 A=sparse.coo_matrix((np.ones(2*len(pairs)),(np.r_[pairs[:,0],pairs[:,1]],np.r_[pairs[:,1],pairs[:,0]])),shape=(2708,2708)).tocsr()
 A.data[:]=1;A.setdiag(1)
 d=np.asarray(A.sum(1)).ravel()
 G=sparse.diags(1/np.sqrt(d))@A@sparse.diags(1/np.sqrt(d))
 # Graph-aware preprocessing applied equally to E47 and PCA.
 F=np.asarray(G@X)
 rng=np.random.default_rng(47)
 Q,_=np.linalg.qr(rng.standard_normal((1433,125)))
 Z=F@Q
 U=projector()
 # Hermitian covariance eigenbasis, sorted by decreasing graph-smoothed variance.
 centered=Z-Z.mean(axis=0)
 eigenvalues,V=np.linalg.eigh(centered.T@centered)
 V=V[:,::-1]
 # Rotate the carrier so the fixed E47 sector contains its 47 leading
 # graph-aware covariance directions. Rotation is orthogonal/unitary.
 # This is a learned, unsupervised embedding, not an intrinsic E47 advantage.
 # E47 coordinates in the aligned carrier equal V[:, :47] up to basis rotation.
 target=V[:,:47]
 # Reconstruct the complete carrier rotation mapping E47 basis to target.
 # E47 basis is complex. Choose real orthonormal basis of the real projector
 # through eigendecomposition of Re(U U*), valid for this integer-spin representation.
 projector_real=np.real(U@U.conj().T)
 ev,base=np.linalg.eigh(projector_real)
 Ereal=base[:,-47:]
 assert np.linalg.norm(Ereal@Ereal.T-projector_real)<1e-7
 remainder=base[:,:78]
 rotation=np.column_stack([target,V[:,47:]])@np.column_stack([Ereal,remainder]).T
 assert np.linalg.norm(rotation.T@rotation-np.eye(125))<1e-7
 Ea=Z@rotation@Ereal
 pca=PCA(n_components=47,svd_solver="full").fit(Z)
 Pc=pca.transform(Z)
 # Graph-aware PCA and aligned E47 should match within numerical precision.
 assert np.max(np.abs(np.linalg.norm(Ea-Ea.mean(0),axis=1)-np.linalg.norm(Pc,axis=1)))<1e-6
 records=[]
 for seed in (11,23,47,89,137):
  rng=np.random.default_rng(seed)
  tr=np.concatenate([rng.choice(np.where(y==k)[0],20,replace=False) for k in range(7)])
  remain=np.setdiff1d(np.arange(2708),tr);rng.shuffle(remain)
  val=remain[:500];test=remain[500:1500]
  def score(H):
   H=np.asarray(G@H)
   H=H/(np.linalg.norm(H,axis=1,keepdims=True)+1e-12)
   clf=LogisticRegression(max_iter=1500,random_state=0).fit(H[tr],y[tr])
   return [float(accuracy_score(y[val],clf.predict(H[val]))),float(accuracy_score(y[test],clf.predict(H[test])))]
  records.append({"seed":seed,"E47":score(Ea),"PCA":score(Pc)})
 result={"dataset":"Cora","design":"graph diffusion G@X; common Gaussian QR carrier; graph covariance alignment of E47; PCA fitted to same graph-aware carrier","dimension":47,"seeds":[11,23,47,89,137],"records":records,"caution":"Alignment explicitly optimizes E47 sector against the same covariance as PCA. Any parity is by construction, not an independent E47 performance discovery."}
 for method in ("E47","PCA"):
  vals=np.array([r[method] for r in records])
  result[method]={"validation_mean":float(vals[:,0].mean()),"validation_sd":float(vals[:,0].std(ddof=1)),"test_mean":float(vals[:,1].mean()),"test_sd":float(vals[:,1].std(ddof=1))}
 print(json.dumps(result,indent=2))
 Path("cora-graph-aware-results.json").write_text(json.dumps(result,indent=2))

if __name__=="__main__":
 main()
 graph_aware_study()
