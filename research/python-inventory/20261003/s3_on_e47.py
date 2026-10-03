"""
======================================================================
 The S_3 Structure of E_47
 Decomposing the 47-dimensional kernel under the action of the
 symmetric group permuting the three tensor factors of V_2 ⊗ V_2 ⊗ V_2.
======================================================================

Logic:
  S_3 acts on V = V_2 ⊗ V_2 ⊗ V_2 by permuting the three factors.
  This action commutes with the total Casimir C, hence with K, hence
  preserves the kernel E_47.  We restrict the S_3 representation to
  E_47, compute its character on the three conjugacy classes
  {e}, {transpositions}, {3-cycles}, and decompose into irreducibles
  of S_3 (trivial, sign, standard).

  Then we refine: for each isotypic block W_j ⊂ V, the S_3 action
  is on the multiplicity space M_j (of dimension m_j), and we get the
  full SU(2) × S_3 decomposition of E_47 = W_2 ⊕ W_5.

S_3 irreducibles (character table):
                     e    (12)    (123)
  trivial:           1     1       1
  sign:              1    -1       1
  standard:          2     0      -1
"""

import numpy as np
from numpy.linalg import eigh, eigvalsh

# ---- 1.  Rebuild the standard infrastructure ------------------------

s = 2; d = 5
m_vals = np.arange(s, -s-1, -1)
Jz = np.diag(m_vals).astype(complex)
Jp = np.zeros((d, d), dtype=complex)
for i, m in enumerate(m_vals):
    if m + 1 <= s:
        Jp[i-1, i] = np.sqrt(s*(s+1) - m*(m+1))
Jm = Jp.conj().T
Jx = 0.5 * (Jp + Jm)
Jy = -0.5j * (Jp - Jm)
I5 = np.eye(d, dtype=complex)

def kron3(A, B, C): return np.kron(np.kron(A, B), C)

D = 125
I_V = np.eye(D, dtype=complex)

Jtx = kron3(Jx,I5,I5) + kron3(I5,Jx,I5) + kron3(I5,I5,Jx)
Jty = kron3(Jy,I5,I5) + kron3(I5,Jy,I5) + kron3(I5,I5,Jy)
Jtz = kron3(Jz,I5,I5) + kron3(I5,Jz,I5) + kron3(I5,I5,Jz)

C = Jtx@Jtx + Jty@Jty + Jtz@Jtz
C = 0.5 * (C + C.conj().T)

K = (C - 6*I_V) @ (C - 30*I_V)
K = 0.5 * (K + K.conj().T)

# ---- 2.  Build S_3 permutation operators ---------------------------
# Basis index: |a,b,c⟩  →  25a + 5b + c   with a,b,c ∈ {0,1,2,3,4}.
# Permutation σ acts by:  σ · |a,b,c⟩ = |x_{σ⁻¹(1)}, x_{σ⁻¹(2)}, x_{σ⁻¹(3)}⟩
# Equivalent computational rule: if σ sends position k → σ(k),
# the factor originally at position k ends up at position σ(k).

def build_perm(sigma):
    """sigma: tuple of length 3 giving (σ(0), σ(1), σ(2))."""
    P = np.zeros((D, D), dtype=complex)
    for a in range(5):
        for b in range(5):
            for c in range(5):
                old = (a, b, c)
                new = [0, 0, 0]
                for k in range(3):
                    new[sigma[k]] = old[k]
                old_idx = 25*old[0] + 5*old[1] + old[2]
                new_idx = 25*new[0] + 5*new[1] + new[2]
                P[new_idx, old_idx] = 1
    return P

P_e   = build_perm((0, 1, 2))   # identity
P_12  = build_perm((1, 0, 2))   # transposition (1 2)
P_13  = build_perm((2, 1, 0))   # transposition (1 3)
P_23  = build_perm((0, 2, 1))   # transposition (2 3)
P_123 = build_perm((1, 2, 0))   # 3-cycle (1 2 3):  1→2, 2→3, 3→1
P_132 = build_perm((2, 0, 1))   # 3-cycle (1 3 2)

