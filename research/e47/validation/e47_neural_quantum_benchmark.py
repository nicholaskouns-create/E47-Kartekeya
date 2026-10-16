#!/usr/bin/env python3
"""E47 classical neural and postselected quantum statevector benchmark.
No quantum hardware or Qiskit required. All amplitudes complex128.
"""
import json, time, argparse
from pathlib import Path
import numpy as np
import torch
from scipy.linalg import eigh

def spin2():
    j=2; m=np.arange(j,-j-1,-1,dtype=float)
    z=np.diag(m).astype(complex)
    plus=np.zeros((5,5),complex)
    for col,mm in enumerate(m):
        if col: plus[col-1,col]=np.sqrt((j-mm)*(j+mm+1))
    x=(plus+plus.conj().T)/2
    y=(plus-plus.conj().T)/(2j)
    return x,y,z

def build():
    I=np.eye(5,dtype=complex); axes=spin2()
    J=[]
    for a in axes:
        J.append(np.kron(np.kron(a,I),I)+np.kron(np.kron(I,a),I)+np.kron(np.kron(I,I),a))
    C=sum(j@j for j in J)
    vals,U=eigh(C)
    # numerical diagonalization: spectral functions avoid high-degree polynomial roundoff
    spin=np.rint((np.sqrt(1+4*vals)-1)/2).astype(int)
    cas=spin*(spin+1)
    kval=(cas-6)*(cas-30)
    gam=1-kval.astype(float)**2/99144
    selected=np.isin(spin,[2,5])
    P=(U[:,selected]@U[:,selected].conj().T)
    G=(U*gam)@U.conj().T
    return C,P,G,U,gam,spin

def bench(n=220, seed=47):
    C,P,G,U,gam,spin=build()
    rng=np.random.default_rng(seed)
    psi=rng.normal(size=125)+1j*rng.normal(size=125)
    psi/=np.linalg.norm(psi)
    target=P@psi; q=np.vdot(target,target).real
    target/=np.sqrt(q)
    times={}; traces={}
    t=time.perf_counter(); v=psi.copy()
    for k in range(n+1):
        if k in [0,1,5,10,25,50,100,220,n]:
            traces[str(k)]={'numpy_residual':float(np.linalg.norm(v-P@psi)), 'projected_fidelity':float(abs(np.vdot(target,v))**2/np.vdot(v,v).real)}
        if k<n: v=G@v
    times['numpy_seconds']=time.perf_counter()-t
    t=time.perf_counter(); Gt=torch.from_numpy(np.ascontiguousarray(G)); vt=torch.from_numpy(psi.copy())
    for _ in range(n): vt=Gt@vt
    times['pytorch_seconds']=time.perf_counter()-t
    torch_err=float(np.linalg.norm(vt.numpy()-v))
    # Quantum statevector simulation: each application of Gamma is a valid
    # postselected ancilla branch, with block unitary [[G,sqrt(I-GÂ²)],
    # [sqrt(I-GÂ²),-G]]. Implemented in the common eigenbasis of G.
    # All-success joint probability = ||Gamma^n psi||Â², NOT 1.
    t=time.perf_counter(); amps=U.conj().T@psi
    quantum_trace={}
    for k in range(n+1):
        if k in [0,1,5,10,25,50,100,220,n]:
            branch=U@amps
            success=float(np.vdot(branch,branch).real)
            normalized=branch/np.sqrt(success)
            quantum_trace[str(k)]={'all_success_probability':success,
                'conditional_fidelity_to_projected_input':float(abs(np.vdot(target,normalized))**2),
                'difference_from_numpy_branch':float(np.linalg.norm(branch-(np.linalg.matrix_power(G,k)@psi)))}
        if k<n: amps*=gam
    times['quantum_statevector_seconds']=time.perf_counter()-t
    # Explicit ancilla unitary unitarity check in eigenbasis
    sqrt=np.sqrt(np.maximum(0,1-gam**2))
    B=np.block([[np.diag(gam),np.diag(sqrt)],[np.diag(sqrt),-np.diag(gam)]])
    unitary_err=float(np.linalg.norm(B.conj().T@B-np.eye(250),ord=2))
    eigenvalues,counts=np.unique(spin,return_counts=True)
    exact_r=15/17
    errors={str(k):float(exact_r**k) for k in [0,1,5,10,25,50,100,220,n]}
    out={'configuration':{'iterations':n,'seed':seed,'dimension':125,'kernel_rank':int(np.rint(np.trace(P).real)),'backend':'CPU complex128'},
       'spin_sector_dimensions':dict(zip(map(str,eigenvalues),map(int,counts))),
       'checks':{'casimir_hermiticity_error':float(np.linalg.norm(C-C.conj().T)),
           'projector_idempotence_error':float(np.linalg.norm(P@P-P)),
           'projector_commutator_error':float(np.linalg.norm(P@G-G@P)),
           'gamma_eigenvalue_radius_complement':float(max(abs(gam[~np.isin(spin,[2,5])]))),
           'exact_rate':exact_r,'operator_norm_error_at_n':float(exact_r**n),
           'numpy_torch_branch_difference':torch_err,
           'quantum_block_unitarity_error':unitary_err,
           'numpy_quantum_final_branch_difference':float(np.linalg.norm(v-U@amps))},
       'information_retention':{'initial_projected_probability':float(q),
           'discarded_squared_norm':float(1-q),
           'final_unconditional_branch_probability':float(np.vdot(v,v).real),
           'final_conditional_fidelity':float(abs(np.vdot(target,v))**2/np.vdot(v,v).real),
           'warning':'Projection preserves selected amplitudes but does not guarantee task-relevant information retention.'},
       'time_seconds':times,'numpy_trace':traces,'quantum_trace':quantum_trace,'theoretical_operator_norm_errors':errors,
       'caveat':'Quantum simulation is an ideal postselected ancilla-unitary statevector simulation, not a quantum circuit gate-count or hardware benchmark. Timings across these implementations are not equivalent workloads.'}
    return out

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--iterations',type=int,default=220);parser.add_argument('--output',default='e47_results.json');a=parser.parse_args()
    result=bench(a.iterations)
    Path(a.output).write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))