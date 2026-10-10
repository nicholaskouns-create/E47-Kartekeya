"""Workbench observables cross-checked against canonical full matrix evolution."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from e47.workbench import EPSILON, GAP, QMAX, VALUES, geometry, matrices, simulate, validate

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('mode',['discrete','continuous'])
@pytest.mark.parametrize('seed',[0,47,125])
def test_compressed_observables_match_full_matrix(mode,seed):
    C,K,P,G=matrices()
    eigenvalues,U=np.linalg.eigh(C)
    rng=np.random.default_rng(seed)
    psi=rng.normal(size=125)+1j*rng.normal(size=125)
    psi/=np.linalg.norm(psi)
    coeff=U.conj().T@psi
    weights=[float((np.abs(coeff[np.abs(eigenvalues-v)<1e-7])**2).sum()) for v in VALUES]
    result=simulate(weights,steps=20,mode=mode,horizon=1)
    projected=P@psi
    for record in result['records']:
        if mode=='discrete': current=np.linalg.matrix_power(G,record['n'])@psi
        else:
            q=((eigenvalues-6)*(eigenvalues-30))**2
            current=U@(np.exp(-q*record['tau']/GAP)*coeff)
        assert record['probability']==pytest.approx(np.linalg.norm(current)**2,abs=1e-10)
        assert record['error']==pytest.approx(np.linalg.norm(current-projected),abs=1e-10)
        assert record['error']<=record['bound']+1e-12
        normalized=current/np.linalg.norm(current)
        target=projected/np.linalg.norm(projected)
        assert record['fidelity']==pytest.approx(abs(np.vdot(target,normalized))**2,abs=1e-10)


def test_selected_and_complement_edge_cases():
    selected=simulate([0,0,1,0,0,0,0])
    assert all(r['error']==0 and r['occupancy']==1 for r in selected['records'])
    complement=simulate([0,0,0,0,0,0,1],mode='continuous',horizon=100)
    assert all(r['fidelity'] is None for r in complement['records'])
    assert complement['records'][-1]['probability']==0
    assert complement['records'][-1]['occupancy'] is None


@pytest.mark.parametrize('kwargs',[
 {'weights':[0]*7},{'weights':[1,2]},{'weights':[1,1,1,-1,1,1,1]},
 {'weights':[float('nan')]*7},{'weights':[1]*7,'steps':0},
 {'weights':[1]*7,'steps':True},{'weights':[1]*7,'steps':1.5},
 {'weights':[1]*7,'epsilon':2/QMAX},{'weights':[1]*7,'epsilon':float('inf')},
 {'weights':[1]*7,'mode':'unknown'},{'weights':[1]*7,'horizon':0}])
def test_invalid_inputs_rejected(kwargs):
    with pytest.raises(ValueError): simulate(**kwargs)


def test_geometry_closed_connected_and_planar():
    g=geometry();verts=np.array(g['vertices']);normals=np.array(g['normals']);A=np.array(g['adjacency'])
    assert [len(verts),g['edge_count'],len(g['faces'])]==[90,135,47]
    assert g['edge_incidence_minmax']==[2,2]
    assert g['face_histogram']=={4:3,5:14,6:23,7:6,8:1}
    assert g['euler']==2
    assert np.max(verts@normals.T-1)<1e-8
    assert np.array_equal(A,A.T)
    assert sum(abs(x)<1e-8 for x in g['laplacian_spectrum'])==1
    assert np.max(np.abs(np.linalg.norm(normals,axis=1)-1))<1e-12
    for normal,face in zip(normals,g['faces']):assert np.max(np.abs(verts[face]@normal-1))<1e-8


def test_bundle_is_traceable_and_valid():
    report=validate();assert report['status']=='pass'
    bundle=json.loads((ROOT/'website/interfaces/e47-research-workbench/data.json').read_text())
    assert bundle['canonical']['kernel_dimension']==47
    assert bundle['comparison_audit']['status']=='unresolved parameter provenance'
    for source in bundle['sources']['sources']:
        path=ROOT/'research/e47/workbench-inputs'/source['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==source['sha256']


def test_portable_geometry_output(tmp_path):
    output=tmp_path/'nested'/'geometry.npz'
    result=subprocess.run([sys.executable,'-m','e47.workbench','--geometry-only','--output',str(output)],cwd=ROOT,text=True,capture_output=True,env={**os.environ,'PYTHONPATH':str(ROOT/'src')+os.pathsep+os.environ.get('PYTHONPATH','')})
    assert result.returncode==0,result.stderr
    with np.load(output) as data:
        assert data['vertices'].shape==(90,3)
        assert data['normals'].shape==(47,3)
        assert data['labels'].shape==(47,3)


def test_offline_package_csp_hashes_match_exact_inline_bytes(tmp_path):
    """A corrupted packaging step must not ship scripts the CSP will reject."""
    import base64
    from html.parser import HTMLParser

    output=tmp_path/'workbench.html'
    subprocess.run([sys.executable,str(ROOT/'scripts/package_e47_workbench.py'),'--output',str(output)],check=True,capture_output=True)

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.policy='';self.blocks={};self.current=None
        def handle_starttag(self,tag,attrs):
            attrs=dict(attrs)
            if tag=='meta' and attrs.get('http-equiv')=='Content-Security-Policy':self.policy=attrs['content']
            if tag in {'style','script'}:
                assert 'src' not in attrs
                self.current=tag;self.blocks[tag]=''
        def handle_endtag(self,tag):
            if self.current==tag:self.current=None
        def handle_data(self,data):
            if self.current:self.blocks[self.current]+=data

    parser=Parser();parser.feed(output.read_text())
    assert "connect-src 'none'" in parser.policy
    for block in parser.blocks.values():
        digest=base64.b64encode(hashlib.sha256(block.encode()).digest()).decode()
        assert 'sha256-'+digest in parser.policy
    assert 'OFFLINE_BUNDLE' in parser.blocks['script']
    assert "await fetch('./data.json')" not in parser.blocks['script']
