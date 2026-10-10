"""Reproducible workbench adapters over the canonical E47 core (E1/E2).

Browser dynamics operate on seven sector weights, sufficient for the displayed
norm, energy and occupancy observables. They do not reconstruct state phases.
"""
from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull, HalfspaceIntersection

from .su2_kernel import build_e47_operators
from .projector import construct_e47_projector
from .contraction import build_contraction

VALUES = np.array([0, 2, 6, 12, 20, 30, 42], dtype=float)
COUNTS = np.array([1, 9, 25, 28, 27, 22, 13])
Q = ((VALUES - 6) * (VALUES - 30)) ** 2
SELECTED = Q == 0
GAP = 11664
QMAX = 186624
EPSILON = 1 / 99144


@lru_cache(maxsize=1)
def matrices():
    ops = build_e47_operators()
    C, K = ops.casimir.full(), ops.kernel.full()
    P = construct_e47_projector(ops).projector.full()
    return C, K, P, build_contraction(K, EPSILON)


def validate():
    C, K, P, G = matrices()
    I = np.eye(125)
    checks = []

    def check(name, actual, expected, tolerance=0):
        difference = float(np.max(np.abs(np.asarray(actual) - np.asarray(expected))))
        checks.append(dict(name=name, actual=actual, expected=expected,
                           residual=difference, tolerance=tolerance, passed=difference <= tolerance))

    eigenvalues = np.linalg.eigvalsh(C)
    counts = [int(np.sum(np.abs(eigenvalues - v) < 1e-7)) for v in VALUES]
    check('Casimir sector dimensions', counts, COUNTS.tolist())
    check('Projector rank', int(np.linalg.matrix_rank(P, tol=1e-7)), 47)
    check('Projector trace', float(np.trace(P).real), 47, 1e-9)
    check('Casimir Hermiticity', float(np.linalg.norm(C-C.conj().T, 2)), 0, 1e-10)
    check('Projector idempotence', float(np.linalg.norm(P@P-P, 2)), 0, 1e-10)
    check('Kernel annihilation', float(np.linalg.norm(K@P, 2)), 0, 1e-8)
    polynomial = C@(C-2*I)@(C-12*I)@(C-20*I)@(C-31*I)@(C-42*I)/1814400
    check('Polynomial projector agreement', float(np.linalg.norm(P-polynomial, 2)), 0, 1e-8)
    check('Complement contraction radius', float(np.max(np.abs(np.linalg.eigvalsh(G-P)))), 15/17, 1e-9)
    rng = np.random.default_rng(47)
    state = rng.normal(size=125)+1j*rng.normal(size=125)
    state /= np.linalg.norm(state)
    target = P@state
    current = np.linalg.matrix_power(G, 220)@state
    check('220-step matrix convergence', float(np.linalg.norm(current-target)), 0, 2e-12)
    # Independently compare the matrix iterate to the compressed observables.
    lam, basis = np.linalg.eigh(C)
    coeff = np.abs(basis.conj().T@state)**2
    weights = [float(coeff[np.abs(lam-v)<1e-7].sum()) for v in VALUES]
    experiment = simulate(weights, steps=220)
    check('Compressed/matrix probability agreement', experiment['records'][-1]['probability'], float(np.linalg.norm(current)**2), 1e-10)
    geo = geometry()
    check('Crystal V/E/F topology', [len(geo['vertices']), geo['edge_count'], len(geo['faces'])], [90,135,47])
    check('Crystal Euler characteristic', geo['euler'], 2)
    check('Every edge has two incident faces', geo['edge_incidence_minmax'], [2,2])
    return dict(schema='E47-WORKBENCH-VALIDATION-1.0', evidence=['E1','E2'],
                status='pass' if all(c['passed'] for c in checks) else 'fail', checks=checks,
                scope='Finite-dimensional numerical reconstruction; no hardware or empirical certification.')


def simulate(weights, *, steps=220, epsilon=EPSILON, mode='discrete', horizon=15):
    w = np.asarray(weights, dtype=float)
    if w.shape != (7,) or not np.all(np.isfinite(w)) or np.any(w<0) or not np.isfinite(w.sum()) or w.sum()<=0:
        raise ValueError('Supply seven finite nonnegative sector weights with positive total.')
    if isinstance(steps, bool) or not isinstance(steps, (int, np.integer)) or not 1<=steps<=1000:
        raise ValueError('steps must be an integer from 1 to 1000')
    if mode not in {'discrete','continuous'}:
        raise ValueError('Unknown evolution mode')
    if not np.isfinite(epsilon) or not 0<epsilon<2/QMAX:
        raise ValueError('epsilon must lie strictly between 0 and 2/q_max')
    if not np.isfinite(horizon) or not 0<horizon<=100:
        raise ValueError('horizon must lie in (0,100]')
    w = w/w.sum()
    a = float(w[SELECTED].sum())
    rho = float(np.max(np.abs(1-epsilon*Q[~SELECTED])))
    records=[]
    for n in range(steps+1):
        tau=n*horizon/steps if mode=='continuous' else n*epsilon*GAP
        factors=(1-epsilon*Q)**n if mode=='discrete' else np.exp(-Q*tau/GAP)
        evolved=w*factors**2
        b=float(evolved[~SELECTED].sum())
        prob=a+b
        occupancy=a/prob if prob>0 else None
        effective=float(np.dot(evolved[~SELECTED],Q[~SELECTED])/b) if b>0 else None
        records.append(dict(n=n, tau=tau, error=float(np.sqrt(b)),
                            bound=float(np.sqrt(max(0,1-a))*(rho**n if mode=='discrete' else np.exp(-tau))),
                            probability=prob, occupancy=occupancy,
                            fidelity=occupancy if a>0 else None,
                            lambda_eff=effective, energy=float(np.dot(evolved,Q)/prob) if prob>0 else None,
                            occupancy_derivative_tau=2*(effective/GAP)*occupancy*(1-occupancy) if effective is not None and occupancy is not None else None))
    return dict(schema='E47-WORKBENCH-RUN-1.0', version='1.0.0', evidence='E2',
                inputs=dict(weights=w.tolist(),steps=int(steps),epsilon=epsilon,mode=mode,horizon=horizon),
                rho=rho,kernel_weight=a,records=records,
                scope='Sector norm observables; conditional fidelity is undefined for zero selected weight.')


