"""
Pytest Precision Suite for E47 Spectral Kernel and Invariants
"""
import pytest
import numpy as np
from src.e47.core_matrix_compiler import compute_casimir_operator, construct_e47_projector

def test_clebsch_gordan_closure():
    m_j = {0: 1, 1: 3, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}
    total_dim = sum(m * (2*j + 1) for j, m in m_j.items())
    assert total_dim == 125

def test_p47_projector_identities():
    C = compute_casimir_operator(s=2.0)
    K, P47 = construct_e47_projector(C)
    
    # Check Hermiticity
    assert np.linalg.norm(P47 - P47.conj().T) < 1e-12
    # Check Idempotence
    assert np.linalg.norm(P47 @ P47 - P47) < 1e-12
    # Check Exact Trace
    tr_val = np.real(np.trace(P47))
    assert abs(tr_val - 47.0) < 1e-12
    # Check Coherence Ratio
    assert abs((tr_val / 125.0) - 0.376) < 1e-12

def test_5adic_valuations():
    assert 5**(-3) == 1.0 / 125.0
    assert 5**(0) == 1.0
