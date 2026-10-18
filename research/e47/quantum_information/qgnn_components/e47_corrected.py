"""E47 packed encoding, coupled basis, measurement and CPTP relaxation.
Run: OPENBLAS_NUM_THREADS=1 python e47_corrected.py
Qiskit Statevector is the quantum circuit simulator; no quantum device used.
"""
from pathlib import Path
import json, platform, importlib.metadata
import numpy as np
from scipy.linalg import eigh
from qiskit import QuantumCircuit, qpy, transpile, qasm3
from qiskit.quantum_info import Statevector, DensityMatrix

OUT=Path(__file__).resolve().parent
TOL=2e-10
checks=[]
def check(name,error,tol=TOL):
    error=float(error)
    checks.append(dict(name=name,error=error,tolerance=tol,passed=error<=tol))
    if error>tol: raise AssertionError(checks[-1])
def err(a,b): return np.linalg.norm(a-b)
def embed(a):
    b=np.zeros((128,128),complex); b[:125,:125]=a; return b

def operators():
    m=np.arange(2,-3,-1); plus=np.zeros((5,5),complex)
    for i in range(1,5): plus[i-1,i]=np.sqrt(6-m[i]*(m[i]+1))
    spin=[(plus+plus.T)/2,(plus-plus.T)/(2j),np.diag(m)]
    eye=np.eye(5)
    local=[[np.kron(np.kron(s if k==0 else eye,s if k==1 else eye),s if k==2 else eye) for s in spin] for k in range(3)]
    total=[sum(local[k][a] for k in range(3)) for a in range(3)]
    C=sum(x@x for x in total)
    C12=sum((local[0][a]+local[1][a])@(local[0][a]+local[1][a]) for a in range(3))
    return C,C12,total

def coupled_basis(C,C12,Jz):
    # Commuting observables resolve every (j,j12,m). Irrational coefficients
    # avoid degeneracy. Phases are fixed by largest product-basis component >0.
    _,V=eigh(C+np.sqrt(2)*C12+np.sqrt(3)*Jz)
    values=lambda A: np.real(np.einsum('ij,ij->j',V.conj(),A@V))
    cas,inter,mag=values(C),values(C12),values(Jz)
    labels=[(int(round((np.sqrt(1+4*c)-1)/2)),int(round((np.sqrt(1+4*t)-1)/2)),int(round(m))) for c,t,m in zip(cas,inter,mag)]
    order=sorted(range(125),key=lambda i: labels[i])
    V=V[:,order].astype(complex); labels=[labels[i] for i in order]
    for i in range(125):
        z=V[np.argmax(abs(V[:,i])),i]; V[:,i]*=np.conj(z)/abs(z)
    return V,labels

def membership_circuit(selected):
    qc=QuantumCircuit(8,name='E47_membership')
    for index in selected:
        zeros=[k for k in range(7) if not (int(index)>>k)&1]
        for k in zeros: qc.x(k)
        qc.mcx(list(range(7)),7)
        for k in zeros: qc.x(k)
    return qc

def make_channel(gamma,alpha):
    A=np.diag(gamma).astype(complex)
    Bs=[]
    for k in np.flatnonzero(abs(gamma)<1-1e-14):
        b=np.zeros((128,128),complex); b[alpha,k]=np.sqrt(1-gamma[k]**2); Bs.append(b)
    return [A]+Bs

