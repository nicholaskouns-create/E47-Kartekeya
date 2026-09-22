"""E47 -> lock -> 3+1 metric numerical certificate."""
import numpy as np

J=np.arange(7)
C=J*(J+1)
MULT=np.array([1,9,25,28,27,22,13])
K=(C-6)*(C-30)
K2=K*K
P=((C==6)|(C==30))
OMEGA=47/125
GAP=K2[K2>0].min()
NORM=K2.max()

assert MULT.sum()==125
assert MULT[P].sum()==47
assert GAP==11664
assert NORM==186624
assert NORM/GAP==16

w0=MULT/125

def L(t):
    """Declared normalized complement-drain lock functional."""
    return 1-np.sum(w0[~P]*np.exp(-2*K2[~P]*t))

def dL(t):
    return np.sum(2*K2[~P]*w0[~P]*np.exp(-2*K2[~P]*t))

g00_star=-(78/125)**(-1)
gs_star=(47/125)**2

def metric(t):
    l=L(t)
    return np.diag([g00_star*l, gs_star*l, gs_star*l, gs_star*l])

assert np.isclose(L(0),OMEGA)
assert dL(0)>0
for t in np.linspace(0,8/GAP,1001):
    assert OMEGA <= L(t) <= 1+1e-12
    assert dL(t)>=0
    ev=np.linalg.eigvalsh(metric(t))
    assert ev[0]<0 and np.all(ev[1:]>0)

print("PASS")
print("dim H =",MULT.sum())
print("dim ker K =",MULT[P].sum())
print("Omega_c =",OMEGA)
print("gap(K^2) =",GAP)
print("norm(K^2) =",NORM)
print("kappa =",NORM/GAP)
print("L(0) =",L(0))
print("L(8/Delta) =",L(8/GAP))
print("g00(Omega) =",g00_star*OMEGA)
print("gs(Omega) =",gs_star*OMEGA)
print("signature = (-,+,+,+)")
print()
print("Logical status:")
print("CERTIFIED: spectral data -> semigroup -> kernel projection/complement decay.")
print("DERIVED GIVEN DEFINITION: declared complement-drain functional -> monotone L.")
print("GEOMETRIC REALIZATION: L -> metric uses the stated linear metric map;")
print("uniqueness of that map is not implied by the spectral data alone.")
