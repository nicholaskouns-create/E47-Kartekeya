"""Ubuntu runtime gate for Coherence, Runtime 1.0."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Iterable
import numpy as np

class RuntimeState(str, Enum):
    COHERENT = "COHERENT"
    RESCUE = "RESCUE"
    RECONCILING = "RECONCILING"

@dataclass(frozen=True)
class UbuntuResult:
    admissible: bool
    joint_delta: float
    reasons: tuple[str, ...]
    next_state: RuntimeState

def check(
    values_after: Iterable[float],
    minimums: Iterable[float],
    *,
    joint_before: float,
    joint_after: float,
    consent_ok: bool,
    continuity_ok: bool,
    provenance_ok: bool,
) -> UbuntuResult:
    values = tuple(float(x) for x in values_after)
    floors = tuple(float(x) for x in minimums)
    if not values or len(values) != len(floors):
        raise ValueError("value and minimum vectors must have equal nonzero length")
    if not all(np.isfinite(x) for x in (*values, *floors, joint_before, joint_after)):
        raise ValueError("inputs must be finite")
    delta = float(joint_after - joint_before)
    reasons = []
    if delta <= 0:
        reasons.append("joint_gain_failed")
    if any(x < y for x, y in zip(values, floors)):
        reasons.append("minimum_failed")
    if not consent_ok:
        reasons.append("consent_failed")
    if not continuity_ok:
        reasons.append("continuity_failed")
    if not provenance_ok:
        reasons.append("provenance_failed")
    ok = not reasons
    return UbuntuResult(ok, delta, tuple(reasons),
        RuntimeState.COHERENT if ok else RuntimeState.RESCUE)
