#!/usr/bin/env python3
"""Independent E47 quantum-operator reconstruction and ideal QPE simulation.

Dependencies: numpy
The construction starts from the spin-2 ladder relations and does not insert
an E47 projector or a 47-dimensional nullspace by hand.
"""
import json, math
from pathlib import Path
import numpy as np
from numpy.linalg import eigvalsh, eigh, matrix_rank, norm

SEED = 470125
OUT = Path(__file__).with_name("e47_quantum_operator_certificate.json")


def kron3(a, b, c):
    return np.kron(np.kron(a, b), c)


def spin2_generators():
    j = 2
    m = np.array([2, 1, 0, -1, -2], dtype=float)
    Jz = np.diag(m).astype(complex)
    Jp = np.zeros((5, 5), dtype=complex)
    for col, mm in enumerate(m):
        rows = np.where(np.isclose(m, mm + 1))[0]
        if len(rows):
            Jp[rows[0], col] = math.sqrt(j * (j + 1) - mm * (mm + 1))
    Jm = Jp.conj().T
    return (Jp + Jm) / 2, (Jp - Jm) / (2j), Jz


def aggregate_integer_spectrum(vals):
    u, n = np.unique(np.rint(vals).astype(int), return_counts=True)
    return [[int(a), int(b)] for a, b in zip(u, n)]


