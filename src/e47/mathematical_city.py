"""Mathematical City: E47 quantum spin system analysis.

This module implements the canonical E47 quantum formalism for analyzing
three-coupled spin-2 systems and their projective subspaces.
"""

from __future__ import annotations
import numpy as np
import scipy.linalg as la


def spin_matrices(j: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate Jx, Jy, Jz spin-j matrices.
    
    Parameters
    ----------
    j : float
        Spin quantum number.
        
    Returns
    -------
    Jx, Jy, Jz : np.ndarray
        Spin component matrices of shape (2j+1, 2j+1).
    """
    m = np.arange(j, -j - 1, -1, dtype=float)
    d = 2*j + 1
    Jz = np.diag(m)
    Jp = np.zeros((d, d), complex)
    for col, mc in enumerate(m):
        rows = np.where(np.isclose(m, mc+1))[0]
        if rows.size:
            Jp[int(rows[0]), col] = np.sqrt(j*(j+1) - mc*(mc+1))
    Jm = Jp.conj().T
    return (Jp+Jm)/2, (Jp-Jm)/(2j), Jz


def kron3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Three-way Kronecker product: a ⊗ b ⊗ c.
    
    Parameters
    ----------
    a, b, c : np.ndarray
        Matrices to tensor product.
        
    Returns
    -------
    result : np.ndarray
        Kronecker product of a, b, and c.
    """
    return np.kron(np.kron(a, b), c)


def compute_e47_projector(j: float = 2) -> tuple[np.ndarray, dict]:
    """Compute the E47 projector and canonical subspace.
    
    Constructs the three-spin Heisenberg Hamiltonian and computes
    the projector onto the kernel subspace of the Casimir operator.
    
    Parameters
    ----------
    j : float, optional
        Spin quantum number (default: 2 for spin-2 system).
        
    Returns
    -------
    P : np.ndarray
        Projector onto E47 subspace, shape (d³, d³).
    info : dict
        Metadata including dimension, trace, and norms.
    """
    d = 2*j + 1
    I5 = np.eye(5, dtype=complex)
    I = np.eye(d**3, dtype=complex)
    
    # Generate total spin operators
    Jx, Jy, Jz = spin_matrices(j)
    JT = []
    for J in (Jx, Jy, Jz):
        JT.append(kron3(J, I5, I5) + kron3(I5, J, I5) + kron3(I5, I5, J))
    
    # Casimir operator C = J²
    C = sum(J @ J for J in JT)
    C = (C + C.conj().T) / 2
    
    # K = (C - 6I)(C - 30I)
    K = (C - 6*I) @ (C - 30*I)
    K = (K + K.conj().T) / 2
    K2 = K @ K
    
    # Eigendecompose K²
    w, V = la.eigh(K2)
    E = V[:, w < 1e-8]
    P = E @ E.conj().T
    
    # Compute statistics
    trace_P = np.trace(P).real
    info = {
        "dimension": round(trace_P),
        "dimension_ratio": trace_P / (d**3),
        "projector_idempotent_error": la.norm(P @ P - P, 2),
        "kernel_norm": la.norm(K @ P, 2),
        "eigenvalues_zero": np.sum(w < 1e-8),
        "eigenvalues_nonzero": np.sum(w > 1e-8),
    }
    
    return P, info


def compute_kraus_operators(j: float = 2) -> tuple[np.ndarray, np.ndarray, dict]:
    """Compute Kraus operators for quantum channel.
    
    Generates the dephasing channel M0, M1 and verifies completeness.
    
    Parameters
    ----------
    j : float, optional
        Spin quantum number (default: 2).
        
    Returns
    -------
    M0, M1 : np.ndarray
        Kraus operators.
    info : dict
        Channel statistics.
    """
    d = 2*j + 1
    I = np.eye(d**3, dtype=complex)
    
    # Compute K operator
    I5 = np.eye(5, dtype=complex)
    Jx, Jy, Jz = spin_matrices(j)
    JT = []
    for J in (Jx, Jy, Jz):
        JT.append(kron3(J, I5, I5) + kron3(I5, J, I5) + kron3(I5, I5, J))
    
    C = sum(J @ J for J in JT)
    C = (C + C.conj().T) / 2
    K = (C - 6*I) @ (C - 30*I)
    K = (K + K.conj().T) / 2
    K2 = K @ K
    
    # Eigenvalues for channel construction
    w = np.linalg.eigvalsh(K2)
    nz = w[w > 1e-8]
    eps = 1 / nz.max()
    
    # Time parameter
    t = 5 / nz.min()
    
    # Kraus operators
    M0 = la.expm(-t * K2)
    Q = I - M0.conj().T @ M0
    q, U = la.eigh((Q + Q.conj().T) / 2)
    M1 = (U * np.sqrt(np.clip(q, 0, None))) @ U.conj().T
    
    info = {
        "completeness_error": la.norm(M0.conj().T @ M0 + M1.conj().T @ M1 - I, 2),
        "time_parameter": t,
        "epsilon": eps,
    }
    
    return M0, M1, info


def analyze_state_preparation(j: float = 2, seed: int = 47) -> dict:
    """Analyze postselected state preparation.
    
    Parameters
    ----------
    j : float, optional
        Spin quantum number (default: 2).
    seed : int, optional
        Random seed (default: 47).
        
    Returns
    -------
    results : dict
        Preparation statistics including fidelity and probability.
    """
    d = 2*j + 1
    I = np.eye(d**3, dtype=complex)
    I5 = np.eye(5, dtype=complex)
    
    # Get projector and Kraus operators
    P, _ = compute_e47_projector(j)
    M0, M1, _ = compute_kraus_operators(j)
    
    # Random initial state
    rng = np.random.default_rng(seed)
    psi = rng.normal(size=d**3) + 1j * rng.normal(size=d**3)
    psi /= la.norm(psi)
    
    # Target state
    target = P @ psi
    target /= la.norm(target)
    
    # Apply channel and postselect
    out = M0 @ psi
    p = np.vdot(out, out).real
    out /= np.sqrt(p)
    
    fidelity = abs(np.vdot(target, out))**2
    haar_avg_prob = np.trace(M0.conj().T @ M0).real / (d**3)
    
    return {
        "postselection_probability": p,
        "postselected_fidelity": fidelity,
        "haar_average_probability": haar_avg_prob,
    }


def run_e47_analysis(j: float = 2, verbose: bool = True) -> dict:
    """Run complete E47 analysis pipeline.
    
    Parameters
    ----------
    j : float, optional
        Spin quantum number (default: 2).
    verbose : bool, optional
        Print results to stdout (default: True).
        
    Returns
    -------
    results : dict
        Complete analysis results.
    """
    # Compute projector
    P, proj_info = compute_e47_projector(j)
    
    # Compute Kraus operators
    M0, M1, kraus_info = compute_kraus_operators(j)
    
    # Analyze state preparation
    prep_info = analyze_state_preparation(j)
    
    results = {
        "projector": proj_info,
        "kraus": kraus_info,
        "preparation": prep_info,
    }
    
    if verbose:
        print(f"E47 Analysis (j={j}):")
        print(f"  dim E47 = {proj_info['dimension']}")
        print(f"  Omega = {proj_info['dimension_ratio']:.6f}")
        print(f"  ||P² - P||₂ = {proj_info['projector_idempotent_error']:.2e}")
        print(f"  ||KP||₂ = {proj_info['kernel_norm']:.2e}")
        print(f"  Kraus completeness = {kraus_info['completeness_error']:.2e}")
        print(f"  postselection probability = {prep_info['postselection_probability']:.6f}")
        print(f"  postselected fidelity = {prep_info['postselected_fidelity']:.6f}")
        print(f"  Haar-average probability = {prep_info['haar_average_probability']:.6f}")
    
    return results


if __name__ == "__main__":
    results = run_e47_analysis(j=2, verbose=True)
