"""MANTA E47 fused engines.

Spectral kernel Γ = I − εK² on V₂⊗³ (dim 125).
THE MATRIX: classical statevector n≤8 with sampled-amplitude 125-lift.
MANTA: typed simulation bridge — capture scales thrust. Not a physical propulsion law.

Evidence: E0/E1 algebra of K; E2 motion; lift is not a Hilbert isomorphism.
"""
import numpy as np
from dataclasses import dataclass

CASIMIR = np.array([0., 2., 6., 12., 20., 30., 42.])
MULT = np.array([1, 9, 25, 28, 27, 22, 13])
C = np.repeat(CASIMIR, MULT)
K = (C - 6) * (C - 30)
K2 = K * K
P = ((C == 6) | (C == 30)).astype(float)
EPS = 1 / 99144
OMEGA_C = 47 / 125
DIM_V = 125


class SpectralEngine:
    def __init__(self, seed=470125):
        r = np.random.default_rng(seed)
        self.psi = r.normal(size=DIM_V) + 1j * r.normal(size=DIM_V)
        self.psi /= np.linalg.norm(self.psi)
        self.n = 0

    def inject(self, vec):
        v = np.asarray(vec, dtype=complex)
        self.psi = v / (np.linalg.norm(v) or 1)

    def step(self):
        self.psi = (1 - EPS * K2) * self.psi
        self.psi /= np.linalg.norm(self.psi)
        self.n += 1
        return {
            "step": self.n,
            "capture": float(np.sum(P * np.abs(self.psi) ** 2)),
            "leak": float(np.linalg.norm(K2 * self.psi)),
            "omega_c": OMEGA_C,
        }


class MatrixEngine:
    """E0/E1 classical statevector. n ≤ 8. Not a QPU."""

    def __init__(self, n=3):
        self.reset(n)

    def reset(self, n=3):
        self.n = int(max(1, min(8, n)))
        self.psi = np.zeros(1 << self.n, dtype=complex)
        self.psi[0] = 1

    def h(self, q):
        s = 1 / np.sqrt(2)
        self._apply1(q, np.array([[s, s], [s, -s]], dtype=complex))

    def cnot(self, c, t):
        cb = 1 << (self.n - 1 - c)
        tb = 1 << (self.n - 1 - t)
        v = self.psi.copy()
        for i in range(v.size):
            if (i & cb) and not (i & tb):
                j = i | tb
                self.psi[i], self.psi[j] = v[j], v[i]

    def _apply1(self, q, U):
        step = 1 << (self.n - 1 - q)
        v = self.psi
        for base in range(0, v.size, 2 * step):
            for k in range(step):
                i, j = base + k, base + k + step
                a, b = v[i], v[j]
                v[i] = U[0, 0] * a + U[0, 1] * b
                v[j] = U[1, 0] * a + U[1, 1] * b

    def bell(self):
        self.reset(max(2, self.n))
        self.h(0)
        self.cnot(0, 1)

    def ghz(self):
        self.reset(self.n)
        self.h(0)
        for q in range(1, self.n):
            self.cnot(0, q)

    def lift125(self):
        """Sampled-amplitude feature map into the 125-carrier. Not an isomorphism."""
        n = self.psi.size
        idx = np.floor(np.arange(DIM_V) * (n - 1) / 124).astype(int) if n > 1 else np.zeros(DIM_V, dtype=int)
        vec = self.psi[idx]
        vec = vec / (np.linalg.norm(vec) or 1)
        return vec


@dataclass
class Pilot:
    throttle: float = 0
    yaw: float = 0
    pitch: float = 0
    roll: float = 0


class MantaEngine:
    def __init__(self):
        self.p = np.array([0., 42., 0.])
        self.v = np.zeros(3)
        self.yaw = self.pitch = self.roll = 0.

    def step(self, u, spec, dt=1 / 60):
        # Typed simulation bridge, not a physical propulsion law.
        coherence = .65 + .35 * np.clip(spec["capture"], 0, 1)
        self.yaw += u.yaw * 1.35 * dt
        self.pitch += u.pitch * 1.35 * dt
        self.roll += u.roll * 1.35 * dt
        sy, cy = np.sin(self.yaw), np.cos(self.yaw)
        sp, cp = np.sin(self.pitch), np.cos(self.pitch)
        # three.js basis: yaw=0 faces −Z; +yaw = nose left on chase cam.
        forward = np.array([-sy * cp, sp, -cy * cp])
        a = forward * (28 * np.clip(u.throttle, 0, 1) * coherence)
        hover = np.array([0., (42 - self.p[1]) * .045, 0.])
        self.v += (a + hover - .12 * self.v) * dt
        self.p += self.v * dt
        return {
            "position": self.p.copy(),
            "velocity": self.v.copy(),
            "speed": float(np.linalg.norm(self.v)),
            "coherence": float(coherence),
        }


class MantaE47:
    def __init__(self, seed=470125):
        self.spectral = SpectralEngine(seed)
        self.manta = MantaEngine()
        self.matrix = MatrixEngine(3)
        self.locked = False

    def tick(self, pilot, dt=1 / 60):
        s = self.spectral.step()
        return {"spectral": s, "manta": self.manta.step(pilot, s, dt), "locked": self.locked}

    def lock_matrix(self):
        self.spectral.inject(self.matrix.lift125())
        self.locked = True
        return "sampled-amplitude-feature-lift-125 · not a Hilbert isomorphism"


if __name__ == "__main__":
    e = MantaE47()
    u = Pilot(throttle=.72, yaw=.10, pitch=.02)
    for _ in range(600):
        out = e.tick(u)
    print("capture", out["spectral"]["capture"])
    print("leak", out["spectral"]["leak"])
    print("speed", out["manta"]["speed"])
    print("position", out["manta"]["position"])
    e.matrix.bell()
    print("lock", e.lock_matrix())
    print("capture_after_bell", e.spectral.step()["capture"])
