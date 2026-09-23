from __future__ import annotations

import numpy as np

# -----------------------------------------------------------------------------
# Locked E47 constants
# -----------------------------------------------------------------------------
DIM = 125
ROOTS = (6.0, 30.0)
EPSILON = 1.0 / 99144.0
EXPECTED_CASIMIR = {
    0.0: 1,
    2.0: 9,
    6.0: 25,
    12.0: 28,
    20.0: 27,
    30.0: 22,
    42.0: 13,
}
EXPECTED_K2_POSITIVE = (11664.0, 12544.0, 19600.0, 32400.0, 186624.0)
EXPECTED_KERNEL_DIM = 47
EXPECTED_GAP = 11664.0
EXPECTED_NORM_K2 = 186624.0
EXPECTED_RHO = 15.0 / 17.0


def _kron3(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> np.ndarray:
    return np.kron(np.kron(a, b), c)


def spin_j_generators(j: int = 2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return Hermitian Jx, Jy, Jz in the |j,m> basis, m=j,...,-j."""
    if j < 0 or int(j) != j:
        raise ValueError("j must be a non-negative integer for this runtime")

    j = int(j)
    mvals = np.arange(j, -j - 1, -1, dtype=float)
    d = len(mvals)
    index = {float(m): i for i, m in enumerate(mvals)}

    Jp = np.zeros((d, d), dtype=complex)
    for m in mvals:
        if m < j:
            src = index[float(m)]
            dst = index[float(m + 1)]
            Jp[dst, src] = np.sqrt(j * (j + 1) - m * (m + 1))

    Jm = Jp.conj().T
    Jx = 0.5 * (Jp + Jm)
    Jy = (Jp - Jm) / (2.0j)
    Jz = np.diag(mvals).astype(complex)
    return Jx, Jy, Jz


def locked_e47_casimir() -> np.ndarray:
    """Construct C=J_tot^2 on V_2 tensor V_2 tensor V_2, dimension 125."""
    Jx, Jy, Jz = spin_j_generators(2)
    I5 = np.eye(5, dtype=complex)

    def total(A: np.ndarray) -> np.ndarray:
        return (
            _kron3(A, I5, I5)
            + _kron3(I5, A, I5)
            + _kron3(I5, I5, A)
        )

    Jxt, Jyt, Jzt = total(Jx), total(Jy), total(Jz)
    C = Jxt @ Jxt + Jyt @ Jyt + Jzt @ Jzt
    return 0.5 * (C + C.conj().T)


def e47_operators(C: np.ndarray, atol: float = 1e-10) -> dict:
    """Construct I, K, K^2, Gamma, and the orthogonal E47 projector Lambda."""
    C = np.asarray(C, dtype=complex)
    if C.shape != (DIM, DIM):
        raise ValueError(f"Locked E47 expects C.shape == {(DIM, DIM)}, got {C.shape}")
    if not np.allclose(C, C.conj().T, atol=atol, rtol=0):
        raise ValueError("C must be Hermitian")

    I = np.eye(DIM, dtype=complex)
    K = (C - ROOTS[0] * I) @ (C - ROOTS[1] * I)
    K2 = K @ K
    Gamma = I - EPSILON * K2

    eigenvalues, V = np.linalg.eigh(C)
    selected = np.logical_or(
        np.isclose(eigenvalues, ROOTS[0], atol=atol, rtol=0),
        np.isclose(eigenvalues, ROOTS[1], atol=atol, rtol=0),
    )
    V_kernel = V[:, selected]
    Lambda = V_kernel @ V_kernel.conj().T

    return {
        "I": I,
        "K": K,
        "K2": K2,
        "Γ": Gamma,
        "Gamma": Gamma,
        "Λ": Lambda,
        "Lambda": Lambda,
        "eigenvalues": eigenvalues,
        "kernel_basis": V_kernel,
    }


def _aggregate(inputs, alpha=None) -> np.ndarray:
    X = np.asarray(inputs, dtype=complex)
    if X.ndim == 1:
        Sigma = X.copy()
    elif X.ndim == 2:
        Sigma = X.sum(axis=0)
    else:
        raise ValueError("inputs must be one vector or a stack of vectors")

    if Sigma.shape != (DIM,):
        raise ValueError(f"aggregated state must have shape {(DIM,)}, got {Sigma.shape}")

    if alpha is not None:
        a = np.asarray(alpha, dtype=complex)
        if a.shape != (DIM,):
            raise ValueError(f"alpha must have shape {(DIM,)}, got {a.shape}")
        Sigma = Sigma + a

    return Sigma


def recursive_step(
    C: np.ndarray,
    inputs,
    Psi,
    *,
    alpha=None,
    tolerance: float = 1e-10,
    max_contractions: int = 512,
    atol: float = 1e-10,
) -> dict:
    """
    One complete Sigma -> Psi -> Gamma^n -> Omega -> Lambda -> Sigma' cycle.

    Omega is evaluated BEFORE the exact projector is applied.  This keeps the
    certainty gate informative: applying Lambda first would force K Lambda ~= 0
    numerically and make the gate tautological.
    """
    ops = e47_operators(C, atol=atol)
    K = ops["K"]
    Gamma = ops["Γ"]
    Lambda = ops["Λ"]

    # Sigma: aggregation (+ optional alpha re-initialization baseline)
    Sigma = _aggregate(inputs, alpha=alpha)

    # Psi: state evolution
    evolved = np.asarray(Psi(Sigma), dtype=complex)
    if evolved.shape != (DIM,):
        raise ValueError(f"Psi(Sigma) must have shape {(DIM,)}, got {evolved.shape}")

    # Gamma: contract transient modes until the residual-based certainty bound holds.
    state = evolved.copy()
    residual_history = []
    Omega = False

    for n in range(max_contractions + 1):
        residual = float(np.linalg.norm(K @ state))
        residual_history.append(residual)
        if residual <= tolerance:
            Omega = True
            break
        if n < max_contractions:
            state = Gamma @ state

    pre_projection = state.copy()

    # Lambda: deterministic collapse only after the certainty gate is satisfied.
    # If the gate is not satisfied within max_contractions, preserve the last
    # contracted state instead of silently declaring collapse.
    M = Lambda @ state if Omega else state
    Sigma_next = M.copy()

    return {
        "Σ": Sigma,
        "Sigma": Sigma,
        "K": K,
        "Ψ": Psi,
        "Psi": Psi,
        "Γ": Gamma,
        "Gamma": Gamma,
        "Λ": Lambda,
        "Lambda": Lambda,
        "Ω": Omega,
        "Omega": Omega,
        "I": ops["I"],
        "M": M,
        "Σ′": Sigma_next,
        "Σ_next": Sigma_next,
        "pre_projection": pre_projection,
        "residual": residual_history[-1],
        "residual_history": np.asarray(residual_history),
        "contractions": len(residual_history) - 1,
    }


def recursive_run(
    C: np.ndarray,
    inputs,
    Psi,
    *,
    cycles: int = 1,
    alpha=None,
    reinitialize=None,
    tolerance: float = 1e-10,
    max_contractions: int = 512,
    atol: float = 1e-10,
) -> dict:
    """
    Repeat complete recursive cycles.

    After each successful cycle, Sigma' becomes the next cycle's sole input.
    Optional reinitialize(cycle_index, Sigma_next) may return a new alpha vector.
    """
    if cycles < 1:
        raise ValueError("cycles must be >= 1")

    current_inputs = inputs
    current_alpha = alpha
    history = []

    for cycle in range(cycles):
        step = recursive_step(
            C,
            current_inputs,
            Psi,
            alpha=current_alpha,
            tolerance=tolerance,
            max_contractions=max_contractions,
            atol=atol,
        )
        history.append(step)

        if not step["Ω"]:
            break

        current_inputs = np.asarray([step["Σ_next"]])
        if reinitialize is not None:
            current_alpha = reinitialize(cycle, step["Σ_next"])

    final = history[-1]
    return {
        "cycles_requested": cycles,
        "cycles_completed": len(history),
        "converged": bool(final["Ω"]),
        "history": history,
        "Σ′": final["Σ′"],
        "Σ_next": final["Σ_next"],
        "M": final["M"],
    }


def certify_locked_e47(C: np.ndarray, atol: float = 1e-9) -> dict:
    """Executable certificate for the locked E47 algebra and contraction."""
    ops = e47_operators(C, atol=min(atol, 1e-10))
    I, K, K2, Gamma, Lambda = (
        ops["I"], ops["K"], ops["K2"], ops["Γ"], ops["Λ"]
    )

    c_eigs = np.linalg.eigvalsh(C)
    rounded_c = np.rint(c_eigs).astype(int)
    unique_c, counts_c = np.unique(rounded_c, return_counts=True)
    spectrum = {float(v): int(n) for v, n in zip(unique_c, counts_c)}

    k2_eigs = np.linalg.eigvalsh(K2)
    positive = k2_eigs[k2_eigs > atol]
    positive_unique = tuple(float(x) for x in np.unique(np.rint(positive).astype(int)))
    gap = float(np.min(positive))
    norm_k2 = float(np.max(positive))
    rho = float(np.max(np.abs(1.0 - EPSILON * positive)))

    rank_lambda = int(np.count_nonzero(np.linalg.eigvalsh(Lambda) > 0.5))
    projector_error = float(np.linalg.norm(Lambda @ Lambda - Lambda))
    kernel_error = float(np.linalg.norm(K @ Lambda))
    gamma_fixed_error = float(np.linalg.norm(Gamma @ Lambda - Lambda))
    commutator_error = float(np.linalg.norm(C @ Lambda - Lambda @ C))

    tests = {
        "C_Hermitian": np.allclose(C, C.conj().T, atol=atol, rtol=0),
        "Casimir_spectrum": spectrum == EXPECTED_CASIMIR,
        "kernel_rank_47": rank_lambda == EXPECTED_KERNEL_DIM,
        "projector_idempotent": projector_error <= atol,
        "K_Lambda_zero": kernel_error <= 1e-8,
        "Gamma_fixes_kernel": gamma_fixed_error <= 1e-8,
        "C_commutes_Lambda": commutator_error <= 1e-8,
        "K2_positive_spectrum": positive_unique == EXPECTED_K2_POSITIVE,
        "gap_11664": np.isclose(gap, EXPECTED_GAP, atol=1e-6, rtol=0),
        "norm_186624": np.isclose(norm_k2, EXPECTED_NORM_K2, atol=1e-6, rtol=0),
        "epsilon_1_over_99144": np.isclose(EPSILON, 1 / 99144, atol=0, rtol=0),
        "rho_15_over_17": np.isclose(rho, EXPECTED_RHO, atol=1e-12, rtol=0),
        "Omega_c_47_over_125": np.isclose(rank_lambda / DIM, 47 / 125, atol=0, rtol=0),
    }

    return {
        "PASS": bool(all(tests.values())),
        "tests": tests,
        "spectrum_C": spectrum,
        "positive_spectrum_K2": positive_unique,
        "rank_Lambda": rank_lambda,
        "Omega_c": rank_lambda / DIM,
        "epsilon": EPSILON,
        "gap_K2": gap,
        "norm_K2": norm_k2,
        "rho_transient": rho,
        "projector_error": projector_error,
        "kernel_error": kernel_error,
        "gamma_fixed_error": gamma_fixed_error,
        "commutator_error": commutator_error,
    }


def identity_evolution(x: np.ndarray) -> np.ndarray:
    """Minimal Psi for smoke tests."""
    return x


if __name__ == "__main__":
    C = locked_e47_casimir()
    cert = certify_locked_e47(C)

    rng = np.random.default_rng(470125)
    inputs = rng.normal(size=(4, DIM)) + 1j * rng.normal(size=(4, DIM))
    result = recursive_step(C, inputs, identity_evolution)

    print("E47 certificate:", "PASS" if cert["PASS"] else "FAIL")
    print("spec(C):", cert["spectrum_C"])
    print("rank(Lambda):", cert["rank_Lambda"])
    print("Omega_c:", cert["Omega_c"])
    print("spec+(K^2):", cert["positive_spectrum_K2"])
    print("gap(K^2):", cert["gap_K2"])
    print("||K^2||_2:", cert["norm_K2"])
    print("epsilon:", cert["epsilon"])
    print("rho_transient:", cert["rho_transient"])
    print("certainty Omega:", result["Ω"])
    print("contractions:", result["contractions"])
    print("final residual ||K M_pre||:", result["residual"])
    print("post-collapse ||K M||:", np.linalg.norm(result["K"] @ result["M"]))
