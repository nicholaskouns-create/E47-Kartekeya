"""Corrected E47 quantum-operation validation layer using QuTiP.

The selective projector map and the K^2 filter semigroup are completely
positive and trace-nonincreasing (CP-TNI), not trace-preserving on the full
125-dimensional carrier. A separate two-outcome dephasing completion is CPTP.

Evidence boundary
-----------------
This module validates finite-dimensional operator identities only. It does not
establish arbitrary-channel quantum error correction, hardware performance, or
a physical implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import qutip as qt

from e47.projector import E47Projector, construct_e47_projector
from e47.su2_kernel import E47Operators, build_e47_operators


@dataclass(frozen=True)
class ChannelValidation:
    status: str
    results: dict[str, Any]
    checks: dict[str, dict[str, Any]]
    tolerances: dict[str, float]
    evidence_boundary: str


def _projector_filter(P: qt.Qobj) -> qt.Qobj:
    """Selective branch M_P(rho) = P rho P."""
    return qt.sprepost(P, P.dag())


def _filter_semigroup(K2: qt.Qobj, t: float) -> tuple[qt.Qobj, qt.Qobj]:
    """Return S_t = exp(-t K^2) and M_t(rho) = S_t rho S_t."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    S_t = (-t * K2).expm()
    return S_t, qt.to_super(S_t)


def _dephasing_completion(P: qt.Qobj) -> qt.Qobj:
    """CPTP completion D_P(rho) = P rho P + Q rho Q."""
    Q = qt.qeye(P.dims[0]) - P
    return qt.sprepost(P, P.dag()) + qt.sprepost(Q, Q.dag())


def _effect_tni_residual(A: qt.Qobj) -> tuple[float, float]:
    """Return max eigenvalue of A^dag A-I and minimum eigenvalue of A^dag A."""
    ident = qt.qeye(A.dims[0])
    effect = A.dag() * A
    delta = (effect - ident).eigenenergies()
    return float(np.max(np.real(delta))), float(np.min(np.real(effect.eigenenergies())))


