# E47 Prism Spectral Formalism

**Record:** \`E47-PRISM-FORMALISM-20260922\`  
**Machine receipt:** \`MC-MATRIX-E47-PRISM-20260922-001\`  
**Status:** exact spectral identities + E1 software/numerical parity  
**Public instrument:** https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/matrix/

## 1. Typed pipeline

THE MATRIX and E47 remain distinct spaces until an explicit feature map is applied:

\[
|\psi\rangle\in (\mathbb C^2)^{\otimes 8}\cong\mathbb C^{256}
\xrightarrow{\,L\,}
v\in V_2^{\otimes3}\cong\mathbb C^{125}.
\]

Here \(L\) is the documented normalized sampled-amplitude **feature lift** used by THE MATRIX. It is not a Hilbert-space isomorphism.

The canonical E47 Casimir on the 125-dimensional carrier is

\[
C=J_{\rm tot}^2
=\sum_{\lambda\in\{0,2,6,12,20,30,42\}}\lambda P_\lambda,
\]

with multiplicities

\[
(1,9,25,28,27,22,13),\qquad
1+9+25+28+27+22+13=125.
\]

## 2. Spectral prism

For a normalized \(v\in\mathbb C^{125}\), define the band weight

\[
w_\lambda(v)=\|P_\lambda v\|^2.
\]

Because the spectral projectors are mutually orthogonal and resolve the identity,

\[
\boxed{\sum_\lambda w_\lambda(v)=1.}
\]

The E47 selector is

\[
K=(C-6I)(C-30I),
\qquad
E_{47}=\ker K=E_6\oplus E_{30},
\]

so

\[
P_{47}=P_6+P_{30},
\qquad
\boxed{w_{E47}(v)=\|P_{47}v\|^2=w_6(v)+w_{30}(v).}
\]

This is the exact mathematical content of the “E47 prism” metaphor: one typed 125-state vector is resolved into seven Casimir bands, and the \(\lambda=6\) and \(\lambda=30\) bands are selected as E47.

## 3. Rank fraction versus state weight

The projector rank is

\[
\operatorname{rank}P_{47}=25+22=47,
\qquad
\Omega_c=\frac{\operatorname{Tr}P_{47}}{125}=\frac{47}{125}=0.376.
\]

\(\Omega_c\) is a rank fraction. It is also the E47 probability for the maximally mixed state \(I/125\), and the Haar mean of \(\|P_{47}v\|^2\) over uniformly distributed unit vectors:

\[
\operatorname{Tr}\!\left(P_{47}\frac{I}{125}\right)=\frac{47}{125},
\qquad
\mathbb E_{\rm Haar}\,\|P_{47}v\|^2=\frac{47}{125}.
\]

It is **not** the E47 weight of every state.

## 4. Certified MATRIX state

Configuration:

- 8 qubits
- 24 layers
- maximum MPS bond \(\chi=16\)
- phase \(\phi=0.7\)
- ideal brickwork CNOT entangler
- typed \(256\to125\) normalized feature lift

The independently reconstructed spectral weights are:

| Casimir \(\lambda\) | multiplicity | \(w_\lambda\) |
|---:|---:|---:|
| 0 | 1 | 0.003873208953955917 |
| 2 | 9 | 0.06049575013782006 |
| **6** | **25** | **0.12153223655298497** |
| 12 | 28 | 0.17853315216187027 |
| 20 | 27 | 0.17702406495212444 |
| **30** | **22** | **0.25351593478374257** |
| 42 | 13 | 0.2050256524575022 |

Thus

\[
\boxed{
w_{E47}
=
0.12153223655298497
+
0.25351593478374257
=
0.3750481713367275
}
\]

or

\[
\boxed{37.50481713367275\%}.
\]

Against the rank fraction,

\[
w_{E47}-\frac{47}{125}
=
-0.0009518286632724804,
\]

i.e. \(-0.09518286632724804\) percentage points.

The seven weights are strongly non-uniform. The proximity to \(47/125\) for this one circuit/lift is therefore an **observed state-specific numerical fact**, not an identity.

## 5. Kernel-energy identity

Since \(K\) is a polynomial in \(C\),

\[
K
=
\sum_\lambda(\lambda-6)(\lambda-30)P_\lambda,
\]

and therefore

\[
\boxed{
\langle v,K^2v\rangle
=
\sum_\lambda
[(\lambda-6)(\lambda-30)]^2w_\lambda(v).
}
\]

For the certified MATRIX state,

\[
\langle K^2\rangle
=
44699.14038394355.
\]

The E47 bands contribute zero to this energy because \(K(6)=K(30)=0\).

## 6. Machine parity

The live Supabase \`matrix-cube-adapter@3\` independently resolves all seven bands from the typed 125-state vector.

Certified parity:

- spectral-weight sum: \(1\) to floating precision
- \(\max_\lambda |w_\lambda^{\rm Python}-w_\lambda^{\rm live}|=2.942091015256665\times10^{-15}\)
- \(|w_{E47}^{P_{47}}-(w_6+w_{30})|=1.5543122344752192\times10^{-15}\)
- receipt: \`MC-MATRIX-E47-PRISM-20260922-001\` PASS

## 7. Evidence boundary

- The Casimir spectrum, projector identities, rank 47, and \(w_{E47}=w_6+w_{30}\) are exact finite-dimensional mathematics.
- The quoted seven band weights are numerical properties of the certified MATRIX circuit after the documented feature lift.
- THE MATRIX is a software quantum simulator, not quantum hardware.
- The \(256\to125\) map is a typed feature map, not a Hilbert-space identification.
- \(47/125\) is a rank fraction / isotropic expectation, not a universal state probability.
- No physical law, hardware effect, or experimental quantum claim is inferred from the numerical proximity \(37.504817\%\approx37.6\%\).

## 8. Reproduce

\`\`\`bash
python scripts/validate_e47_prism_matrix.py
python scripts/validate_e47_prism_matrix.py --live-adapter
\`\`\`

Canonical implementation surfaces:

- \`scripts/validate_e47_prism_matrix.py\`
- \`website/interfaces/matrix/\`
- \`supabase/functions/matrix-cube-adapter/index.ts\`
- \`website/data/MC-MATRIX-E47-PRISM-20260922-001.json\`

## 9. Cross-platform authorities

- GitHub mathematical authority: https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/E47_Prism_Spectral_Formalism.md
- Notion Formalism Registry: https://app.notion.com/p/3e346094fd30818e99c1d04635983c62?pvs=204 · `FRM-96`
- Google Drive long-form mirror: https://docs.google.com/document/d/1wCmn5J4Tjo0qVV5AOoHUxD1tXComhPf7lU1ntzKtaMs/edit
- Live MATRIX: https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/matrix/
- Machine receipt: https://nicholaskouns-create.github.io/E47-Kartekeya/data/MC-MATRIX-E47-PRISM-20260922-001.json
- Supabase executable witness: https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter · `matrix-cube-adapter@3`
- Supabase City identity: `E47-PRISM-20260922`
- Supabase machine certificate: `MC-MATRIX-E47-PRISM-20260922-001`

The four surfaces are mirrors of one typed object, not independent claims. GitHub holds the mathematical authority, Notion holds the registry record, Drive holds the readable mirror, and Supabase holds the executable witness plus provenance registry.

> A prism does not create the spectrum. It makes the hidden spectrum visible.
