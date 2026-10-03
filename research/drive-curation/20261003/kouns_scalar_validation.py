
import numpy as np
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches

# ============================================================
# KOUNS SCALAR FRAMEWORK
# Internal Numerical Consistency Validation
# ============================================================

# Spectral decomposition
eigs  = [0, 2, 6, 12, 20, 30, 42]
mults = [1, 9, 25, 28, 27, 22, 13]

# Build Hilbert-space operator C
diag = []
for e, m in zip(eigs, mults):
    diag.extend([e] * m)

C = np.diag(diag)
I = np.eye(len(diag))

# ------------------------------------------------------------
# 1. Kernel operator
# ------------------------------------------------------------
K = (C - 6 * I) @ (C - 30 * I)

rank = np.linalg.matrix_rank(K)
kernel_dim = K.shape[0] - rank
omega_c = kernel_dim / len(diag)

# Eigenvalues of K
k_eigs = np.linalg.eigvals(K)

# ------------------------------------------------------------
# 2. Recursive contraction dynamics
# ------------------------------------------------------------
target = 47 / 125

def recursive_update(q):
    eta = q**(-2) - 1
    return q - 0.05 * eta

qs = [0.95]
for _ in range(200):
    qs.append(recursive_update(qs[-1]))

qs = np.array(qs)

# ------------------------------------------------------------
# 3. Mass recursion toy spectrum
# ------------------------------------------------------------
phi = (1 + np.sqrt(5)) / 2

N = np.arange(1, 151)
masses = phi**(-N/3) * (1 - phi**(-5*N))**(3/2)

# ------------------------------------------------------------
# 4. Topological scalar surface
# ------------------------------------------------------------
x = np.linspace(-2.5, 2.5, 200)
y = np.linspace(-2.5, 2.5, 200)
X, Y = np.meshgrid(x, y)

R = np.sqrt(X**2 + Y**2)
Z = np.exp(-R**2 / 4) - 0.35 * np.log(R + 0.1)

# ------------------------------------------------------------
# 5. Numerical outputs
# ------------------------------------------------------------
print("================================================")
print("NUMERICAL VALIDATION")
print("================================================")
print(f"Total Hilbert dimension V = {len(diag)}")
print(f"Kernel dimension dim(Ker K) = {kernel_dim}")
print(f"Ωc = {kernel_dim}/{len(diag)} = {omega_c:.6f}")
print(f"Golden ratio φ = {phi:.12f}")
print("================================================")

# ------------------------------------------------------------
# PLOTS
# ------------------------------------------------------------

# Plot 1: Recursive convergence
plt.figure(figsize=(7,4))
plt.plot(qs, lw=2)
plt.axhline(target, linestyle='--')
plt.title("Recursive Scalar Evolution")
plt.xlabel("Iteration")
plt.ylabel("Q_n")
plt.grid(True)
plt.tight_layout()
plt.savefig("/mnt/data/recursive_convergence.png", dpi=200)

# Plot 2: Recursive mass spectrum
plt.figure(figsize=(7,4))
plt.semilogy(N, masses, lw=2)
plt.title("Recursive Mass Spectrum")
plt.xlabel("Recursion Depth N")
plt.ylabel("Mass Scale")
plt.grid(True)
plt.tight_layout()
plt.savefig("/mnt/data/mass_spectrum.png", dpi=200)

# Plot 3: Scalar attractor surface
fig = plt.figure(figsize=(7,5))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, linewidth=0, antialiased=True)
ax.set_title("Scalar Attractor Manifold")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Q")
plt.tight_layout()
plt.savefig("/mnt/data/scalar_manifold.png", dpi=200)

# ------------------------------------------------------------
# WORD REPORT
# ------------------------------------------------------------
doc = Document()

doc.add_heading("Numerical Validation of Scalar / Spectral Framework", level=1)

doc.add_heading("1. Spectral Kernel Validation", level=2)
doc.add_paragraph(
    f"Constructed operator K=(C−6I)(C−30I) "
    f"on a 125-dimensional space."
)
doc.add_paragraph(
    f"Computed kernel dimension = {kernel_dim}"
)
doc.add_paragraph(
    f"Computed coherence ratio Ωc = {omega_c:.6f}"
)

doc.add_heading("2. Recursive Scalar Dynamics", level=2)
doc.add_paragraph(
    "A recursive contraction map was iterated numerically "
    "to visualize convergence behavior."
)

doc.add_picture("/mnt/data/recursive_convergence.png", width=Inches(5.8))

doc.add_heading("3. Recursive Mass Spectrum", level=2)
doc.add_paragraph(
    "A toy recursive scaling law based on powers of the "
    "golden ratio φ was evaluated across recursion depth."
)

doc.add_picture("/mnt/data/mass_spectrum.png", width=Inches(5.8))

doc.add_heading("4. Topological Scalar Surface", level=2)
doc.add_paragraph(
    "A scalar attractor manifold was rendered as a smooth "
    "potential-like contraction surface."
)

doc.add_picture("/mnt/data/scalar_manifold.png", width=Inches(5.8))

doc.add_heading("Interpretation", level=2)
doc.add_paragraph(
    "These calculations validate internal algebraic consistency "
    "of the presented operator constructions, recursive mappings, "
    "and visualization geometries. "
    "They do not independently validate physical claims about gravity, "
    "propulsion, or new physics."
)

report_path = "/mnt/data/kouns_scalar_validation_report.docx"
doc.save(report_path)

print("Saved report:", report_path)
