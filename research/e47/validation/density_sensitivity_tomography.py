#!/usr/bin/env python3
"""DENSITY inverse reconstruction over a 5×5×5 observation carrier.

Input observations use three integer coordinates in [0,4] plus either:
  target ∈ [0,1], or outcome ∈ {full, epistemic, abstracted, restricted}.

The script reconstructs a 125-state latent field with ART, then independently
projects the field through the canonical rank-47 E47 projector. The P47 gate is
accepted only if its held-out RMSE does not worsen beyond a declared tolerance.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse, json, math
from pathlib import Path
from typing import Iterable

import numpy as np

DIM = 5
N = DIM ** 3
OUTCOME_SCORE = {"full": 0.0, "epistemic": 0.15, "abstracted": 0.55, "restricted": 1.0}


@dataclass(frozen=True)
class Observation:
    id: str
    domain: int
    implementation: int
    operationality: int
    outcome: str | None = None
    target: float | None = None
    epoch: str = ""
    weight: float = 1.0
    source: str = ""
    note: str = ""
    training_excluded: bool = False

    @property
    def y(self) -> float:
        if self.target is not None:
            return float(np.clip(self.target, 0.0, 1.0))
        if self.outcome not in OUTCOME_SCORE:
            raise ValueError(f"{self.id}: target or supported outcome required")
        return OUTCOME_SCORE[self.outcome]


def spin2_generators():
    j = 2
    m = np.arange(j, -j - 1, -1, dtype=float)
    jz = np.diag(m).astype(complex)
    jp = np.zeros((5, 5), dtype=complex)
    for i in range(4):
        mm = m[i + 1]
        jp[i, i + 1] = np.sqrt(j * (j + 1) - mm * (mm + 1))
    jm = jp.conj().T
    return (jp + jm) / 2, (jp - jm) / (2j), jz


def canonical_p47() -> np.ndarray:
    jx, jy, jz = spin2_generators()
    ident = np.eye(5, dtype=complex)

    def total(j):
        return (
            np.kron(np.kron(j, ident), ident)
            + np.kron(np.kron(ident, j), ident)
            + np.kron(np.kron(ident, ident), j)
        )

    c = sum(t @ t for t in map(total, (jx, jy, jz)))
    eigvals, eigvecs = np.linalg.eigh(c)
    mask = np.isclose(eigvals, 6.0, atol=1e-8) | np.isclose(eigvals, 30.0, atol=1e-8)
    p = eigvecs[:, mask] @ eigvecs[:, mask].conj().T
    p = np.real_if_close(p, tol=1000).real
    assert p.shape == (125, 125)
    assert np.linalg.norm(p @ p - p) < 1e-10
    assert round(np.trace(p)) == 47
    return p


def index(d: int, i: int, o: int) -> int:
    return d * 25 + i * 5 + o


def design_row(obs: Observation, sigma: float = 0.72) -> np.ndarray:
    row = np.zeros(N, dtype=float)
    for d in range(DIM):
        for i in range(DIM):
            for o in range(DIM):
                r2 = (
                    (d - obs.domain) ** 2
                    + (i - obs.implementation) ** 2
                    + (o - obs.operationality) ** 2
                )
                row[index(d, i, o)] = math.exp(-r2 / (2 * sigma * sigma))
    row *= max(obs.weight, 1e-9)
    return row / row.sum()


def art(a: np.ndarray, y: np.ndarray, iterations: int = 140, relax: float = 0.42) -> np.ndarray:
    x = np.zeros(a.shape[1], dtype=float)
    for _ in range(iterations):
        for row, target in zip(a, y):
            x += relax * (target - float(row @ x)) * row / (float(row @ row) + 1e-12)
        x = np.clip(x, 0.0, 1.0)
    return x


def split_indices(n: int, holdout: float = 0.2, seed: int = 47):
    rng = np.random.default_rng(seed)
    order = rng.permutation(n)
    n_hold = max(1, int(round(n * holdout))) if n >= 4 else 1
    test = np.sort(order[:n_hold])
    train = np.sort(order[n_hold:])
    return train, test


def rmse(y, pred) -> float:
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(pred)) ** 2)))


def top_cells(x: np.ndarray, n: int = 12):
    rows = []
    for k in np.argsort(x)[::-1][:n]:
        d, rem = divmod(int(k), 25)
        i, o = divmod(rem, 5)
        rows.append({"domain": d, "implementation": i, "operationality": o, "score": float(x[k])})
    return rows


def reconstruct(observations: Iterable[Observation], holdout: float = 0.2, seed: int = 47):
    obs = [o for o in observations if not o.training_excluded]
    if len(obs) < 2:
        raise ValueError("at least two non-excluded observations are required")
    for o in obs:
        if not all(0 <= q <= 4 for q in (o.domain, o.implementation, o.operationality)):
            raise ValueError(f"{o.id}: coordinates must be integer bins 0..4")

    a = np.vstack([design_row(o) for o in obs])
    y = np.array([o.y for o in obs], dtype=float)
    train, test = split_indices(len(obs), holdout=holdout, seed=seed)

    raw = art(a[train], y[train])
    p47 = canonical_p47()
    gated = p47 @ raw

    g_train = a[train] @ gated
    alpha = float((g_train @ y[train]) / (g_train @ g_train + 1e-12))
    gated = np.clip(alpha * gated, 0.0, 1.0)

    pred_raw = a @ raw
    pred_gated = a @ gated
    raw_holdout = rmse(y[test], pred_raw[test])
    gated_holdout = rmse(y[test], pred_gated[test])

    return {
        "schema": "DENSITY-RECONSTRUCT/1.0",
        "carrier": 125,
        "gate": {"name": "P47", "rank": int(round(np.trace(p47)))},
        "n_observations": len(obs),
        "train_ids": [obs[i].id for i in train],
        "holdout_ids": [obs[i].id for i in test],
        "holdout_rmse_raw": raw_holdout,
        "holdout_rmse_p47": gated_holdout,
        "p47_gate_useful": bool(gated_holdout <= raw_holdout + 0.02),
        "observations": [
            asdict(o)
            | {"score": o.y, "pred_raw": float(pred_raw[k]), "pred_p47": float(pred_gated[k]), "held_out": bool(k in test)}
            for k, o in enumerate(obs)
        ],
        "raw_field": raw.tolist(),
        "p47_field": gated.tolist(),
        "raw_top_cells": top_cells(raw),
        "p47_top_cells": top_cells(gated),
    }



def robust_validate(observations: Iterable[Observation], holdout: float = 0.2, repeats: int = 100):
    obs = [o for o in observations if not o.training_excluded]
    a = np.vstack([design_row(o) for o in obs])
    y = np.array([o.y for o in obs], dtype=float)
    p47 = canonical_p47()

    def evaluate(train, test):
        raw = art(a[train], y[train])
        gated = p47 @ raw
        g_train = a[train] @ gated
        alpha = float((g_train @ y[train]) / (g_train @ g_train + 1e-12))
        gated = np.clip(alpha * gated, 0.0, 1.0)
        return rmse(y[test], (a @ raw)[test]), rmse(y[test], (a @ gated)[test])

    loo_raw, loo_p47 = [], []
    for k in range(len(obs)):
        train = np.array([i for i in range(len(obs)) if i != k], dtype=int)
        rr, rg = evaluate(train, np.array([k], dtype=int))
        loo_raw.append(rr)
        loo_p47.append(rg)

    repeated = []
    for seed in range(repeats):
        train, test = split_indices(len(obs), holdout=holdout, seed=seed)
        rr, rg = evaluate(train, test)
        repeated.append((rr, rg))

    repeated = np.asarray(repeated, dtype=float)
    collisions = []
    by_coord = {}
    for o in obs:
        by_coord.setdefault((o.domain, o.implementation, o.operationality), []).append((o.epoch, o.y, o.id))
    for coord, rows in by_coord.items():
        if len({round(v, 12) for _, v, _ in rows}) > 1:
            collisions.append({
                "coordinate": list(coord),
                "observations": [{"epoch": e, "target": v, "id": oid} for e, v, oid in rows],
            })

    loo_raw_rmse = float(np.sqrt(np.mean(np.square(loo_raw))))
    loo_p47_rmse = float(np.sqrt(np.mean(np.square(loo_p47)))
    )
    return {
        "loocv_raw_rmse": loo_raw_rmse,
        "loocv_p47_rmse": loo_p47_rmse,
        "repeated_holdout_splits": repeats,
        "repeated_raw_mean_rmse": float(repeated[:, 0].mean()),
        "repeated_p47_mean_rmse": float(repeated[:, 1].mean()),
        "repeated_raw_median_rmse": float(np.median(repeated[:, 0])),
        "repeated_p47_median_rmse": float(np.median(repeated[:, 1])),
        "p47_wins": int(np.sum(repeated[:, 1] < repeated[:, 0])),
        "p47_within_0_02": int(np.sum(repeated[:, 1] <= repeated[:, 0] + 0.02)),
        "p47_robustly_useful": bool(
            loo_p47_rmse <= loo_raw_rmse + 0.02
            and repeated[:, 1].mean() <= repeated[:, 0].mean() + 0.02
        ),
        "temporal_coordinate_collisions": collisions,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="JSON array of observation objects")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--holdout", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=47)
    args = ap.parse_args()

    rows = json.loads(args.input.read_text())
    observations = [Observation(**row) for row in rows]
    result = reconstruct(observations, holdout=args.holdout, seed=args.seed)
    result["robust_validation"] = robust_validate(observations, holdout=args.holdout, repeats=100)
    text = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
