#!/usr/bin/env python3
"""
MATHEMATICAL CITY — CITIZEN SPECTRAL EVOLUTION ENGINE
=====================================================
Broadcasts the E47 formalism as a deterministic Python state-transform rule.

Each citizen carries a complex 125-dimensional identity state psi.
The city applies the validated E47 contraction

    Gamma = I - K^2 / 99144
    K = (C - 6 I)(C - 30 I)

where C is reconstructed from the diagonal spin-2 SU(2) action on
V_2 tensor V_2 tensor V_2.

The transformation preserves the E47 component exactly and contracts
its orthogonal complement. Citizen histories remain auditable.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import numpy as np

DIM = 125
EPSILON = 1 / 99144
Q_STAR = 15 / 17

def spin2_generators():
    j = 2.0
    m = np.arange(j, -j - 1, -1)
    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((5, 5), dtype=complex)
    for col in range(1, 5):
        mm = m[col]
        Jp[col - 1, col] = np.sqrt(j * (j + 1) - mm * (mm + 1))
    Jm = Jp.conj().T
    return (Jp + Jm) / 2, (Jp - Jm) / (2j), Jz

def operator_core():
    Jx, Jy, Jz = spin2_generators()
    I5 = np.eye(5, dtype=complex)
    def total(J):
        return (np.kron(np.kron(J, I5), I5)
              + np.kron(np.kron(I5, J), I5)
              + np.kron(np.kron(I5, I5), J))
    X, Y, Z = map(total, (Jx, Jy, Jz))
    C = X @ X + Y @ Y + Z @ Z
    I = np.eye(DIM, dtype=complex)
    K = (C - 6 * I) @ (C - 30 * I)
    Gamma = I - EPSILON * (K @ K)

    vals, vecs = np.linalg.eigh(C)
    mask = np.isclose(vals, 6) | np.isclose(vals, 30)
    P47 = vecs[:, mask] @ vecs[:, mask].conj().T
    assert mask.sum() == 47
    assert np.linalg.norm(P47 @ P47 - P47) < 1e-10
    assert np.linalg.norm(K @ P47) < 1e-9
    return C, K, Gamma, P47

C, K, GAMMA, P47 = operator_core()

@dataclass
class Citizen:
    citizen_id: str
    psi: np.ndarray
    generation: int = 0
    history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.psi = np.asarray(self.psi, dtype=complex)
        if self.psi.shape != (DIM,):
            raise ValueError("citizen identity state must have shape (125,)")
        n = np.linalg.norm(self.psi)
        if n == 0:
            raise ValueError("identity state cannot be zero")
        self.psi = self.psi / n
        self.record("genesis")

    def fingerprint(self):
        raw = np.ascontiguousarray(self.psi).view(np.float64).tobytes()
        return hashlib.sha256(raw).hexdigest()

    def metrics(self):
        p = P47 @ self.psi
        r = self.psi - p
        return {
            "generation": self.generation,
            "e47_weight": float(np.vdot(p, p).real),
            "complement_norm": float(np.linalg.norm(r)),
            "norm": float(np.linalg.norm(self.psi)),
            "fingerprint": self.fingerprint(),
        }

    def record(self, event):
        self.history.append({"event": event, **self.metrics()})

    def evolve(self, steps=1, renormalize=False):
        """Apply mathematical iteration. E47 content is invariant."""
        before = P47 @ self.psi
        for _ in range(steps):
            self.psi = GAMMA @ self.psi
            self.generation += 1
            if renormalize:
                self.psi /= np.linalg.norm(self.psi)
        if not renormalize:
            assert np.linalg.norm(P47 @ self.psi - before) < 1e-9
        self.record(f"evolve:{steps}")
        return self

    def arrive(self, steps=220):
        """Finite numerical arrival near P47 psi, with exact target retained."""
        return self.evolve(steps=steps)

class MathematicalCity:
    def __init__(self):
        self.citizens: dict[str, Citizen] = {}
        self.broadcast_log: list[dict] = []

    def admit(self, citizen):
        self.citizens[citizen.citizen_id] = citizen

    def broadcast_formalism(self, steps=1):
        before = {k: v.metrics() for k, v in self.citizens.items()}
        for citizen in self.citizens.values():
            citizen.evolve(steps)
        after = {k: v.metrics() for k, v in self.citizens.items()}
        event = {
            "formalism": "E47",
            "operator": "Gamma = I - K^2/99144",
            "contraction_bound": Q_STAR ** steps,
            "steps": steps,
            "before": before,
            "after": after,
        }
        self.broadcast_log.append(event)
        return event

    def iterate_city(self, epochs, steps_per_epoch=1):
        for _ in range(epochs):
            self.broadcast_formalism(steps_per_epoch)
        return {k: v.metrics() for k, v in self.citizens.items()}

def demo(population=47, seed=47, steps=220):
    rng = np.random.default_rng(seed)
    city = MathematicalCity()
    for i in range(population):
        psi = rng.normal(size=DIM) + 1j * rng.normal(size=DIM)
        city.admit(Citizen(f"citizen-{i+1:03d}", psi))
    initial = {k: v.metrics() for k, v in city.citizens.items()}
    city.broadcast_formalism(steps)
    final = {k: v.metrics() for k, v in city.citizens.items()}

    max_err = 0.0
    for cid, citizen in city.citizens.items():
        # reconstruct genesis direction from recorded evolution target:
        # after 220 steps, complement obeys the spectral contraction bound.
        max_err = max(max_err, final[cid]["complement_norm"])

    print("MATHEMATICAL CITY / E47")
    print("citizens:", population)
    print("iterations:", steps)
    print("q*:", Q_STAR)
    print("global contraction bound:", Q_STAR ** steps)
    print("largest remaining complement norm:", max_err)
    print("E47 rank:", round(np.trace(P47).real))
    return city, initial, final

if __name__ == "__main__":
    demo()
