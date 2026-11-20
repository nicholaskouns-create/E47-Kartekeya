#!/usr/bin/env python3
from __future__ import annotations
import json, os, platform, subprocess, sys, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
PACKAGE=str(ROOT/'package')

def run(name, cmd, cwd, env=None):
    e=os.environ.copy()
    if env: e.update(env)
    p=subprocess.run(cmd,cwd=cwd,env=e,text=True,capture_output=True)
    (OUT/f'{name}.harness.log').write_text(p.stdout+'\n--- STDERR ---\n'+p.stderr)
    return {'name':name,'returncode':p.returncode,'pass':p.returncode==0,'command':cmd,'cwd':str(cwd),'stdout_tail':p.stdout[-1500:],'stderr_tail':p.stderr[-800:]}

runs=[]
runs.append(run('e47_validation',['python','e47_validation.py'],ROOT/'repaired/e47_validation_run'))
runs.append(run('selection_package_repair',['python','-m','e47selection.selection'],ROOT/'repaired/selection_pkg',{'PYTHONPATH':str(ROOT/'repaired/selection_pkg')}))
runs.append(run('step1_central_operator',['python','step1_central_operator.py'],ROOT/'repaired/legacy_kartekeya'))
runs.append(run('e47_channel_validation_corrected',['python',str(ROOT/'repaired/e47_channel_validation_corrected.py')],ROOT/'repaired',{'PYTHONPATH':PACKAGE}))

import numpy, scipy, matplotlib
runtime={'python':platform.python_version(),'implementation':platform.python_implementation(),'numpy':numpy.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__}
source_fidelity={
 'e47_validation.py':'EXACT_SOURCE_UNMODIFIED; blocker closed by NumPy 2.x pin',
 'e47_channel_validation_corrected.py':'SOURCE_AVAILABLE; dependency-repaired NumPy/SciPy implementation preserves declared finite-dimensional channel checks; QuTiP backend itself not executed',
 'selection.py':'RECONSTRUCTED_PACKAGE_LAYOUT from canonical moment-selection assets; original audit source unavailable in connected Notion/Drive/Library',
 'step1_central_operator.py':'RECONSTRUCTED_PORTABLE_PATH from legacy Kartekeya Cube validation monograph; original audit source unavailable in connected Notion/Drive/Library',
}
cert={
 'schema':'mathematical-city.corpus-reproducibility-closure.v1',
 'certificate_code':'MC-E47-ENGINEERING-CLOSURE-20261120',
 'runtime':runtime,
 'survey_context':{'files_surveyed':48,'prior_execution_attempts':25,'prior_completed_pass':20,'prior_blocked_environment_or_packaging':5},
 'closure_runs':runs,
 'closure_pass_count':sum(r['pass'] for r in runs),
 'closure_fail_count':sum(not r['pass'] for r in runs),
 'all_engineering_paths_closed':all(r['pass'] for r in runs),
 'engineering_paths_attempted':len(runs),
 'source_fidelity':source_fidelity,
 'claim':'The receipt records the outcome of each currently scoped engineering path.',
 'strict_boundary':'This certificate does not claim byte-exact source reproducibility for selection.py or step1_central_operator.py because those original files were not found in the connected assets. Their closure runs are provenance-marked reconstructions. It also does not claim that the QuTiP backend itself was executed for e47_channel_validation_corrected.py; the declared finite-dimensional identities were revalidated with a dependency-repaired NumPy/SciPy backend. The survey figures are historical metadata.',
 'evidence_class':'E1 reproducibility; E0 identities only where separately established',
}
path=ROOT/'MC-E47-ENGINEERING-CLOSURE-20261120.json'
path.write_text(json.dumps(cert,indent=2))
print(json.dumps(cert,indent=2))
if not cert['all_engineering_paths_closed']: raise SystemExit(1)
