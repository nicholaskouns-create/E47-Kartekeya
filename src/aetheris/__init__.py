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
from .flight_runtime import (
    DEFAULT_VEHICLE_SPECS,
    BoundaryTransitionReceipt,
    E47Projection,
    E47Witness,
    E47WitnessReceipt,
    ExperimentalE47Adapter,
    FunctionVehicleAdapter,
    State6DOF,
    VehicleBoundary,
    VehicleRegistry,
    VehicleSpec,
    VehicleStep,
)
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
    "BoundaryTransitionReceipt",
    "DEFAULT_VEHICLE_SPECS",
    "E47Projection",
    "E47Witness",
    "E47WitnessReceipt",
    "ExperimentalE47Adapter",
    "FunctionVehicleAdapter",
    "ModuleReceipt",
    "ModuleResult",
    "RUNTIME_VERSION",
    "RuntimeContext",
    "RuntimeModule",
    "STATE_SCHEMA",
    "State6DOF",
    "VehicleBoundary",
    "VehicleRegistry",
    "VehicleSpec",
    "VehicleStep",
    "StatePacket",
    "canonicalize",
    "digest_data",
]

__version__ = RUNTIME_VERSION
