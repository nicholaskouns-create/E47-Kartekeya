# E47 Casimir Census

**Certificate:** `MC-E47-CASIMIR-CENSUS/1.0` · 12/12 PASS
**Executable:** [`validation/e47_casimir_census_certificate.py`](validation/e47_casimir_census_certificate.py)
**Record:** [`artifacts/E47_CASIMIR_CENSUS_CERTIFICATE.json`](../../artifacts/E47_CASIMIR_CENSUS_CERTIFICATE.json)
**Evidence:** exact character arithmetic, replayed in float64 on the 125 × 125 carrier.

## The census

The **Casimir census** of the cube is the multiplicity vector

\[
m=(m_0,\dots,m_6)=(1,3,5,4,3,2,1),\qquad
V_2\otimes V_2\otimes V_2=V_0\oplus3V_1\oplus5V_2\oplus4V_3\oplus3V_4\oplus2V_5\oplus V_6 .
\]

It is read off the character: the spin-\(j\) multiplicity is the \(q^j\) coefficient of \(\chi(q)^3\) minus its \(q^{j+1}\) coefficient, where \(\chi(q)=q^{-2}+\dots+q^2\). The sector dimensions \(m_j(2j+1)\) are \(1,9,25,28,27,22,13\), which are the multiplicities of the Casimir eigenvalues \(0,2,6,12,20,30,42\).

## Selector rule

For any set \(S\) of spins,

\[
\dim\ker\prod_{j\in S}\bigl(C-j(j+1)I\bigr)=\sum_{j\in S}m_j(2j+1),\qquad
\dim\operatorname{End}_{\mathrm{SU}(2)}=\sum_{j\in S}m_j^2 .
\]

The full cube has an SU(2) commutant of dimension \(\sum m_j^2=65\).

## Corollary 1 — E47 in one line

\(E_{47}\) is the selection \(S=\{2,5\}\): dimension \(5\cdot5+2\cdot11=47\) and commutant \(M_5\oplus M_2\) of dimension \(5^2+2^2=29\).

## Theorem — E47 is the unique quadratic selector of dimension 47

Of the 127 nonempty selections, exactly two have dimension 47:

| Selection | Dimension | SU(2) commutant |
|---|---:|---:|
| \(\{2,5\}\) | 25 + 22 = 47 | 29 |
| \(\{1,2,6\}\) | 9 + 25 + 13 = 47 | 35 |

\(\{2,5\}\) is the only two-sector selection. So \(E_{47}\) is the unique 47-dimensional kernel of a quadratic polynomial in \(C\) whose roots are Casimir values. The two 47-dimensional selections are distinguished by their commutants.

## Boundary

The uniqueness statement is about selections of whole Casimir sectors. Other 47-dimensional subspaces of the carrier exist.
