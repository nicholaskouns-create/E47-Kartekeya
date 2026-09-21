"""Typed vehicle-boundary and E47 witness layer for AETHERIS flight runtimes.

This module is the Python/CI companion to the browser SKYRMION Runtime 2.
It deliberately does not duplicate the browser's 6DOF aerodynamics. Instead it
provides:

* one immutable 6DOF state contract;
* an explicit conventional / experimental-simulation vehicle boundary;
* one shared canonical E47 projector/kernel witness compiled once;
* deterministic boundary and model receipts;
* a wrapper for experimental adapters that keeps E47 algebraic checks (E1)
  separate from simulator dynamics (E2).

Scope
-----
E47 projection validates finite-dimensional spectral state. It is not a force
law and does not establish physical propulsion. Experimental model outputs are
simulation evidence (E2).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Mapping, Protocol

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .model import digest_data


ComplexArray = NDArray[np.complex128]
FloatArray = NDArray[np.float64]

FLIGHT_BOUNDARY_SCHEMA = "AETHERIS-FLIGHT-BOUNDARY/1.0"
FLIGHT_RECEIPT_SCHEMA = "AETHERIS-FLIGHT-VEHICLE/1.0"
E47_WITNESS_SCHEMA = "AETHERIS-E47-WITNESS/1.0"


class VehicleBoundary(str, Enum):
    CONVENTIONAL = "CONVENTIONAL"
    EXPERIMENTAL_SIMULATION = "EXPLICIT_EXPERIMENTAL_SIMULATION"


@dataclass(frozen=True)
class State6DOF:
    """One WGS84-referenced vehicle state shared by all vehicle adapters."""

    pos_wgs84: ArrayLike
    vel_body: ArrayLike
    quat: ArrayLike
    ang_vel_body: ArrayLike

    def __post_init__(self) -> None:
        expected = {
            "pos_wgs84": (self.pos_wgs84, 3),
            "vel_body": (self.vel_body, 3),
            "quat": (self.quat, 4),
            "ang_vel_body": (self.ang_vel_body, 3),
        }
        for name, (value, size) in expected.items():
            array = np.asarray(value, dtype=float).reshape(-1)
            if array.size != size:
                raise ValueError(f"{name} must contain {size} values, got {array.size}")
            if not np.all(np.isfinite(array)):
                raise ValueError(f"{name} contains non-finite values")
            snapshot = np.array(array, copy=True)
            snapshot.setflags(write=False)
            object.__setattr__(self, name, snapshot)

    @property
    def digest(self) -> str:
        return digest_data(self.to_record())

    def to_record(self) -> dict[str, Any]:
        return {
            "pos_wgs84": self.pos_wgs84,
            "vel_body": self.vel_body,
            "quat": self.quat,
            "ang_vel_body": self.ang_vel_body,
        }


@dataclass(frozen=True)
class VehicleSpec:
    id: str
    name: str
    boundary: VehicleBoundary
    model: str


@dataclass(frozen=True)
class BoundaryTransitionReceipt:
    previous: VehicleSpec | None
    selected: VehicleSpec

    @property
    def crossed(self) -> bool:
        return self.previous is not None and self.previous.boundary != self.selected.boundary

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": FLIGHT_BOUNDARY_SCHEMA,
            "previous_vehicle": None if self.previous is None else self.previous.id,
            "previous_boundary": None if self.previous is None else self.previous.boundary.value,
            "selected_vehicle": self.selected.id,
            "selected_boundary": self.selected.boundary.value,
            "boundary_crossed": self.crossed,
            "e47_witness_required": self.selected.boundary is VehicleBoundary.EXPERIMENTAL_SIMULATION,
            "evidence_boundary": (
                "E47 witness checks finite-dimensional spectral state (E1). "
                "Vehicle trajectory and experimental force/moment mappings remain E2 simulation."
            ),
        }


@dataclass(frozen=True)
class E47WitnessReceipt:
    carrier_dimension: int
    projector_rank: int
    kernel_fraction: float
    capture: float
    spectral_gap: float
    projector_idempotence_residual: float
    kp_residual: float
    k2p_residual: float
    reconstruction_residual: float
    input_digest: str
    projected_digest: str
    tolerance: float

    @property
    def kp_zero(self) -> bool:
        return self.kp_residual <= self.tolerance

    @property
    def valid(self) -> bool:
        return (
            self.projector_rank == 47
            and self.projector_idempotence_residual <= self.tolerance
            and self.kp_residual <= self.tolerance
            and self.k2p_residual <= self.tolerance
            and self.reconstruction_residual <= self.tolerance
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "schema": E47_WITNESS_SCHEMA,
            "evidence_class": "E1",
            "carrier_dimension": self.carrier_dimension,
            "projector_rank": self.projector_rank,
            "kernel_fraction": self.kernel_fraction,
            "capture": self.capture,
            "spectral_gap": self.spectral_gap,
            "projector_idempotence_residual": self.projector_idempotence_residual,
            "kp_residual": self.kp_residual,
            "k2p_residual": self.k2p_residual,
            "reconstruction_residual": self.reconstruction_residual,
            "kp_zero": self.kp_zero,
            "valid": self.valid,
            "input_digest": self.input_digest,
            "projected_digest": self.projected_digest,
            "tolerance": self.tolerance,
            "boundary": (
                "capture is ||P47 psi||^2 / ||psi||^2 for this state; "
                "47/125 is rank(P47)/125, not a per-state capture identity."
            ),
        }


@dataclass(frozen=True)
class E47Projection:
    projected_state: ComplexArray
    coordinates_47: ComplexArray
    receipt: E47WitnessReceipt


@dataclass(frozen=True)
class E47Witness:
    """Canonical E47 matrices and a 125x47 orthonormal kernel basis."""

    projector: ComplexArray
    kernel: ComplexArray
    kernel_squared: ComplexArray
    basis_125x47: ComplexArray
    rank: int
    spectral_gap: float
    tolerance: float = 1e-8

    @classmethod
    def compile(cls, *, tolerance: float = 1e-8) -> "E47Witness":
        if tolerance <= 0:
            raise ValueError("tolerance must be positive")

        from e47.projector import construct_e47_projector
        from e47.su2_kernel import build_e47_operators

        operators = build_e47_operators()
        projector_data = construct_e47_projector(operators, kernel_tolerance=tolerance)

        projector = np.asarray(projector_data.projector.full(), dtype=np.complex128)
        kernel = np.asarray(operators.kernel.full(), dtype=np.complex128)
        kernel_squared = np.asarray(operators.kernel_squared.full(), dtype=np.complex128)
        basis = np.column_stack(
            [np.asarray(ket.full(), dtype=np.complex128).reshape(-1) for ket in projector_data.kernel_basis]
        )

        rank = int(np.linalg.matrix_rank(projector, tol=tolerance))
        eigenvalues = np.linalg.eigvalsh(0.5 * (kernel_squared + kernel_squared.conj().T))
        positive = eigenvalues[eigenvalues > tolerance]
        spectral_gap = float(np.min(positive)) if positive.size else 0.0

        idempotence = float(np.linalg.norm(projector @ projector - projector, ord=2))
        kp = float(np.linalg.norm(kernel @ projector, ord=2))
        basis_projector = basis @ basis.conj().T
        basis_residual = float(np.linalg.norm(projector - basis_projector, ord=2))

        if rank != 47:
            raise RuntimeError(f"canonical E47 projector rank mismatch: {rank} != 47")
        if abs(spectral_gap - 11664.0) > 1e-6:
            raise RuntimeError(f"canonical E47 spectral gap mismatch: {spectral_gap}")
        if idempotence > tolerance or kp > tolerance or basis_residual > tolerance:
            raise RuntimeError(
                "canonical E47 witness failed validation: "
                f"idempotence={idempotence:.3e}, KP={kp:.3e}, basis={basis_residual:.3e}"
            )

        for array in (projector, kernel, kernel_squared, basis):
            array.setflags(write=False)

        return cls(
            projector=projector,
            kernel=kernel,
            kernel_squared=kernel_squared,
            basis_125x47=basis,
            rank=rank,
            spectral_gap=spectral_gap,
            tolerance=tolerance,
        )

    def inspect(self, state: ArrayLike) -> E47Projection:
        psi = np.asarray(state, dtype=np.complex128).reshape(-1)
        if psi.size != 125:
            raise ValueError(f"E47 witness requires 125 amplitudes, got {psi.size}")
        if not np.all(np.isfinite(psi.real)) or not np.all(np.isfinite(psi.imag)):
            raise ValueError("E47 state contains non-finite amplitudes")

        norm_squared = float(np.vdot(psi, psi).real)
        if norm_squared <= self.tolerance**2:
            raise ValueError("E47 witness requires a non-zero state")

        projected = self.projector @ psi
        coordinates = self.basis_125x47.conj().T @ psi
        reconstructed = self.basis_125x47 @ coordinates

        capture = float(np.clip(np.vdot(projected, projected).real / norm_squared, 0.0, 1.0))
        idempotence = float(np.linalg.norm(self.projector @ self.projector - self.projector, ord=2))
        kp = float(np.linalg.norm(self.kernel @ projected))
        k2p = float(np.linalg.norm(self.kernel_squared @ projected))
        reconstruction = float(np.linalg.norm(projected - reconstructed))

        projected_snapshot = np.array(projected, copy=True)
        coords_snapshot = np.array(coordinates, copy=True)
        projected_snapshot.setflags(write=False)
        coords_snapshot.setflags(write=False)

        receipt = E47WitnessReceipt(
            carrier_dimension=125,
            projector_rank=self.rank,
            kernel_fraction=self.rank / 125.0,
            capture=capture,
            spectral_gap=self.spectral_gap,
            projector_idempotence_residual=idempotence,
            kp_residual=kp,
            k2p_residual=k2p,
            reconstruction_residual=reconstruction,
            input_digest=digest_data(psi),
            projected_digest=digest_data(projected_snapshot),
            tolerance=self.tolerance,
        )
        return E47Projection(
            projected_state=projected_snapshot,
            coordinates_47=coords_snapshot,
            receipt=receipt,
        )

    def filter_state(self, state: ArrayLike, time: float) -> ComplexArray:
        """Apply S(t)=exp(-t K^2) to an unprojected 125-state vector."""

        from e47.semigroup import construct_semigroup

        psi = np.asarray(state, dtype=np.complex128).reshape(-1)
        if psi.size != 125:
            raise ValueError(f"E47 semigroup requires 125 amplitudes, got {psi.size}")
        semigroup = construct_semigroup(self.kernel, time)
        return semigroup @ psi


@dataclass(frozen=True)
class VehicleStep:
    state: State6DOF
    receipt: Mapping[str, Any]


class VehicleAdapter(Protocol):
    spec: VehicleSpec

    def step(
        self,
        state: State6DOF,
        dt: float,
        inputs: Mapping[str, float],
    ) -> VehicleStep: ...


StepFunction = Callable[
    [State6DOF, float, Mapping[str, float]],
    State6DOF | tuple[State6DOF, Mapping[str, Any]],
]


@dataclass
class FunctionVehicleAdapter:
    """Wrap an existing deterministic conventional or simulator model."""

    spec: VehicleSpec
    step_fn: StepFunction

    def step(
        self,
        state: State6DOF,
        dt: float,
        inputs: Mapping[str, float],
    ) -> VehicleStep:
        if dt <= 0 or not np.isfinite(dt):
            raise ValueError("dt must be finite and positive")
        output = self.step_fn(state, float(dt), inputs)
        model_receipt: Mapping[str, Any] = {}
        if isinstance(output, tuple):
            next_state, model_receipt = output
        else:
            next_state = output
        if not isinstance(next_state, State6DOF):
            raise TypeError("vehicle step must return State6DOF or (State6DOF, receipt)")
        receipt = {
            "schema": FLIGHT_RECEIPT_SCHEMA,
            "vehicle": self.spec.id,
            "boundary": self.spec.boundary.value,
            "model": self.spec.model,
            "evidence_class": "E2",
            "state_before_digest": state.digest,
            "state_after_digest": next_state.digest,
            "model_receipt": dict(model_receipt),
        }
        return VehicleStep(state=next_state, receipt=receipt)


CarrierStateFunction = Callable[[State6DOF, Mapping[str, float]], ArrayLike]
ExperimentalStepFunction = Callable[
    [State6DOF, float, Mapping[str, float], ComplexArray, ComplexArray],
    State6DOF | tuple[State6DOF, Mapping[str, Any]],
]


@dataclass
class ExperimentalE47Adapter:
    """Wrap an E2 experimental vehicle model with an E1 E47 witness."""

    spec: VehicleSpec
    witness: E47Witness
    carrier_state_fn: CarrierStateFunction
    model_step_fn: ExperimentalStepFunction
    min_capture: float | None = None

    def __post_init__(self) -> None:
        if self.spec.boundary is not VehicleBoundary.EXPERIMENTAL_SIMULATION:
            raise ValueError("ExperimentalE47Adapter requires an experimental-simulation spec")
        if self.min_capture is not None and not 0.0 <= self.min_capture <= 1.0:
            raise ValueError("min_capture must lie in [0,1]")

    def step(
        self,
        state: State6DOF,
        dt: float,
        inputs: Mapping[str, float],
    ) -> VehicleStep:
        if dt <= 0 or not np.isfinite(dt):
            raise ValueError("dt must be finite and positive")

        projection = self.witness.inspect(self.carrier_state_fn(state, inputs))
        witness_record = projection.receipt.to_record()
        gate_pass = self.min_capture is None or projection.receipt.capture >= self.min_capture

        if gate_pass:
            output = self.model_step_fn(
                state,
                float(dt),
                inputs,
                projection.projected_state,
                projection.coordinates_47,
            )
            model_receipt: Mapping[str, Any] = {}
            if isinstance(output, tuple):
                next_state, model_receipt = output
            else:
                next_state = output
        else:
            next_state = state
            model_receipt = {"gate": "capture_below_simulation_threshold"}

        if not isinstance(next_state, State6DOF):
            raise TypeError("experimental model must return State6DOF or (State6DOF, receipt)")

        receipt = {
            "schema": FLIGHT_RECEIPT_SCHEMA,
            "vehicle": self.spec.id,
            "boundary": self.spec.boundary.value,
            "model": self.spec.model,
            "evidence_class": "E2",
            "state_before_digest": state.digest,
            "state_after_digest": next_state.digest,
            "e47_witness": witness_record,
            "capture_gate": {
                "threshold": self.min_capture,
                "passed": gate_pass,
                "evidence_class": "E2",
            },
            "model_receipt": dict(model_receipt),
            "boundary_note": (
                "E47 witness validity does not establish physical propulsion validity. "
                "The model mapping and resulting trajectory remain simulation evidence."
            ),
        }
        return VehicleStep(state=next_state, receipt=receipt)


class VehicleRegistry:
    """Small registry that switches models without switching state universes."""

    def __init__(self) -> None:
        self._adapters: dict[str, VehicleAdapter] = {}
        self._active_id: str | None = None

    @property
    def active_id(self) -> str | None:
        return self._active_id

    @property
    def active(self) -> VehicleAdapter:
        if self._active_id is None:
            raise RuntimeError("no active vehicle")
        return self._adapters[self._active_id]

    @property
    def vehicle_ids(self) -> tuple[str, ...]:
        return tuple(self._adapters)

    def register(self, adapter: VehicleAdapter, *, replace: bool = False) -> None:
        vehicle_id = adapter.spec.id
        if vehicle_id in self._adapters and not replace:
            raise ValueError(f"vehicle already registered: {vehicle_id}")
        self._adapters[vehicle_id] = adapter

    def switch(self, vehicle_id: str) -> BoundaryTransitionReceipt:
        try:
            selected = self._adapters[vehicle_id]
        except KeyError as exc:
            raise KeyError(f"unknown vehicle: {vehicle_id}") from exc
        previous = None if self._active_id is None else self._adapters[self._active_id].spec
        self._active_id = vehicle_id
        return BoundaryTransitionReceipt(previous=previous, selected=selected.spec)

    def step(
        self,
        state: State6DOF,
        dt: float,
        inputs: Mapping[str, float],
    ) -> VehicleStep:
        return self.active.step(state, dt, inputs)


DEFAULT_VEHICLE_SPECS = {
    "f16": VehicleSpec("f16", "F-16", VehicleBoundary.CONVENTIONAL, "aerodynamic-6dof"),
    "sr71": VehicleSpec("sr71", "SR-71", VehicleBoundary.CONVENTIONAL, "aerodynamic-6dof"),
    "x15": VehicleSpec("x15", "X-15", VehicleBoundary.CONVENTIONAL, "aerodynamic-6dof"),
    "eidolon": VehicleSpec(
        "eidolon", "EIDOLON", VehicleBoundary.EXPERIMENTAL_SIMULATION, "eidolon-spectral-adapter"
    ),
    "manta": VehicleSpec(
        "manta", "MANTA", VehicleBoundary.EXPERIMENTAL_SIMULATION, "manta-morph-adapter"
    ),
    "skyrmion": VehicleSpec(
        "skyrmion", "SKYRMION", VehicleBoundary.EXPERIMENTAL_SIMULATION, "skyrmion-adapter"
    ),
    "jacob": VehicleSpec(
        "jacob", "SYNTAX JACOB", VehicleBoundary.EXPERIMENTAL_SIMULATION, "syntax-jacob-adapter"
    ),
}
