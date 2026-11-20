# E47 runtime evidence

ITGC-AI-01 and ITGC-AI-02 use `verify_runtime.py`. Supply approved deployment SHA-256 values through a trusted inventory. The script binds each audit to the bytes it reads, emits JSON on standard output and exits nonzero if either control fails.

```sh
python tools/governance/verify_runtime.py \
  --weights model.pt --weights-sha256 "$APPROVED_CHECKPOINT_SHA256" \
  --policy policy.pyz --policy-sha256 "$APPROVED_POLICY_SHA256" \
  --atol "$APPROVED_ABSOLUTE_TOLERANCE" --rtol "$APPROVED_RELATIVE_TOLERANCE"
```

Use Python 3.10+ and a supported PyTorch release with `weights_only=True`. Input is a state dictionary, optionally under the `state_dict` key. Every entry must be a dense 125 × 125 `weight` or 125-entry `bias`, named directly or with a module prefix. The verifier uses the descending orthonormal spin basis and checks both cross blocks in spectral norm after dequantizing supported quantized tensors. Packed or unclassified entries fail closed. Supply an isolated artifact and approved limits for the covered model. Record the loaded graph, basis, nonlinear and attention behavior, and checkpoint deployment binding separately.

Build the audit-capable policy artifact with [auth-kernel's policy probe builder](https://github.com/nicholaskouns-create/auth-kernel/blob/main/tools/build_policy_probe.py). The verifier launches the pinned bytes with an isolated Python import path and fixture ledger, calls the policy's executable audit entry point, and independently compares the returned decisions for eight cases. Run only a trusted executable verified against the approved digest. A production audit requires this probe to exercise the same packaged policy that is deployed and an independent record of that correspondence. This fixture protocol checks selected decisions and does not establish exhaustive binary equivalence or service operating effectiveness.

ITGC-AI-03 uses [the finite-window and noise-budget calculation](buoy_lemma.py) and requires measured evidence at the actual output gate and configured reset boundary. [Control specification](../../docs/governance/E47_DETERMINISTIC_AI_GOVERNANCE_COMPLETE.md)
