"""EIDOLON sector engine: the lock cap holds lock_target independently of the step size.

Evidence class E2. These are properties of the game model's integrator.
"""

from __future__ import annotations

import pytest

from eidolon import Craft, EidolonEngine


@pytest.mark.parametrize("dt", [0.05, 1.0 / 30.0, 1.0 / 60.0, 0.005, 0.001])
def test_exact_cap_holds_lock_target_at_any_step(dt):
    craft = Craft(mode="translate")
    assert craft.lock_cap == "exact"
    engine = EidolonEngine(craft, dt=dt, duration=12.0).run()
    settled = [s.L for s in engine.history if s.t >= 5.0]
    assert min(settled) >= craft.lock_target - 1e-12
    assert max(settled) <= craft.lock_target + 2e-4
    assert engine.history[-1].n.sum() == pytest.approx(1.0, abs=1e-12)


def test_flight_outcome_no_longer_depends_on_the_step():
    ranges = [
        EidolonEngine(Craft(mode="translate"), dt=dt, duration=48.0).run().history[-1].range_m
        for dt in (0.05, 1.0 / 60.0, 0.005)
    ]
    assert max(ranges) - min(ranges) < 0.5


def test_legacy_cap_settles_above_target_by_the_step_factor():
    craft = Craft(mode="translate", lock_cap="legacy")
    for dt in (0.05, 1.0 / 60.0):
        final = EidolonEngine(craft, dt=dt, duration=48.0).run().history[-1]
        assert final.L == pytest.approx(craft.lock_target / (1.0 - dt), abs=1e-4)


def test_geodesic_mode_is_not_capped():
    final = EidolonEngine(Craft(mode="geodesic"), duration=24.0).run().history[-1]
    assert final.L > 0.99


def test_unknown_lock_cap_is_rejected():
    with pytest.raises(ValueError):
        EidolonEngine(Craft(lock_cap="unknown"))
