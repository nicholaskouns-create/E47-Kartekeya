"""E47 exact SU(2) spectral kernel: NumPy implementation.
H = spin-2 tensor cube, dim 125; ker K has rank 47.
Requires numpy. No model training or quantum hardware execution is implied.
"""
import numpy as np

def spin_two():
    m = np.arange(2, -3, -1, dtype=float)
    z = np.diag(m).astype(complex)
    plus = np.zeros((5, 5), dtype=complex)
    for i in range(1, 5):
        mi = m[i]
        plus[i-1, i] = np.sqrt((2-mi)*(2+mi+1))
    x = (plus + plus.conj().T)/2
    y = (plus - plus.conj().T)/(2j)
    return x, y, z

def e47():
    eye = np.eye(5, dtype=complex)
    js = spin_two()
    total = [sum(np.kron(np.kron(a,b),c) for a,b,c in (
        (j,eye,eye),(eye,j,eye),(eye,eye,j))) for j in js]
    casimir = sum(j @ j for j in total)
    ident = np.eye(125, dtype=complex)
    k = (casimir-6*ident) @ (casimir-30*ident)
    gamma = ident - (k @ k)/99144
    eigenvalues, vectors = np.linalg.eigh(casimir)
    mask = np.isclose(eigenvalues,6,atol=1e-8) | np.isclose(eigenvalues,30,atol=1e-8)
    projector = vectors[:,mask] @ vectors[:,mask].conj().T
    assert mask.sum() == 47
    assert np.linalg.norm(projector @ projector-projector,2) < 1e-10
    assert np.linalg.norm(gamma @ projector-projector,2) < 1e-10
    return casimir, k, gamma, projector

def contract(state, steps=220):
    _, _, gamma, projector = e47()
    v = np.asarray(state, dtype=complex)
    if v.shape != (125,):
        raise ValueError("Expected a 125-component state")
    for _ in range(steps):
        v = gamma @ v
    return v, projector @ state

def test():
    c,k,g,p = e47()
    assert np.linalg.matrix_rank(p,tol=1e-8)==47
    for n in (1, 5, 20):
        error = np.linalg.norm(np.linalg.matrix_power(g,n)-p,2)
        assert np.isclose(error,(15/17)**n,atol=1e-9)
    print("E47 exact spectral checks PASS")

if __name__ == "__main__":
    test()
