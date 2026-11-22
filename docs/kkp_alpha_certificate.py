"""KKP-R alpha from Omega_c. Executable exact + finite-matrix certificate."""
import sympy as sp
import numpy as np
phi = (1 + sp.sqrt(5))/2
Omega = sp.Rational(47,125)
alpha = sp.simplify(Omega/phi**2)
F = sp.Matrix([[1,1],[1,0]])
assert sp.simplify(phi**2-phi-1)==0
assert sp.simplify((F-phi*sp.eye(2)).det())==0
assert sp.simplify(alpha-(141-47*sp.sqrt(5))/250)==0
assert sp.simplify(sp.sqrt(sp.Rational(30,6))-(phi+1/phi))==0
P=np.diag(np.r_[np.ones(47),np.zeros(78)])
assert np.allclose(P@P,P)
assert np.isclose(np.trace(P),47)
eigenvalues,eigenvectors=np.linalg.eigh(np.array([[1.,1.],[1.,0.]]))
e=eigenvectors[:,-1]
Q=np.outer(e,e)
w=float(phi**(-2))
A=np.kron(P,w*Q)
A2=np.kron(P,w*np.eye(2))
assert np.isclose(np.trace(A)/125,float(alpha))
assert np.isclose(np.trace(A2)/250,float(alpha))
assert np.isclose(np.trace(A2)/125,2*float(alpha))
assert not np.isclose(float(2*alpha),float(alpha))
print("alpha =",sp.N(alpha,60))
print("exact identity and composite traces: PASS")
print("Uniqueness as a physical gravitational correction: NOT established.")