@lru_cache(maxsize=1)
def geometry():
    labels=[]; normals=[]
    for J,js in [(2,list(range(5))),(5,[3,4])]:
        for r,j12 in enumerate(js):
            for m in range(-J,J+1):
                z=m/(J+1)
                phi=2*np.pi*(r/len(js)+m/47+(0 if J==2 else 1/94))
                normals.append([np.sqrt(1-z*z)*np.cos(phi),np.sqrt(1-z*z)*np.sin(phi),z])
                labels.append(dict(J=J,j12=j12,m=m))
    normals=np.array(normals)
    vertices=HalfspaceIntersection(np.column_stack((normals,-np.ones(47))),np.zeros(3)).intersections
    hull=ConvexHull(vertices)
    faces=[]; edges=Counter(); incident={}
    for i,normal in enumerate(normals):
        ids=np.where(np.abs(vertices@normal-1)<1e-8)[0]
        points=vertices[ids]; center=points.mean(axis=0)
        u=points[0]-center; u/=np.linalg.norm(u); v=np.cross(normal,u)
        order=np.argsort(np.arctan2((points-center)@v,(points-center)@u))
        face=[int(k) for k in ids[order]];faces.append(face)
        for j,left in enumerate(face):
            edge=tuple(sorted((left,face[(j+1)%len(face)])))
            edges[edge]+=1; incident.setdefault(edge,[]).append(i)
    adjacency=np.zeros((47,47))
    for neighbours in incident.values():
        if len(neighbours)==2:
            a,b=neighbours;adjacency[a,b]=adjacency[b,a]=1
    lap=np.diag(adjacency.sum(axis=1))-adjacency
    eigenvalues=np.linalg.eigvalsh(lap)
    radii=np.linalg.norm(vertices,axis=1)
    sphericity=np.pi**(1/3)*(6*hull.volume)**(2/3)/hull.area
    return dict(vertices=vertices.tolist(),normals=normals.tolist(),faces=faces,labels=labels,
                edges=[list(e) for e in sorted(edges)],edge_count=len(edges),euler=len(vertices)-len(edges)+len(faces),
                edge_incidence_minmax=[min(edges.values()),max(edges.values())],
                face_histogram=dict(sorted(Counter(map(len,faces)).items())),
                adjacency=adjacency.astype(int).tolist(),laplacian_spectrum=eigenvalues.tolist(),
                metrics=dict(volume=float(hull.volume),area=float(hull.area),sphericity=float(sphericity),
                             radius_min=float(radii.min()),radius_max=float(radii.max())),
                scope='Halfspace geometry reconstructed from supplied measure_e47.py. Face labels are a chosen mapping, not a derivation of spatial physics.')


def build_bundle(root):
    root=Path(root)
    canonical=json.loads((root/'website/data/e47-canonical-kernel.json').read_text())
    sources=json.loads((root/'research/e47/workbench-inputs/provenance.json').read_text())
    comparison_path=root/'research/e47/workbench-inputs/full_x5f_three_x5f_system_x5f_comparison.csv'
    bundle=dict(schema='E47-WORKBENCH-BUNDLE-1.0',version='1.0.0',canonical=canonical['canonical'],
                geometry=geometry(),validation=validate(),sources=sources,
                comparison_audit=dict(status='unresolved parameter provenance',reported_rho=0.9946643266360042,
                                      canonical_rho=15/17,
                                      inferred_small_step=(1-0.9946643266360042)/GAP,
                                      sha256=hashlib.sha256(comparison_path.read_bytes()).hexdigest(),
                                      note='Reported radius is compatible with a smaller step, but the CSV supplies no generator or epsilon. Inferred epsilon is a hypothesis. Material rows are reduced models, not measurements.'),
                reference_run=simulate(COUNTS/125))
    target=root/'website/interfaces/e47-research-workbench/data.json'
    target.write_text(json.dumps(bundle,indent=2,allow_nan=False)+'\n')
    return bundle


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Write portable JSON bundle or geometry NPZ')
    parser.add_argument('--geometry-only',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    if args.geometry_only:
        geo=geometry()
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            if args.output.suffix=='.npz':
                np.savez_compressed(args.output,vertices=geo['vertices'],normals=geo['normals'],labels=[[x['J'],x['j12'],x['m']] for x in geo['labels']])
            else: args.output.write_text(json.dumps(geo,indent=2)+'\n')
        print(json.dumps(geo['metrics'],indent=2))
    else:
        bundle=build_bundle(root)
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True)
            args.output.write_text(json.dumps(bundle,indent=2,allow_nan=False)+'\n')
        print(f"Workbench: {bundle['validation']['status']}; {len(bundle['validation']['checks'])} checks")
        if bundle['validation']['status']!='pass': raise SystemExit(1)


if __name__=='__main__': main()
