# Software-in-the-loop comparison

The workload projects noisy three-spin amplitudes into E47. A NumPy float64 backend uses dense eigendecomposition. A separately compiled C++ float32 backend applies a sparse Richardson iteration. A fixed-point payload crosses the audit boundary. Trials use the same seeded inputs and fault scenario for every detector. The eight scenarios include clean runs, axis order, root selection, two calibration drift severities, early termination, wrong-job replay, and a decoder error after the audit point. Each scenario contains 600 seeded input draws. This is simulation with targeted fault injection. The injected scenarios have no estimated field frequencies.

The policy tolerance is $10^{-3}$ in the physical norm. Leakage is distance to E47. Wrong output is distance to the intended projection of the requested input. An independently assembled orthonormal spin-ladder operator provides the numerical reference for both labels. The exact audit computes $\|Kx\|^2$ over integers in the scaled native basis with a checked accumulator bound and exact threshold arithmetic. It accepts only when $\|Kx\|\le108\tau$, rejects when $\|Kx\|>432\tau$, and otherwise returns inconclusive. Inconclusive results block automatic acceptance. The benchmark checks the mathematical basis conversion numerically before running.

| Detector | Unsafe leakage accepted, upstream | Unsafe leakage accepted, downstream | Clean payloads blocked | Safe small-drift payloads blocked | Wrong-job outputs accepted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Cross-backend agreement | 2400/2400 | 592/592 | 0/600 | 0/600 | 600/600 |
| Shared-spec consistency check | 2400/2400 | 592/592 | 0/600 | 0/600 | 600/600 |
| Norm screen | 2400/2400 | 592/592 | 0/600 | 0/600 | 600/600 |
| Independent exact $K$ | 0/2400 | 592/592 | 0/600 | 164/600 | 600/600 |
| Independent projector | 0/2400 | 592/592 | 0/600 | 0/600 | 600/600 |
| Independent reference replay | 0/2400 | 592/592 | 0/600 | 0/600 | 0/600 |

The upstream columns cover layout, wrong root, large operator drift, and early stop. The downstream decoder swap corrupts the delivered vector after all detectors inspect it. Reference replay has trusted input and checks output correctness. The shared-spec check is an executable baseline for checking the configured relation. It shares the faulted transform and input with the producers. The independent projector and replay use the intended specification and form stronger cross-checks.

On the upstream faults, the paired difference versus shared-spec consistency and backend agreement was 2,400 fewer unsafe acceptances. The independent projector achieved the same leakage detection and blocked 164 fewer safe small-drift payloads. The exact residual provides a sound acceptance rule for observed bytes by construction. The run provides evidence for independent specification and correct audit placement, with no observed reduction beyond the independent projector for leakage or independent replay for correctness. The 600 wrong-job acceptances are expected because those payloads lie inside E47. The results do not establish field reliability, hardware portability, or a general advantage over existing formal or empirical methods.

The complete counts are in [benchmark-results.json](benchmark-results.json). Reproduce with make benchmark. The random seed is 470125. No test of statistical significance is reported across fault classes because the class mixture is fixed by design and the injected fault parameters are shared within each class.

Related primary literature on correlated failures in independent implementations is [Knight and Leveson, 1986](https://doi.org/10.1109/TSE.1986.6312924).
