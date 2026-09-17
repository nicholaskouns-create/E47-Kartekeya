import numpy as np
from aetheris.model import StatePacket
from aetheris.closed_loop import CouplingConfig, WaveForgeEidolonCoupler, run_closed_loop
from aetheris.runtime import AetherisRuntime


def packet(force=(1., 0., 0.)):
    return StatePacket(kind="field.flight", payload={
        "field": {"force": np.array(force)},
        "craft": {"position": np.zeros(3), "velocity": np.zeros(3)},
    })


def test_typed_coupling_certificate_passes():
    rt = AetherisRuntime()
    rt.register(WaveForgeEidolonCoupler(CouplingConfig(dt=.01, mass=2.)))
    result = rt.execute(packet(), ["aetheris.waveforge_eidolon"])
    assert result.certificate.status == "PASS"
    assert len(result.certificate.receipts) == 1
    assert all(c.passed for c in result.certificate.receipts[0].checks)


def test_constant_force_matches_closed_form_velocity():
    cfg = CouplingConfig(dt=.01, mass=2.)
    states, _ = run_closed_loop(packet((4., 0., 0.)), 100, cfg)
    final = states[-1]
    expected_v = np.array([2., 0., 0.])
    assert np.allclose(final.payload["craft"]["velocity"], expected_v, atol=1e-12, rtol=0)


def test_zero_force_preserves_velocity():
    p = StatePacket(kind="field.flight", payload={
        "field": {"force": np.zeros(3)},
        "craft": {"position": np.zeros(3), "velocity": np.array([1.,2.,3.])},
    })
    states, _ = run_closed_loop(p, 32, CouplingConfig(dt=.005))
    assert np.allclose(states[-1].payload["craft"]["velocity"], [1.,2.,3.], atol=1e-12, rtol=0)


def test_deterministic_replay_digest():
    cfg = CouplingConfig(dt=.01, mass=2.)
    a, _ = run_closed_loop(packet((4.,1.,-2.)), 25, cfg)
    b, _ = run_closed_loop(packet((4.,1.,-2.)), 25, cfg)
    assert a[-1].digest == b[-1].digest


def test_step_partition_convergence():
    # Same constant acceleration over T=1. Semi-implicit position error is O(dt).
    coarse, _ = run_closed_loop(packet((2.,0.,0.)), 100, CouplingConfig(dt=.01, mass=2.))
    fine, _ = run_closed_loop(packet((2.,0.,0.)), 200, CouplingConfig(dt=.005, mass=2.))
    xc = coarse[-1].payload["craft"]["position"][0]
    xf = fine[-1].payload["craft"]["position"][0]
    exact = .5
    assert abs(xf-exact) < abs(xc-exact)
    assert abs(xf-xc) < .01