def main():
    rng=np.random.default_rng(470125)
    C,C12,J=operators(); V,labels=coupled_basis(C,C12,J[2])
    expected={0:1,1:9,2:25,3:28,4:27,5:22,6:13}
    actual={j:sum(l[0]==j for l in labels) for j in range(7)}
    check('Casimir sector dimensions',actual!=expected,0)
    check('125 distinct coupled labels',len(set(labels))!=125,0)
    lam=np.array([j*(j+1) for j,t,m in labels])
    check('coupled basis orthonormal',err(V.conj().T@V,np.eye(125)))
    check('Casimir diagonalization',err(C@V,V*lam))
    check('intermediate Casimir labels',err(C12@V,V*np.array([t*(t+1) for j,t,m in labels])))
    check('magnetic labels',err(J[2]@V,V*np.array([m for j,t,m in labels])))
    W=np.eye(128,dtype=complex); W[:125,:125]=V.conj().T
    check('seven-qubit Schur unitary',err(W.conj().T@W,np.eye(128)))
    selected=np.array([i for i,l in enumerate(labels) if l[0] in (2,5)])
    p=np.zeros(128); p[selected]=1; P=np.diag(p); Q=np.eye(128)-P
    check('projector rank 47',abs(np.trace(P)-47),0)
    K=(C-6*np.eye(125))@(C-30*np.eye(125))
    Pprod=W.conj().T@P@W
    check('kernel annihilation',err(embed(K)@Pprod,0),1e-8)
    check('projector idempotence',err(Pprod@Pprod,Pprod))
    for a in range(3): check(f'collective generator {a} invariance',err(Pprod@embed(J[a])-embed(J[a])@Pprod,0))
    check('three unused states rejected',np.sum(p[125:]),0)
    basis_qc=QuantumCircuit(7); basis_qc.unitary(W,list(range(7)),label='coupled_basis')
    syndrome=membership_circuit(selected)
    full=QuantumCircuit(8); full.compose(basis_qc,range(7),inplace=True); full.compose(syndrome,inplace=True)
    # Exhaustive circuit truth table, including the 3 unused states.
    wrong=0.; data_disturbance=0.
    for k in range(128):
        initial=np.zeros(256,complex); initial[k]=1
        final=Statevector(initial).evolve(syndrome).data
        target=np.zeros(256,complex); target[k+128*int(p[k])]=1
        wrong=max(wrong,err(final,target))
    check('all 128 packed membership inputs',wrong)
    psi=rng.normal(size=125)+1j*rng.normal(size=125); psi/=np.linalg.norm(psi)
    initial=np.zeros(256,complex); initial[:125]=psi
    final=Statevector(initial).evolve(full).data
    packed=W@np.r_[psi,np.zeros(3)]
    check('full basis transform and ancilla state',err(final,np.r_[(1-p)*packed,p*packed]))
    success=float(np.vdot(psi,Pprod[:125,:125]@psi).real)
    check('Born probability',abs(np.linalg.norm(final[128:])**2-success))
    # Inverse basis transform after tagging: branch equals P_product |psi>.
    decode=QuantumCircuit(8); decode.unitary(W.conj().T,range(7))
    decoded=Statevector(final).evolve(decode).data
    check('successful branch equals physical projector',err(decoded[128:],Pprod@np.r_[psi,np.zeros(3)]))
    # Tracing ancilla implements nonselective projective measurement.
    measured=np.outer(final[:128],final[:128].conj())+np.outer(final[128:],final[128:].conj())
    rho=np.outer(packed,packed.conj())
    check('nonselective measurement channel',err(measured,P@rho@P+Q@rho@Q))
    check('nonselective measurement trace',abs(np.trace(measured)-1))
    # CPTP relaxation: fixed E47, spectral attenuation elsewhere, reset to alpha.
    gamma=np.zeros(128); gamma[:125]=1-((lam-6)*(lam-30))**2/99144
    alpha=int(selected[0]); As=make_channel(gamma,alpha)
    completeness=sum(a.conj().T@a for a in As)
    check('relaxation Kraus completeness',err(completeness,np.eye(128)))
    B=np.diag(gamma); tau=np.zeros((128,128),complex); tau[alpha,alpha]=1
    def update(r): return B@r@B.conj().T+np.trace((np.eye(128)-B.conj().T@B)@r)*tau
    evolved=update(rho)
    # Simulate a flagged attenuation instrument and a measurement/feed-forward
    # reset, without constructing a 16384 x 16384 dense superoperator.
    D=np.diag(np.sqrt(np.maximum(0,1-gamma**2)))
    dilation=np.block([[B,-D],[D,B]])
    check('attenuation dilation unitary',err(dilation.conj().T@dilation,np.eye(256)))
    attenuator=QuantumCircuit(8); attenuator.unitary(dilation,range(8))
    flagged=Statevector(np.r_[packed,np.zeros(128)]).evolve(attenuator).data
    keep,reset=flagged[:128],flagged[128:]
    reset_circuit=QuantumCircuit(7); reset_circuit.reset(range(7))
    for bit in range(7):
        if (alpha>>bit)&1: reset_circuit.x(bit)
    reset_prob=float(np.vdot(reset,reset).real)
    reset_rho=np.outer(reset,reset.conj())/reset_prob
    simulated_reset=DensityMatrix(reset_rho).evolve(reset_circuit).data
    sim=np.outer(keep,keep.conj())+reset_prob*simulated_reset
    check('Qiskit flagged circuit and reset equals update',err(sim,evolved))
    with open(OUT/'attenuation_and_reset.qpy','wb') as f: qpy.dump([attenuator,reset_circuit],f)
    check('relaxation trace',abs(np.trace(evolved)-1))
    check('relaxation Hermiticity',err(evolved,evolved.conj().T))
    check('relaxation positivity',max(0,-np.linalg.eigvalsh(evolved).min()))
    code=rng.normal(size=47)+1j*rng.normal(size=47); code/=np.linalg.norm(code)
    v=np.zeros(128,complex); v[selected]=code; code_rho=np.outer(v,v.conj())
    check('arbitrary E47 state fixed',err(update(code_rho),code_rho))
    maxerr=0.; minval=0.
    for _ in range(10):
        z=rng.normal(size=(128,4))+1j*rng.normal(size=(128,4)); r=z@z.conj().T; r/=np.trace(r)
        s=update(r); maxerr=max(maxerr,abs(np.trace(s)-1)); minval=min(minval,np.linalg.eigvalsh(s).min())
    check('ten mixed states trace',maxerr)
    check('ten mixed states positivity',max(0,-minval))
    rho_star=15/17
    check('complement amplitude bound',abs(max(abs(gamma[(1-p).astype(bool)]))-rho_star))
    qpop=lambda r: float(np.trace(Q@r).real)
    check('one-step leakage bound',max(0,qpop(evolved)-rho_star**2*qpop(rho)))
    r=rho.copy()
    for _ in range(220): r=update(r)
    limit=P@rho@P+qpop(rho)*tau
    check('220-step density limit',err(r,limit))
    # Worst-case complement: spin 3, where gamma=15/17.
    k=next(i for i,l in enumerate(labels) if l[0]==3)
    v=np.zeros(128); v[k]=1; worst=np.outer(v,v)
    check('sharp leakage rate',abs(qpop(update(worst))-rho_star**2))
    # Physical graph-neighborhood update: nonnegative normalized mixture of
    # reduced unitary interactions, then local unitary, then CPTP relaxation.
    # Demo a two-node product input and a diagonal entangling interaction.
    phase=np.exp(-1j*0.03*np.outer(np.arange(128)/127,np.arange(128)/127))
    pair=packed[:,None]*v[None,:]*phase
    reduced=pair@pair.conj().T
    aggregate=0.6*rho+0.4*reduced
    graph_out=update(aggregate)
    check('graph mixture trace',abs(np.trace(graph_out)-1))
    check('graph mixture positivity',max(0,-np.linalg.eigvalsh(graph_out).min()))
    np.savez_compressed(OUT/'e47_operators.npz',C=C,C12=C12,V=V,W=W,P_packed=P,P_product=Pprod,gamma=gamma)
    mapping=[dict(index=i,bits=format(i,'07b'),j=j,j12=t,m=m,selected=bool(p[i])) for i,(j,t,m) in enumerate(labels)]
    mapping += [dict(index=i,bits=format(i,'07b'),unused=True,selected=False) for i in range(125,128)]
    (OUT/'encoding.json').write_text(json.dumps(mapping,indent=2))
    with open(OUT/'basis_and_measurement.qpy','wb') as f: qpy.dump(full,f)
    # Export executable OpenQASM 3 with the actual unitary synthesized to u/cx.
    native=transpile(full,basis_gates=['u','cx'],optimization_level=1)
    native.add_register(__import__('qiskit').ClassicalRegister(1,'result'))
    native.measure(7,0)
    (OUT/'basis_and_measurement.qasm').write_text(qasm3.dumps(native))
    # Check the synthesized gate sequence as well, before measurement.
    native_sv=Statevector(initial).evolve(native.remove_final_measurements(inplace=False)).data
    # QASM3 includes global phase; allow no phase adjustment here.
    check('synthesized u/cx circuit state',err(native_sv,final),1e-9)
    report=dict(status='PASS' if all(c['passed'] for c in checks) else 'FAIL',checks=checks,
        simulator='Qiskit Statevector and DensityMatrix circuit simulation',hardware_run=False,
        versions={k:importlib.metadata.version(k) for k in ['numpy','scipy','qiskit']},
        python=platform.python_version(),seed=470125,selected_dimension=47,carrier_dimension=125,
        amplitude_rate=rho_star,population_rate=rho_star**2,random_state_success_probability=success,
        synthesized_gate_counts=dict(native.count_ops()),synthesized_depth=native.depth())
    (OUT/'validation.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
