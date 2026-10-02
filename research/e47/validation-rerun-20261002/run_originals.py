import subprocess, os, pathlib, json, hashlib, sys
root=pathlib.Path(__file__).resolve().parent
repo=root.parent/'e47-repo'
paths={
 'spectral_core':repo/'research/e47/first-principles/e47_spectral_explication_proof.py',
 'spectral_matrix':repo/'research/e47/validation/e47_spectral_matrix_proof.py',
 'signature_symmetry':repo/'research/e47/validation/e47_signature_symmetry_certificate.py',
 'noiseless_ququint':repo/'research/e47/validation/e47_noiseless_heisenberg_weyl.py',
 'newton_product':repo/'research/e47/newton-e47-product/newton_mean_e47_product_validator.py',
 'spacetime':root/'spacetime_original.py',
 'twisted_triple':root/'twisted_original.py',
}
env=dict(os.environ,PYTHONPATH=str(root.parent/'python_deps'),E47_CERT_OUT=str(root/'signature_certificate.json'),OPENBLAS_NUM_THREADS='1')
results=[]
for name,path in paths.items():
 if not path.exists(): path=root/(name+'_source.py')
 p=subprocess.run([sys.executable,str(path)],cwd=root,env=env,capture_output=True,text=True)
 (root/(name+'.log')).write_text(p.stdout+p.stderr)
 (root/(name+'_source.py')).write_bytes(path.read_bytes())
 r=dict(name=name,exit_code=p.returncode,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source=str(path),log=name+'.log')
 results.append(r)
 print(name,'EXIT',p.returncode, p.stdout[-300:],p.stderr[-500:])
(root/'original_runs.json').write_text(json.dumps(results,indent=2))
assert all(r['exit_code']==0 for r in results)
