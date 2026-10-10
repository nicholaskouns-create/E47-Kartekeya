import numpy as np
from scipy.linalg import eigh
m=np.arange(-2,3)
Jp=np.zeros((5,5),complex)
for i,mm in enumerate(m[:-1]): Jp[i+1,i]=np.sqrt(6-mm*(mm+1))
Jm=Jp.conj().T
Jx=(Jp+Jm)/2; Jy=(Jp-Jm)/(2j); Jz=np.diag(m)
I5=np.eye(5); I=np.eye(125)
def total(A):return np.kron(np.kron(A,I5),I5)+np.kron(np.kron(I5,A),I5)+np.kron(np.kron(I5,I5),A)
C=sum(total(A)@total(A) for A in [Jx,Jy,Jz]); C=(C+C.conj().T)/2
w,U=eigh(C)
vals=[0,2,6,12,20,30,42]
counts=[int(np.sum(abs(w-v)<1e-7)) for v in vals]
P=(U[:,(abs(w-6)<1e-7)|(abs(w-30)<1e-7)])@U[:,(abs(w-6)<1e-7)|(abs(w-30)<1e-7)].conj().T
K=(C-6*I)@(C-30*I)
G=I-(K@K)/99144
rho=max(abs(1-((v-6)*(v-30))**2/99144) for v in vals if v not in [6,30])
rng=np.random.default_rng(47)
psi=rng.standard_normal(125)+1j*rng.standard_normal(125);psi/=np.linalg.norm(psi)
x=psi.copy()
for _ in range(220):x=G@x
q=P@psi
# Quantum filter: G is Hermitian contraction. One-step successful Kraus operator G; complementary Kraus sqrt(I-G†G).
# Normalized conditional state after 220 successes.
qnorm=q/np.linalg.norm(q); xnorm=x/np.linalg.norm(x)
phase=np.vdot(qnorm,xnorm); phase/=abs(phase)
print('casimir_counts',counts)
print('projector_rank',np.linalg.matrix_rank(P,tol=1e-7))
print('projector_idempotence_2',np.linalg.norm(P@P-P,2))
print('K_P_2',np.linalg.norm(K@P,2))
print('gamma_complement_radius',rho)
print('expected_radius',15/17)
print('220_operator_error_exact',rho**220)
print('220_state_error',np.linalg.norm(x-q))
print('quantum_filter_success_probability_220',np.linalg.norm(x)**2)
print('quantum_conditional_fidelity',abs(np.vdot(qnorm,xnorm))**2)
print('quantum_conditional_state_error_phase_aligned',np.linalg.norm(xnorm-phase*qnorm))
assert counts==[1,9,25,28,27,22,13]
assert np.linalg.matrix_rank(P,tol=1e-7)==47
assert abs(rho-15/17)<1e-12
assert np.linalg.norm(P@P-P,2)<1e-12
assert np.linalg.norm(x-q)<2e-12
assert abs(np.vdot(qnorm,xnorm))**2>1-1e-12
print('ALL_ASSERTIONS_PASSED')
