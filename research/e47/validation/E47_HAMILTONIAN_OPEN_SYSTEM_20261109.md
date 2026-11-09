# E47 Hamiltonian gradient, unitary and GKSL certificate

**Date:** 2026-11-09  
**Evidence:** finite-dimensional exact mathematics plus executed Python/Numpy/SciPy model, not physical experiment.  
**Result:** 14/14 recorded checks pass.

## Model

Let `C` be the total-spin Casimir on `V_2 tensor V_2 tensor V_2` (dimension 125). Define

`K = (C - 6 I)(C - 30 I)`, `P = P_6 + P_30`, `Q = I - P`, `H = g K^2`, `g=1/11664`.

Then `rank(P)=47`, `rank(Q)=78`, `ker(H)=ran(P)`, the positive gap of `K^2` is `11664`, and its maximum eigenvalue is `186624`.

**Gradient:** `d psi/dt = -H psi`; `||Q psi(t)|| <= exp(-t)||Q psi(0)||` for this normalized g.

**Unitary:** `d rho/dt = -i[H,rho]`; `Tr(Q rho(t))` is constant.

**Lindblad:** with `L_a = |s><e_a|` for 78 orthonormal Q basis states and one normalized selected state `s`, the GKSL generator yields `Tr(Q rho(t)) = Tr(Q rho(0)) exp(-t)` for `kappa=1`. This is a constructed relaxation model, not spontaneous decay caused by the closed Hamiltonian alone.

For seeded state 47, initial Q population = `0.6702997212702106`; at dimensionless t=8, Lindblad population = `0.0002248605059796261`, versus unitary population = `0.6702997212702106`. Maximum trace error `2.22e-16`; minimum numerical density eigenvalue `-1.17e-15`; finite difference GKSL derivative error `4.40e-5`.

## Reproduction

```bash
python -m pip install numpy scipy matplotlib
python validate.py
```

The script writes `results.json` and `comparison.png`. In the seven GitHub repositories, the same source is named `research/e47/validation/e47_hamiltonian_open_system_20261109.py`, and JSON is named `e47_hamiltonian_open_system_20261109_results.json`.

## Artifact SHA-256

- `validate.py`: `a39674dcee50b38b6887517e01630a982aeef52901c7033889774e9ab9bf7fb6`
- `results.json`: `8b67eff4d4c253ce826cd7e78c7544fc86a1313dc0e8ef735f7b7c1273e1d841`
- `comparison.png`: `b80d976fccf7e0f73650e77e6a00ec9afdd32f681463396997330a8982145b07`

## Links

- [Canonical GitHub source](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/validation/e47_hamiltonian_open_system_20261109.py)
- [Frozen JSON receipt](https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/e47/validation/e47_hamiltonian_open_system_20261109_results.json)
- [Published E47 visual instrument](https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/hamiltonian-memory/)
- [The Mathematical City Notion hub](https://app.notion.com/p/0b778ea1fbe04d20b7b3e998abd4ca76)

## Scope

The analytic gradient and Lindblad decay laws follow from the chosen operators; the numerical checks verify one implementation. Physical materials, neutrino-phonon interactions, qubit hardware, experimental quantum-memory fidelity and coherence lifetime are separate questions. The Lindblad reset maps the Q sector into a chosen selected state and does not recover arbitrary encoded logical quantum information from Q.