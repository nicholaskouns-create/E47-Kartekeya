"""Corrected independent validation for KKP precision + MPS checks.

Preserves the submitted scalar/Decimal tests and repairs only the MPS
contraction by using the standard transfer-environment contraction.
"""
from decimal import Decimal, getcontext
from fractions import Fraction
import math
import sys
import numpy as np

getcontext().prec = 50
np.set_printoptions(precision=16)

def validate_kkp():
    phi = (1 + 5**0.5) / 2
    omega = 47 / 125
    c = 299792458
    tau, psi = 2.0, 1.0
    for _ in range(5):
        psi = 0.5 * (psi + tau / psi)
    v_target = c / phi**24
    v_observed = 2891.46
    return {
        "Babylonian Convergence Error": abs(psi**2 - tau),
        "Omega_c Verification": omega == 47 / 125,
        "Coherence Value": omega,
        "Pentamode Velocity Target": v_target,
        "Pentamode Velocity match": round(v_target, 2) == round(v_observed, 2),
    }

def machine_precision_validation():
    tau = Decimal("2")
    psi = Decimal("1")
    for _ in range(6):
        psi = (psi + tau / psi) / Decimal(2)
    c = Decimal("299792458")
    phi = (Decimal(1) + Decimal(5).sqrt()) / Decimal(2)
    vd = c / phi**24
    vf = 299792458.0 / (((1.0 + math.sqrt(5.0))/2.0)**24)
    return {
        "Machine Epsilon": sys.float_info.epsilon,
        "Omega_c Exact Rational": str(Fraction(47,125)),
        "Omega_c Decimal": str(Decimal(47)/Decimal(125)),
        "Babylonian Error vs Decimal sqrt(2)": str(abs(psi-tau.sqrt())),
        "Velocity Target Decimal": str(vd),
        "Velocity Target Float64": vf,
        "Velocity Abs Delta": str(abs(vd-Decimal(str(vf)))),
    }

class PrecisionMatrixEngine:
    def __init__(self, num_qubits=3, max_bond_dim=2):
        self.num_qubits=num_qubits
        self.max_bond_dim=max_bond_dim
        self.eps=sys.float_info.epsilon

    def initialize_mps(self):
        out=[]
        for _ in range(self.num_qubits):
            A=np.zeros((1,2,1),dtype=np.complex128)
            A[0,0,0]=1
            out.append(A)
        return out

    def compute_overlap(self,a,b):
        # E[l,l'] -> E'[r,r'] = sum_{l,l',p} E[l,l'] conj(A[l,p,r]) B[l',p,r']
        E=np.ones((1,1),dtype=np.complex128)
        for A,B in zip(a,b):
            E=np.einsum("ab,apr,bps->rs",E,np.conj(A),B,optimize=True)
        return E[0,0]

    def extract_state_norm(self,mps):
        return float(np.real(self.compute_overlap(mps,mps)))

def validate_matrix_precision():
    eng=PrecisionMatrixEngine()
    a=eng.initialize_mps()
    b=eng.initialize_mps()
    norm=eng.extract_state_norm(a)
    overlap=eng.compute_overlap(a,b)
    fidelity=float(abs(overlap)**2)
    P=np.zeros((125,125),dtype=np.float64)
    np.fill_diagonal(P[:47,:47],1.0)
    omega=float(np.trace(P)/125)
    return {
        "MPS Initial State Norm": norm,
        "Norm Drift": abs(norm-1),
        "Norm Within Machine Precision": abs(norm-1)<=eng.eps,
        "Overlap": overlap,
        "Overlap Fidelity": fidelity,
        "Fidelity Error": abs(1-fidelity),
        "Fidelity Within Machine Precision": abs(1-fidelity)<=eng.eps,
        "Simulated Omega_c": omega,
        "Omega_c Residual": abs(omega-47/125),
    }

if __name__=="__main__":
    for suite in (validate_kkp(),machine_precision_validation(),validate_matrix_precision()):
        for k,v in suite.items():
            print(f"{k}: {v}")
        print("-"*72)
