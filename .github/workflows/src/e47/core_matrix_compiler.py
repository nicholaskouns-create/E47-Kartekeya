"""
E47 Core Matrix Algebra & SU(2) Spectral Kernel Compiler
Refactored, type-annotated, and verified for exact spectral projections.
"""
import numpy as np
from typing import Dict, Tuple, Any

def get_spin_generators(s: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generates SU(2) spin generators J_x, J_y, J_z for spin s."""
    d = int(2 * s + 1)
    m = np.linspace(s, -s, d)
    Jz = np.diag(m)
    
    Jplus = np.zeros((d, d), dtype=complex)
    for i in range(d - 1):
        m_val = m[i + 1]
        Jplus[i, i + 1] = np.sqrt(s * (s + 1) - m_val * (m_val + 1))
        
    Jminus = Jplus.conj().T
    Jx = 0.5 * (Jplus + Jminus)
    Jy = -0.5j * (Jplus - Jminus)
    return Jx, Jy, Jz

def build_triple_tensor_generators(s: float = 2.0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Constructs total angular momentum operators on V_s^{\\otimes 3} (Dim = 125 for s=2)."""
    Jx, Jy, Jz = get_spin_generators(s)
    I = np.eye(int(2 * s + 1), dtype=complex)
    
    Jx_tot = np.kron(np.kron(Jx, I), I) + np.kron(np.kron(I, Jx), I) + np.kron(np.kron(I, I), Jx)
    Jy_tot = np.kron(np.kron(Jy, I), I) + np.kron(np.kron(I, Jy), I) + np.kron(np.kron(I, I), Jy)
    Jz_tot = np.kron(np.kron(Jz, I), I) + np.kron(np.kron(I, Jz), I) + np.kron(np.kron(I, I), Jz)
    
    return Jx_tot, Jy_tot, Jz_tot

def compute_casimir_operator(s: float = 2.0) -> np.ndarray:
    """Calculates total Casimir operator C = J_x^2 + J_y^2 + J_z^2."""
    Jx_tot, Jy_tot, Jz_tot = build_triple_tensor_generators(s)
    return Jx_tot @ Jx_tot + Jy_tot @ Jy_tot + Jz_tot @ Jz_tot

def construct_e47_projector(C: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Constructs polynomial kernel K = (C - 6I)(C - 30I) and exact P47 projector."""
    I125 = np.eye(125, dtype=complex)
    K = (C - 6.0 * I125) @ (C - 30.0 * I125)
    
    eigvals, eigvecs = np.linalg.eigh(C)
    # Select eigenspaces corresponding to j=2 (lambda=6) and j=5 (lambda=30)
    idx_47 = np.where(np.isclose(eigvals, 6.0, atol=1e-5) | np.isclose(eigvals, 30.0, atol=1e-5))[0]
    
    E47_basis = eigvecs[:, idx_47]
    P47 = E47_basis @ E47_basis.conj().T
    return K, P47
