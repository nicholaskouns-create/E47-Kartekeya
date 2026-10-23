# Mnemosyne Python Codex · bounded validation

Source: user-provided 96-page PDF, `Mnemosyne Python Codex(5).pdf`; SHA-256 `35ac62a8d677c1f574b1abe1467474828ccda3c2777ffe8c988266ec2491d303`.

Method: independently reconstruct spin-2 generators using NumPy, form the 125-dimensional triple tensor Casimir, diagonalize using SciPy, and verify the foundational claims. The PDF includes multiple concatenated code fragments and prose, so it was **not** executed wholesale.

| Check | Result |
|---|---|
| Triple tensor dimension 125 | PASS |
| Casimir multiplicities [1,9,25,28,27,22,13] | PASS |
| E47 rank 47 | PASS |
| Orthogonal projector idempotence | PASS |
| Nonzero K² spectral gap 11664 | PASS |
| Gamma contraction factor 15/17 | PASS |
| Gamma fixes the kernel | PASS |

**7/7 PASS.** Projector idempotence Frobenius residual: approximately `1.15e-14`; contraction factor `0.8823529411764706`.

This is a focused mathematical reproduction, not a claim that every page, simulation, physical extrapolation, or theorem in the Codex has been validated. The original PDF is not included in this GitHub change.
