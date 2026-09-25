import numpy as np

TITLE = "E47 FLOW AS A SINGLE 125 × 125 SPECTRAL MATRIX MACHINE"

j = 2
m = np.arange(j, -j - 1, -1, dtype=float)
d = 2*j + 1

Jz = np.diag(m).astype(complex)
Jp = np.zeros((d, d), dtype=complex)
for r in range(d - 1):
    mm = m[r + 1]
    Jp[r, r + 1] = np.sqrt(j*(j+1) - mm*(mm+1))

Jm = Jp.conj().T
Jx = (Jp + Jm)/2
Jy = (Jp - Jm)/(2j)
I5 = np.eye(5, dtype=complex)

def k3(A,B,C):
    return np.kron(np.kron(A,B),C)

JxT = k3(Jx,I5,I5) + k3(I5,Jx,I5) + k3(I5,I5,Jx)
JyT = k3(Jy,I5,I5) + k3(I5,Jy,I5) + k3(I5,I5,Jy)
JzT = k3(Jz,I5,I5) + k3(I5,Jz,I5) + k3(I5,I5,Jz)

C = JxT@JxT + JyT@JyT + JzT@JzT
I = np.eye(125, dtype=complex)

K = (C - 6*I) @ (C - 30*I)
Q = K @ K

cew, cev = np.linalg.eigh(C)
mask = np.isclose(cew, 6) | np.isclose(cew, 30)
V47 = cev[:,mask]
P47 = V47 @ V47.conj().T

C_expected = np.array([0,2,6,12,20,30,42], float)
M_expected = np.array([1,9,25,28,27,22,13], int)
K_blocks = (C_expected - 6)*(C_expected - 30)
Q_blocks = K_blocks**2

rho_min = Q_blocks[Q_blocks > 0].min()
rho_max = Q_blocks.max()
eps_star = 2/(rho_min + rho_max)
rho_star = (rho_max - rho_min)/(rho_max + rho_min)

R = I - eps_star*Q
Rn = np.linalg.matrix_power(R, 300)

spec = np.rint(cew).astype(int)
u, mult = np.unique(spec, return_counts=True)

checks = [
    ("dim V = 125", C.shape == (125,125)),
    ("Casimir spectrum", np.array_equal(u, C_expected.astype(int))),
    ("Casimir multiplicities", np.array_equal(mult, M_expected)),
    ("K blocks", np.allclose(K_blocks, [180,112,0,-108,-140,0,432])),
    ("Q blocks", np.allclose(Q_blocks, [32400,12544,0,11664,19600,0,186624])),
    ("rank P47 = 47", np.linalg.matrix_rank(P47, tol=1e-8) == 47),
    ("P47 idempotent", np.linalg.norm(P47@P47-P47) < 1e-10),
    ("K P47 = 0", np.linalg.norm(K@P47) < 1e-8),
    ("rho_min = 11664", np.isclose(rho_min,11664)),
    ("rho_max = 186624", np.isclose(rho_max,186624)),
    ("eps* = 1/99144", np.isclose(eps_star,1/99144)),
    ("rho* = 15/17", np.isclose(rho_star,15/17)),
    ("R^n -> P47", np.linalg.norm(Rn-P47,2) < 1e-12),
    ("Omega_c = 47/125", np.isclose(np.trace(P47).real/125,47/125)),
]

print(TITLE)
print("="*len(TITLE))
for name, ok in checks:
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")

print()
print("K blocks =", K_blocks.astype(int).tolist())
print("Q blocks =", Q_blocks.astype(int).tolist())
print("rho_min =", int(rho_min))
print("rho_max =", int(rho_max))
print("eps* =", eps_star, "= 1/99144")
print("rho* =", rho_star, "= 15/17")
print("||R^300 - P47||_2 =", np.linalg.norm(Rn-P47,2))
print("OVERALL:", "PASS" if all(ok for _,ok in checks) else "FAIL")
