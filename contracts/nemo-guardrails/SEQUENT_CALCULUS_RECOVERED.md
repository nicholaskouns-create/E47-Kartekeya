# INVOKE BY ∧I

## Sequent Calculus Recovered in Invariant Grammar

```text
Γ ⊢ C

G_syn := Issued ∧ InWindow ∧ ToolOk ∧ ArgsOk
X := Bound ∧ Fresh_Σ
Invoke := Candidate ∧ G_syn ∧ X

ValidSig(d) ⊢ V_obs(d)
ValidSig(d) ⊬ Invoke

Candidate, G_syn, X ⊢ Invoke
Invoke ⇔ Candidate ∧ G_syn ∧ X

¬X ⊢ ¬Invoke
¬Fresh_Σ ⊢ ¬X
¬Fresh_Σ ⊢ ¬Invoke

Amnesty(a) ⊢ ¬Active(a)      AX_AMNESTY

Σ ; Γ ⊢ ALLOW ▷ Σ[x.nonce ↦ SPENT]
```

```text
VERDICT  30 of 30  INVOKE BY ∧I
```

Canonical checker: `sequent_calculus_recovered.py`.
