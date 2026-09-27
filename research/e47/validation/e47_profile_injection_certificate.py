#!/usr/bin/env python3
"""MC-E47-PROFILE-INJECTION/1.0 — the general profile-injection lemma.

For n >= 1 and N >= n + 3, map q in R^n to the Brinkmann plane wave
    g_q = -2 du dv + dx^2 + dy^2 + F_q(u)(x^2 - y^2) du^2,
    F_q(u) = u^N + u^n + sum_{a<n} q_a u^a.
(A) Every g_q is Ricci-flat (derived symbolically from the metric).
(B) If n is odd and N is even, the only element (s,a,b) of the plane-wave
    equivalence group  F(u) -> s a^2 F(a u + b), s in {+1,-1}, a != 0 real,
    relating two anchored profiles is (1,1,0), so q -> [g_q] is injective.
(C) If n is even, a = -1 identifies distinct profiles: injectivity fails.

IMPORTED, not proved here: that this group exhausts all isometries between
such plane waves. (B) is therefore conditional on it. The E47 construction in
e47_intrinsic_spacetime_unmarked.py is the case n = 47, N = 78.
"""
from __future__ import annotations
import json, os
from pathlib import Path
import sympy as sp

ROOT=Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents)>3 else Path.cwd()
OUT=(ROOT/"artifacts"/"E47_PROFILE_INJECTION_CERTIFICATE.json") if (ROOT/"artifacts").exists() else Path(__file__).with_name("E47_PROFILE_INJECTION_CERTIFICATE.json")
if os.environ.get("E47_CERT_OUT"): OUT=Path(os.environ["E47_CERT_OUT"])

GRID=[(1,4),(3,6),(5,8),(7,10),(11,14),(47,50),(47,78)]   # odd n, even N >= n+3
EVEN_GRID=[(2,6),(4,8),(46,78)]                             # even n: counterexamples
IMPORTED="The plane-wave equivalence group F(u) -> s a^2 F(a u + b) exhausts isometries between the Brinkmann plane waves g_q."

def brinkmann_ricci():
    u,v,x,y=sp.symbols('u v x y',real=True); X=[u,v,x,y]
    H=sp.Function('H')(u,x,y)
    g=sp.Matrix([[H,-1,0,0],[-1,0,0,0],[0,0,1,0],[0,0,0,1]]); gi=g.inv(); n=4
    Gam=[[[sp.simplify(sum(gi[a,d]*(sp.diff(g[d,c],X[b])+sp.diff(g[d,b],X[c])-sp.diff(g[b,c],X[d])) for d in range(n))/2)
           for c in range(n)] for b in range(n)] for a in range(n)]
    Ric=sp.zeros(n,n)
    for b in range(n):
        for d in range(n):
            Ric[b,d]=sp.simplify(sum(sp.diff(Gam[a][b][d],X[a])-sp.diff(Gam[a][b][a],X[d])
                +sum(Gam[a][a][k]*Gam[k][b][d]-Gam[a][d][k]*Gam[k][b][a] for k in range(n)) for a in range(n)))
    only_uu=all(Ric[i,j]==0 for i in range(n) for j in range(n) if (i,j)!=(0,0))
    uu=sp.simplify(Ric[0,0]+(sp.diff(H,x,2)+sp.diff(H,y,2))/2)==0
    F=sp.Function('F')(u)
    vac=sp.simplify(Ric[0,0].subs(H,F*(x**2-y**2)).doit())==0
    return only_uu and uu, vac

def coefficient_system(n,N):
    """Coefficients of u^N, u^(N-1), and (at b=0) u^n in s a^2 (anchor)(a u + b)."""
    u,a,b,s=sp.symbols('u a b s')
    p=sp.Poly(sp.expand(s*a**2*((a*u+b)**N+(a*u+b)**n)),u)
    cN,cN1=p.coeff_monomial(u**N),p.coeff_monomial(u**(N-1))
    cn=sp.Poly(sp.expand(s*a**2*((a*u)**N+(a*u)**n)),u).coeff_monomial(u**n)
    ok=(sp.expand(cN-s*a**(N+2))==0 and sp.expand(cN1-N*s*a**(N+1)*b)==0 and sp.expand(cn-s*a**(n+2))==0)
    return ok

