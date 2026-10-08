#!/usr/bin/env python3
import sympy as sp
from itertools import product

R=sp.Rational
d=5
I5=sp.eye(d)
Jz=sp.diag(-2,-1,0,1,2)
Jp=sp.zeros(d); Jm=sp.zeros(d)
for i,m in enumerate(range(-2,3)):
    if i<4: Jp[i+1,i]=2-m
    if i>0: Jm[i-1,i]=2+m
G5=sp.diag(1,R(1,4),R(1,6),R(1,4),1)

def total(X):
    return (sp.kronecker_product(X,I5,I5)
            +sp.kronecker_product(I5,X,I5)
            +sp.kronecker_product(I5,I5,X))
Tz,Tp,Tm=map(total,(Jz,Jp,Jm))
G=sp.kronecker_product(G5,G5,G5)
C=Tz*Tz+R(1,2)*(Tp*Tm+Tm*Tp)
I=sp.eye(125)
K=(C-6*I)*(C-30*I)

# Spectral projector polynomial onto c=6,30.
vals=[0,2,6,12,20,30,42]
def lagrange_projector(lam):
    P=sp.eye(125)
    den=sp.Integer(1)
    for mu in vals:
        if mu!=lam:
            P=P*(C-mu*I)
            den*=lam-mu
    return P/den
P=lagrange_projector(6)+lagrange_projector(30)
assert P*P==P
assert P.T*G==G*P
assert K*P==sp.zeros(125)
assert P.rank()==47
print('PASS metric adjoint, exact spectral projector, kernel 47')

# Exact bases for image P and image(I-P).
S=sp.Matrix.hstack(*P.columnspace())
T=sp.Matrix.hstack(*(I-P).columnspace())
assert S.rank()==47 and T.rank()==78
U=T[:, :43]
W=T[:, 43:]
B=sp.Matrix.hstack(S,U,W)
assert B.rank()==125
Binv=B.inv()
E=sp.Matrix.hstack(S,U)
A=Binv[47:90,:]
assert E.rank()==90
assert A.rank()==43
assert 125-A.rank()==82
print('PASS B invertible, E rank 90, A rank 43, ker A dimension 82')

# Since A B = [0_43x47 | I_43 | 0_43x35], ker A = span(S,W).
AB=sp.simplify(A*B)
expected=sp.zeros(43,125)
expected[:,47:90]=sp.eye(43)
assert AB==expected
kerA=sp.Matrix.hstack(S,W)
assert kerA.rank()==82
# The intersection of span(S,U) and span(S,W) is exactly S.
assert sp.Matrix.hstack(E,kerA).rank()==125
interdim=E.rank()+kerA.rank()-125
assert interdim==47==S.rank()
# Membership: S lies in both; dimension forces equality for this explicit witness.
assert A*S==sp.zeros(43,47)
print('PASS E intersection ker A = span(first 47 B columns) = ker K')
print('Construction: B=[basis(im P) | basis(im(I-P))]; A=(B^-1)[47:90,:]; E=B[:,0:90]')
