"""Compare the browser's SVD gauges against independent NumPy QR gauges."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    'canonical_matrix_oracle', ROOT / 'scripts/validate_matrix_quantum_parity.py'
)
oracle = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = oracle
spec.loader.exec_module(oracle)


def test_truncated_browser_state_matches_independent_qr_oracle():
    config = oracle.Config(n=6, layers=8, chi=2, phi=0.7)
    python_state, discarded, _, _ = oracle.mps_matrix_circuit(config)
    script = """
      const fs=require('node:fs'),vm=require('node:vm');let result;
      const ctx={Float64Array,Math,Number,Array,postMessage:x=>result=x};
      vm.createContext(ctx);vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),ctx);
      ctx.onmessage({data:JSON.parse(process.argv[2])});
      console.log(JSON.stringify(result));
    """
    run = subprocess.run(
        ['node', '-e', script,
         str(ROOT / 'website/interfaces/matrix/mps-worker.js'),
         json.dumps({'n': 6, 'layers': 8, 'chi': 2, 'phi': .7, 'validate': True})],
        check=True, capture_output=True, text=True, timeout=60,
    )
    result = json.loads(run.stdout)
    values = np.array(result['statevector'])
    browser_state = values[:, 0] + 1j * values[:, 1]
    assert oracle.phase_aligned_relative_l2(browser_state, python_state) < 1e-9
    assert abs(result['discard'] - discarded) < 1e-9
    assert abs(result['norm'] - np.vdot(python_state, python_state).real) < 1e-9
    assert result['validation']['pass']
    assert result['validation']['relative_l2'] <= result['truncation']['state_error_bound'] + 1e-9
