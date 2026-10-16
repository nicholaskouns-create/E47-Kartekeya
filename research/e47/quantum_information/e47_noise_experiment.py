import torch, math, platform

torch.set_num_threads(2)
dtype = torch.complex128
I5 = torch.eye(5, dtype=dtype)
I = torch.eye(125, dtype=dtype)
m = torch.arange(2, -3, -1, dtype=torch.float64)
sp = torch.zeros((5, 5), dtype=dtype)
for i in range(1, 5):
    mi = m[i].item()
    sp[i - 1, i] = math.sqrt((2 - mi) * (2 + mi + 1))
sx = (sp + sp.conj().T) / 2
sy = (sp - sp.conj().T) / (2j)
sz = torch.diag(m).to(dtype)

def kron3(a, b, c): return torch.kron(torch.kron(a, b), c)
J = [kron3(s,I5,I5)+kron3(I5,s,I5)+kron3(I5,I5,s) for s in (sx,sy,sz)]
C = sum((j @ j for j in J), torch.zeros_like(I))
K = (C - 6*I) @ (C - 30*I)
lam, U = torch.linalg.eigh(C)
mask = ((lam - 6).abs() < 1e-7) | ((lam - 30).abs() < 1e-7)
P = U[:, mask] @ U[:, mask].conj().T


def basis(i,j,k):
    a=torch.zeros(5,dtype=dtype); b=a.clone(); c=a.clone()
    a[i]=1; b[j]=1; c[k]=1
    return kron3(a,b,c)

v0=P@basis(0,2,4)
v1=P@basis(0,2,3)
psi=(v0/torch.linalg.vector_norm(v0)+v1/torch.linalg.vector_norm(v1))/math.sqrt(2)
rho=torch.outer(psi,psi.conj())

def metrics(x):
    fidelity=(psi.conj()@x@psi).real.item()
    survival=torch.trace(P@x).real.item()
    purity=torch.trace(x@x).real.item()
    return fidelity,survival,purity

def channel(x,A,theta):
    up=torch.linalg.matrix_exp(-1j*theta*A)
    um=up.conj().T
    return (up@x@up.conj().T+um@x@um.conj().T)/2

collective=J[2]/6
local=kron3(sz,I5,I5)/2
print('torch', torch.__version__, 'python', platform.python_version())
for label,A in [('collective_z',collective),('local_z',local)]:
    for theta in [0.1,0.3,0.6,1.0]:
        print(label, theta, metrics(channel(rho,A,theta)))
