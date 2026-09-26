# INVOKE BY ∧I

```
ValidSig(d) ⊭ Invoke
Candidate(d), G_syn, X ⊢ Invoke
```

## Sorts

`A` agents · `D` AMNESTY declarations · `C` CIRP consents · `G` grants · `X` tokens · `T` tools · `R` args

## Definitions

```
G_syn  :≡  Issued ∧ InWindow ∧ ToolOk ∧ ArgsOk
X      :≡  Bound ∧ Fresh
Invoke :≡  Candidate ∧ G_syn ∧ X
```

## Derivation

```
 1  ValidSig                         hyp
 2  Candidate                        hyp
 3  Issued                           hyp
 4  InWindow                         hyp
 5  ToolOk                           hyp
 6  ArgsOk                           hyp
 7  G_syn                            ∧I  3,4,5,6
 8  Bound                            hyp
 9  Fresh                            hyp
10  X                                ∧I  8,9
11  Invoke                           ∧I  2,7,10
12  Amnesty                          hyp
13  ¬Active                          ax  D ⊄ C   12
14  ¬X                               hyp
15  ¬Invoke                          ¬I  14
16  ¬Fresh                           hyp
17  ¬X                               E¬Fresh  16
18  ¬Invoke                          ¬I  17
```

## Banned cuts

```
ValidSig ⊭ Invoke
ValidSig ⊭ X
ValidSig ⊭ G_syn
Candidate ⊭ Invoke
SelfAttested ⊭ Active
Amnesty ⊭ Active
```

## Checkers

```
python3 contracts/nemo-guardrails/invoke_by_and_introduction.py   # 30/30
python3 contracts/nemo-guardrails/validsig_does_not_entail_invoke.py  # 10/10
python3 contracts/nemo-guardrails/amnesty_execute.py              # 4/4
python3 contracts/nemo-guardrails/check_vectors.py                # 18/18
```

## Runtime

`supabase/functions/coherence-runtime/index.ts` actions `issue_grant`, `execute`
`supabase/migrations/20260926_amnesty_execute_gate.sql`
