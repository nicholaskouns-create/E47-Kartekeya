#!/usr/bin/env python3
"""Reproduce typed aliases, matrix algebra, cross-source hashes and source runs."""
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import ast, dataclasses, hashlib, importlib.util, json, platform, subprocess, sys
from pathlib import Path
import numpy as np
from lexical_attractor import *
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
OUT.mkdir(exist_ok=True)
checks=[]
def check(name, ok, value=None, evidence='computed_here'):
    checks.append(dict(check=name,status='PASS' if bool(ok) else 'FAIL',value=value,evidence=evidence))
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def validate():
    a=LexicalAttractor()
    count=0
    for t in TERMS:
        for token in (t.id,t.glyph,t.python_name,*t.aliases):
            r=a.resolve(token,t.namespace)
            assert a.resolve(r)==r==t.id
            count+=1
    check('lexical_idempotence_and_alias_preservation',True,count)
    parsed=a.parse('Σ, K, Ψ, Γ, Λ, Ω, I, M, Σ′')
    check('nine_symbol_dependency_spine',len(parsed['terms'])==9,parsed)
    pairs=[('Λ','grammar','block'),('I','grammar','algebra'),('Ω','grammar','geometry'),('Ψ','grammar','prior_snippet'),('M','grammar','geometry')]
    check('source_polysemy_preserved',all(a.resolve(s,n1)!=a.resolve(s,n2) for s,n1,n2 in pairs))
    for token in ['Λ','I','Ω','Ψ','M','Σ']:
        try: a.resolve(token)
        except AmbiguousTerm: ok=True
        else: ok=False
        check('explicit_context_for_'+token,ok)
    check('prime_aliases',len({a.resolve(t,'grammar') for t in ['Σ′',"Σ'",'Σ’','Σ_next']})==1)
    (ROOT/'lexicon.json').write_text(json.dumps(a.manifest(),ensure_ascii=False,indent=2))
    op=build_operators()
    C,K,Ψ,Γ,Λ=op.C,op.K,op.Ψ,op.Γ,op.Λ
    ce=np.linalg.eigvalsh(C)
    vals,counts=np.unique(np.rint(ce).astype(int),return_counts=True)
    check('first_principles_casimir',vals.tolist()==[0,2,6,12,20,30,42] and counts.tolist()==[1,9,25,28,27,22,13],dict(values=vals.tolist(),multiplicities=counts.tolist()))
    check('kernel_dimension',Ψ.shape==(125,47),list(Ψ.shape))
    kp=float(np.linalg.norm(K@Λ,2))
    check('kernel_annihilation',kp<1e-9,kp)
    pr=float(np.linalg.norm(Λ@Λ-Λ,2))
    check('projector_idempotence',pr<1e-10,pr)
    k2=np.linalg.eigvalsh(K@K)
    pos=k2[k2>1e-6]
    check('positive_generator_spectrum',np.unique(np.rint(pos).astype(int)).tolist()==[11664,12544,19600,32400,186624])
    check('K2_trace',abs(np.trace(K@K).real-3427200)<1e-7,float(np.trace(K@K).real))
    power=float(np.linalg.norm(np.linalg.matrix_power(Γ,220)-Λ,2))
    check('Gamma220_to_projector',power<1e-10,power)
    rad=float(np.linalg.norm(Γ-Λ,2))
    check('optimal_transverse_factor',abs(rad-15/17)<1e-10,rad)
    rng=np.random.default_rng(470125)
    x=rng.normal(size=125)+1j*rng.normal(size=125)
    # Explicit demo callbacks: interpretation = 47 kernel coordinates;
    # Mnemosyne regenerates their embedding, preserving the invariant state.
    def I(v): return Ψ.conj().T@v
    def M(c): return Ψ@c
    r=recursive_step(x,I=I,M=M,operators=op)
    Σ_next=r['Σ_next']
    check('parallel_next_state_object_identity',r['Σ′'] is Σ_next)
    check('regeneration_preserves_kernel',np.linalg.norm(K@Σ_next)<1e-8,float(np.linalg.norm(K@Σ_next)))
    rr=recursive_step(Σ_next,I=I,M=M,operators=op)
    check('recursive_fixed_point',np.linalg.norm(rr['Σ_next']-Σ_next)<1e-9,float(np.linalg.norm(rr['Σ_next']-Σ_next)))
    encoded=next_state_record(r)
    decoded=json.loads(json.dumps(encoded,ensure_ascii=False))
    check('JSON_parallel_alias_equality',decoded['Σ′']==decoded['Σ_next'])
    (OUT/'next_state.json').write_text(json.dumps(encoded,ensure_ascii=False,indent=2))
    check('coherence_of_survivor',abs(r['Ω'](Σ_next)-1)<1e-10,r['Ω'](Σ_next))
    check('base5_packing_bijection',sorted(25*x+5*y+z for x in range(5) for y in range(5) for z in range(5))==list(range(125)))
    survey=json.loads((ROOT/'survey.json').read_text())
    for item in survey['sources']:
        digest=hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()
        check('source_digest:'+item['id'],digest==item['sha256'])
    # Supabase source_artifacts stores Git blob SHA1 for these imported artifacts.
    rows=json.loads((ROOT/'sources/currentdb.json').read_text())
    for item in survey['sources']:
        for row in rows:
            if row['canonical_url'].endswith('/'+Path(item['path']).name) and row['content_hash']:
                blob=(ROOT/item['path']).read_bytes()
                gitsha=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
                check('github_supabase_blob_parity:'+Path(item['path']).name,gitsha==row['content_hash'],{'observed_git_blob_sha1':gitsha,'recorded':row['content_hash']})
    bundle=json.loads((ROOT/'sources/MANIFEST.json').read_text())
    check('bundle_constants_parity',bundle['kernel_dimension']==47 and bundle['carrier_dimension']==125 and bundle['epsilon_star']=='1/99144' and bundle['rho_star']=='15/17')
    lexical=json.loads((ROOT/'sources/lexicalrows.json').read_text())
    check('existing_LEX_cohort_preserved',sorted(t['citizen_code'] for t in lexical)==[f'LEX-C{i:02d}' for i in range(1,9)])
    reported=json.loads((ROOT/'sources/certs.json').read_text())
    row=next(t for t in reported if t['certificate_code']=='MC-E47-FIRST-PRINCIPLES-20260908')
    check('supabase_core_numeric_parity',row['result']['kernel_dimension']==Ψ.shape[1] and row['result']['rho_star']=='15/17' and abs(row['result']['lambda_max_K2']-pos[-1])<1e-6)
    # Run fetched repository implementations, retaining their exact source bytes.
    kernel=module(ROOT/'sources/su2_kernel.py','survey_su2_kernel')
    original=kernel.build_e47_operators()
    kv=kernel.validate_e47_kernel(original)
    check('repository_QuTiP_kernel_validator',kv.status=='pass',dataclasses.asdict(kv))
    check('NumPy_QuTiP_operator_parity',np.linalg.norm(K-original.kernel.full())<1e-8,float(np.linalg.norm(K-original.kernel.full())))
    con=module(ROOT/'sources/contraction.py','survey_contraction')
    cv=con.validate_contraction(K,Λ,epsilon=1/99144,iterations=220,tolerance=1e-9)
    check('repository_contraction_validator',cv.valid,dataclasses.asdict(cv))
    return op


