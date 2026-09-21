# Python source

[Repository home](../README.md) · [Reproduce](../docs/reproducibility.md) · [Command directory](../scripts/README.md)

| Package | Purpose | Start with |
|---|---|---|
| [e47](e47/) | SU(2) kernel, projector, contraction, semigroup, and spectral compilation | [Kernel construction](e47/su2_kernel.py) · [Public exports](e47/__init__.py) |
| [aetheris](aetheris/) | State transitions, persistence, computational receipts, and the typed flight/E47 witness boundary | [Runtime](aetheris/runtime.py) · [Flight boundary](aetheris/flight_runtime.py) · [Guide](../docs/aetheris_runtime.md) |
| [manta](manta/) | Programmable-matter simulation model | [Model](manta/programmable_matter.py) · [Component record](manta/component.json) |

The 5×5×5 packing ledger is not an `e47` package and is not identified with `ker K`. It lives in [q5/](../q5/).

Install from the repository root with Python 3.12+:

```bash
python -m pip install -e . -r requirements.txt -r requirements-dev.txt
```

Browser instruments live in [website/interfaces/](../website/interfaces/); the [instrument directory](../docs/instruments.md) links each app to its source.
