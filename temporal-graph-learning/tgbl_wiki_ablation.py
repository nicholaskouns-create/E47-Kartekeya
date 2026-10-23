"""Patch the official TGB TGN runner without replacing its temporal data, negative sampler or MRR evaluator.
Run inside a checkout of shenyangHuang/TGB:
python /path/to/tgbl_wiki_ablation.py --tgb-root . --arm e47 --seed 47 -- [original TGN args]
The official v2 dataset download and model dependencies must already be available.
"""
import argparse, os, pathlib, subprocess, sys, tempfile
p=argparse.ArgumentParser()
p.add_argument("--tgb-root",required=True)
p.add_argument("--arm",choices=["baseline","e47","random"],required=True)
p.add_argument("--seed",type=int,default=47)
args,extra=p.parse_known_args()
root=pathlib.Path(args.tgb_root).resolve()
source=root/"examples/linkproppred/tgbl-wiki/tgn.py"
if not source.is_file():raise SystemExit("Missing upstream TGB TGN script: "+str(source))
s=source.read_text()
injection="""
# Fixed orientation control, applied to TGN node embeddings before the unchanged decoder.
# A fixed orthonormal carrier map makes the intervention valid for any TGN embedding dimension.
import numpy as _np
from scipy.linalg import eigh as _eigh
import torch as _torch
import os as _os
def _project_tgn_embeddings(z):
    arm=_os.environ.get("E47_ARM","baseline")
    if arm=="baseline":return z
    dim=z.shape[-1]
    rng=_np.random.default_rng(47)
    B,_=_np.linalg.qr(rng.standard_normal((max(dim,125),125)))
    B=B[:dim,:]
    if arm=="e47":
        m=_np.array([2,1,0,-1,-2]);up=_np.zeros((5,5))
        for i in range(1,5):up[i-1,i]=_np.sqrt(6-m[i]*(m[i]+1))
        x=(up+up.T)/2;y=(up-up.T)/(2j);zz=_np.diag(m);I=_np.eye(5)
        ops=[_np.kron(_np.kron(a,I),I)+_np.kron(_np.kron(I,a),I)+_np.kron(_np.kron(I,I),a) for a in (x,y,zz)]
        C=sum(a@a for a in ops);w,v=_eigh(C)
        U=v[:,(_np.abs(w-6)<1e-7)|(_np.abs(w-30)<1e-7)]
        assert U.shape==(125,47)
        P=_np.real(U@U.conj().T)
    else:
        U,_=_np.linalg.qr(_np.random.default_rng(int(_os.environ["E47_SEED"])).standard_normal((125,47)))
        P=U@U.T
    # The same fixed map is used for all arms; projection remains differentiable.
    A=B@P@B.T
    A=_torch.as_tensor(A,device=z.device,dtype=z.dtype)
    return z@A
"""
s=injection+"\n"+s
replacements={
"pos_out = model['link_pred'](z[assoc[src]], z[assoc[pos_dst]])":"z = _project_tgn_embeddings(z)\n        pos_out = model['link_pred'](z[assoc[src]], z[assoc[pos_dst]])",
"y_pred = model['link_pred'](z[assoc[src]], z[assoc[dst]])":"z = _project_tgn_embeddings(z)\n            y_pred = model['link_pred'](z[assoc[src]], z[assoc[dst]])",
"MODEL_NAME = 'TGN'":"MODEL_NAME = 'TGN_'+_os.environ.get('E47_ARM','baseline')+'_'+_os.environ.get('E47_SEED','47')"
}
for old,new in replacements.items():
 if s.count(old)!=1:raise SystemExit("Upstream TGN source changed; expected exactly one occurrence: "+old)
 s=s.replace(old,new)
with tempfile.NamedTemporaryFile(mode="w",suffix=".py",dir=source.parent,delete=False) as f:
 f.write(s); patched=pathlib.Path(f.name)
env=os.environ.copy();env["E47_ARM"]=args.arm;env["E47_SEED"]=str(args.seed)
try:
 command=[sys.executable,str(patched)]+([x for x in extra if x!="--"])
 print("TGB TGN intervention",args.arm,"orientation seed",args.seed,flush=True)
 subprocess.run(command,cwd=root,env=env,check=True)
finally:patched.unlink(missing_ok=True)
