#!/usr/bin/env python3
"""EIDOLON — KKP-R sector ODE on the spin-2 cube."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List
import numpy as np

DIM_H = 125
DIM_E47 = 47
DIM_COMP = 78
OMEGA_C = 47.0 / 125.0
DELTA = 11664
KAPPA = 16
G0 = 9.80665
C_LIGHT = 299_792_458.0
EPS = 1e-9
SECTOR_DIMS = np.array([1, 9, 25, 28, 27, 22, 13], dtype=float)
MU2 = np.array([32400, 12544, 0, 11664, 19600, 0, 186624], dtype=float)
GAMMA = MU2 / DELTA
P47 = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0])
KERNEL_MIX = np.array([0, 0, 25, 0, 0, 22, 0], dtype=float) / 47.0
APP_TITLE = "EIDOLON"
APP_SUBTITLE = "Coherence Propulsion Console"
APP_ID = "EIDOLON / KKP-R / E47 / SECTOR ODE"

def _repo_artifacts() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "src").is_dir() and (p / "research").is_dir():
            d = p / "artifacts"
            d.mkdir(parents=True, exist_ok=True)
            return d
    d = Path.cwd() / "artifacts"
    d.mkdir(parents=True, exist_ok=True)
    return d

def assert_lock() -> None:
    assert int(SECTOR_DIMS.sum()) == DIM_H
    assert int(SECTOR_DIMS[P47 == 1].sum()) == DIM_E47
    assert int(MU2[3]) == DELTA
    assert int(GAMMA[6]) == KAPPA
    assert abs(OMEGA_C - 0.376) < 1e-12

assert_lock()


def lambda_p47_matrix() -> np.ndarray:
    """Full 125x125 Eidolon lock projector from the canonical Lambda binding."""
    from e47.lexical_spine import canonical_lambda_matrix
    return canonical_lambda_matrix()


def project_e47_state(state) -> np.ndarray:
    """Apply the canonical full-state Eidolon lock projector."""
    from e47.lexical_spine import project_e47_state as _project
    return _project(state)


@dataclass
class Craft:
    mass_kg: float = 1200.0
    lock_target: float = 0.92
    gain: float = 0.70
    heading_deg: float = 38.0
    pump: float = 0.72
    bus_kw: float = 250.0
    mode: str = "translate"
    scale: str = "kernel"
    seed: int = 47

@dataclass
class Sample:
    t: float
    n: np.ndarray
    L: float
    R: float
    omega: float
    m_eff: float
    thrust: float
    accel: float
    x: float
    y: float
    vx: float
    vy: float
    speed: float
    range_m: float
    heading: float
    budget: float
    stability: float
    pump_into: float
    residual_power: float
    phase: str

class EidolonEngine:
    def __init__(self, craft: Craft | None = None, dt: float = 1.0 / 60.0, duration: float = 48.0):
        self.craft = craft or Craft()
        self.dt = float(dt)
        self.duration = float(duration)
        self.history: List[Sample] = []
        self.n = SECTOR_DIMS / DIM_H
    def lock(self, n=None) -> float:
        n = self.n if n is None else n
        return float((n[2] + n[5]) / max(float(n.sum()), EPS))
    def omega(self, L: float) -> float:
        return float(OMEGA_C * (1.0 - 0.18 * (1.0 - L)) + 0.12 * max(0.0, L - OMEGA_C))
    def m_eff(self, L: float) -> float:
        return self.craft.mass_kg * (DIM_COMP / DIM_H * (1.0 - L) + 1e-6)
    def eta(self, L: float) -> float:
        return float(np.clip(L * L * (1.0 - np.exp(-4.0 * max(0.0, L - 0.15))), 0.0, 1.0))
    def v_e(self, L: float) -> float:
        return C_LIGHT * OMEGA_C * (0.08 + 0.92 * L)
    def phase(self, t: float, L: float) -> str:
        if L < OMEGA_C:
            return "ACQUIRE"
        return {"hover": "HOLD", "geodesic": "COAST", "pulse": "PULSE-HI" if (t % 2.4) < 0.96 else "PULSE-LO", "acquire": "ACQUIRE"}.get(self.craft.mode, "BURN")
    def pump_vector(self, t: float, L: float) -> np.ndarray:
        target = self.craft.lock_target
        if self.craft.mode == "geodesic":
            target = min(1.0, target + 0.08)
        duty = 1.0
        if self.craft.mode == "pulse":
            duty = 1.0 if (t % 2.4) < 0.96 else 0.12
        if self.craft.mode == "geodesic":
            duty = 0.25
        return (self.craft.pump * max(0.0, target - L) * duty * 1.8) * KERNEL_MIX
    def thrust_of(self, L: float, omega: float, n: np.ndarray, t: float) -> float:
        if self.craft.mode in ("geodesic", "acquire", "hover"):
            return 0.0
        resid = float(np.dot(n / max(n.sum(), EPS), GAMMA))
        if self.craft.scale == "si":
            T = 2.0 * self.eta(L) * (self.craft.bus_kw * 1000.0) / max(self.v_e(L), 1.0)
        else:
            T = self.craft.gain * L * (omega / OMEGA_C) * (resid / KAPPA) * self.craft.mass_kg * G0
        if self.craft.mode == "pulse":
            T *= 1.55 if (t % 2.4) < 0.96 else 0.06
        return float(max(0.0, T))
    def stability(self, L: float, omega: float, n: np.ndarray) -> float:
        leak = float(np.dot(n / max(n.sum(), EPS), GAMMA * (1.0 - P47)))
        return float(np.clip(1.0 - abs(omega - OMEGA_C) / OMEGA_C - 0.25 * leak - 0.15 * (1.0 - L), 0, 1))
    def run(self) -> "EidolonEngine":
        self.n = SECTOR_DIMS / DIM_H
        x = y = vx = vy = 0.0
        budget = 1.0
        heading = np.deg2rad(self.craft.heading_deg)
        t = 0.0
        self.history.clear()
        for _ in range(int(self.duration / self.dt) + 1):
            n = self.n
            L = self.lock(n)
            pump = self.pump_vector(t, L)
            dn = -GAMMA * n + pump
            leak = float(np.sum(np.maximum(-dn * (P47 == 0), 0.0)))
            dn = dn.astype(float)
            dn[2] += leak * (25.0 / 47.0)
            dn[5] += leak * (22.0 / 47.0)
            n = np.maximum(n + dn * self.dt, 0.0)
            n = n / max(n.sum(), EPS)
            Ltmp = float((n[2] + n[5]) / max(n.sum(), EPS))
            target = min(1.0, self.craft.lock_target + (0.08 if self.craft.mode == "geodesic" else 0.0))
            if Ltmp > target + 1e-4 and self.craft.mode != "geodesic":
                n[2] *= target / Ltmp
                n[5] *= target / Ltmp
                n = n / max(n.sum(), EPS)
            self.n = n
            L = self.lock(n)
            omega = self.omega(L)
            me = self.m_eff(L)
            T = self.thrust_of(L, omega, n, t)
            drain = 0.0035 * self.craft.pump * (0.25 + L) * (0.4 if self.craft.mode == "geodesic" else 1.0)
            if self.craft.mode == "pulse" and (t % 2.4) < 0.96:
                drain *= 1.7
            budget = float(np.clip(budget - drain * self.dt, 0.0, 1.0))
            if budget < 0.06:
                T *= budget / 0.06
            a = float(np.clip(T / max(me, EPS), 0.0, 2500.0))
            if self.craft.mode in ("hover", "geodesic", "acquire"):
                ax = ay = 0.0
            else:
                ax, ay = a * np.cos(heading), a * np.sin(heading)
            vx += ax * self.dt; vy += ay * self.dt; x += vx * self.dt; y += vy * self.dt
            self.history.append(Sample(t=t, n=n.copy(), L=L, R=1.0-L, omega=omega, m_eff=me, thrust=T, accel=a, x=x, y=y, vx=vx, vy=vy, speed=float(np.hypot(vx, vy)), range_m=float(np.hypot(x, y)), heading=float(self.craft.heading_deg), budget=budget, stability=self.stability(L, omega, n), pump_into=float(pump.sum()), residual_power=float(np.dot(n, GAMMA)), phase=self.phase(t, L)))
            t += self.dt
        return self
    def arr(self, key: str) -> np.ndarray:
        return np.array([getattr(s, key) for s in self.history])
    def summary(self) -> str:
        last = self.history[-1]
        L = self.arr("L")
        t_lock = next((s.t for s in self.history if s.L >= OMEGA_C), float("nan"))
        return "\n".join([f"{APP_TITLE}: {APP_SUBTITLE}", f"[ok] SPECTRAL  Omega_c={OMEGA_C:.3f}  dim E47={DIM_E47}  kappa={KAPPA}", f"[ok] ACQUIRE   t(L>=Omega_c)={t_lock:.2f}s  L0={L[0]:.3f} -> Linf={last.L:.3f}", f"[ok] TERMINAL  Omega={last.omega:.3f}  m_eff={last.m_eff:.3f}  S={last.stability:.3f}"])
    def render(self, out_path: str) -> str:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(10, 4), facecolor="#070B14")
        ax[0].plot(self.arr("t"), self.arr("L"), color="#10B981"); ax[0].axhline(OMEGA_C, color="#EF4444", ls=":"); ax[0].set_title("lock L(t)")
        ax[1].plot(self.arr("x"), self.arr("y"), color="#38BDF8"); ax[1].set_title("trajectory")
        for a in ax:
            a.set_facecolor("#0B1220"); a.tick_params(colors="#94A3B8")
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor=fig.get_facecolor()); plt.close(fig)
        return out_path

def main() -> None:
    eng = EidolonEngine(Craft(mode="translate"), duration=24.0).run()
    print(eng.summary())
    print("RENDER", eng.render(str(_repo_artifacts() / "Eidolon_Propulsion_Sim_Dashboard.png")))

if __name__ == "__main__":
    main()
