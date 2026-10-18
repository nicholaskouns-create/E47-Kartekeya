# E47: tensor validation and fixed-point hardware implementation

The E47 invariant kernel is implemented across complex128 tensor computation, a quantum circuit simulator, and a fixed-point RTL datapath.

## Exact construction

On H = V₂ ⊗ V₂ ⊗ V₂, dim H = 125, define

C = J_total²,
K = (C − 6I)(C − 30I),
E₄₇ = ker K = 5V₂ ⊕ 2V₅,
Γ = I − K²/99144.

The kernel dimension is 47; rank K is 78. The selected dimension fraction is Ω = 47/125 = 0.376. For orthogonal projector P onto E₄₇,

‖Γᴸ − P‖₂ = (15/17)ᴸ.

The exact depth-220 value is 1.0998014527879737 × 10⁻¹². The ideal bound first falls below 10⁻¹⁵ at depth 276. Finite-precision implementations have their own arithmetic floor.

## Executed tensor and quantum validation

The delivered torch_validation.py independently constructs the spin matrices, total Casimir, selector, projector and contraction in PyTorch complex128. All 21 checks passed. These include kernel dimension, selector rank, projector identities, spectral norms at every depth 0 through 220, selected-state leakage, compressed SU(2) commutators, rotation equivariance, analytical/autograd gradient agreement, finite directional differences and 1,000 random-state contractions.

Across all 221 depths the largest absolute difference between measured operator norm and exact contraction law was 4.440892098500626 × 10⁻¹⁶. The measured depth-220 error was 1.100072361068516 × 10⁻¹². Numeric residuals and tolerances are in torch_validation.json.

The companion quantum implementation passed 36 checks using NumPy/SciPy and Qiskit. Its actual seven-qubit basis transformation and eight-qubit membership instrument are included as QPY and synthesized OpenQASM 3. A flagged attenuation instrument followed by conditional reset implements the deterministic density channel

E(ρ) = AρA† + Tr[(I − A†A)ρ]τ,

where A is Γ on the 125-state carrier and zero on three unused states, and τ is a selected E47 state. The channel preserves trace and every E47 density matrix. Γ itself acts on amplitudes; the density channel includes the reset contribution.

## Fixed-point RTL datapath

rtl/e47_contraction_filter.v implements the same amplitude filter in packed coupled coordinates, ordered by (j,j12,m), on 32-bit signed Q8.24 complex coordinates. The sectors occupy:

| j | Packed indices | Exact Γ factor |
|---|---|---|
| 0 | 0 | 103/153 |
| 1 | 1–9 | 10825/12393 |
| 2 | 10–34 | 1 |
| 3 | 35–62 | 15/17 |
| 4 | 63–89 | 9943/12393 |
| 5 | 90–111 | 1 |
| 6 | 112–124 | −15/17 |
| Unused | 125–127 | 0 |

Selected amplitudes pass unchanged, including full-scale signed values. Each other coefficient is quantized toward zero. The Q24 magnitude of 15/17 is 0x00E1E1E1, giving a complement coefficient bound of 0.882352888584137. Products use 64 bits and truncate toward zero, preventing arithmetic rounding from enlarging complement amplitudes. This fixed-point bound applies per filtering pass, while the continuous exact law describes the ideal operator.

One coordinate is accepted per enabled clock. Outputs have one-clock pipeline latency and an explicit validity signal. Indices 0 through 127 delimit a full frame; enable bubbles are supported. kernel_locked updates at the frame's final output and indicates that all complement real and imaginary output coordinates are within 256 integer units, or 2⁻¹⁶ in physical Q8.24 units. It is a threshold indication, not an exact mathematical kernel certificate.

All 768 accepted complex outputs across six frames matched the independent integer oracle exactly in Icarus Verilog 12.0. The testbench exercises random full-range inputs, protected-sector preservation, small residuals, imaginary-only residuals, signed extremes, enable gaps and invalid coordinate ordering. The frame indications were 0,1,1,0,0,0 as expected.

The datapath consumes coupled coordinates. A product-coordinate system must supply the W transformation and W† reconstruction externally; those transformations are included in the quantum and numerical package. The RTL implements amplitude filtering. It does not itself implement a quantum density-channel reset.

## Execution and realization

Run the Python/Qiskit checks with e47_corrected.py. Run the independent tensor checks with torch_validation.py. With Icarus Verilog on PATH, run build_rtl_validation.py to regenerate coefficients, compile the RTL and execute the integer comparison. Optional IVERILOG, VVP and IVERILOG_BASE environment variables support locally extracted simulator installations.

The RTL is technology neutral. Simulation is complete. Technology-library synthesis, timing closure, area/power characterization, placement/routing, and 7 nm sign-off have not been executed. No quantum hardware execution is claimed.
