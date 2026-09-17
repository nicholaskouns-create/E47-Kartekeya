"""Typed, deterministic state objects for the AETHERIS runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
import hashlib
import json
import math
from types import MappingProxyType
from typing import Any, Mapping

import numpy as np


STATE_SCHEMA = "aetheris.state/0.1"
CERTIFICATE_SCHEMA = "aetheris.certificate/0.1"


class EvidenceClass(str, Enum):
    """Mathematical City evidence classes carried by module receipts."""

    E0 = "E0"  # exact
    E1 = "E1"  # machine
    E2 = "E2"  # simulation
    E3 = "E3"  # empirical
    E4 = "E4"  # experimental
    H0 = "H0"  # hardware


def _snapshot(value: Any) -> Any:
    """Take a non-mutating snapshot suitable for a StatePacket payload."""

    if isinstance(value, np.ndarray):
        out = np.array(value, copy=True)
        out.setflags(write=False)
        return out
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): _snapshot(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_snapshot(v) for v in value)
    if isinstance(value, set):
        return tuple(sorted((_snapshot(v) for v in value), key=lambda x: repr(x)))
    return value


def canonicalize(value: Any) -> Any:
    """Convert supported scientific Python values to canonical JSON data."""

    if isinstance(value, np.ndarray):
        return {
            "__ndarray__": True,
            "dtype": str(value.dtype),
            "shape": list(value.shape),
            "data": canonicalize(value.tolist()),
        }
    if isinstance(value, np.generic):
        return canonicalize(value.item())
    if isinstance(value, complex):
        return {"__complex__": [canonicalize(value.real), canonicalize(value.imag)]}
    if isinstance(value, float):
        if math.isnan(value):
            return {"__float__": "nan"}
        if math.isinf(value):
            return {"__float__": "inf" if value > 0 else "-inf"}
        return value
    if isinstance(value, Enum):
        return canonicalize(value.value)
    if is_dataclass(value):
        return canonicalize(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): canonicalize(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [canonicalize(v) for v in value]
    if isinstance(value, set):
        encoded = [canonicalize(v) for v in value]
        return sorted(encoded, key=lambda x: json.dumps(x, sort_keys=True, separators=(",", ":")))
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"Unsupported value for canonical serialization: {type(value).__name__}")


def digest_data(value: Any) -> str:
    """SHA-256 digest of canonical JSON data."""

    encoded = json.dumps(
        canonicalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class AssertionRecord:
    """One machine-checkable assertion emitted by a runtime module."""

    name: str
    passed: bool
    observed: Any = None
    expected: Any = None
    tolerance: float | None = None
    evidence_class: EvidenceClass = EvidenceClass.E1

    def to_record(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": bool(self.passed),
            "observed": canonicalize(self.observed),
            "expected": canonicalize(self.expected),
            "tolerance": self.tolerance,
            "evidence_class": self.evidence_class.value,
        }


@dataclass(frozen=True)
class StatePacket:
    """Immutable-by-snapshot typed state passed between AETHERIS modules."""

    kind: str
    payload: Mapping[str, Any]
    metadata: Mapping[str, Any] = field(default_factory=dict)
    parent_digest: str | None = None
    producer: str | None = None
    schema: str = STATE_SCHEMA

    def __post_init__(self) -> None:
        if not self.kind or not isinstance(self.kind, str):
            raise ValueError("StatePacket.kind must be a non-empty string")
        object.__setattr__(self, "payload", _snapshot(self.payload))
        object.__setattr__(self, "metadata", _snapshot(self.metadata))

    def _content(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "kind": self.kind,
            "payload": self.payload,
            "metadata": self.metadata,
            "parent_digest": self.parent_digest,
            "producer": self.producer,
        }

    @property
    def digest(self) -> str:
        return digest_data(self._content())

    @property
    def packet_id(self) -> str:
        return f"pkt_{self.digest[:20]}"

    def evolve(
        self,
        *,
        producer: str,
        payload: Mapping[str, Any] | None = None,
        metadata: Mapping[str, Any] | None = None,
        kind: str | None = None,
    ) -> "StatePacket":
        """Create a child packet linked to this packet's digest."""

        return StatePacket(
            kind=kind or self.kind,
            payload=self.payload if payload is None else payload,
            metadata=self.metadata if metadata is None else metadata,
            parent_digest=self.digest,
            producer=producer,
        )

    def to_record(self) -> dict[str, Any]:
        record = canonicalize(self._content())
        record["packet_id"] = self.packet_id
        record["digest"] = self.digest
        return record
