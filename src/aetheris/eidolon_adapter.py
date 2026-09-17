"""Eidolon ↔ AETHERIS citizen adapter contract.

The deployed transport lives in the Supabase `eidolon-city-adapter` edge function.
This module keeps the repository-side typed contract explicit and testable.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping

CITY_GRAMMAR = "CITY-INVARIANT/1.0"
WORLD_ID = "EIDOLON-CITY-01"

@dataclass(frozen=True)
class WorldInteraction:
    actor_code: str
    operation: str
    interaction: Mapping[str, Any]

    def invariant_packet(self, *, runtime_instance: str, identity: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "schema": CITY_GRAMMAR,
            "object": {"actor_code": self.actor_code, "world_id": WORLD_ID},
            "operator": self.operation,
            "invariant": {"identity": dict(identity), "state_scope": "private_to_instance"},
            "witness": dict(self.interaction),
            "evidence": "E1",
            "provenance": {"runtime_instance": runtime_instance},
            "next_action": "route_to_citizen_runtime",
        }

LAY_GUIDE = {
    "sequence": ["What is this?", "Try it", "What changed?", "Why it matters"],
    "default_mode": "lay",
}

EGGHEAD_MODE = {
    "default_hidden": True,
    "shows": ["equations", "evidence_class", "proof_witness", "provenance", "AETHERIS receipt", "state digests"],
}

QUIET_SIMULATION = {
    "hud": "minimal",
    "advanced_panels": "on_demand",
    "decorative_motion": "reduced",
    "technical_overlay": "Egghead Mode",
}
