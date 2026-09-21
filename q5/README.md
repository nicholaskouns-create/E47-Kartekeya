# Q5

The 5×5×5 map. One word per cell. π(x,y,z) = 25x + 5y + z.
Σ = {0,1,2,3,4}³. |Σ| = 125. Word = xyz as quinary digits.

Witness: Drive `validate_lig_proof.py` / poster validator.
Residuals sit in `codec.py`. City certificates become rows later.
No wrapping layer. No new authority.

```
python q5/validator.py
python q5/host.py          # emit the Pages cube from this ledger
python q5/host.py serve    # host website/ with the cube on :8000
python -m pytest tests/test_q5.py -v
```

Live cube: [Q5 on GitHub Pages](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/) · Notion slots: [Q5 · 125-word ledger](https://www.notion.so/3e246094fd308151966ae74dedb2976a)

`host.py` is the one-pass host. It does not mint a credential. It copies `cells.jsonl` onto the existing Pages tree and serves `website/`. Three.js is the onsite vendor file.

| File | Role |
|---|---|
| `codec.py` | Packing bijection and measured residuals |
| `q5.ts` | Same packing map in TypeScript |
| `cells.jsonl` | Frozen 125-word ledger |
| `validator.py` | Ledger check. Does not construct C, K, or P |
| `host.py` | Validate, emit Pages cube, host `website/` |
| `slots.json` · `ledger.ts` | Notion slot URLs and GitHub row bind |
| `website/interfaces/q5/` | Emitted cube (onsite three.js) |

47 = 142₅ · 78 = 303₅ · 125 = 1000₅ · Ω_c = 47/125 = 0.142₅
ε* = 1/99144 · ρ* = 15/17 · K² gap 11664 · K² max 186624
cube ‖PᵀLP − L‖_F = 8√3 · ‖PᵀLP − L‖₂ = 2√2

## z = 0

| x\\y | 0 | 1 | 2 | 3 | 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **0** | `000` 0 | `010` 5 | `020` 10 | `030` 15 | `040` 20 |
| **1** | `100` 25 | `110` 30 | `120` 35 | `130` 40 | `140` 45 |
| **2** | `200` 50 | `210` 55 | `220` 60 | `230` 65 | `240` 70 |
| **3** | `300` 75 | `310` 80 | `320` 85 | `330` 90 | `340` 95 |
| **4** | `400` 100 | `410` 105 | `420` 110 | `430` 115 | `440` 120 |

## z = 1

| x\\y | 0 | 1 | 2 | 3 | 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **0** | `001` 1 | `011` 6 | `021` 11 | `031` 16 | `041` 21 |
| **1** | `101` 26 | `111` 31 | `121` 36 | `131` 41 | `141` 46 |
| **2** | `201` 51 | `211` 56 | `221` 61 | `231` 66 | `241` 71 |
| **3** | `301` 76 | `311` 81 | `321` 86 | `331` 91 | `341` 96 |
| **4** | `401` 101 | `411` 106 | `421` 111 | `431` 116 | `441` 121 |

## z = 2

| x\\y | 0 | 1 | 2 | 3 | 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **0** | `002` 2 | `012` 7 | `022` 12 | `032` 17 | `042` 22 |
| **1** | `102` 27 | `112` 32 | `122` 37 | `132` 42 | `142` 47 |
| **2** | `202` 52 | `212` 57 | `222` 62 | `232` 67 | `242` 72 |
| **3** | `302` 77 | `312` 82 | `322` 87 | `332` 92 | `342` 97 |
| **4** | `402` 102 | `412` 107 | `422` 112 | `432` 117 | `442` 122 |

## z = 3

| x\\y | 0 | 1 | 2 | 3 | 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **0** | `003` 3 | `013` 8 | `023` 13 | `033` 18 | `043` 23 |
| **1** | `103` 28 | `113` 33 | `123` 38 | `133` 43 | `143` 48 |
| **2** | `203` 53 | `213` 58 | `223` 63 | `233` 68 | `243` 73 |
| **3** | `303` 78 | `313` 83 | `323` 88 | `333` 93 | `343` 98 |
| **4** | `403` 103 | `413` 108 | `423` 113 | `433` 118 | `443` 123 |

## z = 4

| x\\y | 0 | 1 | 2 | 3 | 4 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| **0** | `004` 4 | `014` 9 | `024` 14 | `034` 19 | `044` 24 |
| **1** | `104` 29 | `114` 34 | `124` 39 | `134` 44 | `144` 49 |
| **2** | `204` 54 | `214` 59 | `224` 64 | `234` 69 | `244` 74 |
| **3** | `304` 79 | `314` 84 | `324` 89 | `334` 94 | `344` 99 |
| **4** | `404` 104 | `414` 109 | `424` 114 | `434` 119 | `444` 124 |

x is the high place, z the low place. Reading order of `cells.jsonl` is x, then y, then z.
Magnetic labels of V₂ are digit − 2 and are not stored; the codec already knows them.

`codec.py` · `q5.ts` · `cells.jsonl` · `validator.py` · `host.py` · `ledger.ts`
