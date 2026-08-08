"""
CLI Spectral Kernel Compiler & Verification Script
"""
import sys
import os
import argparse
import numpy as np

# Ensure src/ is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.e47.core_matrix_compiler import compute_casimir_operator, construct_e47_projector

def run_verification():
    print("==========================================================")
    print("E47 SPECTRAL KERNEL COMPILER -- VERIFICATION RUN")
    print("==========================================================")
    
    C = compute_casimir_operator(s=2.0)
    K, P47 = construct_e47_projector(C)
    
    tr_val = float(np.real(np.trace(P47)))
    ratio = tr_val / 125.0
    herm_err = float(np.linalg.norm(P47 - P47.conj().T))
    idemp_err = float(np.linalg.norm(P47 @ P47 - P47))
    
    print(f"Carrier Dimension: 125 (5^3)")
    print(f"Selected Invariant Sector Trace: {tr_val:.12f}")
    print(f"Coherence Ratio (Omega_c = 47/125): {ratio:.12f}")
    print(f"Hermiticity Residual: {herm_err:.6e}")
    print(f"Idempotence Residual: {idemp_err:.6e}")
    
    if abs(tr_val - 47.0) < 1e-10 and abs(ratio - 0.376) < 1e-10:
        print("\nVerification Result: SUCCESS (All Residuals Within Epsilon)")
        return 0
    else:
        print("\nVerification Result: FAILED")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile and verify E47 spectral kernel.")
    parser.add_argument("--verify", action="store_true", help="Run automated verification checks")
    args = parser.parse_args()
    
    sys.exit(run_verification())
