#!/usr/bin/env python3
"""KKP-R G47: exact integer highest-weight basis, Casimir, rank and dynamics.
Requires sympy. The computed artifacts are exact; this is not a Lean/Coq compiler receipt.
"""
import json
from pathlib import Path
import sympy as sp

SEEDS_J2 = [[[4,1],[8,-4],[12,24],[16,-4],[20,1]],[[4,1],[8,-3],[12,12],[16,-1],[28,-1],[32,6],[36,-6],[40,1]],[[4,1],[8,-2],[12,4],[28,-2],[32,8],[36,-4],[52,4],[56,-4],[60,4]],[[4,1],[8,-1],[28,-3],[32,6],[52,12],[56,-6],[76,-1],[80,1]],[[4,1],[28,-4],[52,24],[76,-4],[100,1]]]
SEEDS_J5 = [[[1,-1],[5,1]],[[1,-1],[25,1]]]
N = 125
I = sp.eye(5)
jp = sp.zeros(5)
jm = sp.zeros(5)
for a,b,v in [(0,1,1),(1,2,1),(2,3,6),(3,4,4)]:
    jp[a,b] = v
for a,b,v in [(1,0,4),(2,1,6),(3,2,1),(4,3,1)]:
    jm[a,b] = v
z = sp.diag(2,1,0,-1,-2)
def total(A):
    return sp.kronecker_product(A,I,I) + sp.kronecker_product(I,A,I) + sp.kronecker_product(I,I,A)
Jp,Jm,Jz = total(jp),total(jm),total(z)
C = Jp*Jm + Jz*Jz - Jz

def chain(terms, spin):
    v = sp.zeros(N,1)
    for i,coeff in terms:
        v[i] += coeff
    assert Jp*v == sp.zeros(N,1)
    assert Jz*v == spin*v
    result = []
    for _ in range(2*spin+1):
        assert C*v == spin*(spin+1)*v
        result.append(v)
        v = Jm*v
    assert v == sp.zeros(N,1)
    return result

cols2 = [v for seed in SEEDS_J2 for v in chain(seed,2)]
cols5 = [v for seed in SEEDS_J5 for v in chain(seed,5)]
U = sp.Matrix.hstack(*(cols2 + cols5))
assert U.shape == (125,47)
assert C*U == U*sp.diag(*([6]*25+[30]*22))
K = (C-6*sp.eye(N))*(C-30*sp.eye(N))
assert K*U == sp.zeros(N,47)

# Fast exact rank witness over F_101: nonzero minor modulo 101 implies rank_Q U = 47.
def modular_rank(A,p=101):
    rows = [[int(A[i,j])%p for j in range(A.cols)] for i in range(A.rows)]
    pivot_row=0
    for col in range(A.cols):
        pivot=next((r for r in range(pivot_row,len(rows)) if rows[r][col]),None)
        if pivot is None:
            continue
        rows[pivot_row],rows[pivot]=rows[pivot],rows[pivot_row]
        inv=pow(rows[pivot_row][col],-1,p)
        rows[pivot_row]=[(v*inv)%p for v in rows[pivot_row]]
        for r in range(pivot_row+1,len(rows)):
            factor=rows[r][col]
            if factor:
                rows[r]=[(x-factor*y)%p for x,y in zip(rows[r],rows[pivot_row])]
        pivot_row+=1
    return pivot_row

assert modular_rank(U,101) == 47
G=U.T*U
# Positive definiteness of Gram follows from exact full column rank over Q.
# The rational orthogonal projector is P = U*(U.T*U)^(-1)*U.T.
phi=(1+sp.sqrt(5))/2
omega=sp.Rational(47,125)
alpha=1/phi
a_kkp=sp.simplify(omega*alpha**2)
assert sp.simplify(a_kkp-(141-47*sp.sqrt(5))/250)==0
n=sp.symbols('n',integer=True,nonnegative=True)
psi0,delta=sp.symbols('psi0 delta')
psi_star=sp.simplify(omega*phi**2*delta)
assert sp.simplify(alpha*psi_star+omega*delta-psi_star)==0
# Stationary error is exactly alpha**n*(psi0-psi_star).
output={
 "dimension":[125,47],"spin_blocks":[25,22],"modular_prime":101,
 "modular_rank":47,"CU_equals_Udiag":True,"KU_zero":True,
 "seeds_j2":SEEDS_J2,"seeds_j5":SEEDS_J5,
 "stationary_error":"psi_n - psi_star = phi**(-n)*(psi0-psi_star)",
 "source_perturbation":"abs(e_n) <= alpha**n*abs(e_0) + omega*sum(alpha**(n-1-k)*abs(delta_k-delta_star),k=0..n-1)",
 "bianchi_status":"conditional scalar-model estimate; full covariant limit not established"
}
if __name__=="__main__":
    target=Path(__file__).with_name("certificate.json")
    target.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,indent=2))
