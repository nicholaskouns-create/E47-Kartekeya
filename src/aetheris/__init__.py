"""AETHERIS: proof-bound compositional runtime for Mathematical City instruments."""

from .model import (
    CERTIFICATE_SCHEMA,
    STATE_SCHEMA,
    AssertionRecord,
    EvidenceClass,
    StatePacket,
    canonicalize,
    digest_data,
)
from .modules import E47ProjectorModule, FunctionModule, IdentityModule
from .persistence import ExecutionStore, InMemoryStore, JsonlStore
from .runtime import (
    RUNTIME_VERSION,
    AetherisRuntime,
    ExecutionCertificate,
    ExecutionResult,
    ModuleReceipt,
    ModuleResult,
    RuntimeContext,
    RuntimeModule,
)

__all__ = [
    "AetherisRuntime",
    "AssertionRecord",
    "CERTIFICATE_SCHEMA",
    "E47ProjectorModule",
    "EvidenceClass",
    "ExecutionCertificate",
    "ExecutionResult",
    "ExecutionStore",
    "FunctionModule",
    "IdentityModule",
    "InMemoryStore",
    "JsonlStore",
    "ModuleReceipt",
    "ModuleResult",
    "RUNTIME_VERSION",
    "RuntimeContext",
    "RuntimeModule",
    "STATE_SCHEMA",
    "StatePacket",
    "canonicalize",
    "digest_data",
]
