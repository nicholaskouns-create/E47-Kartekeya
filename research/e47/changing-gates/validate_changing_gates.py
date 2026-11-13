"""Validate changing learned gates against the exact E47 contraction identity."""
from pathlib import Path
import hashlib, json, platform
import numpy as np
import scipy
from e47_qgnn import construct, E47QGNN

def main():
    d=construct()
    b,p,g=d['B'],d['P'],d['Gamma']
    q=np.eye(125)-p
    model=E47QGNN(d)
    rng=np.random.default_rng(20261113)
    records=[]
    for trial in range(10):
        full=np.eye(125,dtype=complex)
        inside=np.eye(47,dtype=complex)
        outside=q.copy()
        for layer in range(1,65):
            angles=rng.uniform(-np.pi,np.pi,4)
            v=model.evolve(angles,np.eye(47,dtype=complex))
            u=b@v@b.conj().T+q
            full=u@g@full
            inside=v@inside
            outside=g@outside
            target=b@inside@b.conj().T
            actual=float(np.linalg.norm(full-target,2))
            records.append(dict(trial=trial,layer=layer,angles=angles.tolist(),
                identity_residual=float(np.linalg.norm(full-target-outside,2)),
                contraction_equality_error=abs(actual-(15/17)**layer),
                gate_leakage=float(np.linalg.norm(q@u@p,2)),
                operator_error=actual,predicted_error=(15/17)**layer))
    maxima={k:max(r[k] for r in records) for k in
            ['identity_residual','contraction_equality_error','gate_leakage']}
    receipt=dict(status='PASS' if max(maxima.values())<1e-10 else 'FAIL',
        seed=20261113,sequences=10,layers_per_sequence=64,
        total_layer_checks=len(records),tolerance=1e-10,maxima=maxima,
        source_url='https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/observatory-inputs/e47_qgnn.py',
        source_sha256=hashlib.sha256(Path(__file__).with_name('e47_qgnn.py').read_bytes()).hexdigest(),
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        evidence='Double-precision matrix simulation; randomized gate sequences, not a new optimizer-training run.',
        records=records)
    Path(__file__).with_name('receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='records'},indent=2))
    if receipt['status']!='PASS': raise SystemExit(1)

if __name__=='__main__': main()