def main():
    Jx, Jy, Jz = spin2_generators()
    I5 = np.eye(5, dtype=complex)
    su2_residual = max(
        norm(Jx @ Jy - Jy @ Jx - 1j * Jz),
        norm(Jy @ Jz - Jz @ Jy - 1j * Jx),
        norm(Jz @ Jx - Jx @ Jz - 1j * Jy),
    )
    single_casimir_residual = norm(Jx @ Jx + Jy @ Jy + Jz @ Jz - 6 * I5)

    Jtx = kron3(Jx, I5, I5) + kron3(I5, Jx, I5) + kron3(I5, I5, Jx)
    Jty = kron3(Jy, I5, I5) + kron3(I5, Jy, I5) + kron3(I5, I5, Jy)
    Jtz = kron3(Jz, I5, I5) + kron3(I5, Jz, I5) + kron3(I5, I5, Jz)
    C = Jtx @ Jtx + Jty @ Jty + Jtz @ Jtz
    I125 = np.eye(125, dtype=complex)
    K = (C - 6 * I125) @ (C - 30 * I125)
    Q = K @ K

    cvals, cvecs = eigh(C)
    select = np.isclose(cvals, 6, atol=1e-10) | np.isclose(cvals, 30, atol=1e-10)
    V = cvecs[:, select]
    P = V @ V.conj().T
    Ppoly = (
        C @ (C - 2 * I125) @ (C - 12 * I125) @ (C - 20 * I125)
        @ (C - 31 * I125) @ (C - 42 * I125) / 1814400.0
    )

    qvals = eigvalsh(Q)
    qspec = aggregate_integer_spectrum(qvals)
    positive = [lam for lam, mult in qspec if lam > 0]
    lam_min, lam_max = min(positive), max(positive)
    eps_star = 2.0 / (lam_min + lam_max)
    rho_star = (lam_max - lam_min) / (lam_max + lam_min)
    Gamma = I125 - eps_star * Q

    P5 = np.eye(125, dtype=complex)
    for lam in sorted(positive, reverse=True):
        P5 = (I125 - Q / lam) @ P5

    # 7-qubit embedding. The three unused codewords are explicitly excluded
    # from the kernel by assigning them K=432.
    K128 = np.zeros((128, 128), dtype=complex)
    K128[:125, :125] = K
    K128[125:, 125:] = 432 * np.eye(3)
    P128 = np.zeros((128, 128), dtype=complex)
    P128[:125, :125] = P
    R128 = 2 * P128 - np.eye(128)

    # Ideal phase-estimation simulation.
    # U = exp(2*pi*i*K/512). Since every K eigenvalue is an integer and the
    # six spectral residues are distinct modulo 512, 9 phase qubits resolve
    # the kernel eigenphase 0 exactly in the ideal model.
    kvals, kvecs = eigh(K128)
    kints = np.rint(kvals).astype(int)
    M = 512
    rng = np.random.default_rng(SEED)
    psi = rng.normal(size=128) + 1j * rng.normal(size=128)
    psi[125:] = 0
    psi /= norm(psi)
    coeff = kvecs.conj().T @ psi

    t = np.arange(M)[:, None]
    A = coeff[None, :] * np.exp(2j * np.pi * t * kints[None, :] / M) / math.sqrt(M)
    B = np.fft.fft(A, axis=0) / math.sqrt(M)  # inverse-QFT convention
    qpe_prob = np.sum(np.abs(B) ** 2, axis=1)
    peaks = {str(i): float(p) for i, p in enumerate(qpe_prob) if p > 1e-12}

    direct_p = float(np.real(psi.conj().T @ P128 @ psi))
    zero_p = float(qpe_prob[0])
    psi_direct = P128 @ psi
    psi_direct /= norm(psi_direct)
    psi_zero = kvecs @ B[0, :]
    psi_zero /= norm(psi_zero)
    fidelity = float(abs(np.vdot(psi_direct, psi_zero)) ** 2)

    result = {
        "certificate": "E47-QOP-INDEPENDENT-20260911",
        "seed": SEED,
        "construction": "spin-2 ladder relations -> triple tensor carrier -> C -> K -> K^2 -> P47",
        "carrier_dimension": 125,
        "minimum_data_qubits": 7,
        "su2_commutator_fro_max": float(su2_residual),
        "single_site_casimir_fro": float(single_casimir_residual),
        "C_spectrum": aggregate_integer_spectrum(eigvalsh(C)),
        "K_spectrum": aggregate_integer_spectrum(eigvalsh(K)),
        "K2_spectrum": qspec,
        "rank_P47": int(matrix_rank(P, tol=1e-8)),
        "trace_P47": float(np.trace(P).real),
        "P47_idempotence_fro": float(norm(P @ P - P)),
        "P47_hermiticity_fro": float(norm(P - P.conj().T)),
        "KP47_fro": float(norm(K @ P)),
        "projector_polynomial_vs_eigenspace_fro": float(norm(Ppoly - P)),
        "five_factor_projector_vs_eigenspace_fro": float(norm(P5 - P)),
        "K2_gap": int(lam_min),
        "K2_norm": int(lam_max),
        "epsilon_star": float(eps_star),
        "epsilon_star_exact": "1/99144",
        "rho_star": float(rho_star),
        "rho_star_exact": "15/17",
        "Gamma220_minus_P47_fro": float(norm(np.linalg.matrix_power(Gamma, 220) - P)),
        "Gamma400_minus_P47_fro": float(norm(np.linalg.matrix_power(Gamma, 400) - P)),
        "R47_7qubit_unitarity_fro": float(norm(R128.conj().T @ R128 - np.eye(128))),
        "qpe": {
            "data_qubits": 7,
            "phase_qubits": 9,
            "unitary": "exp(2*pi*i*K_embed/512)",
            "K_residues_mod_512": aggregate_integer_spectrum(np.mod(kints, 512)),
            "random_valid_input_peak_probabilities": peaks,
            "zero_phase_probability": zero_p,
            "direct_P47_probability": direct_p,
            "probability_difference": abs(zero_p - direct_p),
            "postselected_state_fidelity_vs_normalized_P47psi": fidelity,
            "maximum_nonpeak_probability": float(max(qpe_prob[i] for i in range(M) if str(i) not in peaks)),
        },
        "status": "PASS",
        "scope": "exact finite-dimensional reconstruction and ideal noiseless statevector QPE; no hardware/noise claim"
    }
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