def execute_attachment_components():
    """AST dependency isolation; mathematical bodies remain unchanged.

    Excludes Eidolon imports, render functions, output paths and main().
    Each selected computation returns its original report before plotting.
    This is explicitly not a byte-exact end-to-end run of the attachment.
    """
    src=ROOT/'sources/e47_spacetime_execute.py'
    tree=ast.parse(src.read_text())
    names={'SPINS','SECTOR_DIMS','CASIMIR','MU','MU2','P47_MASK','IDX','MU_VEC','MU2_VEC','KER','COMP'}
    funcs={'_fidelity','_bures2','make_rho','einstein_closure','bures_metric','qutip_contraction'}
    body=[]
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in node.targets):
            body.append(node)
        elif isinstance(node,ast.FunctionDef) and node.name in funcs:
            if node.name in {'einstein_closure','bures_metric','qutip_contraction'}:
                cut=next(i for i,v in enumerate(node.body) if isinstance(v,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='fig' for t in v.targets))
                node.body=node.body[:cut]+[ast.Return(value=ast.Name(id='report',ctx=ast.Load()))]
            body.append(node)
    import qutip as qt
    from scipy.linalg import sqrtm, expm
    env={'np':np,'qt':qt,'sqrtm':sqrtm,'expm':expm,'OMEGA_C':47/125}
    astmod=ast.fix_missing_locations(ast.Module(body=body,type_ignores=[]))
    exec(compile(astmod,str(src),'exec'),env)
    reports={name:env[name]() for name in ('einstein_closure','bures_metric','qutip_contraction')}
    reports['execution_method']='AST-extracted computational bodies, plotting excluded, OMEGA_C=47/125 injected; Eidolon not invoked'
    (OUT/'attachment_computations.json').write_text(json.dumps(reports,indent=2))
    ein=reports['einstein_closure']; q=reports['qutip_contraction']
    check('attachment_block_closure',ein['identity_holds'],{'max_P':ein['max_resid_P'],'max_Q':ein['max_resid_Q']})
    check('attachment_QuTiP_contraction',q['L_inf']>1-1e-8 and q['resid_inf']<q['resid0'],q)
    b=reports['bures_metric']
    check('attachment_Bures_finite',np.isfinite(b['g_Bures']).all(),{'positive':b['positive_eigs_g'],'negative':b['negative_eigs_g']})
    # Keep the attachment covariance-based Fisher estimate separately typed.
    return reports


