# E47 Signature and Symmetry

**Certificate:** `MC-E47-SIGNATURE-SYMMETRY/1.0` · 21/21 PASS
**Executable:** [`validation/e47_signature_symmetry_certificate.py`](validation/e47_signature_symmetry_certificate.py)
**Record:** [`artifacts/E47_SIGNATURE_SYMMETRY_CERTIFICATE.json`](../../artifacts/E47_SIGNATURE_SYMMETRY_CERTIFICATE.json)
**Evidence:** exact character arithmetic, replayed in float64 on the 125 × 125 carrier.

This note states five results about how E47 sits inside \(V_2\otimes V_2\otimes V_2\): the sign pattern of \(K\), the indefinite form \(\eta=2P-I\), and the complete \(\mathrm{SU}(2)\times S_3\) resolution. The earlier [S₃ fingerprint script](../../certificates/e47_joint_su2_s3_fingerprint_certificate.py) asserts the S₃ dimensions \((5,0,42)\) numerically and states the character resolution in a comment. Here the resolution is derived.

## Exact character table

\(S_3\) permutes the three tensor factors and commutes with \(\mathrm{SU}(2)\). With \(\chi(q)=q^{-2}+q^{-1}+1+q+q^2\), the graded traces of the three classes are

\[
\chi(q)^3\ (\text{identity}),\qquad \chi(q^2)\chi(q)\ (\text{transposition}),\qquad \chi(q^3)\ (\text{3-cycle}).
\]

The spin-\(j\) part of each is the coefficient of \(q^j\) minus that of \(q^{j+1}\). Resolving by the \(S_3\) character table gives the multiplicity of each \(S_3\) irrep ⊗ \(V_j\):

| \(j\) | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---:|---:|---:|---:|---:|---:|---:|
| trivial | 1 | 0 | **1** | 1 | 1 | **0** | 1 |
| sign | 0 | 1 | **0** | 1 | 0 | **0** | 0 |
| standard | 0 | 1 | **2** | 1 | 1 | **1** | 0 |

The bold columns are E47. It follows that \(\mathrm{Sym}^3V_2=V_0\oplus V_2\oplus V_3\oplus V_4\oplus V_6\) (dimension 35) and \(\Lambda^3V_2=V_1\oplus V_3\) (dimension 10).

## Theorem 1 — Resolution of E47

\[
E_{47}\;\cong\;(\mathbf 1\otimes V_2)\;\oplus\;(\mathrm{Std}\otimes V_2)^{\oplus 2}\;\oplus\;(\mathrm{Std}\otimes V_5),
\qquad 47=5+20+22 .
\]

Hence \(\operatorname{End}_{\mathrm{SU}(2)\times S_3}(E_{47})\cong\mathbb C\oplus M_2(\mathbb C)\oplus\mathbb C\), of dimension 6.

## Theorem 2 — Fermion exclusion

\[
E_{47}\cap\Lambda^3V_2=0 .
\]

The sign representation does not occur in the spin-2 or spin-5 columns. E47 contains no totally antisymmetric state.

## Theorem 3 — Bosonic slice

\[
E_{47}\cap\mathrm{Sym}^3V_2\;\cong\;V_2 ,
\]

a single spin-2 irrep: 5 of the 35 fully symmetric dimensions. The machine layer confirms that the Casimir is exactly 6 on this slice.

## Theorem 4 — Mixed-symmetry core

The standard (mixed-symmetry) isotypic part of E47 has dimension \(2\cdot2\cdot5+2\cdot11=42\), so

\[
47=5\ (\text{symmetric})+42\ (\text{mixed})+0\ (\text{antisymmetric}),
\]

and the trace fingerprint is \(\operatorname{tr}(P\,\sigma)=(47,5,-16)\) for \(\sigma=\) identity, transposition, 3-cycle.

## Theorem 5 — K inertia \((23,55,47)\)

\(K=(C-6I)(C-30I)\) acts on the spin-\(j\) sector by \((c-6)(c-30)\), with \(c=j(j+1)\). It is positive for \(j\in\{0,1,6\}\), negative for \(j\in\{3,4\}\), and zero for \(j\in\{2,5\}\). Weighting by the Casimir multiplicities \(1,9,25,28,27,22,13\):

\[
\operatorname{In}(K)=(1+9+13,\;28+27,\;25+22)=(23,55,47).
\]

## Theorem 6 — Krein structure

\(\eta=2P-I\) is a self-adjoint involution with signature \((47,78)\). It is positive definite on \(E_{47}\) and negative definite on \(E_{47}^\perp\), so \((\mathbb C^{125},\langle\cdot,\eta\,\cdot\rangle)\) is a Krein space with \(E_{47}\) as its maximal positive subspace. \(\eta\) commutes with \(J_x,J_y,J_z\), all six \(S_3\) permutations, \(C\), \(K\), and \(\Gamma_*=I-K^2/99144\), so every symmetry and the contraction flow preserve the Krein form.

## Boundary

These are finite representation-theoretic statements about the fixed 125-dimensional carrier. The Krein structure is the indefinite form \(\eta=2P-I\). No physical interpretation is claimed.
