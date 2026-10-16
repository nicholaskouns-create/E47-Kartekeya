import torch, math, json, platform
from pathlib import Path

torch.set_num_threads(2)
dtype=torch.complex128
I5=torch.eye(5,dtype=dtype)
I=torch.eye(125,dtype=dtype)
m=torch.arange(2,-3,-1,dtype=torch.float64)
sp=torch.zeros((5,5),dtype=dtype)
for i in range(1,5):
    mi=m[i].item(); sp[i-1,i]=math.sqrt((2-mi)*(2+mi+1))
sx=(sp+sp.conj().T)/2
sy=(sp-sp.conj().T)/(2j)
sz=torch.diag(m).to(dtype)

def kron3(a,b,c): return torch.kron(torch.kron(a,b),c)
J=[kron3(s,I5,I5)+kron3(I5,s,I5)+kron3(I5,I5,s) for s in (sx,sy,sz)]
C=sum((j@j for j in J),torch.zeros_like(I))
K=(C-6*I)@(C-30*I)
lam,U=torch.linalg.eigh(C)
mask=((lam-6).abs()<1e-7)|((lam-30).abs()<1e-7)
P=U[:,mask]@U[:,mask].conj().T

def basis(i,j,k):
    a=torch.zeros(5,dtype=dtype); b=a.clone(); c=a.clone(); a[i]=1; b[j]=1; c[k]=1
    return kron3(a,b,c)

# Logical qubit from two E47 states with distinct total-m support.
v0=P@basis(0,2,4); v1=P@basis(0,2,3)
zero=v0/torch.linalg.vector_norm(v0); one=v1/torch.linalg.vector_norm(v1)
psi=(zero+one)/math.sqrt(2)
rho=torch.outer(psi,psi.conj())

def channel(x,A,theta):
    up=torch.linalg.matrix_exp(-1j*theta*A); um=up.conj().T
    return (up@x@up.conj().T+um@x@um.conj().T)/2

def fidelity(state,x): return float((state.conj()@x@state).real)

def survival(x): return float(torch.trace(P@x).real)

# Collective dephasing preserves E47; local dephasing generally leaks.
collective=J[2]/6
local=kron3(sz,I5,I5)/2

# Unencoded five-level control uses two basis states of the first spin.
ctrl=(torch.tensor([1,1,0,0,0],dtype=dtype)/math.sqrt(2))
ctrl_rho=torch.outer(ctrl,ctrl.conj())
ctrl_A=sz/2

def ctrl_channel(x,A,theta):
    up=torch.linalg.matrix_exp(-1j*theta*A); um=up.conj().T
    return (up@x@up.conj().T+um@x@um.conj().T)/2

rows=[]
for theta in [0.1,0.3,0.6,1.0]:
    c=channel(rho,collective,theta)
    l=channel(rho,local,theta)
    u=ctrl_channel(ctrl_rho,ctrl_A,theta)
    rows.append({
        'theta':theta,
        'e47_collective_fidelity':fidelity(psi,c),
        'e47_collective_survival':survival(c),
        'e47_local_fidelity':fidelity(psi,l),
        'e47_local_survival':survival(l),
        'unencoded_control_fidelity':fidelity(ctrl,u),
    })

result={
    'environment':{'python':platform.python_version(),'torch':torch.__version__,'dtype':'complex128'},
    'carrier_dimension':125,
    'e47_rank':int(mask.sum()),
    'projector_residual':float(torch.linalg.matrix_norm(P@P-P,ord=2)),
    'evidence_boundary':'Numerical symmetry-protection benchmark for specified channels; not universal quantum error correction or experimental validation.',
    'rows':rows,
}
print(json.dumps(result,indent=2))
