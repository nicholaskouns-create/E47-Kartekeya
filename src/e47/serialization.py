"""Serialization of E47 validation certificates to JSON.

This module converts immutable validation result dataclasses to JSON-compatible
dictionaries and writes them to disk with reproducible formatting.

Scope
-----
Serialization is faithful: invalid certificates are recorded as-is, without
re-running validation or hiding errors. The serializer's role is data
representation only.
"""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from e47.validation_results import E47ValidationResults


def _to_json_compatible(value: Any) -> Any:
    """Recursively convert a certificate value to JSON-compatible form.

    Supports dataclasses, dicts, lists, tuples, NumPy scalars, and primitives.
    Raises TypeError for unsupported types.

    Parameters
    ----------
    value
        The value to convert.

    Returns
    -------
    Any
        A JSON-compatible representation.

    Raises
    ------
    TypeError
        If the value type is not supported.
    """

    if is_dataclass(value):
        return {
            key: _to_json_compatible(item)
            for key, item in asdict(value).items()
        }

    if isinstance(value, dict):
        return {
            str(key): _to_json_compatible(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple)):
        return [_to_json_compatible(item) for item in value]

    if hasattr(value, "item"):
        return _to_json_compatible(value.item())

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    raise TypeError(
        f"Unsupported certificate value of type {type(value).__name__}: {value!r}"
    )


def validation_results_to_dict(
    results: E47ValidationResults,
) -> dict[str, Any]:
    """Convert aggregated E47 validation results to a JSON-compatible dictionary.

    Parameters
    ----------
    results
        Complete E47 validation certificate.

    Returns
    -------
    dict
        Dictionary with five top-level keys: kernel_validation, projector_validation,
        contraction_validation, semigroup_validation, qutip_validation. Each value
        is a fully JSON-compatible dict.

    Raises
    ------
    TypeError
        If any certificate field contains an unsupported type.
    """

    payload = _to_json_compatible(results)
    # `valid` is a @property on E47ValidationResults, not a dataclass field,
    # so asdict() does not include it.  Add it explicitly.
    payload["valid"] = results.valid
    return payload


def write_validation_certificate(
    results: E47ValidationResults,
    output_path: str | Path,
) -> None:
    """Write an E47 validation certificate to a JSON file.

    The file is written with sorted keys for reproducibility and ends with
    a newline. Character encoding is UTF-8.

    Parameters
    ----------
    results
        Complete E47 validation certificate.
    output_path
        Path to the output JSON file. Parent directories are created if needed.

    Raises
    ------
    TypeError
        If any certificate field contains an unsupported type.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = validation_results_to_dict(results)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, sort_keys=True, indent=2)
        f.write("\n")


def read_validation_certificate(
    input_path: str | Path,
) -> dict[str, Any]:
    """Read a previously written E47 validation certificate from JSON.

    Parameters
    ----------
    input_path
        Path to the JSON file.

    Returns
    -------
    dict
        The deserialized certificate dictionary.

    Raises
    ------
    FileNotFoundError
        If the input file does not exist.
    json.JSONDecodeError
        If the file is not valid JSON.
    """

    path = Path(input_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


__all__ = [
    "read_validation_certificate",
    "validation_results_to_dict",
    "write_validation_certificate",
]
