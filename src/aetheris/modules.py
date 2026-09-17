"""Built-in AETHERIS modules and adapters for existing City instruments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

import numpy as np

from .model import AssertionRecord, EvidenceClass, StatePacket
from .runtime import ModuleResult, RuntimeContext


ModuleCallable = Callable[[StatePacket, RuntimeContext], ModuleResult | StatePacket | Mapping[str, Any]]


@dataclass
class FunctionModule:
    """Wrap any existing lab/solver function in the AETHERIS module protocol."""

    name: str
    function: ModuleCallable
    version: str = "0.1.0"
    evidence_class: EvidenceClass = EvidenceClass.E1
    accepted_kind: str | None = None

    def accepts(self, packet: StatePacket) -> bool:
        return self.accepted_kind is None or packet.kind == self.accepted_kind

    def execute(self, packet: StatePacket, context: RuntimeContext) -> ModuleResult:
        output = self.function(packet, context)
        if isinstance(output, ModuleResult):
            return output
        if isinstance(output, StatePacket):
            return ModuleResult(packet=output)
        if isinstance(output, Mapping):
            return ModuleResult(packet=packet.evolve(producer=self.name, payload=output))
        raise TypeError(
            "FunctionModule callable must return ModuleResult, StatePacket, or a mapping payload"
        )


@dataclass
class IdentityModule:
    """Minimal contract module useful for wiring and transport validation."""

    name: str = "aetheris.identity"
    version: str = "0.1.0"
    evidence_class: EvidenceClass = EvidenceClass.E0

    def accepts(self, packet: StatePacket) -> bool:
        return True

    def execute(self, packet: StatePacket, context: RuntimeContext) -> ModuleResult:
        child = packet.evolve(producer=self.name)
        return ModuleResult(
            packet=child,
            checks=(
                AssertionRecord(
                    name="payload_preserved",
                    passed=True,
                    observed=packet.digest,
                    expected="deterministic transport",
                    evidence_class=self.evidence_class,
                ),
            ),
            measurements={"module_index": context.module_index},
        )


@dataclass
class E47ProjectorModule:
    """Project a 125-component state vector into the canonical E47 sector."""

    name: str = "e47.projector"
    version: str = "0.1.0"
    evidence_class: EvidenceClass = EvidenceClass.E1
    state_key: str = "state"
    tolerance: float = 1e-8
    normalize: bool = False

    def accepts(self, packet: StatePacket) -> bool:
        return self.state_key in packet.payload

    def execute(self, packet: StatePacket, context: RuntimeContext) -> ModuleResult:
        from e47.projector import construct_e47_projector

        x = np.asarray(packet.payload[self.state_key], dtype=np.complex128).reshape(-1)
        if x.size != 125:
            raise ValueError(f"E47 projection requires 125 amplitudes, got {x.size}")
        if not np.all(np.isfinite(x.real)) or not np.all(np.isfinite(x.imag)):
            raise ValueError("E47 state contains non-finite amplitudes")

        projector_data = construct_e47_projector()
        P = projector_data.projector.full()
        y = P @ x
        projected_norm = float(np.linalg.norm(y))
        if self.normalize and projected_norm > self.tolerance:
            y = y / projected_norm

        leakage = float(np.linalg.norm(y - P @ y))
        idempotence_error = float(np.linalg.norm(P @ P - P, ord=2))
        rank = int(projector_data.kernel_dimension)

        new_payload = dict(packet.payload)
        new_payload[self.state_key] = y
        new_metadata = dict(packet.metadata)
        new_metadata["aetheris.e47"] = {
            "projector_rank": rank,
            "coherence_fraction": rank / 125,
            "normalized": bool(self.normalize and projected_norm > self.tolerance),
        }

        checks = (
            AssertionRecord(
                name="e47_rank",
                passed=rank == 47,
                observed=rank,
                expected=47,
                evidence_class=self.evidence_class,
            ),
            AssertionRecord(
                name="projector_idempotence",
                passed=idempotence_error <= self.tolerance,
                observed=idempotence_error,
                expected=0.0,
                tolerance=self.tolerance,
                evidence_class=self.evidence_class,
            ),
            AssertionRecord(
                name="projected_state_invariant",
                passed=leakage <= self.tolerance,
                observed=leakage,
                expected=0.0,
                tolerance=self.tolerance,
                evidence_class=self.evidence_class,
            ),
        )

        return ModuleResult(
            packet=packet.evolve(
                producer=self.name,
                payload=new_payload,
                metadata=new_metadata,
            ),
            checks=checks,
            measurements={
                "input_norm": float(np.linalg.norm(x)),
                "projected_norm_before_normalization": projected_norm,
                "projection_leakage": leakage,
                "projector_idempotence_error": idempotence_error,
                "projector_rank": rank,
                "coherence_fraction": rank / 125,
            },
        )
