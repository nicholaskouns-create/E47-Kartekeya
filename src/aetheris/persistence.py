"""Optional persistence adapters for AETHERIS execution records."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Protocol

from .model import canonicalize
from .runtime import ExecutionResult


class ExecutionStore(Protocol):
    def append(self, result: ExecutionResult) -> None: ...


@dataclass
class InMemoryStore:
    """Simple non-governing store useful for tests and embedded runtimes."""

    records: list[dict] = field(default_factory=list)

    def append(self, result: ExecutionResult) -> None:
        self.records.append(
            {
                "certificate": result.certificate.to_record(),
                "packet": result.packet.to_record(),
            }
        )


@dataclass
class JsonlStore:
    """Append-only local store; each line is independently portable JSON."""

    path: Path | str

    def append(self, result: ExecutionResult) -> None:
        path = Path(self.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "certificate": result.certificate.to_record(),
            "packet": result.packet.to_record(),
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(
                json.dumps(
                    canonicalize(record),
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            )
