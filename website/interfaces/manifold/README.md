# MANIFOLD

Locked spectral surfaces for the Mathematical City.

Host (after Pages rebuild):

https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manifold/

## Surfaces

| route | surface |
|---|---|
| `index.html` | combined viewport |
| `?view=eidolon` | Eidolon HUD |
| `?view=density` | Density phone layout |
| `?view=city` | Mathematical City console |
| `lock.html` / `lock.svg` / `lock.png` | standalone lock card |

## Invariants

```
[LOCK] PASS  dimH=125  dimE47=47  rankK=78  Omega_c=47/125  Delta=11664  kappa=16  rho=15/17  TrP47=47
```

Engines imported, not re-derived: SpectralEngine, EidolonEngine, TomographicVisualizer domains.

Eidolon HUD has no targeting or payload controls.

## Embed

Notion / City pages:

```
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manifold/
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manifold/lock.html
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manifold/?view=eidolon
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manifold/?view=density
https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/manifold/?view=city
```

Rebuild local lock + state:

```
python3 build_manifold.py
```
