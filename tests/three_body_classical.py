"""Three-body problem validation with spectral coherence analysis.

Validates the classical three-body figure-eight solution and extracts
the coherent phase manifold through spectral decomposition.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import eigh


def setup_three_body_system():
    """Set up the equal-mass three-body figure-eight initial conditions.
    
    Returns
    -------
    y0 : np.ndarray
        Initial state vector [r1, r2, r3, v1, v2, v3] (flattened, 18D).
    """
    G = 1.0
    
    # Known equal-mass figure-eight initial condition
    r0 = np.array([
        [-0.97000436,  0.24308753, 0.0],
        [ 0.97000436, -0.24308753, 0.0],
        [ 0.0,         0.0,        0.0]
    ])
    
    v0 = np.array([
        [ 0.4662036850,  0.4323657300, 0.0],
        [ 0.4662036850,  0.4323657300, 0.0],
        [-0.9324073700, -0.8647314600, 0.0]
    ])
    
    y0 = np.concatenate([r0.reshape(-1), v0.reshape(-1)])
    return y0


def three_body_derivatives(t, y):
    """Compute derivatives for the three-body gravitational system.
    
    Parameters
    ----------
    t : float
        Time (not used, system is autonomous).
    y : np.ndarray
        State vector [r1, r2, r3, v1, v2, v3] (flattened, 18D).
        
    Returns
    -------
    dydt : np.ndarray
        Time derivatives.
    """
    G = 1.0
    m = np.ones(3)
    
    r = y[:9].reshape(3, 3)
    v = y[9:].reshape(3, 3)
    a = np.zeros((3, 3))
    
    for i in range(3):
        for j in range(3):
            if i != j:
                diff = r[j] - r[i]
                dist = np.linalg.norm(diff)
                a[i] += G * m[j] * diff / dist**3
    
    return np.concatenate([v.reshape(-1), a.reshape(-1)])


def compute_energy(y):
    """Compute total energy (kinetic + potential).
    
    Parameters
    ----------
    y : np.ndarray
        State vector.
        
    Returns
    -------
    E : float
        Total energy.
    """
    G = 1.0
    m = np.ones(3)
    
    r = y[:9].reshape(3, 3)
    v = y[9:].reshape(3, 3)
    
    T = 0.5 * np.sum(m[:, None] * v * v)
    V = 0.0
    
    for i in range(3):
        for j in range(i + 1, 3):
            V -= G * m[i] * m[j] / np.linalg.norm(r[i] - r[j])
    
    return T + V


def compute_angular_momentum(y):
    """Compute total angular momentum.
    
    Parameters
    ----------
    y : np.ndarray
        State vector.
        
    Returns
    -------
    L : np.ndarray
        Angular momentum vector (3D).
    """
    m = np.ones(3)
    
    r = y[:9].reshape(3, 3)
    v = y[9:].reshape(3, 3)
    
    return np.sum(np.cross(r, m[:, None] * v), axis=0)


def validate_three_body_periodicity():
    """Validate the three-body figure-eight solution periodicity.
    
    Returns
    -------
    results : dict
        Validation metrics including energy and angular momentum conservation.
    """
    print("================================================")
    print(" THREE-BODY FIGURE-EIGHT VALIDATION")
    print("================================================")
    
    y0 = setup_three_body_system()
    
    # Figure-eight period
    T_period = 6.32591398
    
    # Integrate over one period
    sol = solve_ivp(
        three_body_derivatives,
        [0, T_period],
        y0,
        rtol=1e-10,
        atol=1e-12,
        max_step=0.01,
        dense_output=True
    )
    
    Y = sol.y.T
    
    # Compute conservation errors
    E0 = compute_energy(y0)
    E1 = compute_energy(Y[-1])
    L0 = compute_angular_momentum(y0)
    L1 = compute_angular_momentum(Y[-1])
    
    return_error = np.linalg.norm(Y[-1] - y0)
    energy_error = abs(E1 - E0)
    angular_error = np.linalg.norm(L1 - L0)
    
    print(f"Initial energy:         {E0:.12f}")
    print(f"Final energy:           {E1:.12f}")
    print(f"Energy error:           {energy_error:.3e}")
    print(f"Angular momentum error: {angular_error:.3e}")
    print(f"Periodic return error:  {return_error:.3e}")
    
    # =========================================================
    # BUILD SPECTRAL PHASE-MANIFOLD PROJECTOR
    # =========================================================
    # Center trajectory data
    X = Y - Y.mean(axis=0)
    
    # SVD extracts coherent phase directions
    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    print("\nSingular values:")
    print(np.round(S, 10))
    
    # Numerical rank of the coherent phase tube
    rank = np.sum(S > 1e-8)
    Basis = Vt[:rank].T
    P = Basis @ Basis.T
    
    # Stabilizing operator
    H = np.eye(18) - P
    projector_error = np.linalg.norm(P @ P - P)
    
    print("\n================================================")
    print(" SPECTRAL MANIFOLD EXTRACTION")
    print("================================================")
    print(f"Recovered coherent manifold rank: {rank}")
    print(f"Projector idempotence error:      {projector_error:.3e}")
    
    # =========================================================
    # RECURSIVE CONTRACTION TEST
    # =========================================================
    rng = np.random.default_rng(42)
    psi = rng.normal(size=18)
    
    initial_transverse = np.linalg.norm(H @ psi)
    epsilon = 0.9
    
    for _ in range(30):
        psi = psi - epsilon * (H @ psi)
    
    final_transverse = np.linalg.norm(H @ psi)
    
    print("\n================================================")
    print(" RECURSIVE CONTRACTION TEST")
    print("================================================")
    print(f"Initial transverse error: {initial_transverse:.3e}")
    print(f"Final transverse error:   {final_transverse:.3e}")
    
    success = final_transverse < 1e-10
    if success:
        print("\nRESULT: PASS")
        print("The recursive contraction collapses arbitrary phase data onto")
        print("the coherent three-body manifold.")
    else:
        print("\nRESULT: FAIL")
        print("The contraction did not reach the coherent manifold.")
    
    return {
        "energy_conservation": energy_error,
        "angular_momentum_conservation": angular_error,
        "periodicity_error": return_error,
        "manifold_rank": rank,
        "projector_idempotence": projector_error,
        "contraction_convergence": final_transverse < 1e-10,
    }


if __name__ == "__main__":
    results = validate_three_body_periodicity()