# ---- 3.  Sanity checks ---------------------------------------------
# (a) Trace of permutation on V equals 5^{# cycles}
assert np.isclose(np.trace(P_e).real,   125)
assert np.isclose(np.trace(P_12).real,   25)
assert np.isclose(np.trace(P_123).real,   5)
# (b) S_3 multiplication relations
assert np.allclose(P_12 @ P_12, P_e)
assert np.allclose(P_123 @ P_123, P_132)
assert np.allclose(P_123 @ P_123 @ P_123, P_e)
assert np.allclose(P_12 @ P_123 @ P_12, P_132)
# (c) Permutations commute with C and K
for P in (P_12, P_13, P_23, P_123, P_132):
    assert np.allclose(P @ C - C @ P, 0, atol=1e-10)
    assert np.allclose(P @ K - K @ P, 0, atol=1e-10)

print("="*70)
print(" THE S_3 STRUCTURE OF E_47")
print("="*70)
print()
print("Permutation operators built, sanity-checked, and verified to")
print("commute with C and K (so they preserve E_47 = ker K).")

# ---- 4.  Project onto E_47 and compute the S_3 character -----------
w, v = eigh(K)
kernel_basis = v[:, np.abs(w) < 1e-8]              # 125 × 47
assert kernel_basis.shape == (125, 47)
P_E = kernel_basis @ kernel_basis.conj().T          # projector onto E_47

# Restrict each P_σ to E_47.  In the kernel basis U:  P_σ|_E = U† P_σ U.
def restrict(P): return kernel_basis.conj().T @ P @ kernel_basis

chi_e   = np.trace(restrict(P_e)).real
chi_12  = np.trace(restrict(P_12)).real
chi_123 = np.trace(restrict(P_123)).real

print()
print("Character of E_47 as an S_3-representation:")
print(f"  χ(e)     = {chi_e:>6.3f}    (= dim E_47 = 47)")
print(f"  χ((12))  = {chi_12:>6.3f}")
print(f"  χ((123)) = {chi_123:>6.3f}")

# ---- 5.  Decompose into S_3 irreducibles ---------------------------
# n_α = (1/|G|) Σ_g χ(g) χ_α(g*)  with |G| = 6
n_triv = (chi_e + 3*chi_12 + 2*chi_123) / 6
n_sign = (chi_e - 3*chi_12 + 2*chi_123) / 6
n_std  = (2*chi_e + 0*chi_12 - 2*chi_123) / 6     # =(chi_e - chi_123)/3

print()
print("Decomposition of E_47 as S_3-representation (forgetting SU(2)):")
print(f"  multiplicity of trivial:   {n_triv:>6.3f}")
print(f"  multiplicity of sign:      {n_sign:>6.3f}")
print(f"  multiplicity of standard:  {n_std:>6.3f}")
print(f"  dim check:  1·{round(n_triv)} + 1·{round(n_sign)} + 2·{round(n_std)} "
      f"= {round(n_triv) + round(n_sign) + 2*round(n_std)}")

# ---- 6.  Refine: full SU(2) × S_3 decomposition --------------------
# For each isotypic block W_j, compute the S_3 character on M_j by
# dividing the W_j character by 2j+1.

print()
print("Refinement to the full SU(2) × S_3 decomposition.")
print("For each j ∈ {0,...,6}, we restrict the permutation operators to")
print("the j-th isotypic block W_j and compute the S_3 character on the")
print("multiplicity space M_j (dim m_j).")

# Get the C eigenspaces
eigs_C = eigvalsh(C).real
w_C, v_C = eigh(C)

# Allowed j values and their (eigenvalue, multiplicity m_j)
j_data = [(0,0,1), (1,2,3), (2,6,5), (3,12,4), (4,20,3), (5,30,2), (6,42,1)]