def real_solutions(n,N):
    """All real (s,a,b), s=+-1, a!=0, with s a^(N+2)=1, N s a^(N+1) b=0, s a^(n+2)=1."""
    a=sp.symbols('a',real=True); sols=[]
    for s in (1,-1):
        for r in sp.real_roots(sp.Poly(s*a**(N+2)-1,a)):
            if r!=0 and s*r**(n+2)==1: sols.append((s,int(r),0))
    return sorted(set(sols))

def injective_after_group(n,N):
    """With (s,a,b)=(1,1,0) the relation F_c(u)=F_d(u) forces c=d coefficientwise."""
    u=sp.symbols('u'); c=sp.symbols(f'c0:{n}'); d=sp.symbols(f'd0:{n}')
    Fc=u**N+u**n+sum(c[i]*u**i for i in range(n)); Fd=u**N+u**n+sum(d[i]*u**i for i in range(n))
    diff=sp.Poly(sp.expand(Fc-Fd),u)
    return all(sp.expand(diff.coeff_monomial(u**i)-(c[i]-d[i]))==0 for i in range(n)) and diff.degree()<n

def even_counterexample(n,N):
    """d = e_1 and c = -e_1 give distinct profiles related by (s,a,b)=(1,-1,0)."""
    u=sp.symbols('u')
    Fd=u**N+u**n+u; Fc=u**N+u**n-u
    return sp.expand(Fc-(-1)**2*Fd.subs(u,-u))==0 and sp.expand(Fc-Fd)!=0

def main():
    ricci_ok,vacuum_ok=brinkmann_ricci()
    grid={f"{n},{N}":dict(system=coefficient_system(n,N),solutions=real_solutions(n,N),
                          injective=injective_after_group(n,N)) for n,N in GRID}
    even={f"{n},{N}":dict(solutions=real_solutions(n,N),counterexample=even_counterexample(n,N)) for n,N in EVEN_GRID}
    checks={
      'brinkmann_ricci_reduction':ricci_ok,
      'every_profile_vacuum':vacuum_ok,
      'coefficient_identities':all(v['system'] for v in grid.values()),
      'odd_n_group_trivial':all(v['solutions']==[(1,1,0)] for v in grid.values()),
      'odd_n_injective':all(v['injective'] for v in grid.values()),
      'e47_case_47_78_covered':grid['47,78']['solutions']==[(1,1,0)] and grid['47,78']['injective'],
      'minimal_top_degree_suffices_47_50':grid['47,50']['solutions']==[(1,1,0)],
      'even_n_extra_solution':all(v['solutions']==[(1,-1,0),(1,1,0)] for v in even.values()),
      'even_n_counterexample':all(v['counterexample'] for v in even.values()),
    }
    checks={k:bool(v) for k,v in checks.items()}
    cert={'schema':'MC-E47-PROFILE-INJECTION/1.0','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,
      'lemma':{
        'family':'g_q = -2 du dv + dx^2 + dy^2 + F_q(u)(x^2 - y^2) du^2, F_q = u^N + u^n + sum_{a<n} q_a u^a',
        'A_vacuum':'Ric = -(1/2)(H_xx + H_yy) du^2 for any H(u,x,y); H = F(u)(x^2 - y^2) is harmonic, so every g_q is Ricci-flat.',
        'B_injectivity':'n odd, N even, N >= n+3: the equivalence group element relating two anchored profiles is (s,a,b) = (1,1,0), so q = q\'.',
        'C_parity_obstruction':'n even: (s,a,b) = (1,-1,0) relates q and q\' with q\'_a = (-1)^a q_a; the map is not injective.',
        'e47_instance':'n = 47, N = 78 (used in e47_intrinsic_spacetime_unmarked.py); N = 50 would also do.',
      },
      'grid':{k:{'solutions':[list(s) for s in v['solutions']],'injective':v['injective']} for k,v in grid.items()},
      'even_grid':{k:{'solutions':[list(s) for s in v['solutions']],'counterexample':v['counterexample']} for k,v in even.items()},
      'evidence':{'A':'E0 (symbolic)','B':'E0 conditional on the imported fact','C':'E0 (explicit counterexample)'},
      'conditional_on':[IMPORTED],
      'boundary':'The lemma uses only the dimension n of the parameter space, not the structure of E47. Injectivity into the moduli space modulo all diffeomorphisms is conditional on the imported fact.'}
    OUT.write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n'); print(json.dumps(cert,indent=2,sort_keys=True))
    if cert['status']!='PASS': raise SystemExit(1)
if __name__=='__main__': main()
