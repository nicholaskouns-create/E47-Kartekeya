import numpy as np
from math import sqrt

j = 2
m = np.arange(j, -j - 1, -1, dtype=float)
Jz = np.diag(m)
Jp = np.zeros((2*j + 1, 2*j + 1), dtype=complex)

for col, mc in enumerate(m):
    mp = mc + 1
    if mp <= j:
        rows = np.where(np.isclose(m, mp))[0]
        if rows.size:
            Jp[rows[0], col] = np.sqrt(j*(j+1) - mc*(mc+1))

Jm = Jp.conj().T
Jx = (Jp + Jm) / 2
Jy = (Jp - Jm) / (2j)
I5 = np.eye(5, dtype=complex)
kron3 = lambda a,b,c: np.kron(np.kron(a,b),c)

JxT = kron3(Jx,I5,I5)+kron3(I5,Jx,I5)+kron3(I5,I5,Jx)
JyT = kron3(Jy,I5,I5)+kron3(I5,Jy,I5)+kron3(I5,I5,Jy)
JzT = kron3(Jz,I5,I5)+kron3(I5,Jz,I5)+kron3(I5,I5,Jz)

C = JxT@JxT + JyT@JyT + JzT@JzT
evals, _ = np.linalg.eigh(C)

spec = np.array([0,2,6,12,20,30,42], float)
mult = [int(np.sum(np.isclose(evals, x, atol=1e-9))) for x in spec]

I = np.eye(125)
K = (C-6*I)@(C-30*I)
kevals, U = np.linalg.eigh(K)
mask = np.isclose(kevals,0,atol=1e-8)
P = U[:,mask]@U[:,mask].conj().T

mu = np.trace(C).real/125
var = np.trace((C-mu*I)@(C-mu*I)).real/125

q = kevals**2
q = q[q>1e-12]
eps = 2/(q.min()+q.max())
Gamma = I-eps*(K@K)

print("spec(C) =", spec.tolist())
print("mult(C) =", mult)
print("mu =", mu)
print("sigma^2 =", var)
print("dim ker(K) =", int(mask.sum()))
print("Omega_c =", int(mask.sum())/125)
print("||P^2-P||_2 =", np.linalg.norm(P@P-P,2))
print("||KP||_2 =", np.linalg.norm(K@P,2))
print("eps* =", eps)
print("rho* =", (q.max()-q.min())/(q.max()+q.min()))
print("||Gamma^250-P||_2 =", np.linalg.norm(np.linalg.matrix_power(Gamma,250)-P,2))
