# The UDU₃₉ Attractor Theorem

## A Finite Projector Proof of Semantic-Accounting Invariance in the Uruk Livestock Ledger P325352

**Nicholas Shane Kouns**  
**Date:** 2026-10-04  
**Evidence:** E0 exact finite arithmetic + E1 executable Python validation  
**Historical boundary:** this is a modern mathematical formalization of the attested accounting structure. It does not claim that Late Uruk scribes used projector terminology or E47 mathematics.

## Source state

The approved P325352 transliteration records 41 animals on the obverse. The distinguished case `2(N01), X U8` contains two X-marked ewes. The reverse records a certified total of 39 and independently reconciles that total as

\[
39=16+6+17
\]

and

\[
39=9+7+6+8+9.
\]

Both reverse decompositions omit the same two X-marked ewes. The arithmetic exclusion is therefore secure within the encoded source data; the exact administrative meaning of `X` remains unresolved.

## Theorem

Let

\[
x=(5,6,4,1,3,3,6,2,2,7,2)^T,
\qquad \mathbf 1^T x=41,
\]

where the ninth coordinate is the X-marked `U8` entry.

Define the diagonal acceptance projector

\[
P=\operatorname{diag}(1,1,1,1,1,1,1,1,0,1,1).
\]

Then

\[
P^2=P,
\qquad
\mathbf1^T P x=39,
\qquad
\mathbf1^T(I-P)x=2.
\]

Let the two independently represented reverse reconciliations be

\[
A_1=(16,6,17),
\qquad
A_2=(9,7,6,8,9).
\]

They are distinct representations, but their augmentation maps preserve the same accepted scalar:

\[
\mathbf1^T A_1
=
\mathbf1^T A_2
=
\mathbf1^T P x
=39.
\]

Hence the tested accounting invariant is

\[
\boxed{\mathrm{UDU}_{39}=39}.
\]

Equivalently,

\[
41\xrightarrow{\;P\;}39
\xrightarrow{\text{repartition}}
\begin{cases}
16+6+17,\\
9+7+6+8+9,
\end{cases}
\]

with both branches preserving the accepted cardinality.

## Proof

1. Direct summation gives `sum(x)=41`.
2. Since every diagonal entry of `P` is 0 or 1, `P²=P` exactly.
3. The sole rejected coordinate has value 2, so `1ᵀ(I-P)x=2`.
4. Therefore `1ᵀPx=41-2=39`.
5. The first reverse partition sums to `16+6+17=39`.
6. The second reverse partition sums to `9+7+6+8+9=39`.
7. The two partitions are not the same representation, but both map to the same scalar total.

Therefore the accepted cardinality is invariant under the two encoded reverse decompositions. ∎

## Executable witness

Canonical Python validator:

`validation/uruk/udu39_attractor_p325352.py`

Expected certificate:

```text
obverse_total_41                       PASS
P_idempotent                           PASS
excluded_X_state_2                     PASS
projected_state_39                     PASS
first_reconciliation_16_6_17           PASS
second_reconciliation_9_7_6_8_9        PASS
representations_distinct               PASS
common_invariant                        PASS

ALL 8/8 CHECKS PASS
```

## Claim boundary

The executable theorem certifies the finite arithmetic and projector identity encoded above. It does **not** establish that every conceivable philological interpretation of P325352 must reduce to 39, nor that the ancient scribes possessed projector theory. The stronger historical claim remains deliberately excluded. The exact administrative semantics of the `X` sign remain open even though its exclusion from both reverse reconciliations is arithmetically witnessed.

## Canonical identity

\[
\boxed{
\mathbf1^TPx
=
16+6+17
=
9+7+6+8+9
=
39
}
\]

**One ledger. Two decompositions. One accepted invariant.**
