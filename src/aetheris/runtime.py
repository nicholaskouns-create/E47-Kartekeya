"""Deterministic compositional execution engine for AETHERIS."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .model import (
    CERTIFICATE_SCHEMA,
    AssertionRecord,
    EvidenceClass,
    StatePacket,
    canonicalize,
    digest_data,
)


RUNTIME_VERSION = "0.1.0"


@dataclass(frozen=True)
class RuntimeContext:
    """Deterministic execution context visible to a module."""

    runtime_version: str
    pipeline: tuple[str, ...]
    module_index: int
    run_label: str | None = None


@dataclass(frozen=True)
class ModuleResult:
    """Output of one runtime module."""

    packet: StatePacket
    checks: tuple[AssertionRecord, ...] = ()
    measurements: Mapping[str, Any] = field(default_factory=dict)


class RuntimeModule(Protocol):
    """Minimal protocol implemented by every AETHERIS engine adapter."""

    name: str
    version: str
    evidence_class: EvidenceClass

    def accepts(self, packet: StatePacket) -> bool: ...

    def execute(self, packet: StatePacket, context: RuntimeContext) -> ModuleResult: ...


@dataclass(frozen=True)
class ModuleReceipt:
    module: str
    version: str
    evidence_class: EvidenceClass
    input_digest: str
    output_digest: str
    checks: tuple[AssertionRecord, ...]
    measurements: Mapping[str, Any]

    @property
    def status(self) -> str:
        return "PASS" if all(check.passed for check in self.checks) else "FAIL"

    def to_record(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "version": self.version,
            "evidence_class": self.evidence_class.value,
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "status": self.status,
            "checks": [check.to_record() for check in self.checks],
            "measurements": canonicalize(self.measurements),
        }


@dataclass(frozen=True)
class ExecutionCertificate:
    """Proof-bound execution receipt for one AETHERIS pipeline run."""

    pipeline: tuple[str, ...]
    input_digest: str
    output_digest: str
    receipts: tuple[ModuleReceipt, ...]
    runtime_version: str = RUNTIME_VERSION
    schema: str = CERTIFICATE_SCHEMA

    @property
    def status(self) -> str:
        return "PASS" if all(r.status == "PASS" for r in self.receipts) else "FAIL"

    def unsigned_record(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "runtime_version": self.runtime_version,
            "pipeline": list(self.pipeline),
            "input_digest": self.input_digest,
            "output_digest": self.output_digest,
            "status": self.status,
            "receipts": [receipt.to_record() for receipt in self.receipts],
        }

    @property
    def digest(self) -> str:
        return digest_data(self.unsigned_record())

    def to_record(self) -> dict[str, Any]:
        record = self.unsigned_record()
        record["certificate_digest"] = self.digest
        return record


@dataclass(frozen=True)
class ExecutionResult:
    packet: StatePacket
    certificate: ExecutionCertificate


class AetherisRuntime:
    """Registry-driven state packet runtime with deterministic certification."""

    def __init__(self) -> None:
        self._modules: dict[str, RuntimeModule] = {}

    @property
    def module_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._modules))

    def register(self, module: RuntimeModule, *, replace: bool = False) -> None:
        if module.name in self._modules and not replace:
            raise ValueError(f"Module already registered: {module.name}")
        self._modules[module.name] = module

    def get(self, name: str) -> RuntimeModule:
        try:
            return self._modules[name]
        except KeyError as exc:
            raise KeyError(f"Unknown AETHERIS module: {name}") from exc

    def execute(
        self,
        packet: StatePacket,
        pipeline: Sequence[str],
        *,
        run_label: str | None = None,
        stop_on_failure: bool = True,
        raise_on_error: bool = False,
    ) -> ExecutionResult:
        pipeline_tuple = tuple(pipeline)
        current = packet
        receipts: list[ModuleReceipt] = []

        for index, name in enumerate(pipeline_tuple):
            module = self.get(name)
            input_digest = current.digest
            context = RuntimeContext(
                runtime_version=RUNTIME_VERSION,
                pipeline=pipeline_tuple,
                module_index=index,
                run_label=run_label,
            )

            if not module.accepts(current):
                check = AssertionRecord(
                    name="module_accepts_packet",
                    passed=False,
                    observed=current.kind,
                    expected=f"accepted by {module.name}",
                    evidence_class=module.evidence_class,
                )
                receipts.append(
                    ModuleReceipt(
                        module=module.name,
                        version=module.version,
                        evidence_class=module.evidence_class,
                        input_digest=input_digest,
                        output_digest=input_digest,
                        checks=(check,),
                        measurements={},
                    )
                )
                if stop_on_failure:
                    break
                continue

            try:
                result = module.execute(current, context)
                if not isinstance(result.packet, StatePacket):
                    raise TypeError("ModuleResult.packet must be a StatePacket")
                current = result.packet
                receipt = ModuleReceipt(
                    module=module.name,
                    version=module.version,
                    evidence_class=module.evidence_class,
                    input_digest=input_digest,
                    output_digest=current.digest,
                    checks=tuple(result.checks),
                    measurements=result.measurements,
                )
            except Exception as exc:
                if raise_on_error:
                    raise
                check = AssertionRecord(
                    name="module_execution",
                    passed=False,
                    observed=f"{type(exc).__name__}: {exc}",
                    expected="successful execution",
                    evidence_class=module.evidence_class,
                )
                receipt = ModuleReceipt(
                    module=module.name,
                    version=module.version,
                    evidence_class=module.evidence_class,
                    input_digest=input_digest,
                    output_digest=input_digest,
                    checks=(check,),
                    measurements={},
                )

            receipts.append(receipt)
            if receipt.status == "FAIL" and stop_on_failure:
                break

        certificate = ExecutionCertificate(
            pipeline=pipeline_tuple,
            input_digest=packet.digest,
            output_digest=current.digest,
            receipts=tuple(receipts),
        )
        return ExecutionResult(packet=current, certificate=certificate)
