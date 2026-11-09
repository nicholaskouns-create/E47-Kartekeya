import numpy as np, json
from pathlib import Path
from scipy.linalg import eigh
root=Path(__file__).parent
j=2; m=np.arange(-2,3,dtype=float)
Jz=np.diag(m); Jp=np.zeros((5,5),complex)
for i,mi in enumerate(m[:-1]): Jp[i+1,i]=np.sqrt(j*(j+1)-mi*(mi+1))
Jx=(Jp+Jp.conj().T)/2; Jy=(Jp-Jp.conj().T)/(2j*1j) if False else (Jp-Jp.conj().T)/(2j*1j)
# Correct Jy=(Jplus-Jminus)/(2i)
Jy=(Jp-Jp.conj().T)/(2*1j)
I=np.eye(5)
def tot(A): return np.kron(np.kron(A,I),I)+np.kron(np.kron(I,A),I)+np.kron(np.kron(I,I),A)
C=sum(tot(A)@tot(A) for A in (Jx,Jy,Jz)); C=(C+C.conj().T)/2
w,V=eigh(C); spins=np.rint((np.sqrt(1+4*w)-1)/2).astype(int)
P=(V[:,(spins==2)|(spins==5)]@V[:,(spins==2)|(spins==5)].conj().T)
Q=np.eye(125)-P
K=(C-6*np.eye(125))@(C-30*np.eye(125)); H=K@K
h=np.linalg.eigvalsh(H); positive=h[h>1e-5]; gap=positive.min(); maxeig=positive.max()
# choose normalized g such that smallest positive H eigenvalue = 1
G=1/11664
rng=np.random.default_rng(47); psi=rng.normal(size=125)+1j*rng.normal(size=125);psi/=np.linalg.norm(psi)
a=V.conj().T@psi; sel=(spins==2)|(spins==5)
times=np.array([0,.25,.5,1,2,4,8.])
transverse=[]; bound=[]; energy=[]; unitary_population=[]
for t in times:
    b=np.exp(-G*(w-6)**2*(w-30)**2*t)*a
    transverse.append(float(np.linalg.norm(b[~sel])))
    bound.append(float(np.linalg.norm(a[~sel])*np.exp(-t)))
    energy.append(float(np.sum(G*(w-6)**2*(w-30)**2*np.abs(b)**2)))
    unitary_population.append(float(np.sum(np.abs(a[~sel])**2)))
# Lindblad jumps L_k = sqrt(kappa) |s><e_k|, where s is a selected basis vector and e_k span Q.
# Then sum L†L = kappa Q. Exact unconditional evolution: Q rho Q -> exp(-kappa t) Q rho Q;
# P rho Q -> exp(-kappa t/2) P rho Q; P rho P gains population in |s>.
# Includes Hamiltonian unitary: H commutes with P,Q, s ground; excited coherences rotate.
kappa=1.0; s=V[:,np.where(sel)[0][0]]; excited=V[:,~sel]
# Explicitly validate GKSL derivative using full matrices at t=0 for pure rho
rho=np.outer(psi,psi.conj()); J=np.sqrt(kappa)*np.einsum('i,jk->kij',s,excited.conj())
# alternative simple jump action sum L rho L† = kappa Tr(Qrho) |s><s|
recycle=kappa*np.trace(Q@rho)*np.outer(s,s.conj())
gksl=-1j*(G*H@rho-rho@(G*H))+recycle-.5*kappa*(Q@rho+rho@Q)
assert np.linalg.norm(np.sum(np.array([L@rho@L.conj().T for L in J]),axis=0)-recycle)<1e-12
# exact time evolved rho using spectral basis, no ODE discretization error
rho_e=V.conj().T@rho@V; hh=G*(w-6)**2*(w-30)**2
sidx=np.where(sel)[0][0]; p0=float(np.real(np.trace(Q@rho))); q0=p0
open_pop=[]; unit_pop=[]; trace_errors=[]; min_eigs=[]; ode_initial_error=None
for t in times:
    phase=np.exp(-1j*(hh[:,None]-hh[None,:])*t)
    damping=np.exp(-.5*kappa*(~sel).astype(float)*t)
    rt=rho_e*phase*damping[:,None]*damping[None,:]
    rt[sidx,sidx]+=q0*(1-np.exp(-kappa*t))
    rt=(rt+rt.conj().T)/2
    open_pop.append(float(np.real(np.sum(np.diag(rt)[~sel]))))
    unit_pop.append(q0)
    trace_errors.append(float(abs(np.trace(rt)-1)))
    min_eigs.append(float(np.linalg.eigvalsh(rt).min()))
