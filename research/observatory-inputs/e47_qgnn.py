"""E47 QGNN: fixed-carrier graph-signal model and exact quantum-state simulator.
Run: OPENBLAS_NUM_THREADS=1 python e47_qgnn.py
Dependencies: numpy, scipy. Results are synthetic, noiseless simulations.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import minimize


def herm(a): return (a + a.conj().T) / 2

def normalize(x):
    n = np.linalg.norm(x, axis=0, keepdims=True)
    if np.any(n < 1e-12):
        raise ValueError('Zero or negligible encoded/projected input; supply another input or explicit baseline.')
    return x / n


def construct():
    eye = np.eye(5)
    m = np.arange(2, -3, -1)
    jp = np.zeros((5, 5), complex)
    for i in range(4): jp[i, i+1] = np.sqrt(6-m[i+1]*(m[i+1]+1))
    spin = [(jp+jp.T)/2, (jp-jp.T)/(2j), np.diag(m)]
    def embed(a, site):
        f = [eye, eye, eye]; f[site] = a
        return np.kron(np.kron(f[0], f[1]), f[2])
    jt = [sum(embed(a,s) for s in range(3)) for a in spin]
    c = herm(sum(a@a for a in jt))
    ev, v = np.linalg.eigh(c)
    selected = np.isclose(ev,6,atol=1e-9)|np.isclose(ev,30,atol=1e-9)
    b = v[:,selected]; p = b@b.conj().T
    k = (c-6*np.eye(125))@(c-30*np.eye(125))
    gamma = herm(np.eye(125)-k@k/99144)
    cycle = np.roll(eye,1,axis=0)+np.roll(eye,-1,axis=0)
    axes = [embed(cycle,s)/2 for s in range(3)]
    coords = np.array(list(np.ndindex(5,5,5)))
    # Three edge types and a node-position potential; coordinates are part of input structure.
    potential = np.diag(np.cos(2*np.pi*coords[:,0]/5)+0.7*np.sin(2*np.pi*coords[:,2]/5))
    raw = axes+[potential]
    generators = []
    for a in raw:
        h = herm(b.conj().T@a@b)
        h /= max(np.linalg.norm(h,2),1e-12)
        generators.append(h)
    observable = herm(b.conj().T@np.diag(np.sin(2*np.pi*coords[:,1]/5))@b)
    observable /= np.linalg.norm(observable,2)
    return dict(C=c,K=k,Gamma=gamma,B=b,P=p,eigenvalues=ev,
                generators=generators,observable=observable,adjacency=2*sum(axes))


class E47QGNN:
    """Exact compressed simulation. Inputs: complex (125,batch) node amplitudes.
    Angles: (depth,4). Each gate lifts to exp(-i theta P A P) on the carrier.
    Returns expectation values; classical optimizer supplies trainability.
    """
    def __init__(self, core, depth=1):
        self.core=core; self.depth=depth
        self.spec=[np.linalg.eigh(h) for h in core['generators']]

    def encode(self, signals):
        x=np.asarray(signals,dtype=complex)
        if x.ndim==1: x=x[:,None]
        if x.ndim!=2 or x.shape[0]!=125 or not np.all(np.isfinite(x)):
            raise ValueError('Expected finite amplitudes with shape (125,batch).')
        x=normalize(x)
        z=self.core['B'].conj().T@x
        probability=np.sum(abs(z)**2,axis=0)
        return normalize(z),probability

    def evolve(self, angles, z, jacobian=False):
        angles=np.asarray(angles,float).reshape(self.depth,len(self.spec))
        y=z.copy(); deriv=np.zeros((angles.size,)+z.shape,complex)
        for n,theta in enumerate(angles.ravel()):
            e,v=self.spec[n%len(self.spec)]
            u=(v*np.exp(-1j*theta*e))@v.conj().T
            y=u@y
            if jacobian:
                deriv=np.einsum('ab,pbc->pac',u,deriv)
                deriv[n] += -1j*self.core['generators'][n%len(self.spec)]@y
        return (y,deriv) if jacobian else y

    def predict(self, angles, z, jacobian=False):
        out=self.evolve(angles,z,jacobian)
        y,dy=out if jacobian else (out,None)
        oy=self.core['observable']@y
        pred=np.sum(y.conj()*oy,axis=0).real
        if not jacobian: return pred
        grad=2*np.einsum('pab,ab->pb',dy.conj(),oy).real
        return pred,grad


def validate_and_train():
    d=construct(); b,p,g=d['B'],d['P'],d['Gamma']
    eye=np.eye(125); q=eye-p; rng=np.random.default_rng(47)
    checks={}; metrics={}
    def check(name, value, tol=1e-9):
        metrics[name]=float(value); checks[name]=bool(value<tol)
    check('casimir_spectrum_error',np.max(abs(d['eigenvalues']-np.repeat([0,2,6,12,20,30,42],[1,9,25,28,27,22,13]))))
    checks['rank_47']=b.shape==(125,47)
    check('projector_error',np.linalg.norm(p@p-p,2))
    check('contraction_radius_error',abs(np.linalg.norm(g-p,2)-15/17))
    checks['torus_375_edges']=int(np.sum(d['adjacency']>0)/2)==375
    checks['torus_degree_6']=bool(np.all(np.sum(d['adjacency']>0,axis=0)==6))
    model=E47QGNN(d)
    theta=np.array([0.34,-0.27,0.21,0.48])
    u47=model.evolve(theta,np.eye(47,dtype=complex))
    u=b@u47@b.conj().T+q
    check('unitarity_error',np.linalg.norm(u.conj().T@u-eye,2))
    check('trainable_gate_leakage',np.linalg.norm(q@u@p,2))
    check('filter_gate_commutator',np.linalg.norm(g@u-u@g,2))
    # Noncommuting graph generators support a nontrivial variational family.
    comm=max(np.linalg.norm(a@h-h@a,2) for a in d['generators'] for h in d['generators'])
    metrics['maximum_generator_commutator']=float(comm)
    checks['noncommuting_generators']=bool(comm>1e-3)
    for n in [1,7,30]:
        sequence=np.linalg.matrix_power(u@g,n)
        target=b@np.linalg.matrix_power(u47,n)@b.conj().T
        check(f'learned_depth_{n}_exact_bound_error',abs(np.linalg.norm(sequence-target,2)-(15/17)**n),1e-8)
    # Explicit unitary dilation on seven data qubits and one flag ancilla.
    # Padding filter zero excludes unused addresses 125,126,127 from success.
    g128=np.zeros((128,128),complex); g128[:125,:125]=g
    ge,gv=np.linalg.eigh(herm(g128))
    s=(gv*np.sqrt(np.maximum(0,1-ge**2)))@gv.conj().T
    dilation=np.block([[g128,s],[s,-g128]])
    check('eight_qubit_dilation_unitarity',np.linalg.norm(dilation.conj().T@dilation-np.eye(256),2),1e-8)
    x=normalize(rng.normal(size=125)+1j*rng.normal(size=125))
    state=np.zeros(256,complex); state[:125]=x
    branch=(dilation@state)[:128]
    check('ancilla_zero_branch_error',np.linalg.norm(branch[:125]-g@x))
    metrics['one_step_success_probability']=float(np.vdot(branch,branch).real)
    xn=np.linalg.matrix_power(g,220)@x; px=p@x
    check('220_step_projection_error',np.linalg.norm(xn-px),1e-9)
    metrics['220_step_conditional_fidelity']=float(abs(np.vdot(normalize(px),normalize(xn)))**2)
    metrics['220_step_success_probability']=float(np.vdot(xn,xn).real)
    # A deterministic physical alternative: reset every failed filter outcome to alpha in E47.
    alpha=b[:,0]; defect=herm(eye-g@g)
    rho=np.outer(x,x.conj()); output=g@rho@g+np.trace(defect@rho).real*np.outer(alpha,alpha.conj())
    check('reset_channel_trace_error',abs(np.trace(output)-1))
    checks['reset_channel_positive']=bool(np.linalg.eigvalsh(herm(output)).min()>-1e-9)
    check('reset_channel_kernel_fixed_error',np.linalg.norm(g@np.outer(alpha,alpha.conj())@g-np.outer(alpha,alpha.conj())))
    # Synthetic teacher-student regression, 64 train / 32 unseen inputs.
    signals=rng.normal(size=(125,96))+1j*rng.normal(size=(125,96))
    z,success=model.encode(signals)
    labels=model.predict(theta,z)
    train=z[:,:64]; target=labels[:64]
    def objective(t):
        pred,jac=model.predict(t,train,True); residual=pred-target
        return float(np.mean(residual**2)),2*jac@residual/len(residual)
    t0=np.zeros(4); initial,_=objective(t0)
    probe=np.array([0.1,-0.2,0.05,0.3]); _,analytic=objective(probe)
    h=1e-6; numeric=np.array([(objective(probe+np.eye(4)[i]*h)[0]-objective(probe-np.eye(4)[i]*h)[0])/(2*h) for i in range(4)])
    check('analytic_gradient_error',np.max(abs(numeric-analytic)),1e-8)
    fit=minimize(objective,t0,jac=True,method='L-BFGS-B',options={'maxiter':200,'ftol':1e-15,'gtol':1e-10})
    held=float(np.mean((model.predict(fit.x,z[:,64:])-labels[64:])**2))
    checks['training_loss_decreased']=bool(fit.fun<initial*1e-4)
    checks['held_out_teacher_recovery']=held<1e-8
    metrics.update(initial_train_mse=initial,final_train_mse=float(fit.fun),held_out_mse=held,
                   optimizer_success=bool(fit.success),optimizer_message=str(fit.message),
                   learned_angles=fit.x.tolist(),teacher_angles=theta.tolist(),
                   mean_exact_projection_success_probability=float(success.mean()))
    # Verify zero-overlap handling explicitly.
    try: model.encode(q@x)
    except ValueError: checks['zero_overlap_rejected']=True
    else: checks['zero_overlap_rejected']=False
    report={'status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'metrics':metrics,
            'scope':'Double-precision ideal statevector/unitary simulation and synthetic teacher regression; no QPU run or application benchmark.',
            'versions':{'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    root=Path(__file__).resolve().parent
    (root/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    np.savez(root/'trained_model.npz',angles=fit.x,teacher_angles=theta)
    print(json.dumps(report,indent=2))
    if not all(checks.values()): raise SystemExit(1)

if __name__=='__main__': validate_and_train()
