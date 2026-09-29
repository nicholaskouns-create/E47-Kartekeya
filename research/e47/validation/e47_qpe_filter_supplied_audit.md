# E47 QPE filter — supplied audit transcript

Source: user submission, 29 September 2026. The Python source and output below are preserved as supplied, separated so the script remains executable. This transcript was not regenerated during upload.

Script: [e47_qpe_filter_proof.py](e47_qpe_filter_proof.py)

Dependencies: NumPy and SciPy.

Run from the repository root:

```bash
python research/e47/validation/e47_qpe_filter_proof.py
```

## Supplied output

```text
=========================================================
      E47 QUANTUM PHASE ESTIMATION FILTER AUDIT          
=========================================================
Carrier Space Dimension        : 125
Evaluation Register Qubits     : 6 (dim 64)
Eigenphase Discretization Step : dt = 2π / 64
Classical Subspace Overlap     : 0.4025587456
QPE Post-Selection Success Prob: 0.4025587456
Probability Discrepancy        : 2.22e-16
Post-Filtered State Fidelity   : 1.000000000000
Kernel Residual ||K * psi||    : 1.54e-14

QPE Measurement Distribution on Ancilla Register:
  λ =  0 (bin: |000000⟩) :   1.52%
  λ =  2 (bin: |000010⟩) :   5.84%
  λ =  6 (bin: |000110⟩) :  17.50%  <-- FILTER TARGET (E47)
  λ = 12 (bin: |001100⟩) :  22.69%
  λ = 20 (bin: |010100⟩) :  19.92%
  λ = 30 (bin: |011110⟩) :  22.76%  <-- FILTER TARGET (E47)
  λ = 42 (bin: |101010⟩) :   9.77%
=========================================================
```