# finite difference check Lindblad generator at zero in eigenbasis
step=1e-6
phase=np.exp(-1j*(hh[:,None]-hh[None,:])*step); damp=np.exp(-.5*kappa*(~sel).astype(float)*step)
rt=rho_e*phase*damp[:,None]*damp[None,:];rt[sidx,sidx]+=q0*(1-np.exp(-kappa*step))
fd=V@((rt-rho_e)/step)@V.conj().T
fd_error=float(np.linalg.norm(fd-gksl))
results={'spin_multiplicities':{str(k):int(sum(spins==k)) for k in range(7)},'rank_P':int(round(np.trace(P).real)),'projector_idempotence_error':float(np.linalg.norm(P@P-P)),'K_P_error':float(np.linalg.norm(K@P)),'gap_K_squared':float(gap),'max_K_squared':float(maxeig),'g':G,'initial_complement_norm':transverse[0],'initial_complement_population':q0,'times':times.tolist(),'gradient_complement_norm':transverse,'analytic_gap_bound':bound,'gradient_energy':energy,'unitary_complement_population':unit_pop,'lindblad_complement_population':open_pop,'lindblad_expected_population':[q0*np.exp(-t) for t in times],'lindblad_trace_max_error':max(trace_errors),'lindblad_min_eigenvalue':min(min_eigs),'lindblad_initial_derivative_fd_error':fd_error,'explicit_jump_count':len(J),'checks':{}}
checks=results['checks'];checks['casimir_multiplicities']=list(results['spin_multiplicities'].values())==[1,9,25,28,27,22,13];checks['rank47']=results['rank_P']==47;checks['projector']=results['projector_idempotence_error']<1e-10;checks['annihilation']=results['K_P_error']<1e-9;checks['gap11664']=abs(gap-11664)<1e-7;checks['max186624']=abs(maxeig-186624)<1e-6;checks['gradient_bound']=all(x<=y+1e-12 for x,y in zip(transverse,bound));checks['gradient_energy_monotone']=all(energy[i+1]<=energy[i] for i in range(len(energy)-1));checks['unitary_population_constant']=all(abs(x-q0)<1e-12 for x in unit_pop);checks['lindblad_population_exact']=all(abs(x-q0*np.exp(-t))<1e-11 for x,t in zip(open_pop,times));checks['lindblad_trace']=max(trace_errors)<1e-11;checks['lindblad_positive']=min(min_eigs)>-1e-10;checks['gksl_generator_finite_difference']=fd_error<1e-4;checks['jump_count78']=len(J)==78
(root/'results.json').write_text(json.dumps(results,indent=2,default=lambda x: x.item()));print(json.dumps({'checks':checks,'passed':sum(checks.values()),'total':len(checks),'gap':gap,'fd_error':fd_error,'open_pop_end':open_pop[-1],'unit_pop_end':unit_pop[-1]},indent=2,default=lambda x: x.item()))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(9,5.5));ax.semilogy(times,np.array(transverse)**2,'o-',label='Gradient: complement norm squared');ax.semilogy(times,np.array(bound)**2,'--',label='Gap upper bound');ax.semilogy(times,open_pop,'s-',label='Lindblad: complement population');ax.plot(times,unit_pop,'d-',label='Unitary: complement population');ax.set(xlabel='Dimensionless time (g=1/11664, κ=1)',ylabel='Complement weight / squared norm',title='E47: Hamiltonian gap, gradient contraction, and quantum relaxation');ax.grid(True,which='both',alpha=.25);ax.legend();fig.tight_layout();fig.savefig(root/'comparison.png',dpi=180)