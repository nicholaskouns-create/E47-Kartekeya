"""Proof-bound AETHERIS closed-loop coupling for WaveForge -> Eidolon.

This module defines the numerical interface contract. It validates software
coupling semantics only; physical interpretation remains a separate evidence
question.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping
import numpy as np

from .model import AssertionRecord, EvidenceClass, StatePacket, digest_data
from .runtime import ModuleResult, RuntimeContext


@dataclass(frozen=True)
class CouplingConfig:
    dt: float = 1.0 / 120.0
    mass: float = 1.0
    coupling_gain: float = 1.0
    tolerance: float = 1e-12


def _vec3(x: Any, name: str) -> np.ndarray:
    a = np.asarray(x, dtype=np.float64)
    if a.shape != (3,) or not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must be a finite 3-vector")
    return a


def canonical_coupling_step(payload: Mapping[str, Any], cfg: CouplingConfig) -> dict[str, Any]:
    """Deterministic symplectic field-to-flight step.

    WaveForge contributes a sampled force-density resultant F. Eidolon consumes
    the same typed F. Semi-implicit Euler gives v[n+1]=v[n]+dt F/m and
    x[n+1]=x[n]+dt v[n+1]. This is stable for constant forcing and makes the
    interface independently reproducible.
    """
    field = payload["field"]
    craft = payload["craft"]
    force = cfg.coupling_gain * _vec3(field["force"], "field.force")
    position = _vec3(craft["position"], "craft.position")
    velocity = _vec3(craft["velocity"], "craft.velocity")
    if not np.isfinite(cfg.dt) or cfg.dt <= 0 or not np.isfinite(cfg.mass) or cfg.mass <= 0:
        raise ValueError("dt and mass must be finite and positive")
    acceleration = force / cfg.mass
    velocity_next = velocity + cfg.dt * acceleration
    position_next = position + cfg.dt * velocity_next
    return {
        "field": dict(field),
        "craft": {
            **dict(craft),
            "position": position_next,
            "velocity": velocity_next,
            "acceleration": acceleration,
        },
        "coupling": {
            "dt": cfg.dt,
            "mass": cfg.mass,
            "gain": cfg.coupling_gain,
            "force": force,
        },
    }


class WaveForgeEidolonCoupler:
    name = "aetheris.waveforge_eidolon"
    version = "1.0.0"
    evidence_class = EvidenceClass.E1

    def __init__(self, config: CouplingConfig | None = None) -> None:
        self.config = config or CouplingConfig()

    def accepts(self, packet: StatePacket) -> bool:
        return packet.kind == "field.flight" and "field" in packet.payload and "craft" in packet.payload

    def execute(self, packet: StatePacket, context: RuntimeContext) -> ModuleResult:
        cfg = self.config
        out = canonical_coupling_step(packet.payload, cfg)
        force = np.asarray(out["coupling"]["force"])
        v0 = _vec3(packet.payload["craft"]["velocity"], "craft.velocity")
        v1 = np.asarray(out["craft"]["velocity"])
        x0 = _vec3(packet.payload["craft"]["position"], "craft.position")
        x1 = np.asarray(out["craft"]["position"])
        expected_dv = cfg.dt * force / cfg.mass
        expected_dx = cfg.dt * v1
        checks = (
            AssertionRecord("finite_output", bool(np.all(np.isfinite(v1)) and np.all(np.isfinite(x1))), True, True, evidence_class=EvidenceClass.E1),
            AssertionRecord("force_to_velocity_contract", bool(np.allclose(v1-v0, expected_dv, rtol=0, atol=cfg.tolerance)), v1-v0, expected_dv, cfg.tolerance, EvidenceClass.E1),
            AssertionRecord("velocity_to_position_contract", bool(np.allclose(x1-x0, expected_dx, rtol=0, atol=cfg.tolerance)), x1-x0, expected_dx, cfg.tolerance, EvidenceClass.E1),
        )
        child = packet.evolve(producer=self.name, payload=out)
        return ModuleResult(child, checks, {"coupling_digest": digest_data(out["coupling"]), "dt": cfg.dt})


def run_closed_loop(initial: StatePacket, steps: int, config: CouplingConfig | None = None):
    """Execute repeated certified coupling steps and return every immutable state."""
    if steps < 1:
        raise ValueError("steps must be >= 1")
    module = WaveForgeEidolonCoupler(config)
    current = initial
    states = [current]
    receipts = []
    for i in range(steps):
        result = module.execute(current, RuntimeContext("0.1.0", (module.name,), i, "closed-loop"))
        if not all(c.passed for c in result.checks):
            raise RuntimeError("closed-loop coupling invariant failed")
        current = result.packet
        states.append(current)
        receipts.append(result)
    return tuple(states), tuple(receipts)
