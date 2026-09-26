import numpy as np

# ============================================================
# E47 FIRST-PRINCIPLES SPECTRAL PROJECTION VALIDATOR
# ============================================================

tol = 1e-10
j = 2
m = np.arange(j, -j - 1, -1, dtype=float)
d = 2 * j + 1

Jz = np.diag(m).astype(complex)
Jp = np.zeros((d, d), dtype=complex)

for i in range(d - 1):
    mm = m[i + 1]
    Jp[i, i + 1] = np.sqrt(j * (j + 1) - mm * (mm + 1))

Jm = Jp.conj().T
Jx = (Jp + Jm) / 2
Jy = (Jp - Jm) / (2j)
I5 = np.eye(5, dtype=complex)

def kron3(A, B, C):
    return np.kron(np.kron(A, B), C)

JxT = kron3(Jx, I5, I5) + kron3(I5, Jx, I5) + kron3(I5, I5, Jx)
JyT = kron3(Jy, I5, I5) + kron3(I5, Jy, I5) + kron3(I5, I5, Jy)
JzT = kron3(Jz, I5, I5) + kron3(I5, Jz, I5) + kron3(I5, I5, Jz)

I = np.eye(125, dtype=complex)
C = JxT @ JxT + JyT @ JyT + JzT @ JzT

# Casimir spectrum and multiplicities.
evals = np.linalg.eigvalsh(C)
rounded = np.rint(evals).astype(int)
vals, mults = np.unique(rounded, return_counts=True)

# Exact E47 selector.
K = (C - 6 * I) @ (C - 30 * I)

# Degree-6 spectral projector polynomial:
# p(lambda)=1 for lambda in {6,30}, and 0 on {0,2,12,20,42}.
P47 = (
    C
    @ (C - 2 * I)
    @ (C - 12 * I)
    @ (C - 20 * I)
    @ (C - 31 * I)
    @ (C - 42 * I)
) / 1814400.0

H = I - P47

# Independent spectral reconstruction of P47.
w, U = np.linalg.eigh(C)
mask = np.isclose(w, 6, atol=tol) | np.isclose(w, 30, atol=tol)
P_spec = U[:, mask] @ U[:, mask].conj().T

# Optimal linear contraction on the positive K^2 spectrum.
K2 = K @ K
positive_k2 = np.linalg.eigvalsh(K2)
positive_k2 = positive_k2[positive_k2 > 1e-8]
Delta = float(np.min(positive_k2))
M = float(np.max(positive_k2))
eps_star = 2.0 / (Delta + M)
rho_star = (M - Delta) / (M + Delta)

Gamma = I - eps_star * K2

checks = {
    "dim(V)=125":
        C.shape == (125, 125),

    "spec(C)":
        np.array_equal(vals, np.array([0, 2, 6, 12, 20, 30, 42])),

    "mult(C)":
        np.array_equal(mults, np.array([1, 9, 25, 28, 27, 22, 13])),

    "rank(P47)=47":
        np.linalg.matrix_rank(P47, tol=1e-8) == 47,

    "tr(P47)=47":
        abs(np.trace(P47).real - 47) < 1e-8,

    "P47^2=P47":
        np.linalg.norm(P47 @ P47 - P47) < 1e-8,

    "P47*=P47":
        np.linalg.norm(P47.conj().T - P47) < 1e-8,

    "KP47=0":
        np.linalg.norm(K @ P47) < 1e-8,

    "P47K=0":
        np.linalg.norm(P47 @ K) < 1e-8,

    "P47=P_spec":
        np.linalg.norm(P47 - P_spec) < 1e-8,

    "H=I-P47":
        np.linalg.norm(P47 + H - I) < 1e-12,

    "P47H=HP47=0":
        np.linalg.norm(P47 @ H) < 1e-8 and np.linalg.norm(H @ P47) < 1e-8,

    "Gamma P47=P47":
        np.linalg.norm(Gamma @ P47 - P47) < 1e-8,

    "P47 Gamma=P47":
        np.linalg.norm(P47 @ Gamma - P47) < 1e-8,
}

print("E47 FIRST-PRINCIPLES SPECTRAL PROJECTION CERTIFICATE")
print("spec(C) =", vals.tolist())
print("mult(C) =", mults.tolist())
print("rank(P47) =", np.linalg.matrix_rank(P47, tol=1e-8))
print("tr(P47)   =", float(np.trace(P47).real))
print("Delta(K^2) =", Delta)
print("||K^2||    =", M)
print("epsilon*   =", eps_star)
print("rho*       =", rho_star)
print()

for name, ok in checks.items():
    print(f"{'PASS' if ok else 'FAIL'}  {name}")

print()
print(f"{sum(checks.values())}/{len(checks)} checks PASS")
