"""E47 Validation Results and Spectral Analysis.

This module contains the canonical validation data and results for the E47
quantum spin system, including Casimir spectrum multiplicities, projector
properties, and quantum channel characteristics.
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class E47ValidationResults:
    """Canonical E47 system validation results.
    
    Attributes
    ----------
    carrier_dimension : int
        Dimension of the full Hilbert space (d³ for three spin-2 systems).
    casimir_spectrum_multiplicities : dict[str, int]
        Multiplicities of Casimir operator eigenvalues.
    kernel_dimension : int
        Dimension of E47 kernel subspace.
    coherence_fraction : float
        Actual coherence fraction (kernel_dim / carrier_dim).
    expected_coherence_fraction : float
        Theoretical coherence fraction.
    projector_idempotence_spectral_norm : float
        ||P² - P||₂ error (should be ~0).
    projector_hermiticity_spectral_norm : float
        ||P - P†||₂ error (should be 0).
    kernel_action_spectral_norm : float
        ||KP||₂ error (should be ~0).
    commutator_C_P_spectral_norm : float
        ||[C, P]||₂ error (should be ~0).
    K2_smallest_nonzero_eigenvalue : float
        Smallest non-zero eigenvalue of K².
    K2_largest_eigenvalue : float
        Largest eigenvalue of K².
    contraction_epsilon : float
        Contraction parameter for dephasing channel.
    transient_spectral_radius : float
        Spectral radius of time-evolved operator.
    quantum_filter_time : float
        Time parameter for quantum filter.
    kraus_completeness_spectral_norm : float
        ||M₀†M₀ + M₁†M₁ - I||₂ error (should be ~0).
    single_random_state_success_probability : float
        Success probability for single random state.
    postselected_fidelity_to_E47_projection : float
        Fidelity of postselected state to E47 projection.
    haar_average_success_probability : float
        Average success probability over Haar-random states.
    ideal_asymptotic_average_success_probability : float
        Theoretical asymptotic limit.
    """
    carrier_dimension: int
    casimir_spectrum_multiplicities: Dict[str, int]
    kernel_dimension: int
    coherence_fraction: float
    expected_coherence_fraction: float
    projector_idempotence_spectral_norm: float
    projector_hermiticity_spectral_norm: float
    kernel_action_spectral_norm: float
    commutator_C_P_spectral_norm: float
    K2_smallest_nonzero_eigenvalue: float
    K2_largest_eigenvalue: float
    contraction_epsilon: float
    transient_spectral_radius: float
    quantum_filter_time: float
    kraus_completeness_spectral_norm: float
    single_random_state_success_probability: float
    postselected_fidelity_to_E47_projection: float
    haar_average_success_probability: float
    ideal_asymptotic_average_success_probability: float

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return asdict(self)

    def validate_projector_properties(self) -> dict[str, bool]:
        """Validate that projector properties meet theoretical requirements.
        
        Returns
        -------
        validation : dict[str, bool]
            Boolean flags indicating whether each property is valid
            (within numerical tolerance).
        """
        TOLERANCE = 1e-10
        
        return {
            "is_idempotent": self.projector_idempotence_spectral_norm < TOLERANCE,
            "is_hermitian": self.projector_hermiticity_spectral_norm < TOLERANCE,
            "kernel_orthogonal": self.kernel_action_spectral_norm < TOLERANCE,
            "commutes_with_C": self.commutator_C_P_spectral_norm < TOLERANCE,
            "kraus_complete": self.kraus_completeness_spectral_norm < TOLERANCE,
            "dimension_correct": self.kernel_dimension == 47,
            "coherence_correct": abs(
                self.coherence_fraction - self.expected_coherence_fraction
            ) < 1e-6,
            "fidelity_high": self.postselected_fidelity_to_E47_projection > 0.999,
            "success_probability_consistent": abs(
                self.haar_average_success_probability
                - self.ideal_asymptotic_average_success_probability
            ) < 1e-3,
        }

    def print_summary(self) -> None:
        """Print human-readable summary of validation results."""
        print("=" * 70)
        print("E47 VALIDATION RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"\nDimensionality:")
        print(f"  Carrier dimension: {self.carrier_dimension}")
        print(f"  Kernel dimension: {self.kernel_dimension}")
        print(f"  Coherence fraction: {self.coherence_fraction:.6f}")
        print(f"    (Expected: {self.expected_coherence_fraction:.6f})")
        
        print(f"\nCasimir Spectrum Multiplicities:")
        for eigenval, mult in sorted(
            self.casimir_spectrum_multiplicities.items(),
            key=lambda x: int(x[0])
        ):
            print(f"  λ = {eigenval:>2s}: {mult:>2d}")
        
        print(f"\nProjector Properties (Spectral Norms):")
        print(f"  ||P² - P||₂: {self.projector_idempotence_spectral_norm:.4e}")
        print(f"  ||P - P†||₂: {self.projector_hermiticity_spectral_norm:.4e}")
        print(f"  ||KP||₂: {self.kernel_action_spectral_norm:.4e}")
        print(f"  ||[C, P]||₂: {self.commutator_C_P_spectral_norm:.4e}")
        
        print(f"\nK² Eigenvalue Range:")
        print(f"  Smallest nonzero: {self.K2_smallest_nonzero_eigenvalue:.2f}")
        print(f"  Largest: {self.K2_largest_eigenvalue:.2f}")
        print(f"  Ratio: {self.K2_largest_eigenvalue / self.K2_smallest_nonzero_eigenvalue:.2f}")
        
        print(f"\nChannel Parameters:")
        print(f"  Contraction ε: {self.contraction_epsilon:.6e}")
        print(f"  Spectral radius: {self.transient_spectral_radius:.6f}")
        print(f"  Filter time: {self.quantum_filter_time:.6e}")
        print(f"  Kraus completeness: {self.kraus_completeness_spectral_norm:.4e}")
        
        print(f"\nState Preparation Statistics:")
        print(f"  Single state success: {self.single_random_state_success_probability:.6f}")
        print(f"  Postselected fidelity: {self.postselected_fidelity_to_E47_projection:.6f}")
        print(f"  Haar-average success: {self.haar_average_success_probability:.6f}")
        print(f"    (Ideal asymptotic: {self.ideal_asymptotic_average_success_probability:.6f})")
        
        print(f"\nValidation Status:")
        validation = self.validate_projector_properties()
        all_pass = all(validation.values())
        
        for prop, is_valid in validation.items():
            status = "✓ PASS" if is_valid else "✗ FAIL"
            print(f"  {status}: {prop}")
        
        print("\n" + "=" * 70)
        if all_pass:
            print("ALL VALIDATIONS PASSED ✓")
        else:
            print("SOME VALIDATIONS FAILED ✗")
        print("=" * 70)


# Canonical E47 validation data
CANONICAL_E47_RESULTS = E47ValidationResults(
    carrier_dimension=125,
    casimir_spectrum_multiplicities={
        "0": 1,
        "2": 9,
        "6": 25,
        "12": 28,
        "20": 27,
        "30": 22,
        "42": 13,
    },
    kernel_dimension=47,
    coherence_fraction=0.376,
    expected_coherence_fraction=0.376,
    projector_idempotence_spectral_norm=1.6202201482531093e-14,
    projector_hermiticity_spectral_norm=0.0,
    kernel_action_spectral_norm=3.096217692088502e-13,
    commutator_C_P_spectral_norm=2.1299858582432198e-13,
    K2_smallest_nonzero_eigenvalue=11663.99999999996,
    K2_largest_eigenvalue=186624.00000000058,
    contraction_epsilon=5.358367626886129e-06,
    transient_spectral_radius=0.9375000000000004,
    quantum_filter_time=0.0004286694101508931,
    kraus_completeness_spectral_norm=5.445947593057743e-14,
    single_random_state_success_probability=0.32971167069371565,
    postselected_fidelity_to_E47_projection=0.9999654487088581,
    haar_average_success_probability=0.3760117176655198,
    ideal_asymptotic_average_success_probability=0.376,
)


if __name__ == "__main__":
    CANONICAL_E47_RESULTS.print_summary()