print()
print(f"  {'j':>3}  {'m_j':>4}   {'χ_M(e)':>8} {'χ_M((12))':>11} {'χ_M((123))':>12}"
      f"   {'a':>3} {'b':>3} {'c':>3}   M_j as S_3-rep")
print("  " + "-"*78)

decomposition = {}
for j, lam, m_j in j_data:
    # Get basis of W_j (eigenvectors of C with eigenvalue λ = j(j+1))
    mask = np.abs(w_C - lam) < 1e-6
    U_j = v_C[:, mask]                                # 125 × (m_j (2j+1))
    assert U_j.shape[1] == m_j * (2*j+1)

    # Restrict permutations to W_j and take trace, then divide by 2j+1
    Pe_j   = U_j.conj().T @ P_e   @ U_j
    P12_j  = U_j.conj().T @ P_12  @ U_j
    P123_j = U_j.conj().T @ P_123 @ U_j

    chiM_e   = np.trace(Pe_j).real   / (2*j+1)
    chiM_12  = np.trace(P12_j).real  / (2*j+1)
    chiM_123 = np.trace(P123_j).real / (2*j+1)

    # Decompose M_j into S_3 irreps
    a = (chiM_e + 3*chiM_12 + 2*chiM_123) / 6        # trivial mult
    b = (chiM_e - 3*chiM_12 + 2*chiM_123) / 6        # sign mult
    c = (chiM_e - chiM_123) / 3                       # standard mult
    a, b, c = round(a), round(b), round(c)
    decomposition[j] = (a, b, c)

    # Pretty-print M_j as a direct sum
    pieces = []
    if a: pieces.append(f"{a}·triv" if a > 1 else "triv")
    if b: pieces.append(f"{b}·sign" if b > 1 else "sign")
    if c: pieces.append(f"{c}·std"  if c > 1 else "std")
    M_j_str = " ⊕ ".join(pieces) if pieces else "0"

    print(f"  {j:>3}  {m_j:>4}   {chiM_e:>8.2f} {chiM_12:>11.2f} {chiM_123:>12.2f}"
          f"   {a:>3} {b:>3} {c:>3}   M_{j} = {M_j_str}")

# ---- 7.  The decomposition of E_47 = W_2 ⊕ W_5 ---------------------
print()
print("="*70)
print(" RESULT — THE FULL SU(2) × S_3 STRUCTURE OF E_47")
print("="*70)
a2, b2, c2 = decomposition[2]
a5, b5, c5 = decomposition[5]

print()
print("E_47 = W_2 ⊕ W_5,   where:")
print()
print(f"   W_2 = M_2 ⊗ V_2 = ({a2}·triv ⊕ {b2}·sign ⊕ {c2}·std) ⊗ V_2"
      f"  →  dim = {(a2 + b2 + 2*c2)*5}")
print(f"   W_5 = M_5 ⊗ V_5 = ({a5}·triv ⊕ {b5}·sign ⊕ {c5}·std) ⊗ V_5"
      f"  →  dim = {(a5 + b5 + 2*c5)*11}")
print()
print("Expanding:")
print()
print("   E_47 = (V_2 ⊗ trivial)      ←  5-dim, symmetric under S_3")
print("        ⊕ 2·(V_2 ⊗ standard)   ←  20-dim, mixed symmetry under S_3")
print("        ⊕ (V_5 ⊗ standard)     ←  22-dim, mixed symmetry under S_3")
print()
print(f"   dim check: 5 + 20 + 22 = 47  ✓")
print(f"   sign component is ZERO — E_47 contains no fully antisymmetric piece.")

print()
print("Forgetting SU(2), as a pure S_3-representation:")
print()
print(f"   E_47 ≅ 5·trivial ⊕ 0·sign ⊕ 21·standard")
print(f"           5         0           42        →  47 ✓")

