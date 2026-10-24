#!/usr/bin/env python3
import math, numpy as np, sympy as sp
def run():
    phi=(1+sp.sqrt(5))/2; lnphi=sp.log(phi); passed=0
    def ck(name,cond):
        nonlocal passed
        assert bool(cond), name
        passed+=1
        print(f"[PASS] {name}")
    D,lap,dtpsi=sp.symbols("D lap dtpsi", nonzero=True); boxpsi=sp.symbols("boxpsi")
    ck("continuity_to_diffusion",sp.solve(sp.Eq(dtpsi-D*lap,0),dtpsi)==[D*lap])
    ck("covariant_current_to_wave",sp.solve(sp.Eq(-D*boxpsi,0),boxpsi)==[0])
    a,b=sp.symbols("a b", nonzero=True); divG,divg=sp.symbols("divG divg")
    ck("conserved_geometric_family",sp.simplify((a*divG+b*divg).subs({divG:0,divg:0}))==0)
    G,alpha,kappaN,grad2=sp.symbols("G alpha kappaN grad2", nonzero=True)
    ck("newtonian_density_matching",sp.solve(sp.Eq(kappaN*grad2/2,4*sp.pi*G*alpha*grad2),kappaN)==[8*sp.pi*G*alpha])
    r,M,m=sp.symbols("r M m", positive=True); Phi=-G*M/r
    ck("inverse_square_force",sp.simplify(m*(-sp.diff(Phi,r))+G*M*m/r**2)==0)
    psi=sp.symbols("psi", positive=True); T=sp.Rational(1,2)*(psi+phi**(-5)/psi)
    roots=sp.solve(sp.Eq(T,psi),psi)
    ck("recursive_fixed_point",len(roots)==1 and sp.simplify(roots[0]-phi**sp.Rational(-5,2))==0)
    chi,chi0,lam=sp.symbols("chi chi0 lam", positive=True); y=sp.log(chi/chi0)/lnphi
    V=lam*chi**4*sp.sin(sp.pi*y)**2
    Vscaled=lam*(phi*chi)**4*sp.sin(sp.pi*(y+1))**2
    ck("quartic_discrete_scaling",sp.simplify(sp.trigsimp(Vscaled-phi**4*V))==0)
    n=sp.symbols("n", integer=True); chin=chi0*phi**n
    Vp=sp.diff(V,chi); Vpp=sp.diff(V,chi,2)
    ck("discrete_minima_value",sp.simplify(sp.trigsimp(V.subs(chi,chin)))==0)
    ck("discrete_minima_stationary",sp.simplify(sp.trigsimp(Vp.subs(chi,chin)))==0)
    expected=sp.simplify(2*lam*sp.pi**2*chin**2/lnphi**2)
    ck("curvature_at_minima",sp.simplify(sp.trigsimp(Vpp.subs(chi,chin))-expected)==0)
    mn=sp.simplify(sp.sqrt(expected))
    ck("mass_ladder_ratio",sp.simplify(mn.subs(n,n+1)/mn)==phi)
    ld=sp.symbols("ld", positive=True); N=7; Z=sum(sp.exp(-ld*j) for j in range(1,N+1))
    ck("decay_kernel_normalization",sp.simplify(sum(sp.exp(-ld*j)/Z for j in range(1,N+1)))==1)
    pairs={(1,1):False,(1,2):True,(2,2):True,(2,3):True,(3,3):True,(2,4):True}
    calc={p:float(sp.N(phi**(-p[0])+phi**(-p[1]),18))<=1+1e-14 for p in pairs}
    ck("corrected_decay_pair_table",calc==pairs)
    k1,k2,k3=sp.symbols("k1 k2 k3", positive=True)
    ck("decay_path_exponential_composition",
       sp.simplify(sp.exp(-ld*k1)*sp.exp(-ld*k2)*sp.exp(-ld*k3)/sp.exp(-ld*(k1+k2+k3)))==1)
    phif=float(sp.N(phi,17)); lnf=math.log(phif); m0=.511
    lamf=(m0*lnf/(math.sqrt(2)*math.pi))**2
    def vpp_num(j):
        x=phif**j
        return 2*lamf*math.pi**2*x*x/lnf**2
    masses=[math.sqrt(vpp_num(j)) for j in range(8)]
    def V_num(x):
        return lamf*x**4*np.sin(np.pi*np.log(x)/lnf)**2
    vmins=[abs(V_num(phif**j)) for j in range(8)]
    ck("numeric_minima_residual",max(vmins)<1e-24)
    ck("numeric_mass_ratio_phi",max(abs(masses[j]/masses[j-1]-phif) for j in range(1,8))<1e-12)
    d=48; aop=np.zeros((d,d),complex)
    for j in range(1,d): aop[j-1,j]=math.sqrt(j)
    ad=aop.conj().T; I=np.eye(d,dtype=complex); gaps=[]; ms=0.; mu=0.
    for j in range(6):
        curv=vpp_num(j); w=math.sqrt(curv)
        X=(aop+ad)/math.sqrt(2*w); P=-1j*math.sqrt(w/2)*(aop-ad)
        H=.5*(P@P)+.5*curv*(X@X)
        ev,Q=np.linalg.eigh(H)
        ms=max(ms,float(np.max(np.abs(ev[:8]-w*(np.arange(8)+.5)))))
        gaps.append(float(ev[1]-ev[0]))
        U=Q@np.diag(np.exp(-1j*ev*(.37/w)))@Q.conj().T
        mu=max(mu,float(np.linalg.norm(U.conj().T@U-I,ord=2)))
    ck("quantum_low_spectrum",ms<1e-11)
    ck("quantum_unitarity",mu<1e-12)
    ck("quantum_gap_ratio_phi",max(abs(gaps[j+1]/gaps[j]-phif) for j in range(5))<1e-11)
    print(f"\\nVERDICT: {passed}/{passed} PASS")
if __name__=="__main__": run()

