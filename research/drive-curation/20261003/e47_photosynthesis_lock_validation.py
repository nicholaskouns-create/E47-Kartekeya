from __future__ import annotations
import numpy as np

rng = np.random.default_rng(470125)
n, rank_e, rank_adm = 125, 47, 2
theta = 1e-12

def opnorm(a):
    return float(np.linalg.norm(a, 2))

z = rng.normal(size=(n,n)) + 1j*rng.normal(size=(n,n))
Q, _ = np.linalg.qr(z)
VE = Q[:, :rank_e]
Pi = VE @ VE.conj().T
Pi_perp = np.eye(n) - Pi

# Exact admissible projector inside E47
VA = VE[:, :rank_adm]
P = VA @ VA.conj().T
Kc = np.eye(n) - P

# Controlled tilted projector
w1 = np.cos(theta)*VE[:,0] + np.sin(theta)*Q[:,rank_e]
w2 = VE[:,1]
VAt = np.column_stack([w1,w2])
Pt = VAt @ VAt.conj().T

for name, A in [("exact", P), ("tilted", Pt)]:
    defect = Pi @ A @ Pi - A
    rhs = -Pi_perp @ A - Pi @ A @ Pi_perp
    print(name)
    print("lock defect:", opnorm(defect))
    print("decomposition residual:", opnorm(defect-rhs))
    print("left leakage:", opnorm(Pi_perp @ A))
    print("commutator:", opnorm(Pi @ A - A @ Pi))
    print("ranks:", round(np.trace(A).real), round(np.trace(Pi).real))

# Quantum projective measurement completeness
print("measurement completeness:",
      opnorm(Pi.conj().T@Pi + Pi_perp.conj().T@Pi_perp - np.eye(n)))

# High-precision principal-angle quantities are analytically:
# amplitude leakage = sin(theta)
# failure probability = sin(theta)^2
# lifted joint eigenvalue = 1-cos(theta)
print("analytic amplitude leakage:", np.sin(theta))
print("analytic failure probability:", np.sin(theta)**2)
print("analytic lifted eigenvalue:", 1-np.cos(theta), "(binary64 rounds this to zero)")