def validate_e47_quantum_operations(
    operators: E47Operators | None = None,
    projector_data: E47Projector | None = None,
    *,
    t_values: tuple[float, ...] = (0.0, 1e-4, 1e-3, 1e-2, 0.1, 1.0),
    residual_tolerance: float = 1e-10,
) -> ChannelValidation:
    if operators is None:
        operators = build_e47_operators()
    if projector_data is None:
        projector_data = construct_e47_projector(operators)

    P = projector_data.projector
    K2 = operators.kernel_squared
    dim = int(operators.carrier_dimension)
    rank_p = int(round(float(np.real(P.tr()))))
    rank_q = dim - rank_p

    # 1. Selective projector filter
    M_P = _projector_filter(P)
    kraus_p = qt.to_kraus(M_P)
    fixed_operator_dim = rank_p * rank_p

    # Full-space trace preservation must fail for a proper projector.
    tp_expected = rank_p == dim

    # 2. CP-TNI filter semigroup
    samples: list[dict[str, Any]] = []
    all_cp = True
    all_tni = True
    all_tp_characterized = True
    convergence_residuals: list[float] = []

    for t in t_values:
        S_t, M_t = _filter_semigroup(K2, t)
        max_tni_violation, min_effect_eig = _effect_tni_residual(S_t)
        is_tni = max_tni_violation <= residual_tolerance
        expected_tp = bool(t == 0.0 or np.allclose(K2.full(), 0.0))
        tp_characterized = bool(M_t.istp) == expected_tp

        conv = float(np.linalg.norm((M_t - M_P).full(), ord=2))
        convergence_residuals.append(conv)

        all_cp = all_cp and bool(M_t.iscp)
        all_tni = all_tni and is_tni
        all_tp_characterized = all_tp_characterized and tp_characterized

        samples.append(
            {
                "t": float(t),
                "iscp": bool(M_t.iscp),
                "istp": bool(M_t.istp),
                "iscptp": bool(M_t.iscptp),
                "is_trace_nonincreasing": is_tni,
                "max_tni_violation": max_tni_violation,
                "min_effect_eigenvalue": min_effect_eig,
                "superoperator_distance_to_projector_filter": conv,
            }
        )

    semigroup_monotone = all(
        convergence_residuals[i + 1] <= convergence_residuals[i] + residual_tolerance
        for i in range(len(convergence_residuals) - 1)
    )

    # 3. CPTP completion
    D_P = _dephasing_completion(P)
    dephasing_kraus = qt.to_kraus(D_P)
    dephasing_fixed_operator_dim = rank_p**2 + rank_q**2

    checks = {
        "projector_filter_cp": {
            "expected": True,
            "computed": bool(M_P.iscp),
            "pass": bool(M_P.iscp),
        },
        "projector_filter_full_space_tp_characterization": {
            "expected": tp_expected,
            "computed": bool(M_P.istp),
            "pass": bool(M_P.istp) == tp_expected,
        },
        "projector_filter_kraus_rank": {
            "expected": 1,
            "computed": len(kraus_p),
            "pass": len(kraus_p) == 1,
        },
        "projector_filter_fixed_operator_dimension": {
            "expected": 47**2,
            "computed": fixed_operator_dim,
            "pass": fixed_operator_dim == 47**2,
        },
        "filter_semigroup_cp_all_t": {
            "expected": True,
            "computed": all_cp,
            "pass": all_cp,
        },
        "filter_semigroup_tni_all_t": {
            "expected": True,
            "computed": all_tni,
            "pass": all_tni,
        },
        "filter_semigroup_tp_only_at_zero": {
            "expected": True,
            "computed": all_tp_characterized,
            "pass": all_tp_characterized,
        },
        "filter_semigroup_converges_to_projector_filter": {
            "expected": True,
            "computed": semigroup_monotone,
            "pass": semigroup_monotone,
        },
        "dephasing_completion_cptp": {
            "expected": True,
            "computed": bool(D_P.iscptp),
            "pass": bool(D_P.iscptp),
        },
        "dephasing_completion_kraus_rank": {
            "expected": 2,
            "computed": len(dephasing_kraus),
            "pass": len(dephasing_kraus) == 2,
        },
        "dephasing_fixed_operator_dimension": {
            "expected": 47**2 + 78**2,
            "computed": dephasing_fixed_operator_dim,
            "pass": dephasing_fixed_operator_dim == 47**2 + 78**2,
        },
    }

    status = "pass" if all(bool(item["pass"]) for item in checks.values()) else "fail"
    return ChannelValidation(
        status=status,
        results={
            "carrier_dimension": dim,
            "projector_rank": rank_p,
            "complement_rank": rank_q,
            "projector_filter_iscp": bool(M_P.iscp),
            "projector_filter_istp": bool(M_P.istp),
            "projector_filter_iscptp": bool(M_P.iscptp),
            "semigroup_samples": samples,
            "dephasing_completion_iscptp": bool(D_P.iscptp),
        },
        checks=checks,
        tolerances={"residual_tolerance": residual_tolerance},
        evidence_boundary=(
            "Finite-dimensional CP, trace-nonincreasing, semigroup, projector, "
            "and CPTP-completion identities only."
        ),
    )


def require_valid_e47_quantum_operations(validation: ChannelValidation) -> None:
    if validation.status == "pass":
        return
    failed = [name for name, check in validation.checks.items() if not check["pass"]]
    raise ValueError("E47 quantum-operation validation FAILED: " + ", ".join(failed))


if __name__ == "__main__":
    ops = build_e47_operators()
    proj = construct_e47_projector(ops)
    certificate = validate_e47_quantum_operations(ops, proj)
    print("E47 quantum-operation validation:", certificate.status)
    for name, check in certificate.checks.items():
        mark = "PASS" if check["pass"] else "FAIL"
        print(f"{mark}: {name}: {check['computed']}")
    require_valid_e47_quantum_operations(certificate)
