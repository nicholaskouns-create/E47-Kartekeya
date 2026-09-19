# Contributing

E47-Kartekeya is an independent research codebase with multiple instruments and experimental lines of work.

Contributions are most useful when they **extend a local component without silently redefining neighboring components**.

## Start with the component contract

Read:

- `lab-manifest.json`
- `docs/lab_architecture.md`
- the local README or source for the component being changed

State the component you are changing and keep its maturity/evidence label accurate.

## A strong change normally includes

- a narrow technical purpose,
- the smallest coherent implementation,
- a deterministic test when feasible,
- provenance for external data,
- an explicit failure mode,
- documentation when a public contract changes.

Experimental work is welcome. Label it as experimental rather than forcing it through a stable interface.

## Before opening a pull request

Run:

```bash
python scripts/check_lab_contract.py
python -m pytest tests/ -v
node --test scripts/check_website.cjs scripts/check_e47_bridge.cjs scripts/check_eidolon_receipt_binding.mjs
```

Run only the relevant subset when your environment cannot support the whole stack, and state exactly what was executed.

## Evidence discipline

Use the repository evidence classes consistently:

- **E0** exact mathematics
- **E1** deterministic machine reconstruction
- **E2** simulation / numerical experiment
- **E3** independent external replication
- **E4** empirical / experimental evidence
- **H0** hardware design or protocol

A new interface, visualization, model integration, or successful simulation does not automatically change evidence class.

## Interface autonomy

CITY CORE and the public homepage may surface an instrument, but they do not own it.

Do not require unrelated components to route through a new abstraction merely for uniformity. Shared libraries are appropriate where they remove real duplication while preserving direct component access.
