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
    """Project a 125-amplitude state into the canonical rank-47 E47 sector."""

    name: str = "e47.projector"
    version: str = "0.2.0"
    evidence_class: EvidenceClass = EvidenceClass.E1
    state_key: str = "state"
    tolerance: float = 1e-8
    normalize: bool = False

    def accepts(self, packet: StatePacket) -> bool:
        return self.state_key in packet.payload

    def execute(self, packet: StatePacket, context: RuntimeContext) -> ModuleResult:
        from e47.projector import construct_e47_projector
        from e47.su2_kernel import build_e47_operators

        x = np.asarray(packet.payload[self.state_key], dtype=np.complex128).reshape(-1)
        if x.size != 125:
            raise ValueError(f"E47 projection requires 125 amplitudes, got {x.size}")
        if not np.all(np.isfinite(x.real)) or not np.all(np.isfinite(x.imag)):
            raise ValueError("E47 state contains non-finite amplitudes")

        input_norm_squared = float(np.vdot(x, x).real)
        if input_norm_squared <= self.tolerance**2:
            raise ValueError(
                "E47 coherence requires a non-zero 125-amplitude state; "
                "||x||^2 is zero to tolerance"
            )

        operators = build_e47_operators()
        projector_data = construct_e47_projector(operators)
        P = projector_data.projector.full()

        # Validate the matrix actually presented to downstream consumers.  The
        # stored kernel dimension is useful provenance, but the gate is based on
        # the numerical rank of P itself so a malformed projector reports MISS.
        rank = int(np.linalg.matrix_rank(P, tol=self.tolerance))
        projector_status = "PASS" if rank == 47 else "MISS"

        projected = P @ x
        projected_norm = float(np.linalg.norm(projected))
        projected_energy = float(np.vdot(projected, projected).real)
        coherence = float(np.clip(projected_energy / input_norm_squared, 0.0, 1.0))
        complement_fraction = float(np.clip(1.0 - coherence, 0.0, 1.0))

        # Compute <K^2> spectrally, not from a proxy such as rank density.
        # For x = sum_i a_i e_i with K^2 e_i = lambda_i e_i,
        # <K^2> = sum_i lambda_i |a_i|^2 / ||x||^2.
        K2 = operators.kernel_squared.full()
        k2_eigenvalues, k2_eigenvectors = np.linalg.eigh(K2)
        spectral_coefficients = k2_eigenvectors.conj().T @ x
        spectral_weights = np.abs(spectral_coefficients) ** 2
        k2_expectation = float(
            max(0.0, np.dot(k2_eigenvalues.real, spectral_weights) / input_norm_squared)
        )

        rounded_eigenvalues = np.rint(k2_eigenvalues.real).astype(np.int64)
        k2_spectrum = sorted({int(value) for value in rounded_eigenvalues})
        expected_k2_spectrum = [0, 11664, 12544, 19600, 32400, 186624]
        spectral_roundoff = float(
            np.max(np.abs(k2_eigenvalues.real - rounded_eigenvalues))
        )
        spectrum_matches = (
            k2_spectrum == expected_k2_spectrum and spectral_roundoff <= 1e-6
        )

        y = projected
        if self.normalize and projected_norm > self.tolerance:
            y = y / projected_norm

        projection_invariance_error = float(np.linalg.norm(y - P @ y))
        idempotence_error = float(np.linalg.norm(P @ P - P, ord=2))

        new_payload = dict(packet.payload)
        new_payload[self.state_key] = y
        new_metadata = dict(packet.metadata)
        new_metadata["aetheris.e47"] = {
            "carrier_amplitudes": 125,
            "projector_rank": rank,
            "projector_status": projector_status,
            "kernel_fraction": rank / 125,
            "coherence": coherence,
            "complement_fraction": complement_fraction,
            "k2_expectation": k2_expectation,
            "k2_spectrum": k2_spectrum,
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
                name="k2_spectrum",
                passed=spectrum_matches,
                observed=k2_spectrum,
                expected=expected_k2_spectrum,
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
                passed=projection_invariance_error <= self.tolerance,
                observed=projection_invariance_error,
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
                "carrier_amplitudes": 125,
                "input_norm": float(np.sqrt(input_norm_squared)),
                "projected_norm_before_normalization": projected_norm,
                "projection_invariance_error": projection_invariance_error,
                "projector_idempotence_error": idempotence_error,
                "projector_rank": rank,
                "projector_status": projector_status,
                "kernel_fraction": rank / 125,
                "coherence": coherence,
                "complement_fraction": complement_fraction,
                "k2_expectation": k2_expectation,
                "k2_spectrum": k2_spectrum,
                "k2_spectral_roundoff": spectral_roundoff,
            },
        )
