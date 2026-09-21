#!/usr/bin/env python3
"""KKP-R spectral engine. H=V2⊗3 dim 125, K=(C-6I)(C-30I), dim E47=47, Ω_c=47/125."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple

import numpy as np

J_PRIMITIVE: int = 2
D_PRIMITIVE: int = 2 * J_PRIMITIVE + 1
DIM_H: int = D_PRIMITIVE ** 3
SPINS = np.array([0, 1, 2, 3, 4, 5, 6], dtype=int)
MULTIPLICITIES = np.array([1, 3, 5, 4, 3, 2, 1], dtype=int)
SECTOR_DIMS_LOCKED = np.array([1, 9, 25, 28, 27, 22, 13], dtype=int)
CASIMIR_LOCKED = np.array([0, 2, 6, 12, 20, 30, 42], dtype=int)
MU_LOCKED = np.array([180, 112, 0, -108, -140, 0, 432], dtype=int)
MU2_LOCKED = np.array([32400, 12544, 0, 11664, 19600, 0, 186624], dtype=int)
DIM_KERNEL_LOCKED: int = 47
DIM_COMPLEMENT_LOCKED: int = 78
OMEGA_C_LOCKED: float = 47 / 125
R_MARGIN_LOCKED: float = 78 / 47
SPECTRAL_GAP_LOCKED: int = 11664
LAMBDA_MAX_LOCKED: int = 186624
KAPPA_LOCKED: int = 16
RHO_LOCKED: float = 15 / 17
P47_NORMALIZER: float = 1_814_400.0
P47_ON_SPEC_LOCKED = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0])


def P_47(C):
    C = np.asarray(C, dtype=float)
    return (C - 31.0) * C * (C - 2.0) * (C - 12.0) * (C - 20.0) * (C - 42.0) / P47_NORMALIZER


@dataclass(frozen=True)
class SpectralEngine:
    spins: np.ndarray = field(default_factory=lambda: SPINS.copy())
    multiplicities: np.ndarray = field(default_factory=lambda: MULTIPLICITIES.copy())

    def __post_init__(self) -> None:
        object.__setattr__(self, "spins", np.asarray(self.spins, dtype=int))
        object.__setattr__(self, "multiplicities", np.asarray(self.multiplicities, dtype=int))
        self.validate()

    @property
    def subspace_dims(self) -> np.ndarray:
        return 2 * self.spins + 1

    @property
    def sector_dims(self) -> np.ndarray:
        return self.multiplicities * self.subspace_dims

    @property
    def dim_H(self) -> int:
        return int(np.sum(self.sector_dims))

    @property
    def casimir(self) -> np.ndarray:
        return self.spins * (self.spins + 1)

    @property
    def mu(self) -> np.ndarray:
        lam = self.casimir
        return (lam - 6) * (lam - 30)

    @property
    def mu2(self) -> np.ndarray:
        return self.mu ** 2

    @property
    def kernel_mask(self) -> np.ndarray:
        return self.mu == 0

    @property
    def dim_kernel(self) -> int:
        return int(np.sum(self.sector_dims[self.kernel_mask]))

    @property
    def dim_complement(self) -> int:
        return int(np.sum(self.sector_dims[~self.kernel_mask]))

    @property
    def omega_c(self) -> float:
        return self.dim_kernel / self.dim_H

    @property
    def r_margin(self) -> float:
        return self.dim_complement / self.dim_kernel

    @property
    def spectral_gap(self) -> int:
        return int(np.min(self.mu2[~self.kernel_mask]))

    @property
    def lambda_max(self) -> int:
        return int(np.max(self.mu2))

    @property
    def kappa(self) -> float:
        return self.lambda_max / self.spectral_gap

    @property
    def rho(self) -> float:
        return (self.kappa - 1.0) / (self.kappa + 1.0)

    @property
    def P_on_spectrum(self) -> np.ndarray:
        return P_47(self.casimir.astype(float))

    @property
    def trace_P47(self) -> float:
        return float(np.sum(self.sector_dims * self.P_on_spectrum))

    def discrete_contraction(self, steps: int = 30) -> Tuple[np.ndarray, np.ndarray]:
        k = np.arange(0, steps + 1)
        return k, (self.rho ** k)

    def half_life_steps(self) -> float:
        return float(np.log(0.5) / np.log(self.rho))

    def table(self) -> Dict[str, np.ndarray]:
        return {
            "J": self.spins,
            "m_J": self.multiplicities,
            "d_J": self.subspace_dims,
            "dim": self.sector_dims,
            "lambda": self.casimir,
            "mu": self.mu,
            "mu2": self.mu2,
            "P47": self.P_on_spectrum,
            "kernel": self.kernel_mask.astype(int),
        }

    def report(self) -> str:
        rows = [
            " J   m_J  d_J  dim   λ=J(J+1)    μ=(λ-6)(λ-30)      μ²         P47   sector",
            "-" * 82,
        ]
        for J, m, d, dim, lam, muj, mu2j, p, ker in zip(
            self.spins, self.multiplicities, self.subspace_dims, self.sector_dims,
            self.casimir, self.mu, self.mu2, self.P_on_spectrum, self.kernel_mask,
        ):
            tag = "KER E47" if ker else "perp"
            rows.append(
                f" {int(J)}    {int(m)}    {int(d):2d}   {int(dim):3d}    "
                f"{int(lam):4d}     {int(muj):6d}         {int(mu2j):7d}    "
                f"{p:3.0f}   {tag}"
            )
        rows += [
            "-" * 82,
            f"dim H        = {self.dim_H}",
            f"dim E47      = {self.dim_kernel}   = dim E6 + dim E30 = 25 + 22",
            f"rank K       = {self.dim_complement}",
            f"Ω_c          = {self.dim_kernel}/{self.dim_H} = {self.omega_c}",
            f"r            = {self.dim_complement}/{self.dim_kernel} = {self.r_margin}",
            f"Δ            = {self.spectral_gap}   (J=3)",
            f"Λ_max        = {self.lambda_max}  (J=6)",
            f"κ            = Λ_max/Δ = {self.kappa:g}",
            f"ρ            = (κ-1)/(κ+1) = {self.rho} = 15/17",
            f"Tr P_47      = {self.trace_P47}",
            f"k_1/2        = {self.half_life_steps():.6f}",
        ]
        return "\n".join(rows)

    def validate(self) -> None:
        assert D_PRIMITIVE == 5
        assert DIM_H == 125
        assert self.dim_H == 125
        assert np.array_equal(self.sector_dims, SECTOR_DIMS_LOCKED)
        assert np.array_equal(self.casimir, CASIMIR_LOCKED)
        assert np.array_equal(self.mu, MU_LOCKED)
        assert np.array_equal(self.mu2, MU2_LOCKED)
        assert self.dim_kernel == DIM_KERNEL_LOCKED
        assert self.dim_complement == DIM_COMPLEMENT_LOCKED
        assert self.omega_c == OMEGA_C_LOCKED
        assert self.r_margin == R_MARGIN_LOCKED
        assert np.isclose(1.0 / (1.0 + self.r_margin), self.omega_c)
        assert self.spectral_gap == SPECTRAL_GAP_LOCKED
        assert self.lambda_max == LAMBDA_MAX_LOCKED
        assert self.kappa == KAPPA_LOCKED
        assert self.rho == RHO_LOCKED
        assert np.allclose(self.P_on_spectrum, P47_ON_SPEC_LOCKED)
        assert np.isclose(self.trace_P47, 47.0)


def run_engine() -> SpectralEngine:
    eng = SpectralEngine()
    print("[ok] SPECTRAL ENGINE LOCKED")
    print(eng.report())
    return eng


if __name__ == "__main__":
    run_engine()
