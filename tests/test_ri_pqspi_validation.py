import unittest
import numpy as np
from coherence_runtime.ri_pqspi import (
    continuity_manufactured_solution,
    information_continuity_residual,
    quantum_ubuntu_threshold_check,
    run_validation,
)


class RIPQSPIValidationTests(unittest.TestCase):
    def test_manufactured_continuity_solution(self):
        rho, J, dx, dt = continuity_manufactured_solution()
        self.assertLess(information_continuity_residual(rho, J, dx, dt), 1e-3)

    def test_current_shape_is_explicit(self):
        rho = np.zeros((4, 5))
        with self.assertRaises(ValueError):
            information_continuity_residual(rho, np.zeros((2, 4, 5)), 1.0, 1.0)

    def test_ubuntu_threshold(self):
        ok, mag = quantum_ubuntu_threshold_check(
            np.array([0.1, 0.2, 0.15, 0.05]), 0.05
        )
        self.assertTrue(ok)
        self.assertTrue(np.all(mag <= 0.05))

    def test_full_validation(self):
        report = run_validation(seed=47)
        self.assertTrue(report.software_checks_pass)
        self.assertLess(report.continuity_residual, 1e-3)
        self.assertEqual(report.noisy_variances["0.00"], 0.0)


if __name__ == "__main__":
    unittest.main()
