"""Compile static exact-carrier inputs from the user's E47 QGNN attachment.
Usage: OPENBLAS_NUM_THREADS=1 python scripts/compile_observatory_qgnn.py [source.py]
Requires numpy/scipy for compilation only. Browser has no dependencies.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
import numpy as np

root = Path(__file__).resolve().parents[1]
source = Path(sys.argv[1]) if len(sys.argv) > 1 else root / 'research/observatory-inputs/e47_qgnn.py'
spec = importlib.util.spec_from_file_location('attached_e47', source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
core = module.construct()
model = module.E47QGNN(core)
rng = np.random.default_rng(47)
signal = rng.normal(size=125) + 1j*rng.normal(size=125)
z, probability = model.encode(signal)
z = z[:, 0]
pack = lambda a: np.stack([np.asarray(a).real, np.asarray(a).imag], axis=-1).tolist()
angles = [[0,0,0,0],[.34,-.27,.21,.48],[-.7,.23,1.1,-.4]]
fixtures = []
for theta in angles:
    result = model.evolve(theta,z[:,None])[:,0]
    expectation = float(np.vdot(result, core['observable'] @ result).real)
    fixtures.append({'angles':theta,'expectation':expectation,'norm':float(np.vdot(result,result).real),'probabilities':(abs(result)**2).tolist()})
data = {
    'schema':'E47-QGNN-CARRIER-1','dimension':47,'source':{
        'title':'User-provided e47_qgnn-2.py','sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'scope':'Exact noiseless compressed simulation of the attachment; no quantum hardware or quantum-advantage claim.'},
    'generatorLabels':['x-axis torus edges','y-axis torus edges','z-axis torus edges','node-position potential'],
    'eigensystems':[{'eigenvalues':e.tolist(),'vectors':pack(v)} for e,v in model.spec],
    'observable':pack(core['observable']),'input':pack(z),
    'projectionProbability':float(probability[0]),'fixtures':fixtures,
}
out = root / 'website/interfaces/observatory/qgnn-data.json'
out.write_text(json.dumps(data,separators=(',',':'))+'\n')
print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'source_sha256':data['source']['sha256'],'fixtures':[f['expectation'] for f in fixtures]}))
