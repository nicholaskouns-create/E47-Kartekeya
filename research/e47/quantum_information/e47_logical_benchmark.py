import torch, math, json, hashlib, platform
from pathlib import Path
D=torch.complex128; torch.set_num_threads(2)
I5=torch.eye(5,dtype=D); I=torch.eye(125,dtype=D)
m=torch.arange(2,-3,-1,dtype=torch.float64)
Sp=torch.zeros((5,5),dtype=D)
for i in range(1,5):
 q=m[i].item();Sp[i-1,i]=math.sqrt((2-q)*(2+q+1))
Sx=(Sp+Sp.conj().T)/2;Sy=(Sp-Sp.conj().T)/(2j);Sz=torch.diag(m).to(D)
def kron3(a,b,c):return torch.kron(torch.kron(a,b),c)
J=[kron3(s,I5,I5)+kron3(I5,s,I5)+kron3(I5,I5,s) for s in (Sx,Sy,Sz)]
C=sum((j@j for j in J),torch.zeros_like(I));K=(C-6*I)@(C-30*I)
eig,U=torch.linalg.eigh(C);mask=((eig-6).abs()<1e-7)|((eig-30).abs()<1e-7)
P=U[:,mask]@U[:,mask].conj().T; Gamma=I-K@K/99144
# J=2, m=2 highest weight sector: rank five. Choose two codewords from its eigenbasis.
P2=U[:,(eig-6).abs()<1e-7]@U[:,(eig-6).abs()<1e-7].conj().T
mz=torch.diag(J[2]).real
idx=torch.where((mz-2).abs()<1e-10)[0]
W=P2[:,idx]; u,s,vh=torch.linalg.svd(W,full_matrices=False)
assert (s>1e-8).sum().item()==5
B=u[:,:2].contiguous(); assert torch.linalg.matrix_norm(B.conj().T@B-torch.eye(2,dtype=D))<1e-12
logical=torch.tensor([1.,1.],dtype=D)/math.sqrt(2)
psi=B@logical;rho=psi[:,None]@psi.conj()[None,:]
# Random-unitary dephasing E_theta(rho) = (U_theta rho U† + U†rho U)/2
# Diagonal generators permit an exact, fast Hadamard implementation.
Acol=mz/2
Aloc=torch.diag(kron3(Sz,I5,I5)).real/2

def apply(x,a,theta):
 d=a[:,None]-a[None,:]
 return x*torch.cos(theta*d)
def row(name,theta,a):
 out=apply(rho,a,theta)
 decoded=B.conj().T@out@B
 survival=float(torch.trace(P@out).real)
 code_weight=float(torch.trace(decoded).real)
 unconditional=float((logical.conj()@decoded@logical).real)
 conditional=unconditional/code_weight if code_weight>0 else None
 return dict(channel=name,theta=theta,logical_fidelity_unconditional=unconditional,code_weight=code_weight,conditional_fidelity=conditional,e47_survival=survival,purity=float(torch.trace(out@out).real))
# Physical spin-2 unencoded qubit on one spin, |m=2>+|m=1>, same Jz/2 generator
q=torch.zeros(5,dtype=D);q[0]=q[1]=1/math.sqrt(2)
rq=q[:,None]@q.conj()[None,:]; aq=m/2
def bare(theta):
 x=rq*torch.cos(theta*(aq[:,None]-aq[None,:]))
 return float((q.conj()@x@q).real)
thetas=[0.,0.1,0.3,0.6,1.0]
rows=[row(name,t,a) for name,a in [('collective_Jz',Acol),('local_Sz_first_spin',Aloc)] for t in thetas]
for t in thetas:
 rows.append(dict(channel='unencoded_single_spin_Jz',theta=t,logical_fidelity_unconditional=bare(t)))
checks={'carrier_dimension':125,'rank_P47':int(mask.sum()),'J2_m2_multiplicity':int((s>1e-8).sum()),'projector_idempotence':float(torch.linalg.matrix_norm(P@P-P,ord=2)),'kernel_residual':float(torch.linalg.matrix_norm(K@P,ord=2)),'fixed_point_residual':float(torch.linalg.matrix_norm(Gamma@P-P,ord=2)),'code_orthonormality':float(torch.linalg.matrix_norm(B.conj().T@B-torch.eye(2,dtype=D))),'collective_logical_error_max':max(abs(r['logical_fidelity_unconditional']-1) for r in rows if r['channel']=='collective_Jz')}
assert checks['rank_P47']==47 and checks['J2_m2_multiplicity']==5
assert checks['collective_logical_error_max']<1e-10
assert checks['kernel_residual']<1e-9
out={'environment':{'python':platform.python_version(),'torch':torch.__version__,'device':'cpu','dtype':'complex128'},'checks':checks,'noise_definition':'E_theta(rho)=0.5*(exp(-i theta A) rho exp(i theta A)+exp(i theta A) rho exp(-i theta A)); collective A=Jz/2, local A=Sz(first spin)/2','encoding':'two orthonormal J=2,m=2 multiplicity vectors; logical |+> state; recovery is B† rho B with erasure weight retained','results':rows}
path=Path('/mnt/data/e47_logical_benchmark_results.json');path.write_text(json.dumps(out,indent=2))
print(json.dumps(checks,indent=2))
for r in rows:
 if r['theta'] in (0.3,0.6,1.0):print(r)
print('script_sha256',hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
