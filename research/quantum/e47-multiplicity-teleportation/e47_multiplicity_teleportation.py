#!/usr/bin/env python3
"""E47 spin-2 multiplicity-subsystem teleportation: reproducible numerical certificate.

Requires numpy and scipy. Reconstructs a 125x125 total-spin Casimir from
three spin-2 factors; builds the selected 25-dimensional spin-2 isotypic
sector as a gauge 5 x logical 5 isometry; verifies the 25-branch exact ququint
teleportation protocol and protection against collective SU(2) noise.

A mathematical/simulator proof, NOT a physical hardware teleportation claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scipy.linalg import expm

ATOL = 5e-10
D = 5

def spin_two():
    m = np.arange(2, -3, -1)
    jp = np.zeros((5,5), complex)
    for row, mr in enumerate(m):
        for col, mc in enumerate(m):
            if mr == mc+1:
                jp[row,col] = np.sqrt(6 - mc*(mc+1))
    jm = jp.conj().T
    jx = (jp+jm)/2
    jy = (jp-jm)/(2j)
    jz = np.diag(m).astype(complex)
    return jx,jy,jz,jp,jm

def triple_total():
    js = spin_two()
    I = np.eye(5, dtype=complex)
    ops=[]
    for j in js:
        ops.append(np.kron(np.kron(j,I),I)+np.kron(np.kron(I,j),I)+np.kron(np.kron(I,I),j))
    return ops

def basis_25(C, jz, jm):
    # C commutes with Jz, so its M=2 block contains exactly five J=2 copies.
    indices=np.flatnonzero(np.isclose(np.real(np.diag(jz)),2))
    ev, u=np.linalg.eigh(C[np.ix_(indices,indices)])
    chosen=np.flatnonzero(np.isclose(ev,6,atol=1e-8))
    assert len(chosen)==5, f"expected five highest-weight copies, got {len(chosen)}"
    high=np.zeros((125,5),dtype=complex)
    high[indices,:]=u[:,chosen]
    # Deterministic numerical eigenspaces up to phases/unitaries, which do not
    # affect any invariant being certified.
    blocks=[high]
    cur=high
    for m in [2,1,0,-1]:
        cur=(jm@cur)/np.sqrt((2+m)*(2-m+1))
        blocks.append(cur)
    return np.column_stack(blocks)

def random_pure(rng,d):
    v=rng.normal(size=d)+1j*rng.normal(size=d)
    return v/np.linalg.norm(v)

def bell_measurement_branch(psi,a,b):
    """Project explicit three-qudit |psi>_S |Phi>_AB onto a Bell basis.

    This independently implements the physical tensor contraction instead of
    merely evaluating the algebraic expected correction formula.
    """
    d=len(psi)
    omega=np.exp(2j*np.pi/d)
    phi=np.eye(d,dtype=complex)/np.sqrt(d)
    # B_ab[j,k] = omega^(a*j) delta_(k,j+b) / sqrt(d).
    bell=np.zeros((d,d),dtype=complex)
    for j in range(d):
        bell[j,(j+b)%d]=omega**(a*j)/np.sqrt(d)
    three=np.einsum('i,jk->ijk',psi,phi)
    return np.einsum('ij,ijk->k',bell.conj(),three)

def recover(v,a,b):
    d=len(v); omega=np.exp(2j*np.pi/d)
    # Z^a X^-b, the inverse of X^b Z^-a.
    return (omega**(a*np.arange(d)))*np.roll(v,-b)

def test_teleportation(rng,d,trials=12):
    errors=[]; p_errors=[]; twirl_errors=[]; recovery_density_errors=[]
    inputs=[np.eye(d,dtype=complex)[i] for i in range(d)]
    inputs.extend([np.ones(d,dtype=complex)/np.sqrt(d), random_pure(rng,d)])
    inputs.extend(random_pure(rng,d) for _ in range(trials))
    for psi in inputs:
        twirled=np.zeros((d,d),complex)
        recovered_avg=np.zeros((d,d),complex)
        probs=[]
        for a in range(d):
            for b in range(d):
                vb=bell_measurement_branch(psi,a,b)
                p=np.vdot(vb,vb).real
                probs.append(p)
                twirled += np.outer(vb,vb.conj())
                vout=recover(vb,a,b)
                recovered_avg += np.outer(vout,vout.conj())
                errors.append(float(np.linalg.norm(vout-psi/d)))
        p_errors.append(float(max(abs(p-1/d**2) for p in probs)))
        p_errors.append(float(abs(sum(probs)-1)))
        twirl_errors.append(float(np.linalg.norm(twirled-np.eye(d)/d,ord='fro')))
        recovery_density_errors.append(float(np.linalg.norm(recovered_avg-np.outer(psi,psi.conj()),ord='fro')))
    return {"dimension":d,"input_states":len(inputs),"branches_per_state":d*d,
        "max_branch_amplitude_error":max(errors),"max_probability_error":max(p_errors),
        "max_no_message_depolarization_error":max(twirl_errors),
        "max_corrected_channel_error":max(recovery_density_errors)}

def run():
    rng=np.random.default_rng(20261111)
    jx,jy,jz,jp,jm=triple_total()
    C=jx@jx+jy@jy+jz@jz
    evals=np.linalg.eigvalsh(C)
    spec=[0,2,6,12,20,30,42]
    counts=[int(np.count_nonzero(np.isclose(evals,v,atol=1e-8))) for v in spec]
    I125=np.eye(125,dtype=complex)
    K=(C-6*I125)@(C-30*I125)
    e,u=np.linalg.eigh(C)
    P47=(u[:,np.isclose(e,6,atol=1e-8)] @ u[:,np.isclose(e,6,atol=1e-8)].conj().T +
         u[:,np.isclose(e,30,atol=1e-8)] @ u[:,np.isclose(e,30,atol=1e-8)].conj().T)
    W=basis_25(C,jz,jm)
    P2=W@W.conj().T
    # Spin-2 gauge factor uses the same ordering M=2,1,0,-1,-2.
    sx,sy,sz,_,_=spin_two()
    su2_errors=[]; channel_errors=[]; leakage_errors=[]; projected_errors=[]
    # Each SU2 rotation acts on gauge but leaves logical five-dimensional subsystem untouched.
    for index in range(10):
        axis=rng.normal(size=3);axis/=np.linalg.norm(axis)
        theta=float(rng.uniform(-2.8,2.8))
        U125=expm(-1j*theta*(axis[0]*jx+axis[1]*jy+axis[2]*jz))
        Ug=expm(-1j*theta*(axis[0]*sx+axis[1]*sy+axis[2]*sz))
        U25=np.kron(Ug,np.eye(5))
        su2_errors.append(float(np.linalg.norm(W.conj().T@U125@W-U25,ord=2)))
        logical=random_pure(rng,5)
        gauge=random_pure(rng,5)
        encoded=W@np.kron(gauge,logical)
        moved=U125@encoded
        projected=W.conj().T@moved
        leakage_errors.append(float(np.linalg.norm((I125-P2)@moved)))
        projected_errors.append(float(np.linalg.norm(projected-U25@np.kron(gauge,logical))))
        joint=projected.reshape(5,5)
        rho_log=joint.conj().T@joint  # equivalent to partial trace over gauge up to index convention
        # joint.conj().T@joint yields conjugate of |psi><psi| depending index; actual: sum_g v[g,i] conj(v[g,j])
        rho_log=joint.T@joint.conj()
        channel_errors.append(float(np.linalg.norm(rho_log-np.outer(logical,logical.conj()),ord='fro')))
    t5=test_teleportation(rng,5)
    t2=test_teleportation(rng,2)
    result={"certificate":"E47-MULTIPLICITY-TELEPORT-2026-11-11", "algorithm":"NumPy/SciPy deterministic full-carrier reconstruction and qudit Bell-branch simulation",
      "seed":20261111,"carrier_dimension":125,"casimir_eigenvalues":spec,"casimir_sector_dimensions":counts,
      "rank_P47":int(np.rint(np.trace(P47).real)),"rank_P2":int(np.rint(np.trace(P2).real)),
      "selected_E47_complement_rank":int(np.rint(np.trace(I125-P47).real)),
      "max_projector_idempotence_error":float(np.linalg.norm(P47@P47-P47,ord='fro')),
      "max_KP47_error":float(np.linalg.norm(K@P47,ord='fro')),
      "isometry_25_error":float(np.linalg.norm(W.conj().T@W-np.eye(25),ord='fro')),
      "J2_sector_error":float(np.linalg.norm(C@W-6*W,ord='fro')),
      "max_collective_rotation_intertwiner_error":max(su2_errors),
      "max_encoded_state_sector_leakage":max(leakage_errors),
      "max_encoded_rotation_prediction_error":max(projected_errors),
      "max_logical_state_error_after_collective_rotation":max(channel_errors),
      "rotation_trials":len(su2_errors),"logical_ququint_teleportation":t5,
      "logical_qubit_teleportation":t2,
      "evidence_boundary":"Exact analytic protocol and floating-point simulated implementation; not hardware/experimental verification; collective SU(2) noise only for multiplicity protection; no claim of physical matter transport or wormholes."}
    metric_keys=["max_projector_idempotence_error","max_KP47_error","isometry_25_error","J2_sector_error","max_collective_rotation_intertwiner_error","max_encoded_state_sector_leakage","max_encoded_rotation_prediction_error","max_logical_state_error_after_collective_rotation"]
    result["status"]="PASS" if (counts==[1,9,25,28,27,22,13] and result["rank_P47"]==47 and result["rank_P2"]==25 and all(result[k]<ATOL for k in metric_keys) and all(all(v<ATOL for k,v in t.items() if k.startswith('max_')) for t in [t5,t2])) else "FAIL"
    return result

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', default='e47_multiplicity_teleportation_certificate.json')
    args=parser.parse_args()
    res=run()
    Path(args.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(res,indent=2,sort_keys=True))
    if res['status'] != 'PASS':raise SystemExit(1)
if __name__=='__main__': main()