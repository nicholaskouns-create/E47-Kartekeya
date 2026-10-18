"""Independent complex128 PyTorch construction and finite spectral checks."""
from pathlib import Path
import json,torch,math
P=Path(__file__).resolve().parent
torch.set_num_threads(2)
T=torch.complex128; R=torch.float64
checks=[]
def check(name,error,tol=3e-10):
 value=float(error);checks.append(dict(name=name,error=value,tolerance=tol,passed=value<=tol));assert value<=tol,checks[-1]
def norm(x):return torch.linalg.matrix_norm(x,ord=2).item()
def main():
 I5=torch.eye(5,dtype=T);m=torch.arange(2,-3,-1,dtype=R)
 plus=torch.zeros((5,5),dtype=T)
 for i in range(1,5):plus[i-1,i]=math.sqrt(6-m[i].item()*(m[i].item()+1))
 spin=[(plus+plus.T)/2,(plus-plus.T)/(2j),torch.diag(m).to(T)]
 kron=torch.kron
 J=[kron(kron(s,I5),I5)+kron(kron(I5,s),I5)+kron(kron(I5,I5),s) for s in spin]
 C=sum(x@x for x in J);I=torch.eye(125,dtype=T)
 K=(C-6*I)@(C-30*I);G=I-K@K/99144
 ev,V=torch.linalg.eigh(C)
 mask=(abs(ev-6)<1e-9)|(abs(ev-30)<1e-9)
 B=V[:,mask];P47=B@B.conj().T;Q=I-P47
 check('kernel dimension 47',abs(mask.sum().item()-47),0)
 check('selector rank 78',abs(torch.linalg.matrix_rank(K,atol=1e-8,rtol=0).item()-78),0)
 check('projector idempotence',norm(P47@P47-P47))
 check('kernel annihilation',norm(K@P47))
 check('kernel preserved',norm(G@P47-P47))
 check('sharp one-step operator bound',abs(norm(G-P47)-15/17))
 max_abs=0.;power=I.clone();samples={}
 for L in range(221):
  actual=norm(power-P47);theory=(15/17)**L;max_abs=max(max_abs,abs(actual-theory))
  if L in [0,1,10,100,220]:samples[L]=dict(observed=actual,theoretical=theory)
  power=G@power
 check('all depths 0 through 220 absolute norm agreement',max_abs,3e-12)
 check('220-step E47 preservation',norm(power@P47-P47),3e-12)
 check('220-step kernel-to-complement leakage',norm(Q@power@P47),3e-12)
 for i,j in enumerate(J):
  check(f'collective generator {i} projector commutator',norm(j@P47-P47@j))
  check(f'compressed generator {i} SU2 commutator',norm((B.conj().T@J[(i+1)%3]@B)@(B.conj().T@J[(i+2)%3]@B)-(B.conj().T@J[(i+2)%3]@B)@(B.conj().T@J[(i+1)%3]@B)-1j*(B.conj().T@j@B)))
  U=torch.matrix_exp(-0.37j*j)
  check(f'rotation {i} filter equivariance',norm(U@G-G@U))
 torch.manual_seed(470125);x=torch.randn(125,dtype=T,requires_grad=True);d=torch.randn(125,dtype=T);d=d/torch.linalg.vector_norm(d)
 loss=torch.vdot(G@x,G@x).real;loss.backward()
 check('autograd analytical gradient',torch.linalg.vector_norm(x.grad-2*G.conj().T@G@x).item())
 eps=1e-6
 f=lambda z:torch.vdot(G@z,G@z).real
 fd=((f(x.detach()+eps*d)-f(x.detach()-eps*d))/(2*eps)).item()
 exact=torch.vdot(x.grad,d).real.item()
 check('gradient finite directional difference',abs(fd-exact),1e-7)
 X=torch.randn(125,1000,dtype=T);X=X/torch.linalg.vector_norm(X,dim=0)
 check('1000-state finite-depth contraction bound',max(0,(torch.linalg.vector_norm((torch.linalg.matrix_power(G,220)-P47)@X,dim=0).max().item()-(15/17)**220)),3e-12)
 report=dict(status='PASS',dtype='complex128',torch_version=torch.__version__,checks=checks,depth_samples=samples,max_operator_norm_absolute_error=max_abs,
 exact_depth220_error=(15/17)**220,depth_for_1e_minus15=math.ceil(math.log(1e-15)/math.log(15/17)),
 interpretation='Gamma is an amplitude filter; the trace-preserving density update is the separate attenuation-and-reset channel.')
 (P/'torch_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