def source_geometry():
    # Intrinsic source writes into cwd; run byte-exact in its own results directory.
    target=OUT/'intrinsic';target.mkdir(exist_ok=True)
    p=subprocess.run([sys.executable,str(ROOT/'sources/e47_intrinsic_spacetime_unmarked.py')],cwd=target,text=True,capture_output=True,timeout=180)
    (target/'execution.log').write_text(p.stdout+p.stderr)
    cert=target/'E47_INTRINSIC_SPACETIME_UNMARKED_CERTIFICATE.json'
    data=json.loads(cert.read_text()) if cert.exists() else {}
    check('intrinsic_source_execution',p.returncode==0 and data.get('status')=='PASS' and all(data.get('checks',{}).values()),{'exit_code':p.returncode,'certificate':data})
    # Source curvature program writes fixed /mnt/data paths. Relocate only string paths.
    src=ROOT/'sources/e47_bures_fisher_curvature_validation.py'
    code=src.read_text()
    dest=OUT/'bures';dest.mkdir(exist_ok=True)
    transformed=code.replace('/mnt/data/',str(dest)+'/')
    pth=dest/'run_relocated.py';pth.write_text(transformed)
    p=subprocess.run([sys.executable,str(pth)],cwd=dest,text=True,capture_output=True,timeout=180)
    (dest/'execution.log').write_text(p.stdout+p.stderr)
    cert=dest/'e47_bures_fisher_curvature_certificate.json'
    data=json.loads(cert.read_text()) if cert.exists() else {}
    check('curvature_source_execution',p.returncode==0 and bool(data),{'exit_code':p.returncode,'adaptation':'output path literals only'})
    if data:
        old=json.loads((ROOT/'sources/e47_bures_fisher_curvature_certificate.json').read_text())
        errors=[abs(v['Rscalar']-w['Rscalar']) for v,w in zip(data['sample_points'],old['sample_points'])]
        check('curvature_receipt_reproduction',len(errors)==4 and max(errors)<1e-3,{'max_scalar_curvature_difference':max(errors)})
        check('SLD_Bures_relation',data['bures_sld']['Fisher_minus_4Bures_F_norm']<1e-10,data['bures_sld'])
        check('information_leaf_rank4',data['conclusion']['bures_leaf_rank4_all_samples'])
        check('block_identity_after_pullback',data['conclusion']['block_identity_closes_after_SLD_pullback'])
    return data


def record_full_attachment():
    path=OUT/'spacetime/E47_spacetime_execution.json'
    data=json.loads(path.read_text())
    check('attachment_all_four_sections',set(data)=={'einstein','bures','qutip','eidolon'})
    check('attachment_full_block_identity',data['einstein']['identity_holds'])
    check('attachment_full_contraction',data['qutip']['L_inf']>1-1e-8)
    check('attachment_geodesic_model_execution',data['eidolon']['plane_force_is_zero'] and np.isfinite(data['eidolon']['L_inf']),data['eidolon'])
    engine=module(ROOT/'sources/eidolon_engine.py','survey_eidolon_engine')
    check('engine_spectral_parity',engine.DIM_H==125 and engine.DIM_E47==47 and engine.DIM_COMP==78 and engine.DELTA==11664 and abs(engine.OMEGA_C-47/125)<1e-15)
    return data

def full_attachment():
    p=subprocess.run([sys.executable,str(ROOT/'run_spacetime.py')],cwd=ROOT,text=True,capture_output=True,timeout=180)
    (OUT/'spacetime_execution.log').write_text(p.stdout+p.stderr)
    check('attachment_full_execution_exit',p.returncode==0,p.returncode)
    if p.returncode==0: record_full_attachment()


def main():
    errors=[]
    for label,fn in [('lexical_and_core',validate),('attachment_components',execute_attachment_components),('geometry',source_geometry),('full_attachment',full_attachment)]:
        print('Running',label,flush=True)
        try: fn()
        except Exception as e:
            errors.append({'component':label,'error':repr(e)})
            check(label+'_execution',False,repr(e))
    # Completeness is a separate fact from correctness of executed checks.
    gaps=[{'component':'full_platform_inventory','status':'NOT_CLAIMED','reason':'Targeted relevant-asset survey; no exhaustive platform crawl.'}]
    report={'schema':'E47-LEXICAL-VALIDATION-1.0','status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','scope':'Executed lexical, algebraic, source parity and geometry checks','in_toto_status':'COMPLETE_FOR_DECLARED_EXECUTABLE_SCOPE' if all(c['status']=='PASS' for c in checks) else 'INCOMPLETE','checks':checks,'pass_count':sum(c['status']=='PASS' for c in checks),'fail_count':sum(c['status']=='FAIL' for c in checks),'gaps':gaps,'errors':errors,'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},'evidence_policy':'Source evidence classes retained; executed checks are numerical/symbolic software evidence only.'}
    (OUT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({k:report[k] for k in ['status','pass_count','fail_count','in_toto_status','errors']},indent=2))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':
    raise SystemExit(main())
