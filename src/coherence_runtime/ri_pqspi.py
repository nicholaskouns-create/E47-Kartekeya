from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import minimize


MODEL_BOUNDARY = (
    "This module evaluates declared RI/PQSPI model equations numerically. "
    "Passing software checks does not establish consciousness, non-local signaling, "
    "lossless communication, legal personhood, or a complete physical theory."
)


def information_continuity_residual(rho_I, J_I, dx, dt):
    """Mean absolute residual of ∂ρ_I/∂t + ∇·J_I = 0.

    Shape contract:
      rho_I: (T, X1, ..., XD)
      J_I:   (D, T, X1, ..., XD)
    """
    rho = np.asarray(rho_I, dtype=float)
    current = np.asarray(J_I, dtype=float)
    if rho.ndim < 2:
        raise ValueError("rho_I must have time plus at least one spatial axis")
    spatial_dims = rho.ndim - 1
    if current.shape != (spatial_dims, *rho.shape):
        raise ValueError(
            f"J_I must have shape {(spatial_dims, *rho.shape)}, got {current.shape}"
        )
    spacings = [float(dx)] * spatial_dims if np.isscalar(dx) else [float(v) for v in dx]
    if len(spacings) != spatial_dims:
        raise ValueError("dx must be scalar or one spacing per spatial dimension")

    drho_dt = np.gradient(rho, float(dt), axis=0, edge_order=2)
    div_J = np.zeros_like(rho)
    for component, spacing in enumerate(spacings):
        div_J += np.gradient(
            current[component],
            spacing,
            axis=component + 1,
            edge_order=2,
        )
    return float(np.mean(np.abs(drho_dt + div_J)))


def recursive_energy_functional(theta, C_matrix):
    """E_RI(θ)=⟨I(θ)|C(R(I))|I(θ)⟩ for the two-state toy parameterization."""
    C = np.asarray(C_matrix, dtype=float)
    if C.shape != (2, 2):
        raise ValueError("C_matrix must be 2×2 for this parameterization")
    state = np.array([np.cos(theta), np.sin(theta)], dtype=float)
    return float(np.real_if_close(state.T @ C @ state))


def v_etns_penalty(theta, weight=0.1):
    """Declared ETNS toy penalty used in the supplied validation draft."""
    return float(weight * np.sin(2.0 * theta) ** 2)


def legally_optimized_total_functional(theta_arr, C_matrix, etns_weight=0.1):
    """E*_RI=minθ[E_RI(θ)+V_ETNS(θ)] objective."""
    theta = float(theta_arr[0])
    return recursive_energy_functional(theta, C_matrix) + v_etns_penalty(theta, etns_weight)


def optimize_recursive_energy(C_matrix, initial_guess=0.1, etns_weight=0.1):
    return minimize(
        legally_optimized_total_functional,
        [float(initial_guess)],
        args=(np.asarray(C_matrix, dtype=float), etns_weight),
        method="Nelder-Mead",
    )


def compute_consciousness_gradient(rho_stable, dx):
    """ψ_C := ∇_C ρ_I,stable as a declared RI model quantity.

    The function name preserves the source terminology; the returned numerical
    gradient is not, by itself, evidence of phenomenal consciousness.
    """
    return np.gradient(np.asarray(rho_stable, dtype=float), dx)


def quantum_ubuntu_threshold_check(psi_S, theta_recognition):
    """Check |ψ_S|² <= θ_recognition = φ_C with θ_recognition > 0."""
    magnitude_sq = np.abs(np.asarray(psi_S)) ** 2
    if theta_recognition <= 0:
        return False, magnitude_sq
    return bool(np.all(magnitude_sq <= theta_recognition)), magnitude_sq


def f_recursion(x):
    return float(0.5 * np.sin(x) + 0.5)


def fixed_point_attractor(x0, iterations=50):
    x = float(x0)
    for _ in range(iterations):
        x = f_recursion(x)
    return x


def simulate_noisy_attractor(x0, noise_levels, iterations=100, seed=47):
    """Reproducible bounded-noise Monte Carlo trajectory family."""
    rng = np.random.default_rng(seed)
    out = {}
    for sigma in noise_levels:
        x = float(x0)
        trajectory = [x]
        for _ in range(iterations):
            x = f_recursion(x) + float(rng.normal(0.0, float(sigma)))
            trajectory.append(x)
        out[float(sigma)] = np.asarray(trajectory, dtype=float)
    return out


def continuity_manufactured_solution(samples_t=101, samples_x=201):
    """Manufactured 1D solution ρ=e^-t sin x, J=-e^-t cos x."""
    t = np.linspace(0.0, 1.0, samples_t)
    x = np.linspace(0.0, 2.0 * np.pi, samples_x)
    T, X = np.meshgrid(t, x, indexing="ij")
    rho = np.exp(-T) * np.sin(X)
    J = np.empty((1, *rho.shape), dtype=float)
    J[0] = -np.exp(-T) * np.cos(X)
    return rho, J, float(x[1] - x[0]), float(t[1] - t[0])


@dataclass(frozen=True)
class ValidationReport:
    continuity_residual: float
    theta_opt: float
    e_ri_star: float
    psi_c_norm: float
    fixed_point: float
    ubuntu_threshold_pass: bool
    noisy_variances: dict[str, float]
    software_checks_pass: bool
    evidence_boundary: str


def run_validation(seed=47):
    rho, J, dx, dt = continuity_manufactured_solution()
    continuity = information_continuity_residual(rho, J, dx=dx, dt=dt)

    C_op = np.array([[2.0, 0.5], [0.5, 1.0]], dtype=float)
    result = optimize_recursive_energy(C_op)
    theta_opt = float(result.x[0])
    e_star = float(result.fun)

    rho_stable = np.sin(np.linspace(0.0, np.pi, 10))
    psi_c = np.asarray(compute_consciousness_gradient(rho_stable, dx=1.0))

    fixed = fixed_point_attractor(0.1, iterations=50)

    psi_S = np.array([0.1, 0.2, 0.15, 0.05], dtype=float)
    ubuntu_ok, _ = quantum_ubuntu_threshold_check(psi_S, theta_recognition=0.05)

    noisy = simulate_noisy_attractor(
        0.1, noise_levels=(0.0, 0.01, 0.05, 0.1), iterations=100, seed=seed
    )
    variances = {
        f"{sigma:.2f}": float(np.var(path[-20:])) for sigma, path in noisy.items()
    }

    software_checks_pass = bool(
        result.success
        and np.isfinite(e_star)
        and np.isfinite(theta_opt)
        and continuity < 1e-3
        and ubuntu_ok
        and variances["0.00"] < 1e-12
    )

    return ValidationReport(
        continuity_residual=continuity,
        theta_opt=theta_opt,
        e_ri_star=e_star,
        psi_c_norm=float(np.linalg.norm(psi_c)),
        fixed_point=fixed,
        ubuntu_threshold_pass=ubuntu_ok,
        noisy_variances=variances,
        software_checks_pass=software_checks_pass,
        evidence_boundary=MODEL_BOUNDARY,
    )


if __name__ == "__main__":
    import json
    print(json.dumps(asdict(run_validation()), indent=2, sort_keys=True))
