import numpy as np
import pandas as pd

# Requires natal_1965_graph_laplacian.csv from the prior reconstruction.
L = pd.read_csv("natal_1965_graph_laplacian.csv", index_col=0).to_numpy(float)
L = (L+L.T)/2
lam,V = np.linalg.eigh(L)
N=len(lam); I=np.eye(N)

P = V[:,:4] @ V[:,:4].T
Q = I-P
G = Q @ L @ Q
G = (G+G.T)/2

mu=np.linalg.eigvalsh(G)
pos=mu[mu>1e-10]
mu_min,mu_max=pos[0],pos[-1]
eps=2/(mu_min+mu_max)
rho=(mu_max-mu_min)/(mu_max+mu_min)
Gamma=I-eps*G

assert np.linalg.norm(P@P-P,2) < 1e-12
assert np.linalg.norm(G@P,2) < 1e-12
assert np.linalg.norm(Gamma@P-P,2) < 1e-12

for n in [1,5,10,20,40]:
    observed=np.linalg.norm(np.linalg.matrix_power(Gamma,n)-P,2)
    predicted=rho**n
    print(n, observed, predicted, abs(observed-predicted))

print("rank(P) =", np.linalg.matrix_rank(P,tol=1e-10))
print("epsilon* =",eps)
print("rho* =",rho)
